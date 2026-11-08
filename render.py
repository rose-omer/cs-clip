"""Highlight kliplerini CS Demo Manager (csdm) ile kaydeder, adlandırır ve birleştirir.

CSDM demoyu CS2'de bir kez açar, istenen round'lardaki kill anlarını kaydeder ve
her anı "sequence-N-tick-A-to-B.mp4" adıyla demonun klasörüne yazar. Bu modül
parçaları tick'e göre highlight'lara atar, aynı round'un parçalarını birleştirir
ve klibi çıktı klasörüne taşır.
"""

import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

from highlights import TICKRATE

SEQUENCE_RE = re.compile(r"sequence-\d+-tick-(\d+)-to-(\d+)\.mp4$", re.IGNORECASE)
TIMEOUT_LINE = "Zaman aşımı: CS2 takıldı, kapatıldı"
NOT_IN_DB = "Match not found in database"
# csdm hata satırları; çıkış kodu her zaman güvenilir değil
FAIL_MARKERS = ("Game error", "Failed to start", "is not installed", "Missing demo", "must have been analyzed",
                NOT_IN_DB, TIMEOUT_LINE)
# Ölçüm: 41 sn'lik görüntü ~135 sn sürdü (açılış + kayıt + dönüştürme). Takılan CS2'yi bu süreden sonra kapat.
START_ALLOWANCE = 180
SECONDS_PER_CLIP_SECOND = 6
# CS2'nin o parçada çökmesi/takılması: başka başlangıçla yeniden denenir. Diğer hatalar (demo yok,
# veritabanında yok, CS2 kurulu değil) her denemede aynı çıkar.
RETRYABLE = ("Game error", TIMEOUT_LINE)
RECORDING_SYSTEMS = ("CS", "HLAE")
# CSDM tek aralık kaydında "demo_gototick <başlangıç - 65>" yapar (kurulum tick'i başlangıç - 64, bir öncesine atlar).
# CS2 bu tick'ten önceki son FullPacket'i yükleyip oradan ileri oynatır.
GOTO_LEAD = 65
FULLPACKET_MARGIN = 32  # önceki FullPacket'e düşmek için hedefin paketin bu kadar önünde olması
LONG_PRE_SECONDS = 5
MAX_EXTRA_SECONDS = 12  # yeniden denemede baştan fazladan kaydedilip kesilecek en uzun süre (TGA diski şişirir)


class DemoFailed(Exception):
    """CSDM bu demoyu kaydedemedi (CS2 çöktü, başlatılamadı vb.)."""


def segments(h: dict) -> list[list[int]]:
    """Klibin kaydedilecek tick aralıkları (eski JSON'da tek aralık)."""
    return h.get("segments") or [[h["start_tick"], h["end_tick"]]]


def clip_seconds(h: dict) -> float:
    return sum(end - start for start, end in segments(h)) / TICKRATE


def select_clips(highlights: list[dict], min_score: float, limit: int = 0) -> list[dict]:
    """Skoru yeten (en fazla `limit` tane, 0 = sınırsız) klipleri demo sırasına göre döner."""
    chosen = sorted((h for h in highlights if h["score"] >= min_score), key=lambda h: h["score"], reverse=True)
    if limit:
        chosen = chosen[:limit]
    return sorted(chosen, key=lambda h: h["start_tick"])


def clip_filename(prefix: str, h: dict, player: str = "") -> str:
    """{önek}_R{round}_{etiketler}_{silah}.mp4; player (analyze.player_tag) verilirse R'den sonra p-<etiket>."""
    parts = [*([f"p-{player}"] if player else []), *h["labels"], *h.get("weapons", [])[:1]]
    tag = "_".join(re.sub(r'[<>:"/\\|?*]', "", p).replace(" ", "-") for p in parts)
    return f"{prefix}_R{h['round']:02d}_{tag}.mp4" if tag else f"{prefix}_R{h['round']:02d}.mp4"


def concat_list(paths: list[Path]) -> str:
    """ffmpeg concat demuxer listesi. Yollar mutlak: ffmpeg göreli yolu listenin klasörüne göre çözer."""
    return "\n".join("file '" + Path(p).resolve().as_posix().replace("'", "'\\''") + "'" for p in paths)


