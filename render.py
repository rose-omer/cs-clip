"""Highlight kliplerini CS Demo Manager (csdm) ile kaydeder, adlandırır ve birleştirir.

CSDM demoyu CS2'de bir kez açar, istenen round'lardaki kill anlarını kaydeder ve
her anı "sequence-N-tick-A-to-B.mp4" adıyla demonun klasörüne yazar. Bu modül
parçaları tick'e göre highlight'lara atar, aynı round'un parçalarını birleştirir
ve klibi çıktı klasörüne taşır.
"""

import re
import shutil
import subprocess
import time
from pathlib import Path

from highlights import TICKRATE

SEQUENCE_RE = re.compile(r"sequence-\d+-tick-(\d+)-to-(\d+)\.mp4$", re.IGNORECASE)
# csdm hata satırları; çıkış kodu her zaman güvenilir değil
FAIL_MARKERS = ("Game error", "Failed to start", "is not installed", "Missing demo", "must have been analyzed")


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
    """ffmpeg concat demuxer listesi."""
    return "\n".join("file '" + p.as_posix().replace("'", "'\\''") + "'" for p in paths)


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
    ]


def run_streaming(cmd: list[str], env: dict | None = None) -> tuple[int, list[str]]:
    """Komutu çalıştırır, çıktısını satır satır gösterir ve toplar."""
    lines: list[str] = []
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                          text=True, encoding="utf-8", errors="replace") as p:
        for line in p.stdout:
            line = line.rstrip()
            if line:
                print(f"  [csdm] {line}")
                lines.append(line)
    return p.returncode, lines


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
) -> list[Path]:
    """Demonun kliplerini tek CS2 açılışında kaydeder; hazır klipleri atlar."""
    out_dir = Path(out_dir)
    targets = {i: out_dir / clip_filename(prefix, h) for i, h in enumerate(clips)}
    todo = [i for i, dst in targets.items() if not dst.exists()]
    for i in targets.keys() - set(todo):
        print(f"  zaten var: {targets[i].name}")
    if not todo:
        return []

    started = time.time() - 1
    code, lines = runner(video_args(csdm, demo, steamid, [clips[i]["round"] for i in todo], pre, post, clean_hud), env)
    err = failure(lines)
    if err or code:
        raise DemoFailed(err or f"csdm çıkış kodu {code}")

    # CSDM çıktı klasörü ayarını her zaman uygulamıyor; demonun klasörüne de bak.
    folders = {Path(demo).parent, out_dir}
    parts = [p for d in folders if d.is_dir() for p in d.glob("sequence-*.mp4") if p.stat().st_mtime >= started]
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
    return done


def make_montage(paths: list[Path], out: Path, ffmpeg: Path | str | None = None) -> Path | None:
    """Klipleri ffmpeg ile tek videoda birleştirir; ffmpeg yoksa None."""
    ffmpeg = ffmpeg or shutil.which("ffmpeg")
    if ffmpeg is None or not paths:
        return None
    lst = out.with_suffix(".txt")
    lst.write_text(concat_list(paths), encoding="utf-8")
    subprocess.run(
        [str(ffmpeg), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)],
        check=True,
    )
    lst.unlink()
    return out
