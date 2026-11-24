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

# Bağlam ölçütleri (2. sürüm). Etiketleri `labels`'a girmez (klip adları ondan üretilir); `ozellikler`'e girer.
# Sütun yoksa (eski demoparser çıktısı, testler) ölçüt atlanır.
OPENING_POINTS = 1.0  # round'un ilk kill'i
ECO_POINTS = 1.0  # kill başı: rakibin ekipmanı benimkinin ECO_RATIO katı ve en az ECO_MIN_VALUE
ECO_RATIO = 2.5
ECO_MIN_VALUE = 3000
LOW_HP = 20
LOW_HP_POINTS = 1.0  # bir kez: kill anında canım LOW_HP ya da altında
AIR_POINTS = 2.0  # kill başı: havadayken
UTILITY_WEAPONS = ("hegrenade", "inferno", "molotov", "incgrenade")
UTILITY_POINTS = 2.0  # kill başı: bomba ya da molotof
ZEUS_POINTS = 3.0  # kill başı
COLLATERAL_POINTS = 3.0  # aynı tick'te ikinci (ve sonraki) kill
REGULATION_ROUNDS = 24  # MR12: 24'ten sonrası uzatma
OVERTIME_POINTS = 1.0
MATCH_WINNER_POINTS = 2.0  # maçın son round'u, benim takımım kazandı


def _clutch(round_kills: pd.DataFrame, steamid: str, my_team: int,
            team_size: int = TEAM_SIZE) -> tuple[int, int] | None:
    """Oyuncu takımında tek kaldığında (rakip sayısı, tick); durum oluşmadıysa None."""
    alive = {2: team_size, 3: team_size}
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


def _round_end(round_ends: pd.DataFrame | None, last_tick: int) -> tuple[str | None, bool]:
    """(kazanan taraf "T"/"CT", maçın son round'u mu). round_ends yoksa (None, False)."""
    if round_ends is None:
        return None, False
    after = round_ends[round_ends["tick"] >= last_tick].sort_values("tick")
    if after.empty:
        return None, False
    return str(after["winner"].iloc[0]), len(after) == 1


def _winner(round_ends: pd.DataFrame | None, last_tick: int) -> str | None:
    return _round_end(round_ends, last_tick)[0]


def _has(df: pd.DataFrame, *columns: str) -> bool:
    return all(c in df.columns for c in columns)


def _context(group: pd.DataFrame, round_kills: pd.DataFrame, steamid: str, round_no: int,
             won: bool, last_round: bool) -> list[tuple[str, float]]:
    """Bağlam ölçütleri: [(özellik etiketi, puan)]. group: oyuncunun bu round'daki geçerli kill'leri."""
    out: list[tuple[str, float]] = []
    enemy_kills = round_kills[round_kills["attacker_team_num"] != round_kills["user_team_num"]]
    if not enemy_kills.empty and str(enemy_kills["attacker_steamid"].iloc[0]) == steamid:
        out.append(("açılış", OPENING_POINTS))
    if _has(group, "attacker_current_equip_value", "user_current_equip_value"):
        mine = pd.to_numeric(group["attacker_current_equip_value"], errors="coerce")
        theirs = pd.to_numeric(group["user_current_equip_value"], errors="coerce")
        eco = int(((theirs >= ECO_MIN_VALUE) & (theirs >= ECO_RATIO * mine)).sum())
        if eco:
            out.append(("ekonomi farkı", ECO_POINTS * eco))
    if _has(group, "attacker_health"):
        hp = pd.to_numeric(group["attacker_health"], errors="coerce")
        if ((hp > 0) & (hp <= LOW_HP)).any():
            out.append(("az can", LOW_HP_POINTS))
    if _has(group, "attackerinair"):
        air = int(group["attackerinair"].fillna(False).astype(bool).sum())
        if air:
            out.append(("havada", AIR_POINTS * air))
    weapons = group["weapon"].astype(str)
    utility = int(weapons.isin(UTILITY_WEAPONS).sum())
    if utility:
        out.append(("bomba", UTILITY_POINTS * utility))
    zeus = int((weapons == "taser").sum())
    if zeus:
        out.append(("zeus", ZEUS_POINTS * zeus))
    collateral = int(group["tick"].duplicated().sum())
    if collateral:
        out.append(("collateral", COLLATERAL_POINTS * collateral))
    if round_no > REGULATION_ROUNDS:
        out.append(("uzatma", OVERTIME_POINTS))
    if won and last_round:
        out.append(("maçı bitirdi", MATCH_WINNER_POINTS))
    return out