def analyze_args(csdm: Path, demo: Path) -> list[str]:
    return [str(csdm), "analyze", str(demo)]


RECORD_SIZES = {"1080p": (1920, 1080), "1440p": (2560, 1440)}
CRF_RANGE = (14, 35)


def quality_args(resolution: str = "", crf: int = 0) -> list[str]:
    """Kayıt çözünürlüğü / CRF için csdm seçenekleri; boş / 0 = CSDM'in kendi ayarı."""
    out = []
    if resolution:
        if resolution not in RECORD_SIZES:
            raise SystemExit(f"kayit_cozunurluk {' / '.join(RECORD_SIZES)} ya da boş olmalı: {resolution!r}")
        w, h = RECORD_SIZES[resolution]
        out += ["--width", str(w), "--height", str(h)]
    if crf:
        if isinstance(crf, bool) or not isinstance(crf, int) or not CRF_RANGE[0] <= crf <= CRF_RANGE[1]:
            raise SystemExit(f"kayit_crf {CRF_RANGE[0]}-{CRF_RANGE[1]} arasında ya da 0 olmalı: {crf!r}")
        out += ["--ffmpeg-crf", str(crf)]
    return out


def video_args(
    csdm: Path, demo: Path, steamid: str, rounds: list[int], pre: float, post: float, clean_hud: bool,
    quality: list[str] | tuple = (),
    system: str = "CS",
) -> list[str]:
    """Tüm round'ları tek CS2 açılışında kaydeden csdm komutu."""
    return [
        str(csdm), "video", str(demo),
        "--mode", "player", "--steamids", str(steamid), "--event", "kills",
        "--rounds", ",".join(str(r) for r in sorted(set(rounds))),
        "--start-seconds-before", str(pre), "--end-seconds-after", str(post),
        "--no-concatenate-sequences", "--recording-system", system, "--close-game-after-recording",
        "--show-only-death-notices" if clean_hud else "--no-show-only-death-notices",
        "--no-player-voices",  # sesli sohbet kliplere girmesin
        *quality,
    ]


def segment_args(
    csdm: Path, demo: Path, steamid: str, start: int, end: int, clean_hud: bool,
    quality: list[str] | tuple = (), system: str = "CS",
) -> list[str]:
    """Tek tick aralığını kendi CS2 açılışında kaydeden csdm komutu (tek atlama)."""
    return [
        str(csdm), "video", str(demo), str(start), str(end),
        "--focus-player", str(steamid),
        "--no-concatenate-sequences", "--recording-system", system, "--close-game-after-recording",
        "--show-only-death-notices" if clean_hud else "--no-show-only-death-notices",
        "--no-player-voices",  # sesli sohbet kliplere girmesin
        *quality,
    ]


def fullpacket_before(tick: int, fullpackets: list[int]) -> int | None:
    """CS2'nin demo_gototick <tick>'te yüklediği FullPacket (tick'ten önceki son paket)."""
    return max((t for t in fullpackets if t <= tick), default=None)


def retry_starts(start: int, fullpackets: list[int]) -> list[tuple[str, int]]:
    """Parça için denenecek başlangıç tick'leri: [(açıklama, tick)], ilki asıl başlangıç.

    Yeniden denemeler CS2'yi başka bir FullPacket'ten başlatır: ya hedefin önceki paketinden
    (başlangıç paketin hemen önüne çekilir) ya da birkaç saniye erken. Erken başlangıçta fazladan
    kaydedilen baş kısım sonradan kesilir; MAX_EXTRA_SECONDS'tan uzunu denenmez.
    FullPacket listesi yoksa yalnız erken başlangıç denenir; hiçbiri olmuyorsa aynı başlangıç bir kez daha.
    """
    out = [("aynı başlangıç", start)]
    window = fullpacket_before(start - GOTO_LEAD, fullpackets)
    candidates = []
    if window is not None:
        candidates.append(("önceki tam paketten", window + GOTO_LEAD - FULLPACKET_MARGIN))
    candidates.append((f"{LONG_PRE_SECONDS} sn erken", start - LONG_PRE_SECONDS * TICKRATE))
    tried = {window}
    for label, tick in candidates:
        if not 0 < start - tick <= MAX_EXTRA_SECONDS * TICKRATE or tick - GOTO_LEAD < 1:
            continue
        w = fullpacket_before(tick - GOTO_LEAD, fullpackets)
        if fullpackets and w in tried:
            continue  # aynı paketten başlar, öncekinden farkı yok
        tried.add(w)
        out.append((label, tick))
    if len(out) == 1:
        # Takılma çoğu zaman demo daha oynamadan, açılışta oluyor (NOTLAR.md); düz bir tekrar da şans.
        out.append(("aynı başlangıç, yeniden", start))
    return out


