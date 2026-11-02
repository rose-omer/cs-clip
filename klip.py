"""cs-klip: demo -> highlight -> .mp4 klipler.

Kullanım:
  python klip.py <demo veya klasör> [--sadece-analiz] [--prova] [--ayarlar ayarlar.json]

Demo .dem, .dem.zst, .dem.gz ya da .dem.bz2 olabilir. Klasör verilirse içindeki tüm demolar işlenir.
"""

import argparse
import re
import shutil
import sys
import time
from pathlib import Path

from analyze import analyze, print_report, save_json
from config import load_config
from demofile import find_csgo_dir, open_demo
from render import (
    Console,
    ObsRecorder,
    PrintConsole,
    PrintRecorder,
    make_montage,
    render_clips,
    select_clips,
)

DEMO_SUFFIXES = (".dem", ".dem.zst", ".dem.gz", ".dem.bz2")
CSGO_SUBFOLDER = "cs-klip"  # demolar game/csgo/cs-klip/ altına kopyalanır


def collect_demos(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    found = [p for p in sorted(target.iterdir()) if p.name.lower().endswith(DEMO_SUFFIXES)]
    # Aynı demonun hem .dem hem .zst hâli varsa .dem yeter.
    names = {p.name.lower() for p in found}
    return [p for p in found if not (p.suffix != ".dem" and p.with_suffix("").name.lower() in names)]


def safe_demo_name(stem: str) -> str:
    """CS2 konsolunda sorun çıkarmayan ad (boşluk ve özel karakter yok)."""
    return re.sub(r"[^A-Za-z0-9_-]", "_", stem)


def copy_to_csgo(demo: Path, csgo_dir: Path) -> str:
    """Demoyu CS2 klasörüne güvenli adla kopyalar; playdemo için göreli yolu döner."""
    name = safe_demo_name(demo.stem)
    dst = csgo_dir / CSGO_SUBFOLDER / f"{name}.dem"
    dst.parent.mkdir(exist_ok=True)
    if not dst.exists() or dst.stat().st_size != demo.stat().st_size:
        print(f"Demo CS2 klasörüne kopyalanıyor: {dst}")
        shutil.copy2(demo, dst)
    return f"{CSGO_SUBFOLDER}/{name}"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="CS2 demodan highlight klipleri")
    ap.add_argument("hedef", type=Path, help="demo dosyası ya da demo klasörü")
    ap.add_argument("--sadece-analiz", action="store_true", help="klip kaydetme, yalnız listele")
    ap.add_argument("--prova", action="store_true", help="CS2/OBS olmadan komutları göster")
    ap.add_argument("--ayarlar", type=Path, default=Path(__file__).with_name("ayarlar.json"))
    ap.add_argument("--oyuncu", help="ayarlar.json'daki oyuncuyu geçersiz kılar")
    ap.add_argument("--min-skor", type=float, help="ayarlar.json'daki min_skor'u geçersiz kılar")
    args = ap.parse_args()

    cfg = load_config(args.ayarlar)
    player = args.oyuncu or cfg["oyuncu"]
    min_score = cfg["min_skor"] if args.min_skor is None else args.min_skor
    demos = collect_demos(args.hedef)
    if not demos:
        raise SystemExit(f"Demo bulunamadı: {args.hedef}")

    con = rec = csgo_dir = None
    if not args.sadece_analiz:
        if args.prova:
            con, rec = PrintConsole(), PrintRecorder()
        else:
            csgo_dir = Path(cfg["csgo_klasoru"]) if cfg["csgo_klasoru"] else find_csgo_dir()
            if csgo_dir is None or not csgo_dir.is_dir():
                raise SystemExit("CS2 klasörü bulunamadı. ayarlar.json içinde 'csgo_klasoru' ver "
                                 "(…\\Counter-Strike Global Offensive\\game\\csgo).")
            con = Console(cfg["netcon_port"])
            rec = ObsRecorder(cfg["obs_host"], cfg["obs_port"], cfg["obs_sifre"])

    out_dir = Path(cfg["cikti_klasoru"])
    all_clips: list[Path] = []
    for raw in demos:
        print(f"\n=== {raw.name} ===")
        demo = open_demo(raw)
        map_name, steamid, highlights = analyze(demo, player)
        print_report(map_name, highlights, min_score)
        print(f"JSON: {save_json(demo, highlights)}")

        clips = select_clips(highlights, min_score)
        if args.sadece_analiz or not clips:
            continue
        demo_cmd = copy_to_csgo(demo, csgo_dir) if csgo_dir else f"{CSGO_SUBFOLDER}/{safe_demo_name(demo.stem)}"
        all_clips += render_clips(
            clips, demo_cmd, player, out_dir, con, rec,
            load_wait=0 if args.prova else cfg["yukleme_bekle"],
            clean_hud=cfg["temiz_hud"],
            sleep=(lambda s: None) if args.prova else time.sleep,
            steamid=steamid,
        )

    if all_clips and cfg["montaj"]:
        montage = make_montage(all_clips, out_dir / "montaj.mp4")
        print(f"\nMontaj: {montage}" if montage else "\nMontaj atlandı: ffmpeg bulunamadı.")
    if all_clips:
        print(f"\n{len(all_clips)} klip hazır: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
