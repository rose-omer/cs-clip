"""Demodan maç istatistikleri: skor, oyuncu tablosu (ADR, KAST, rating), roundlar, silahlar."""

import json
import math
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

from analyze import resolve_steamid
from highlights import TICKRATE

TRADE_SECONDS = 5  # katilim bu sürede takım arkadaşımca öldürülürse "trade"
SIDE_NUM = {"T": 2, "CT": 3}
EVENTS = ["player_death", "player_hurt", "round_end", "round_officially_ended", "begin_new_match"]


# --- küçük yardımcılar ---

def _sid(value) -> str | None:
    """SteamID'yi metne çevirir; boş/NaN ise None."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text = str(value)
    return None if text in ("", "nan", "None", "0") else text


def _side(value) -> int | None:
    """round_end winner ("T"/"CT" ya da 2/3) -> team_num."""
    if isinstance(value, str):
        return SIDE_NUM.get(value.upper())
    try:
        return int(value) if int(value) in (2, 3) else None
    except (TypeError, ValueError):
        return None


def match_start_tick(starts: pd.DataFrame) -> int:
    """Son begin_new_match; öncesi ısınma/bıçak roundu."""
    return int(starts["tick"].max()) if len(starts) else 0


def real_rounds(round_ends: pd.DataFrame, match_start: int) -> pd.DataFrame:
    """Maç başladıktan sonra kazananı olan roundlar (tick, side, reason), sırayla."""
    ends = round_ends[round_ends["tick"] >= match_start].sort_values("tick")
    sides = ends["winner"].map(_side) if "winner" in ends.columns else pd.Series(dtype=float)
    reasons = ends["reason"].astype(str) if "reason" in ends.columns else "?"
    out = pd.DataFrame({"tick": ends["tick"].astype(int), "side": sides, "reason": reasons})
    return out[out["side"].notna()].reset_index(drop=True)


def round_bounds(end_ticks: list[int], official_ticks: list[int]) -> list[float]:
    """Her roundun bittiği son tick: round_end sonrası bekleme (exit frag) dahil."""
    bounds: list[float] = []
    for i, end in enumerate(end_ticks):
        nxt = end_ticks[i + 1] if i + 1 < len(end_ticks) else math.inf
        later = [t for t in official_ticks if end <= t < nxt]
        bounds.append(math.inf if nxt == math.inf else (min(later) if later else end))
    return bounds


def assign_rounds(events: pd.DataFrame, bounds: list[float]) -> pd.Series:
    """Olayın tick'ine göre 0 tabanlı round indeksi."""
    finite = [b for b in bounds if b != math.inf]
    idx = pd.Series(finite, dtype="float64").searchsorted(events["tick"].to_numpy(), side="left")
    return pd.Series(idx, index=events.index).clip(upper=max(len(bounds) - 1, 0))


# --- takımlar ---

def team_groups(sides: pd.DataFrame) -> tuple[dict[str, int], dict[int, int]]:
    """(oyuncu -> takım 0/1, round -> takım 0'ın tarafı).

    sides: round, steamid, team_num. Takım 0 = ilk roundda T başlayan grup;
    devre/uzatma değişimleri, bilinen oyuncuların o roundki tarafından çıkarılır.
    """
    team_of: dict[str, int] = {}
    side0: dict[int, int] = {}
    rows = sides[sides["team_num"].isin([2, 3])]
    for rnd, group in rows.groupby("round", sort=True):
        votes = Counter(
            int(r.team_num) if team_of[str(r.steamid)] == 0 else 5 - int(r.team_num)
            for r in group.itertuples() if str(r.steamid) in team_of
        )
        s0 = votes.most_common(1)[0][0] if votes else 2
        side0[int(rnd)] = s0
        for r in group.itertuples():
            team_of.setdefault(str(r.steamid), 0 if int(r.team_num) == s0 else 1)
    return team_of, side0


def team_names(sides: pd.DataFrame, team_of: dict[str, int]) -> list[str]:
    """Demodaki klan adı, yoksa Takım A/B."""
    names = ["Takım A", "Takım B"]
    if "team_clan_name" not in sides.columns:
        return names
    for team in (0, 1):
        clans = [str(r.team_clan_name) for r in sides.itertuples()
                 if team_of.get(str(r.steamid)) == team and isinstance(r.team_clan_name, str) and r.team_clan_name.strip()]
        if clans:
            names[team] = Counter(clans).most_common(1)[0][0]
    return names


# --- hesaplar ---

def hltv_rating(kills: int, deaths: int, rounds: int, multi: dict[int, int]) -> float:
    """HLTV 1.0; multi: {1: 1K round sayısı, ..., 5: 5K}."""
    if rounds <= 0:
        return 0.0
    kill_r = kills / rounds / 0.679
    surv_r = (rounds - deaths) / rounds / 0.317
    mk = sum(n * n * multi.get(n, 0) for n in range(1, 6))
    return round((kill_r + 0.7 * surv_r + mk / rounds / 1.277) / 2.7, 2)


