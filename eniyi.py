"""En iyi klipler: klip adlarını ayrıştırır, puanlar ve sıralar.

Klip adı (render.clip_filename): {harita}_{kod8}_R{round:02d}_{etiketler_ve_silah}.mp4
Varsayılan oyuncu dışındakilerin kliplerinde R'den sonra oyuncu etiketi gelir: ..._R05_p-Mert06_4K.mp4
(oyuncunun gerçek puanı <demo>.highlights.<steamid>.json'dan okunur).
Demo ve highlights.json hâlâ duruyorsa gerçek puan kullanılır; yoksa adındaki etiketlerden
highlights.py ile aynı formülle tahmin edilir.
"""

import glob
import json
import re
from datetime import datetime
from pathlib import Path

from analyze import TAG_PREFIX, read_player
from highlights import CLUTCH_SCORE, KILL_BONUSES, MULTIKILL_SCORE

MONTAGE_NAME = "en_iyi_montaj.mp4"
MONTAGE_META = "en_iyi_montaj.json"
DEFAULT_COUNT = 10
MAX_COUNT = 50
ALL_PLAYERS = "*"  # montaj/filtre: herkesin klipleri

NAME_RE = re.compile(r"^(?P<harita>.+?)_(?P<kod>[^_]+)_R(?P<round>\d+)(?:_(?P<tag>.*))?\.mp4$", re.IGNORECASE)

# Eski (sıkışık, Türkçe harfleri düşmüş) ve yeni adlardaki etiketlerin okunur biçimi.
FIXED_LABELS = {
    "wallbang": "wallbang",
    "noscope": "noscope",
    "smokearkası": "smoke arkası", "smokearkasi": "smoke arkası", "smokearkas": "smoke arkası",
    "kör": "kör", "kor": "kör", "kr": "kör",
    "bıçak": "bıçak", "bicak": "bıçak", "bak": "bıçak",
    "hızlı": "hızlı", "hizli": "hızlı", "hzl": "hızlı",
    "ace": "ACE",
}
BONUS_POINTS = {label: points for _, points, label in KILL_BONUSES}
KNIFE_POINTS = 3
FAST_POINTS = 1
HS_POINTS = 0.5
# Silah adlarında alt çizgiden sonra gelen parçalar (m4a1_silencer, usp_silencer_off, knife_t ...)
GUN_TAILS = {"silencer", "off"}
KNIFE_TAILS = {"t", "karambit", "butterfly", "flip", "gut", "tactical", "falchion",
                "survival", "bowie", "push", "ursus", "gypsy", "jackknife", "stiletto", "widowmaker", "css",
                "cord", "canis", "outdoor", "skeleton", "kukri", "bayonet", "m9"}


def label_of(token: str) -> str | None:
    """Ad parçasını okunur etikete çevirir; etiket değilse (silahsa) None."""
    t = token.lower().replace("-", "")
    if t in FIXED_LABELS:
        return FIXED_LABELS[t]
    if m := re.fullmatch(r"1v(\d)clutch", t):
        return f"1v{m.group(1)} clutch"
    if m := re.fullmatch(r"(\d+)hs", t):
        return f"{m.group(1)} HS"
    if m := re.fullmatch(r"([2-9])k", t):
        return f"{m.group(1)}K"
    return None


def parse_name(name: str) -> dict | None:
    """Klip adını {harita, kod, round, oyuncu, etiketler, silahlar} olarak ayrıştırır; kalıba uymuyorsa None.

    oyuncu: p-<etiket> parçasındaki etiket (Mert06); varsayılan oyuncunun kliplerinde None.
    """
    m = NAME_RE.match(name)
    if not m:
        return None
    labels: list[str] = []
    weapons: list[str] = []
    player = None
    prev_weapon = False
    for i, token in enumerate((m.group("tag") or "").split("_")):
        if not token:
            continue
        if i == 0 and token.lower().startswith(TAG_PREFIX) and len(token) > len(TAG_PREFIX):
            player = token[len(TAG_PREFIX):]
            continue
        label = label_of(token)
        if label is not None:
            labels.append(label)
            prev_weapon = False
        elif prev_weapon and (token.lower() in GUN_TAILS
                              or weapons[-1].lower().startswith("knife") and token.lower() in KNIFE_TAILS):
            weapons[-1] += "_" + token
        else:
            weapons.append(token)
            prev_weapon = True
    return {"harita": m.group("harita").lower(), "kod": m.group("kod"), "round": int(m.group("round")),
            "oyuncu": player, "etiketler": labels, "silahlar": weapons}


def estimate_score(labels: list[str]) -> float:
    """highlights.find_highlights formülüyle etiketlerden puan tahmini (kill etiketi yoksa 1 kill)."""
    kills = 1
    score = 0.0
    for label in labels:
        if label == "ACE":
            kills = 5
        elif m := re.fullmatch(r"(\d)K", label):
            kills = int(m.group(1))
        elif m := re.fullmatch(r"1v(\d) clutch", label):
            score += CLUTCH_SCORE.get(int(m.group(1)), 0)
        elif m := re.fullmatch(r"(\d+) HS", label):
            score += HS_POINTS * int(m.group(1))
        elif label in BONUS_POINTS:
            score += BONUS_POINTS[label]
        elif label == "bıçak":
            score += KNIFE_POINTS
        elif label == "hızlı":
            score += FAST_POINTS
    return score + MULTIKILL_SCORE.get(kills, MULTIKILL_SCORE[5])


def rank(rows: list[dict]) -> list[dict]:
    """Skor azalan; eşitlikte yeni tarih önce."""
    return sorted(rows, key=lambda r: (-r["skor"], _neg_date(r["tarih"])))