def attempts(start: int, fullpackets: list[int], system: str, hlae_fallback: bool) -> list[tuple[str, int, str]]:
    """Parçanın kayıt denemeleri: [(açıklama, başlangıç, kayıt sistemi)]."""
    out = [(label, tick, system) for label, tick in retry_starts(start, fullpackets)]
    if hlae_fallback and system != "HLAE":
        out.append(("HLAE ile", start, "HLAE"))
    return out


def retryable(err: str) -> bool:
    return any(m in err for m in RETRYABLE)


def trim_lead(path: Path, seconds: float, ffmpeg: Path) -> Path:
    """Videonun ilk `seconds` saniyesini keser (yeniden kodlar; kopyalamak anahtar kareye yuvarlar)."""
    tmp = path.with_name(path.stem + ".kesik.mp4")
    subprocess.run([str(ffmpeg), "-y", "-loglevel", "error", "-ss", f"{seconds:.3f}", "-i", str(path),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "fast",
                    "-c:a", "aac", "-b:a", "256k", str(tmp)], check=True)
    tmp.replace(path)
    return path


def kill_tree(pid: int) -> None:
    """Süreci ve açtığı her şeyi (csdm -> CS2) kapatır."""
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)


def run_streaming(cmd: list[str], env: dict | None = None, timeout: float | None = None) -> tuple[int, list[str]]:
    """Komutu çalıştırır, çıktısını satır satır gösterir ve toplar.

    timeout dolarsa süreç ağacı kapatılır ve çıktıya TIMEOUT_LINE eklenir (takılan CS2 için).
    """
    lines: list[str] = []
    timed_out = threading.Event()
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                          text=True, encoding="utf-8", errors="replace") as p:
        timer = threading.Timer(timeout, lambda: (timed_out.set(), kill_tree(p.pid))) if timeout else None
        if timer:
            timer.daemon = True
            timer.start()
        try:
            for line in p.stdout:
                line = line.rstrip()
                if line:
                    print(f"  [csdm] {line}")
                    lines.append(line)
        finally:
            if timer:
                timer.cancel()
    if timed_out.is_set():
        lines.append(TIMEOUT_LINE)
    return p.returncode, lines


def record_timeout(clips: list[dict]) -> float:
    """Kaydın en fazla sürebileceği süre: açılış payı + görüntü süresinin katı."""
    return START_ALLOWANCE + SECONDS_PER_CLIP_SECOND * sum(clip_seconds(h) for h in clips)


def failure(lines: list[str]) -> str | None:
    """csdm çıktısında hata satırı varsa onu döner."""
    return next((ln for ln in lines if any(m in ln for m in FAIL_MARKERS)), None)


def part_tick(path: Path) -> int | None:
    m = SEQUENCE_RE.search(path.name)
    return int(m.group(1)) if m else None


def assign_parts(parts: list[Path], clips: list[dict]) -> dict[int, list[Path]]:
    """Parçaları başlangıç tick'ine en yakın highlight'a atar: {klip sırası: [parçalar]}."""

    def distance(tick: int, h: dict) -> int:
        return min(0 if a <= tick <= b else min(abs(tick - a), abs(tick - b)) for a, b in segments(h))

    out: dict[int, list[Path]] = {}
    for p in sorted(parts, key=lambda p: part_tick(p) or 0):
        tick = part_tick(p)
        if tick is None:
            continue
        best = min(range(len(clips)), key=lambda i: distance(tick, clips[i]))
        out.setdefault(best, []).append(p)
    return out


