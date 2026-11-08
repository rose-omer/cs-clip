"""Bir oyuncunun round bazında öne çıkan anlarını skorlar."""

import pandas as pd

TICKRATE = 64  # CS2 demoları 64 tick
PRE_SECONDS = 3  # ilk kill'den önce
POST_SECONDS = 2  # son kill'den sonra
FAST_KILL_SECONDS = 2
MAX_GAP_SECONDS = 8  # daha uzun boşlukta klip parçalara bölünür
TEAM_SIZE = 5
SIDE = {2: "T", 3: "CT"}

MULTIKILL_SCORE = {1: 1, 2: 3, 3: 6, 4: 10, 5: 16}
CLUTCH_SCORE = {1: 1, 2: 4, 3: 7, 4: 10, 5: 14}  # kazanılan 1vN

# (sütun, puan, etiket)
KILL_BONUSES = [
    ("penetrated", 2.0, "wallbang"),
    ("noscope", 2.0, "noscope"),
    ("thrusmoke", 1.5, "smoke arkası"),
    ("attackerblind", 2.0, "kör"),
]


def _clutch(round_kills: pd.DataFrame, steamid: str, my_team: int) -> tuple[int, int] | None:
    """Oyuncu takımında tek kaldığında (rakip sayısı, tick); durum oluşmadıysa None."""
    alive = {2: TEAM_SIZE, 3: TEAM_SIZE}
    for row in round_kills.itertuples():
        if str(row.user_steamid) == steamid:
            return None  # önce ben öldüm
        if not pd.isna(row.user_team_num) and int(row.user_team_num) in alive:
            alive[int(row.user_team_num)] -= 1
        enemies = alive[5 - my_team]
        if alive[my_team] == 1 and enemies >= 1:
            return enemies, int(row.tick)
    return None


def _segments(moments: list[int], pre: float, post: float) -> list[list[int]]:
    """Anları, aralarında MAX_GAP_SECONDS'tan uzun boşluk olan parçalara böler."""
    groups = [[moments[0]]]
    for t in moments[1:]:
        if t - groups[-1][-1] > MAX_GAP_SECONDS * TICKRATE:
            groups.append([t])
        else:
            groups[-1].append(t)
    return [[int(g[0] - pre * TICKRATE), int(g[-1] + post * TICKRATE)] for g in groups]


def _winner(round_ends: pd.DataFrame | None, last_tick: int) -> str | None:
    if round_ends is None:
        return None
    after = round_ends[round_ends["tick"] >= last_tick]
    return None if after.empty else str(after["winner"].iloc[0])


def find_highlights(
    kills: pd.DataFrame,
    steamid: str,
    min_score: float = 3,
    match_start_tick: int = 0,
    round_ends: pd.DataFrame | None = None,
    pre_seconds: float = PRE_SECONDS,
    post_seconds: float = POST_SECONDS,
) -> list[dict]:
    """player_death tablosundan oyuncunun round özetlerini skora göre sıralı döner.

    match_start_tick öncesi (ısınma, bıçak oyunu) kill'ler sayılmaz.
    round_ends (tick, winner) verilirse kazanılan clutch'lar da puanlanır.
    """
    steamid = str(steamid)
    valid = kills[kills["tick"] >= match_start_tick]

    highlights = []
    for round_played, round_kills in valid.groupby("total_rounds_played"):
        round_kills = round_kills.sort_values("tick")
        group = round_kills[
            (round_kills["attacker_steamid"].astype(str) == steamid)
            & (round_kills["user_steamid"].astype(str) != steamid)
            & (round_kills["attacker_team_num"] != round_kills["user_team_num"])
        ]
        if group.empty:
            continue

        n = len(group)
        score = MULTIKILL_SCORE.get(n, 16)
        labels = ["ACE" if n >= 5 else f"{n}K"] if n >= 2 else []
        moments = [int(t) for t in group["tick"]]

        my_team = int(group["attacker_team_num"].iloc[0])
        clutch = _clutch(round_kills, steamid, my_team)
        if clutch and clutch[0] >= 2 and _winner(round_ends, int(round_kills["tick"].iloc[-1])) == SIDE.get(my_team):
            enemies, clutch_tick = clutch
            score += CLUTCH_SCORE[enemies]
            labels.insert(0, f"1v{enemies} clutch")
            moments = sorted(set(moments + [clutch_tick]))

        headshots = int(group["headshot"].astype(bool).sum())
        score += 0.5 * headshots
        if headshots:
            labels.append(f"{headshots} HS")

        for column, bonus, label in KILL_BONUSES:
            hits = int((group[column].astype(int) > 0).sum())
            if hits:
                score += bonus * hits
                labels.append(label)

        knife = int(group["weapon"].astype(str).str.contains("knife|bayonet").sum())
        if knife:
            score += 3 * knife
            labels.append("bıçak")

        fast = int((group["tick"].diff() <= FAST_KILL_SECONDS * TICKRATE).sum())
        if fast:
            score += fast
            labels.append("hızlı")

        if score < min_score:
            continue
        segments = _segments(moments, pre_seconds, post_seconds)
        highlights.append({
            "round": int(round_played) + 1,
            "kills": n,
            "score": score,
            "labels": labels,
            "weapons": sorted(set(group["weapon"].astype(str))),
            "start_tick": segments[0][0],
            "end_tick": segments[-1][1],
            "segments": segments,
        })

    return sorted(highlights, key=lambda h: h["score"], reverse=True)