def find_highlights(
    kills: pd.DataFrame,
    steamid: str,
    min_score: float = 3,
    match_start_tick: int = 0,
    round_ends: pd.DataFrame | None = None,
    pre_seconds: float = PRE_SECONDS,
    post_seconds: float = POST_SECONDS,
    team_size: int = TEAM_SIZE,
) -> list[dict]:
    """player_death tablosundan oyuncunun round özetlerini skora göre sıralı döner.

    match_start_tick öncesi (ısınma, bıçak oyunu) kill'ler sayılmaz.
    round_ends (tick, winner) verilirse kazanılan clutch'lar ve maçı bitiren round da puanlanır.
    team_size: takım başına oyuncu (5v5: 5, wingman: 2); clutch hesabı buna göre.
    Her highlight'ta `puanlar` ([etiket, puan] listesi) puanın nereden geldiğini, `ozellikler` bağlam
    etiketlerini (açılış, ekonomi farkı, ...) verir. `labels` eski biçimdedir; klip adları ondan üretilir.
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
        kill_label = "ACE" if n >= 5 else f"{n}K"
        points: list[list] = [[kill_label, MULTIKILL_SCORE.get(n, 16)]]  # [etiket, puan]: puanın dökümü
        labels = [kill_label] if n >= 2 else []
        moments = [int(t) for t in group["tick"]]

        my_team = int(group["attacker_team_num"].iloc[0])
        winner, last_round = _round_end(round_ends, int(round_kills["tick"].iloc[-1]))
        won = winner is not None and winner == SIDE.get(my_team)
        clutch = _clutch(round_kills, steamid, my_team, team_size)
        if clutch and clutch[0] >= 2 and won:
            enemies, clutch_tick = clutch
            points.append([f"1v{enemies} clutch", CLUTCH_SCORE.get(enemies, CLUTCH_SCORE[5])])
            labels.insert(0, f"1v{enemies} clutch")
            moments = sorted(set(moments + [clutch_tick]))

        headshots = int(group["headshot"].astype(bool).sum())
        if headshots:
            points.append([f"{headshots} HS", 0.5 * headshots])
            labels.append(f"{headshots} HS")

        for column, bonus, label in KILL_BONUSES:
            hits = int((group[column].astype(int) > 0).sum())
            if hits:
                points.append([label, bonus * hits])
                labels.append(label)

        knife = int(group["weapon"].astype(str).str.contains("knife|bayonet").sum())
        if knife:
            points.append(["bıçak", 3 * knife])
            labels.append("bıçak")

        fast = int((group["tick"].diff() <= FAST_KILL_SECONDS * TICKRATE).sum())
        if fast:
            points.append(["hızlı", fast])
            labels.append("hızlı")

        context = _context(group, round_kills, steamid, int(round_played) + 1, won, last_round)
        points += [[label, pts] for label, pts in context]
        score = float(sum(pts for _, pts in points))

        if score < min_score:
            continue
        segments = _segments(moments, pre_seconds, post_seconds)
        highlights.append({
            "round": int(round_played) + 1,
            "kills": n,
            "score": score,
            "labels": labels,
            "ozellikler": [label for label, _ in context],
            "puanlar": points,
            "weapons": sorted(set(group["weapon"].astype(str))),
            "start_tick": segments[0][0],
            "end_tick": segments[-1][1],
            "segments": segments,
        })

    return sorted(highlights, key=lambda h: h["score"], reverse=True)