def join_parts(parts: list[Path], dst: Path, ffmpeg: Path | None) -> Path:
    """Tek parça taşınır; birden çok parça ffmpeg ile (yeniden kodlamadan) birleştirilir."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if len(parts) == 1:
        shutil.move(str(parts[0]), dst)
        return dst
    if ffmpeg is None:
        raise SystemExit("Parçaları birleştirmek için ffmpeg gerekli (winget install Gyan.FFmpeg).")
    lst = dst.with_suffix(".txt")
    lst.write_text(concat_list(parts), encoding="utf-8")
    try:
        subprocess.run([str(ffmpeg), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", str(lst), "-c", "copy", str(dst)], check=True)
    finally:
        lst.unlink(missing_ok=True)
    for p in parts:
        p.unlink()
    return dst


def record_demo(
    demo: Path,
    clips: list[dict],
    steamid: str,
    prefix: str,
    out_dir: Path,
    csdm: Path,
    ffmpeg: Path | None,
    pre: float,
    post: float,
    clean_hud: bool,
    runner=run_streaming,
    env: dict | None = None,
    per_segment: bool = False,
    fallback: bool = True,
    quality: list[str] | tuple = (),
    player: str = "",
    fullpackets: list[int] | None = None,
    system: str = "CS",
    hlae_fallback: bool = False,
    wait_game=None,
) -> list[Path]:
    """Demonun kliplerini tek CS2 açılışında kaydeder; hazır klipleri atlar.

    per_segment: her tick aralığı ayrı CS2 açılışında kaydedilir. Bazı demolarda CS2 ikinci
    atlamada (bir klipten sonrakine geçerken) çöküyor ya da takılıyor; tek atlamada sorunsuz.
    Parçası kaydedilemeyen klip atlanır, diğerleri korunur.
    fallback: tek açılış çöker/takılırsa parça parça yeniden dener.
    quality: quality_args() çıktısı (çözünürlük / CRF).
    player: varsayılan oyuncu dışındakilerin klip adı etiketi (clip_filename).
    Parça parça kayıtta CS2 bir parçada çöker/takılırsa parça başka başlangıçla yeniden denenir
    (retry_starts; fullpackets: demonun FullPacket tick'leri), hlae_fallback ise son olarak HLAE ile.
    system: CSDM kayıt sistemi ("CS" ya da "HLAE").
    wait_game: her CS2 açılışından önce çağrılır; False dönerse (önceki CS2 kapanmadı) açılmaz.
    """
    if system not in RECORDING_SYSTEMS:
        raise ValueError(f"kayıt sistemi {system!r}; olabilecekler: {', '.join(RECORDING_SYSTEMS)}")
    fullpackets = fullpackets or []
    out_dir = Path(out_dir)
    targets = {i: out_dir / clip_filename(prefix, h, player) for i, h in enumerate(clips)}
    todo = [i for i, dst in targets.items() if not dst.exists()]
    for i in targets.keys() - set(todo):
        print(f"  zaten var: {targets[i].name}")
    if not todo:
        return []

    folders = {Path(demo).parent, out_dir}  # CSDM çıktı klasörü ayarını her zaman uygulamıyor

    def new_parts(since: float) -> list[Path]:
        return [p for d in folders if d.is_dir() for p in d.glob("sequence-*.mp4") if p.stat().st_mtime >= since]

    def run(cmd, timeout) -> str | None:
        code, lines = runner(cmd, env, timeout)
        err = failure(lines)
        return err or (f"csdm çıkış kodu {code}" if code else None)

    def record_segment(a: int, b: int) -> str | None:
        """Parçayı kaydeder; CS2 çöker/takılırsa başka başlangıçla yeniden dener. Hata yoksa None."""
        err = None
        tries = attempts(a, fullpackets, system, hlae_fallback)
        for n, (label, start, rec_system) in enumerate(tries):
            if n:
                print(f"  yeniden deneme {n}/{len(tries) - 1}: {label} (tick {start}, {rec_system})")
            if wait_game is not None and not wait_game():
                return err or "CS2 kapanmadı, kayıt başlatılamadı"
            before = set(new_parts(started))
            err = run(segment_args(csdm, demo, steamid, start, b, clean_hud, quality, rec_system),
                      START_ALLOWANCE + SECONDS_PER_CLIP_SECOND * (b - start) / TICKRATE)
            fresh = set(new_parts(started)) - before
            if not err:
                for p in fresh if start < a else ():
                    fix_lead(p, start, a)
                return None
            for p in fresh:  # yarım kalan denemenin parçası
                p.unlink(missing_ok=True)
            if not retryable(err):
                return err
            print(f"  ! tick {start}: {err}")
        return err

    def fix_lead(p: Path, start: int, a: int) -> None:
        """Erken başlatılan parçanın fazladan baş kısmını keser, adını asıl başlangıca çeker."""
        if ffmpeg is None:
            print(f"  ! ffmpeg yok: {p.name} baştan {(a - start) / TICKRATE:.1f} sn uzun kaldı")
            return
        trim_lead(p, (a - start) / TICKRATE, ffmpeg)
        if part_tick(p) == start:
            p.replace(p.with_name(p.name.replace(f"-tick-{start}-", f"-tick-{a}-")))

    started = time.time() - 1
    if not per_segment:
        if wait_game is not None and not wait_game():
            raise DemoFailed("CS2 kapanmadı, kayıt başlatılamadı")
        err = run(video_args(csdm, demo, steamid, [clips[i]["round"] for i in todo], pre, post, clean_hud,
                             quality, system), record_timeout([clips[i] for i in todo]))
        if err:
            if not fallback or NOT_IN_DB in err:
                raise DemoFailed(err)
            print(f"  ! Tek açılışta olmadı ({err}); her parça ayrı açılışta deneniyor.")
            for p in new_parts(started):
                p.unlink(missing_ok=True)  # yarım kalan denemenin parçaları karışmasın
            per_segment = True
    if per_segment:
        total = sum(len(segments(clips[i])) for i in todo)
        k, failed, last_err = 0, set(), None
        for i in todo:
            before = set(new_parts(started))
            for a, b in segments(clips[i]):
                k += 1
                if i in failed:
                    continue
                print(f"  parça {k}/{total} (tick {a}-{b})")
                err = record_segment(a, b)
                if err:
                    if NOT_IN_DB in err:
                        raise DemoFailed(err)
                    print(f"  ! R{clips[i]['round']} atlandı: {err}")
                    failed.add(i)
                    last_err = err
                    for p in set(new_parts(started)) - before:  # bu klibin parçaları başka klibe karışmasın
                        p.unlink(missing_ok=True)
        if len(failed) == len(todo):
            raise DemoFailed(last_err)
        todo = [i for i in todo if i not in failed]

    parts = new_parts(started)
    wanted = [clips[i] for i in todo]
    done = []
    for k, group in assign_parts(parts, wanted).items():
        dst = targets[todo[k]]
        join_parts(group, dst, ffmpeg)
        print(f"  -> {dst.name} ({len(group)} parça)")
        done.append(dst)
    for k, h in enumerate(wanted):
        if targets[todo[k]] not in done:
            print(f"  ! R{h['round']} için video çıkmadı")
    for p in new_parts(started):  # atlanan kliplerin yarım parçaları
        p.unlink(missing_ok=True)
    return done


def make_montage(paths: list[Path], out: Path, ffmpeg: Path | str | None = None) -> Path | None:
    """Klipleri ffmpeg ile tek videoda birleştirir; ffmpeg yoksa None."""
    ffmpeg = ffmpeg or shutil.which("ffmpeg")
    if ffmpeg is None or not paths:
        return None
    lst = out.with_suffix(".txt")
    lst.write_text(concat_list(paths), encoding="utf-8")
    try:
        subprocess.run([str(ffmpeg), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c", "copy", str(out)], check=True)
    finally:
        lst.unlink(missing_ok=True)
    return out
