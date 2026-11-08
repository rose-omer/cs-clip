"""cs-klip: demo -> highlight -> .mp4 klipler.

Kullanım:
  python klip.py <demo veya klasör> [--sadece-analiz] [--prova] [--en-iyi N] [--temizle]
  python klip.py --kontrol

Demo .dem, .dem.zst, .dem.gz ya da .dem.bz2 olabilir. Klasör verilirse içindeki tüm demolar işlenir.
Kayıt CS Demo Manager ile yapılır: her demo için CS2 bir kez açılır.
"""

import argparse
import sys
from pathlib import Path

from analyze import analyze, print_report, save_json
from config import load_config
from demofile import demo_files, find_csgo_dir, open_demo, to_recycle_bin
from kontrol import demo_in_db, preflight
from onarim import ensure_repaired, is_repaired_copy, repaired_path
from render import (
    NOT_IN_DB,
    DemoFailed,
    analyze_args,
    clip_filename,
    make_montage,
    record_demo,
    run_streaming,
    select_clips,
    video_args,
)

DEMO_SUFFIXES = (".dem", ".dem.zst", ".dem.gz", ".dem.bz2")


def collect_demos(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    found = [p for p in sorted(target.iterdir())
             if p.name.lower().endswith(DEMO_SUFFIXES) and not is_repaired_copy(p)]
    # Aynı demonun hem .dem hem .zst hâli varsa .dem yeter.
    names = {p.name.lower() for p in found}
    return [p for p in found if not (p.suffix != ".dem" and p.with_suffix("").name.lower() in names)]


def clip_prefix(map_name: str, demo: Path) -> str:
    """Klip adının başı: harita + maç kodunun ilk 8 hanesi (de_anubis, 1-59cf10f2-… -> anubis_59cf10f2)."""
    code = demo.stem.split("-")[1] if demo.stem.count("-") >= 2 else demo.stem
    return f"{map_name.removeprefix('de_')}_{code[:8]}"


def csdm_analyze(tools: dict, demo: Path) -> str | None:
    """Demoyu CSDM veritabanına ekler; hata varsa mesajını döner."""
    print("  CSDM'e ekleniyor…")
    code, lines = run_streaming(analyze_args(tools["csdm"], demo), tools["env"])
    return (lines[-1] if lines else f"çıkış kodu {code}") if code else None


def print_problems(problems: list[str]) -> None:
    print("\nKayıt başlayamaz:")
    for p in problems:
        print(f"  - {p}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="CS2 demodan highlight klipleri")
    ap.add_argument("hedef", type=Path, nargs="?", help="demo dosyası ya da demo klasörü")
    ap.add_argument("--sadece-analiz", action="store_true", help="klip kaydetme, yalnız listele")
    ap.add_argument("--prova", action="store_true", help="kaydetmeden csdm komutlarını göster")
    ap.add_argument("--kontrol", action="store_true", help="yalnız kayıt öncesi kontrolleri çalıştır")
    ap.add_argument("--temizle", action="store_true", help="kaydı biten demoları Geri Dönüşüm Kutusu'na taşı")
    ap.add_argument("--ayarlar", type=Path, default=Path(__file__).with_name("ayarlar.json"))
    ap.add_argument("--oyuncu", help="ayarlar.json'daki oyuncuyu geçersiz kılar")
    ap.add_argument("--min-skor", type=float, help="ayarlar.json'daki min_skor'u geçersiz kılar")
    ap.add_argument("--en-iyi", type=int, help="maç başına en iyi N an (0 = hepsi)")
    args = ap.parse_args()

    cfg = load_config(args.ayarlar)
    csgo_dir = Path(cfg["csgo_klasoru"]) if cfg["csgo_klasoru"] else find_csgo_dir()
    if args.kontrol:
        _, problems = preflight(cfg, csgo_dir)
        print_problems(problems) if problems else print("Her şey hazır, kayıt başlayabilir.")
        raise SystemExit(1 if problems else 0)
    if args.hedef is None:
        ap.error("demo dosyası ya da klasörü gerekli")

    player = args.oyuncu or cfg["oyuncu"]
    min_score = cfg["min_skor"] if args.min_skor is None else args.min_skor
    limit = cfg["mac_basi_en_fazla"] if args.en_iyi is None else args.en_iyi
    pre, post = cfg["once_sn"], cfg["sonra_sn"]
    demos = collect_demos(args.hedef)
    if not demos:
        raise SystemExit(f"Demo bulunamadı: {args.hedef}")

    plan = []  # (demo, steamid, önek, klipler)
    for raw in demos:
        print(f"\n=== {raw.name} ===")
        demo = open_demo(raw)
        map_name, steamid, highlights = analyze(demo, player, pre, post)
        print_report(map_name, highlights, min_score)
        save_json(demo, highlights)
        clips = select_clips(highlights, min_score, limit)
        if clips:
            plan.append((demo, steamid, clip_prefix(map_name, demo), clips))
    if args.sadece_analiz or not plan:
        return

    out_dir = Path(cfg["cikti_klasoru"])
    if args.prova:
        for demo, steamid, prefix, clips in plan:
            print(f"\n{demo.name}:")
            print("  " + " ".join(video_args(Path("csdm"), demo, steamid, [c["round"] for c in clips],
                                             pre, post, cfg["temiz_hud"])))
            for c in clips:
                print(f"  -> {out_dir / clip_filename(prefix, c)}")
        return

    tools, problems = preflight(cfg, csgo_dir)
    if problems:
        print_problems(problems)
        raise SystemExit(1)

    made: list[Path] = []
    failed: list[tuple[str, str]] = []
    for n, (demo, steamid, prefix, clips) in enumerate(plan, 1):
        print(f"\n[{n}/{len(plan)}] {demo.name}: {len(clips)} klip")
        # İlk FullPacket'i bozuk demolar CS2'yi başa sararken çökertiyor; onarılmış kopyadan kaydet.
        rec, problems = ensure_repaired(demo)
        if problems:
            print(f"  ilk FullPacket onarıldı ({', '.join(problems)}) -> {rec.name}")
        err = None if demo_in_db(tools["pg_bin"], tools["db"], rec, tools["env"]) else csdm_analyze(tools, rec)
        if err:
            failed.append((demo.name, err))
            continue
        try:
            def record():
                # Onarılmış demolarda her parça ayrı açılışta: CS2 ikinci atlamada çöküyor.
                return record_demo(rec, clips, steamid, prefix, out_dir, tools["csdm"], tools["ffmpeg"],
                                   pre, post, cfg["temiz_hud"], env=tools["env"], per_segment=bool(problems))

            try:
                made += record()
            except DemoFailed as e:
                # Veritabanındaki kayıt dosyanın eski hâline ait olabilir (ör. onarılmış kopya yeniden yazıldı).
                if NOT_IN_DB not in str(e) or (err := csdm_analyze(tools, rec)):
                    raise DemoFailed(err or str(e)) from e
                made += record()
        except DemoFailed as e:
            print(f"  ! Kaydedilemedi: {e}. Sıradaki demoya geçiliyor.")
            failed.append((demo.name, str(e)))
            continue
        extra = [repaired_path(demo)] if repaired_path(demo).exists() else []
        if args.temizle and to_recycle_bin(demo_files(demo) + extra):
            print("  demo dosyaları Geri Dönüşüm Kutusu'na taşındı")

    if made and cfg["montaj"]:
        montage = make_montage(made, out_dir / "montaj.mp4", tools["ffmpeg"])
        print(f"\nMontaj: {montage}" if montage else "\nMontaj atlandı: ffmpeg bulunamadı.")
    print(f"\n{len(made)} yeni klip: {out_dir.resolve()}")
    for name, why in failed:
        print(f"  ! {name}: {why}")


if __name__ == "__main__":
    main()
