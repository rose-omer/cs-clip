"""Demodan bir oyuncunun highlight listesini çıkarır."""

import json
from pathlib import Path

from demoparser2 import DemoParser

from highlights import POST_SECONDS, PRE_SECONDS, TICKRATE, find_highlights


def resolve_steamid(players, who: str) -> str | None:
    """Ad (büyük/küçük harf duyarsız) ya da SteamID64 ile oyuncu bulur."""
    for _, p in players.iterrows():
        if who == str(p["steamid"]) or who.casefold() == str(p["name"]).casefold():
            return str(p["steamid"])
    return None


def analyze(
    demo: Path, player: str, pre_seconds: float = PRE_SECONDS, post_seconds: float = POST_SECONDS
) -> tuple[str, str, list[dict]]:
    """(harita, steamid, tüm highlight'lar) döner; skor filtresi uygulanmaz."""
    parser = DemoParser(str(demo))
    players = parser.parse_player_info()
    steamid = resolve_steamid(players, player)
    if steamid is None:
        names = ", ".join(players["name"].astype(str))
        raise SystemExit(f"'{player}' bu demoda yok. Oyuncular: {names}")

    kills = parser.parse_event("player_death", player=["team_num"], other=["total_rounds_played"])
    starts = parser.parse_event("begin_new_match")
    match_start = int(starts["tick"].max()) if len(starts) else 0
    round_ends = parser.parse_event("round_end")
    if "winner" not in round_ends.columns:
        round_ends = None

    highlights = find_highlights(kills, steamid, 0, match_start, round_ends, pre_seconds, post_seconds)
    return parser.parse_header().get("map_name", "?"), steamid, highlights


def print_report(map_name: str, highlights: list[dict], min_score: float) -> None:
    shown = [h for h in highlights if h["score"] >= min_score]
    print(f"{map_name} — {len(shown)} highlight (skor >= {min_score})\n")
    for h in shown:
        print(f"R{h['round']:>2}  skor {h['score']:>5.1f}  {', '.join(h['labels']) or '-'}"
              f"  [{', '.join(h['weapons'])}]  {(h['end_tick'] - h['start_tick']) / TICKRATE:.0f} sn")


def save_json(demo: Path, highlights: list[dict]) -> Path:
    out = demo.with_suffix(".highlights.json")
    out.write_text(json.dumps(highlights, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