def valid_kills(deaths: pd.DataFrame) -> pd.DataFrame:
    """Takım kill'i, intihar ve dünya ölümleri hariç kill'ler."""
    att = deaths["attacker_steamid"].map(_sid)
    vic = deaths["user_steamid"].map(_sid)
    mask = att.notna() & (att != vic) & (deaths["attacker_team_num"] != deaths["user_team_num"])
    return deaths[mask]


def enemy_damage(hurts: pd.DataFrame) -> pd.DataFrame:
    """Rakibe verilen hasar; kalan canla sınırlı (dmg sütunu)."""
    hurts = hurts.sort_values("tick", kind="stable").copy()
    before = hurts.groupby(["round", "user_steamid"])["health"].shift(1).fillna(100)
    hurts["dmg"] = hurts["dmg_health"].clip(lower=0).where(lambda d: d <= before, before)
    att = hurts["attacker_steamid"].map(_sid)
    mask = att.notna() & (att != hurts["user_steamid"].map(_sid)) & (hurts["attacker_team_num"] != hurts["user_team_num"])
    return hurts[mask]


def traded_deaths(kills: pd.DataFrame, team_of: dict[str, int]) -> set[tuple[int, str]]:
    """(round, kurban) — katili TRADE_SECONDS içinde kurbanın takımından biri öldürdü."""
    window = TRADE_SECONDS * TICKRATE
    out = set()
    for rnd, group in kills.groupby("round"):
        rows = list(group.sort_values("tick").itertuples())
        for d in rows:
            victim, killer = str(d.user_steamid), str(d.attacker_steamid)
            if victim not in team_of:
                continue
            for r in rows:
                if (str(r.user_steamid) == killer and d.tick <= r.tick <= d.tick + window
                        and team_of.get(str(r.attacker_steamid)) == team_of.get(victim)):
                    out.add((int(rnd), victim))
                    break
    return out


def opening_duels(kills: pd.DataFrame) -> pd.DataFrame:
    """Her roundun ilk kill'i."""
    return kills.sort_values("tick", kind="stable").groupby("round").head(1)


def player_row(sid: str, name: str, team: int, rounds: int, kills: pd.DataFrame, deaths: pd.DataFrame,
               assists: pd.DataFrame, damage: pd.DataFrame, openings: pd.DataFrame, traded: set) -> dict:
    """Tek oyuncunun tablo satırı."""
    mine = kills[kills["attacker_steamid"].astype(str) == sid]
    died = deaths[deaths["user_steamid"].astype(str) == sid]
    helped = assists[assists["assister_steamid"].astype(str) == sid]
    k, d, a = len(mine), len(died), len(helped)
    per_round = Counter(mine["round"].astype(int))
    multi = Counter(min(n, 5) for n in per_round.values())

    kast_rounds = set(per_round) | set(helped["round"].astype(int))
    kast_rounds |= set(range(rounds)) - set(died["round"].astype(int))
    kast_rounds |= {r for r, v in traded if v == sid}
    hs = int(mine["headshot"].astype(bool).sum())
    dmg = float(damage.loc[damage["attacker_steamid"].astype(str) == sid, "dmg"].sum())
    return {
        "steamid": sid, "ad": name, "takim": team, "kill": k, "death": d, "assist": a,
        "adr": round(dmg / rounds, 1) if rounds else 0.0,
        "hs_yuzde": round(100 * hs / k, 1) if k else 0.0,
        "kd": round(k / d, 2) if d else float(k),
        "kast": round(100 * len(kast_rounds & set(range(rounds))) / rounds, 1) if rounds else 0.0,
        "rating": hltv_rating(k, d, rounds, multi),
        "acilis_kill": int((openings["attacker_steamid"].astype(str) == sid).sum()),
        "acilis_death": int((openings["user_steamid"].astype(str) == sid).sum()),
        "cok_kill": {str(n): multi.get(n, 0) for n in range(2, 6)},
    }


