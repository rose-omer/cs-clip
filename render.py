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


def clip_filename(prefix: str, h: dict) -> str:
    parts = [*h["labels"], *h.get("weapons", [])[:1]]
    tag = "_".join(re.sub(r'[<>:"/\\|?*]', "", p).replace(" ", "-") for p in parts)
    return f"{prefix}_R{h['round']:02d}_{tag}.mp4" if tag else f"{prefix}_R{h['round']:02d}.mp4"


def concat_list(paths: list[Path]) -> str:
    """ffmpeg concat demuxer listesi. Yollar mutlak: ffmpeg göreli yolu listenin klasörüne göre çözer."""
    return "\n".join("file '" + Path(p).resolve().as_posix().replace("'", "'\\''") + "'" for p in paths)


def analyze_args(csdm: Path, demo: Path) -> list[str]:
    return [str(csdm), "analyze", str(demo)]


def video_args(
    csdm: Path, demo: Path, steamid: str, rounds: list[int], pre: float, post: float, clean_hud: bool
) -> list[str]:
    """Tüm round'ları tek CS2 açılışında kaydeden csdm komutu."""
    return [
        str(csdm), "video", str(demo),
        "--mode", "player", "--steamids", str(steamid), "--event", "kills",
        "--rounds", ",".join(str(r) for r in sorted(set(rounds))),
        "--start-seconds-before", str(pre), "--end-seconds-after", str(post),
        "--no-concatenate-sequences", "--recording-system", "CS", "--close-game-after-recording",
        "--show-only-death-notices" if clean_hud else "--no-show-only-death-notices",
        "--no-player-voices",  # sesli sohbet kliplere girmesin
    ]


def segment_args(csdm: Path, demo: Path, steamid: str, start: int, end: int, clean_hud: bool) -> list[str]:
    """Tek tick aralığını kendi CS2 açılışında kaydeden csdm komutu (tek atlama)."""
    return [
        str(csdm), "video", str(demo), str(start), str(end),
        "--focus-player", str(steamid),
        "--no-concatenate-sequences", "--recording-system", "CS", "--close-game-after-recording",
        "--show-only-death-notices" if clean_hud else "--no-show-only-death-notices",
        "--no-player-voices",  # sesli sohbet kliplere girmesin
    ]


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
) -> list[Path]:
    """Demonun kliplerini tek CS2 açılışında kaydeder; hazır klipleri atlar.

    per_segment: her tick aralığı ayrı CS2 açılışında kaydedilir. Bazı demolarda CS2 ikinci
    atlamada (bir klipten sonrakine geçerken) çöküyor ya da takılıyor; tek atlamada sorunsuz.
    Parçası kaydedilemeyen klip atlanır, diğerleri korunur.
    fallback: tek açılış çöker/takılırsa parça parça yeniden dener.
    """
    out_dir = Path(out_dir)
    targets = {i: out_dir / clip_filename(prefix, h) for i, h in enumerate(clips)}
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

    started = time.time() - 1
    if not per_segment:
        err = run(video_args(csdm, demo, steamid, [clips[i]["round"] for i in todo], pre, post, clean_hud),
                  record_timeout([clips[i] for i in todo]))
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
                err = run(segment_args(csdm, demo, steamid, a, b, clean_hud),
                          START_ALLOWANCE + SECONDS_PER_CLIP_SECOND * (b - a) / TICKRATE)
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
