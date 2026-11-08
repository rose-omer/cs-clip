"""Kariyer: analiz edilmiş maçların (<demo>.stats.json) oyuncu satırları.

Yalnız var olan stats.json dosyaları okunur; analiz başlatılmaz, dosyalar değiştirilmez.
Grafikler, ortalamalar ve harita özetleri arayüzde (arayuz/app.js) bu satırlardan hesaplanır.
"""

import json
from datetime import datetime
from pathlib import Path

STATS_SUFFIX = ".stats.json"
METRICS = ("rating", "adr", "kast", "kd", "hs_yuzde", "kill", "death", "assist", "acilis_kill", "acilis_death")


def me(stats: dict) -> dict | None:
    """Maçtaki oyuncunun kendisi (ben bayrağı, yoksa oyuncu_steamid eşleşmesi)."""
    players = stats.get("oyuncular") or []
    sid = str(stats.get("oyuncu_steamid") or "")
    return next((p for p in players if p.get("ben")), None) or next(
        (p for p in players if sid and str(p.get("steamid")) == sid), None)


def match_row(stats: dict, did: str, date: str, has_demo: bool) -> dict | None:
    """stats.json -> kariyer satırı; oyuncu bulunamazsa ya da veri bozuksa None."""
    if not isinstance(stats, dict):
        return None
    p = me(stats)
    teams = stats.get("takimlar") or []
    if p is None or len(teams) < 2:
        return None
    ours = p.get("takim", stats.get("benim_takim", 0))
    ours = ours if ours in (0, 1) else 0
    try:
        a, b = int(teams[ours].get("skor") or 0), int(teams[1 - ours].get("skor") or 0)
    except (TypeError, ValueError, AttributeError):
        return None
    row = {
        "id": did, "tarih": date, "demo_var": has_demo, "harita": stats.get("harita"),
        "round_sayisi": stats.get("round_sayisi") or a + b,
        "skor": [a, b], "sonuc": "G" if a > b else "M" if a < b else "B",
        "ad": p.get("ad"), "cok_kill": {k: int((p.get("cok_kill") or {}).get(k) or 0) for k in ("2", "3", "4", "5")},
    }
    for k in METRICS:
        v = p.get(k)
        row[k] = v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    return row


def stats_files(folders: list[Path]) -> dict[str, Path]:
    """Klasörlerdeki <id>.stats.json dosyaları (demosu silinmiş olanlar da)."""
    found: dict[str, Path] = {}
    for folder in folders:
        if not folder.is_dir():
            continue
        for f in folder.iterdir():
            if f.is_file() and f.name.lower().endswith(STATS_SUFFIX):
                found.setdefault(f.name[: -len(STATS_SUFFIX)], f)
    return found


def career(folders: list[Path], demos: dict[str, Path]) -> dict:
    """GET /api/kariyer: maç satırları eskiden yeniye; tarih demo dosyasının (yoksa stats.json'un) zamanı."""
    files = stats_files(folders)
    for did, p in demos.items():  # demonun yanındaki stats.json öncelikli
        f = p.with_name(did + STATS_SUFFIX)
        if f.is_file():
            files[did] = f
    rows, broken = [], 0
    for did, f in files.items():
        try:
            stats = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            broken += 1
            continue
        demo = demos.get(did)
        src = demo if demo is not None and demo.exists() else f
        date = datetime.fromtimestamp(src.stat().st_mtime).isoformat(timespec="seconds")
        row = match_row(stats, did, date, demo is not None)
        if row is None:
            broken += 1
        else:
            rows.append(row)
    rows.sort(key=lambda r: (r["tarih"], r["id"]))
    pending = sum(1 for did in demos if did not in files)
    return {"maclar": rows, "analiz_bekleyen": pending, "okunamayan": broken}
