"""Demodan bir oyuncunun (ya da herkesin) highlight listesini çıkarır.

Varsayılan oyuncunun (ayarlar.json 'oyuncu') listesi <demo>.highlights.json'a yazılır (liste);
diğer oyuncularınki <demo>.highlights.<steamid>.json'a (oyuncu bilgisiyle birlikte sözlük).
"""

import json
import re
from pathlib import Path

from highlights import POST_SECONDS, PRE_SECONDS, TICKRATE, find_highlights

TAG_PREFIX = "p-"  # klip adındaki oyuncu etiketi: ..._R05_p-Mert06_4K.mp4
TAG_MAX = 20


def resolve_steamid(players, who: str) -> str | None:
    """Ad (büyük/küçük harf duyarsız) ya da SteamID64 ile oyuncu bulur."""
    for _, p in players.iterrows():
        if who == str(p["steamid"]) or who.casefold() == str(p["name"]).casefold():
            return str(p["steamid"])
    return None


def player_tag(name: str, steamid: str = "") -> str:
    """Klip adına giren oyuncu etiketi (öneksiz): yalnız harf ve rakam (Mert_06 -> Mert06).

    Adda harf/rakam yoksa SteamID'nin son 8 hanesi kullanılır.
    """
    tag = "".join(c for c in str(name) if c.isalnum())[:TAG_MAX]
    return tag or str(steamid)[-8:] or "oyuncu"


def highlights_path(demo: Path, steamid: str | None = None) -> Path:
    """Varsayılan oyuncu: <demo>.highlights.json; diğerleri: <demo>.highlights.<steamid>.json."""
    demo = Path(demo)
    if steamid is None:
        return demo.with_suffix(".highlights.json")
    if not re.fullmatch(r"\d+", str(steamid)):
        raise ValueError(f"geçersiz SteamID: {steamid!r}")
    return demo.with_suffix(f".highlights.{steamid}.json")


def _load(demo: Path):
    from demoparser2 import DemoParser

    parser = DemoParser(str(demo))
    players = parser.parse_player_info()
    kills = parser.parse_event("player_death", player=["team_num"], other=["total_rounds_played"])
    starts = parser.parse_event("begin_new_match")
    match_start = int(starts["tick"].max()) if len(starts) else 0
    round_ends = parser.parse_event("round_end")
    if "winner" not in round_ends.columns:
        round_ends = None
    return parser.parse_header().get("map_name", "?"), players, kills, match_start, round_ends


def _missing(players, who: str):
    names = ", ".join(players["name"].astype(str))
    return SystemExit(f"'{who}' bu demoda yok. Oyuncular: {names}")


def analyze_player(
    demo: Path, player: str, pre_seconds: float = PRE_SECONDS, post_seconds: float = POST_SECONDS,
    default: str | None = None,
) -> dict:
    """{harita, steamid, ad, varsayilan, highlights}. player: ad ya da SteamID64.

    varsayilan: oyuncu, `default` (ayarlar.json'daki oyuncu) ile aynı kişi mi; default verilmezse True.
    """
    map_name, players, kills, match_start, round_ends = _load(demo)
    steamid = resolve_steamid(players, player)
    if steamid is None:
        raise _missing(players, player)
    names = {str(r.steamid): str(r.name) for r in players.itertuples()}
    is_default = default is None or resolve_steamid(players, default) == steamid
    hl = find_highlights(kills, steamid, 0, match_start, round_ends, pre_seconds, post_seconds)
    return {"harita": map_name, "steamid": steamid, "ad": names.get(steamid, steamid),
            "varsayilan": is_default, "highlights": hl}


def analyze_all(
    demo: Path, pre_seconds: float = PRE_SECONDS, post_seconds: float = POST_SECONDS, default: str | None = None
) -> dict:
    """Demodaki her oyuncunun highlight'ları tek ayrıştırmayla: {harita, oyuncular: [analyze_player sonucu]}."""
    map_name, players, kills, match_start, round_ends = _load(demo)
    default_sid = resolve_steamid(players, default) if default else None
    rows = []
    for r in players.drop_duplicates("steamid").itertuples():
        sid = str(r.steamid)
        if sid in ("", "0", "nan", "None"):
            continue
        hl = find_highlights(kills, sid, 0, match_start, round_ends, pre_seconds, post_seconds)
        rows.append({"harita": map_name, "steamid": sid, "ad": str(r.name), "varsayilan": sid == default_sid,
                     "highlights": hl})
    return {"harita": map_name, "oyuncular": rows}


def analyze(
    demo: Path, player: str, pre_seconds: float = PRE_SECONDS, post_seconds: float = POST_SECONDS
) -> tuple[str, str, list[dict]]:
    """(harita, steamid, tüm highlight'lar) döner; skor filtresi uygulanmaz."""
    r = analyze_player(demo, player, pre_seconds, post_seconds)
    return r["harita"], r["steamid"], r["highlights"]


def print_report(map_name: str, highlights: list[dict], min_score: float) -> None:
    shown = [h for h in highlights if h["score"] >= min_score]
    print(f"{map_name} — {len(shown)} highlight (skor >= {min_score})\n")
    for h in shown:
        print(f"R{h['round']:>2}  skor {h['score']:>5.1f}  {', '.join(h['labels']) or '-'}"
              f"  [{', '.join(h['weapons'])}]  {(h['end_tick'] - h['start_tick']) / TICKRATE:.0f} sn")


def save_json(demo: Path, highlights: list[dict]) -> Path:
    """Varsayılan oyuncunun listesi (eski biçim, değişmedi)."""
    out = highlights_path(demo)
    out.write_text(json.dumps(highlights, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def save_player(demo: Path, result: dict) -> Path:
    """analyze_player sonucunu kaydeder: varsayılan oyuncu eski dosyaya, diğerleri kendi dosyasına."""
    if result.get("varsayilan"):
        return save_json(demo, result["highlights"])
    out = highlights_path(demo, result["steamid"])
    data = {"oyuncu": result["ad"], "steamid": result["steamid"],
            "etiket": TAG_PREFIX + player_tag(result["ad"], result["steamid"]), "highlights": result["highlights"]}
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def read_player(f: Path) -> dict | None:
    """Oyuncu dosyasını okur: {oyuncu, steamid, etiket, highlights}; eski liste biçiminde yalnız highlights."""
    try:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if isinstance(data, list):
        return {"highlights": data}
    if isinstance(data, dict) and isinstance(data.get("highlights"), list):
        return data
    return None