def _neg_date(iso: str) -> float:
    return -datetime.fromisoformat(iso).timestamp()


def _file_info(p: Path) -> dict:
    st = p.stat()
    return {"tarih": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
            "boyut_mb": round(st.st_size / 1024**2, 1)}


def _read_highlights(f: Path | None) -> dict[int, dict] | None:
    if f is None or not f.is_file():
        return None
    data = read_player(f)
    try:
        return {int(h["round"]): h for h in data["highlights"]} if data else None
    except (ValueError, TypeError, KeyError):
        return None


def player_files(default: Path | None) -> dict[str, tuple[str, dict[int, dict]]]:
    """<demo>.highlights.json'un yanındaki oyuncu dosyaları: etiket (öneksiz) -> (oyuncu adı, round -> highlight)."""
    if default is None or not default.name.endswith(".highlights.json"):
        return {}
    base = default.name[: -len(".highlights.json")]
    out = {}
    for f in sorted(default.parent.glob(glob.escape(base) + ".highlights.*.json")):
        data = read_player(f)
        tag = str((data or {}).get("etiket") or "")
        if not tag.startswith(TAG_PREFIX):
            continue
        try:
            out.setdefault(tag[len(TAG_PREFIX):], (str(data.get("oyuncu") or tag[len(TAG_PREFIX):]),
                                                   {int(h["round"]): h for h in data["highlights"]}))
        except (ValueError, TypeError, KeyError):
            continue
    return out


def clip_row(p: Path, demo: tuple[str, Path | None] | None = None, real: dict[int, dict] | None = None,
             player_name: str | None = None) -> dict | None:
    """Tek klibin satırı. demo: (demo id, highlights.json yolu); real: klibin oyuncusunun round -> highlight.

    player_name: klip başka oyuncunun ise okunur adı (yoksa addaki etiket).
    """
    info = parse_name(p.name)
    if info is None:
        return None
    h = (real or {}).get(info["round"])
    if h is not None:
        labels, weapons, score, guess = list(h.get("labels", [])), list(h.get("weapons", [])), h["score"], False
    else:
        labels, weapons, score, guess = info["etiketler"], info["silahlar"], estimate_score(info["etiketler"]), True
    return {"ad": p.name, "klip": f"/klip/{p.name}", "harita": info["harita"], "kod": info["kod"],
            "round": info["round"], "etiketler": labels, "silahlar": weapons, "skor": float(score),
            "tahmini": guess, "demo": demo[0] if demo else None, "oyuncu": info["oyuncu"],
            "oyuncu_ad": (player_name or info["oyuncu"]) if info["oyuncu"] else None, **_file_info(p)}


def best_clips(out_dir: Path, demos_by_code: dict[str, tuple[str, Path | None]] | None = None) -> list[dict]:
    """Klasördeki (alt klasörler hariç) klipleri sıralı döner.

    demos_by_code: maç kodu -> (demo id, <demo>.highlights.json yolu). Analiz başlatılmaz.
    """
    out_dir = Path(out_dir)
    if not out_dir.is_dir():
        return []
    demos_by_code = demos_by_code or {}
    cache: dict[str, dict[int, dict] | None] = {}
    players: dict[str, dict[str, tuple[str, dict[int, dict]]]] = {}
    rows = []
    for p in out_dir.iterdir():
        if not p.is_file():
            continue
        info = parse_name(p.name)
        if info is None:
            continue
        demo = demos_by_code.get(info["kod"])
        if demo is not None and info["kod"] not in cache:
            cache[info["kod"]] = _read_highlights(demo[1])
            players[info["kod"]] = player_files(demo[1])
        if info["oyuncu"]:
            name, real = players.get(info["kod"], {}).get(info["oyuncu"], (None, None))
            row = clip_row(p, demo, real, name)
        else:
            row = clip_row(p, demo, cache.get(info["kod"]))
        if row is not None:
            rows.append(row)
    return rank(rows)


def by_player(rows: list[dict], player: str | None) -> list[dict]:
    """Oyuncuya göre süzer: None = varsayılan oyuncu, ALL_PLAYERS = herkes, yoksa etiket (Mert06)."""
    if player == ALL_PLAYERS:
        return rows
    want = (player or "").casefold()
    return [r for r in rows if (r.get("oyuncu") or "").casefold() == want]


def montage_info(out_dir: Path) -> dict | None:
    """Mevcut en iyi montajın bilgisi; yoksa None."""
    f = Path(out_dir) / MONTAGE_NAME
    if not f.is_file():
        return None
    meta_data: dict = {}
    meta = f.with_name(MONTAGE_META)
    if meta.is_file():
        try:
            loaded = json.loads(meta.read_text(encoding="utf-8"))
            meta_data = loaded if isinstance(loaded, dict) else {}
        except ValueError:
            meta_data = {}
    return {"klip": f"/klip/{MONTAGE_NAME}", "adet": meta_data.get("adet"), "oyuncu": meta_data.get("oyuncu"),
            **_file_info(f)}


def parse_count(body: dict) -> int | None:
    """POST gövdesindeki adet; geçersizse None."""
    n = body.get("adet", DEFAULT_COUNT) if isinstance(body, dict) else None
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= MAX_COUNT:
        return None
    return n


def parse_player(body: dict) -> tuple[bool, str | None]:
    """POST gövdesindeki oyuncu filtresi: (geçerli mi, değer). Yok/boş = varsayılan oyuncu."""
    p = body.get("oyuncu") if isinstance(body, dict) else None
    if p is None or p == "":
        return True, None
    if not isinstance(p, str) or len(p) > 64 or not (p == ALL_PLAYERS or re.fullmatch(r"\w+", p)):
        return False, None
    return True, p