def build_stats(map_name: str, names: dict[str, str], deaths: pd.DataFrame, hurts: pd.DataFrame,
                round_ends: pd.DataFrame, official_ticks: list[int], sides: pd.DataFrame,
                steamid: str, match_start: int) -> dict:
    """Ayrıştırılmış tablolardan istatistik sözlüğü; demo dosyası gerekmez.

    sides: tick (round_end tick'leri), steamid, team_num[, team_clan_name].
    """
    rounds = real_rounds(round_ends, match_start)
    n = len(rounds)
    bounds = round_bounds(rounds["tick"].tolist(), official_ticks)

    def in_match(df: pd.DataFrame) -> pd.DataFrame:
        df = df[df["tick"] >= match_start].copy()
        df["round"] = assign_rounds(df, bounds)
        return df

    deaths = in_match(deaths)
    deaths = deaths[deaths["user_steamid"].map(_sid).notna()]
    hurts = in_match(hurts)
    kills = valid_kills(deaths)
    assist_mask = deaths["assister_steamid"].map(_sid).notna() & (deaths["assister_team_num"] != deaths["user_team_num"])
    assists = deaths[assist_mask]

    tick_round = {int(t): i for i, t in enumerate(rounds["tick"])}
    sides = sides[sides["tick"].isin(tick_round)].copy()
    sides["round"] = sides["tick"].map(tick_round)
    team_of, side0 = team_groups(sides)
    winners = [0 if int(r.side) == side0.get(i, 2) else 1 for i, r in enumerate(rounds.itertuples())]
    score = [winners.count(0), winners.count(1)]
    clans = team_names(sides, team_of)

    damage = enemy_damage(hurts)
    traded = traded_deaths(kills, team_of)
    openings = opening_duels(kills)
    players = [player_row(sid, names.get(sid, sid), team, n, kills, deaths, assists, damage, openings, traded)
               | {"ben": sid == steamid} for sid, team in team_of.items()]
    players.sort(key=lambda p: (p["takim"], -p["rating"], p["ad"].casefold()))

    my_kills = kills[kills["attacker_steamid"].astype(str) == steamid]
    my_deaths = set(deaths.loc[deaths["user_steamid"].astype(str) == steamid, "round"].astype(int))
    per_round = Counter(my_kills["round"].astype(int))
    weapons = [
        {"silah": str(w), "kill": len(g), "hs": int(g["headshot"].astype(bool).sum())}
        for w, g in my_kills.groupby("weapon")
    ]
    weapons.sort(key=lambda w: (-w["kill"], w["silah"]))
    return {
        "harita": map_name,
        "round_sayisi": n,
        "takimlar": [{"ad": clans[t], "skor": score[t], "kazandi": score[t] > score[1 - t]} for t in (0, 1)],
        "benim_takim": team_of.get(steamid, 0),
        "oyuncu_steamid": steamid,
        "oyuncular": players,
        "roundlar": [
            {"no": i + 1, "kazanan_takim": winners[i], "benim_kill": per_round.get(i, 0),
             "ben_oldum": i in my_deaths, "neden": str(r.reason)}
            for i, r in enumerate(rounds.itertuples())
        ],
        "silahlar": weapons,
    }


# --- demo ---

def match_stats(demo: Path, player: str) -> dict:
    """Demoyu ayrıştırıp oyuncunun maç istatistiklerini döner."""
    from demoparser2 import DemoParser

    parser = DemoParser(str(demo))
    info = parser.parse_player_info()
    steamid = resolve_steamid(info, player)
    if steamid is None:
        names = ", ".join(info["name"].astype(str))
        raise SystemExit(f"'{player}' bu demoda yok. Oyuncular: {names}")

    events = dict(parser.parse_events(EVENTS, player=["team_num"]))
    empty = pd.DataFrame({"tick": pd.Series(dtype="int64")})
    match_start = match_start_tick(events.get("begin_new_match", empty))
    round_ends = events.get("round_end", empty)
    if "winner" not in round_ends.columns:
        raise SystemExit("Demoda round sonucu (round_end winner) yok.")
    official = [int(t) for t in events.get("round_officially_ended", empty)["tick"].unique()]

    end_ticks = real_rounds(round_ends, match_start)["tick"].tolist()
    sides = parser.parse_ticks(["team_num", "team_clan_name"], ticks=end_ticks) if end_ticks else \
        pd.DataFrame(columns=["tick", "steamid", "team_num", "team_clan_name"])
    names = {str(r.steamid): str(r.name) for r in info.itertuples()}
    return build_stats(parser.parse_header().get("map_name", "?"), names, events["player_death"],
                       events["player_hurt"], round_ends, official, sides, steamid, match_start)


def stats_path(demo: Path) -> Path:
    return Path(demo).with_name(Path(demo).stem + ".stats.json")


def save_stats(demo: Path, stats: dict) -> Path:
    out = stats_path(demo)
    out.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def load_stats(demo: Path) -> dict | None:
    """Demodan yeni bir .stats.json varsa onu döner."""
    out, demo = stats_path(demo), Path(demo)
    if not out.exists() or (demo.exists() and demo.stat().st_mtime >= out.stat().st_mtime):
        return None
    try:
        return json.loads(out.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def print_summary(stats: dict) -> None:
    a, b = stats["takimlar"]
    print(f"{stats['harita']} — {a['ad']} {a['skor']}–{b['skor']} {b['ad']} ({stats['round_sayisi']} round)\n")
    print(f"{'oyuncu':<16}{'K':>4}{'D':>4}{'A':>4}{'ADR':>7}{'HS%':>6}{'KAST':>6}{'rating':>8}")
    for p in stats["oyuncular"]:
        mark = "*" if p["ben"] else " "
        print(f"{mark}{p['ad'][:15]:<15}{p['kill']:>4}{p['death']:>4}{p['assist']:>4}"
              f"{p['adr']:>7.1f}{p['hs_yuzde']:>6.1f}{p['kast']:>6.1f}{p['rating']:>8.2f}  (takım {p['takim']})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("kullanım: python stats.py <demo.dem> <oyuncu>")
    print_summary(match_stats(Path(sys.argv[1]), sys.argv[2]))
