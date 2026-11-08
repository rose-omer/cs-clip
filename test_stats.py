import json
import os

import pandas as pd

from highlights import TICKRATE
from stats import (
    assign_rounds, build_stats, hltv_rating, load_stats, opening_duels, round_bounds,
    save_stats, team_groups, traded_deaths, valid_kills,
)

T, CT = 2, 3
A_TEAM = ["a1", "a2"]  # ilk yarı T
B_TEAM = ["b1", "b2"]  # ilk yarı CT


def death(tick, attacker, victim, att_team, vic_team, assister=None, weapon="ak47", headshot=False):
    return {
        "tick": tick, "attacker_steamid": attacker, "attacker_team_num": att_team,
        "user_steamid": victim, "user_team_num": vic_team,
        "assister_steamid": assister, "assister_team_num": att_team if assister else None,
        "weapon": weapon, "headshot": headshot,
    }


def hurt(tick, attacker, victim, att_team, vic_team, dmg, health):
    return {"tick": tick, "attacker_steamid": attacker, "attacker_team_num": att_team,
            "user_steamid": victim, "user_team_num": vic_team, "dmg_health": dmg, "health": health}


def sides_for(ticks_and_swap):
    """[(tick, a_side)] -> her round_end tick'inde 4 oyuncunun tarafı."""
    rows = []
    for tick, a_side in ticks_and_swap:
        rows += [{"tick": tick, "steamid": s, "team_num": a_side, "team_clan_name": "team_A"} for s in A_TEAM]
        rows += [{"tick": tick, "steamid": s, "team_num": 5 - a_side, "team_clan_name": ""} for s in B_TEAM]
    return pd.DataFrame(rows)


def ends(rows):
    return pd.DataFrame([{"tick": t, "winner": w, "reason": r} for t, w, r in rows])


# --- rating ---

def test_rating_matches_hltv_formula():
    multi = {1: 6, 2: 3, 3: 1}
    kill_r = 14 / 22 / 0.679
    surv_r = (22 - 18) / 22 / 0.317
    mk_r = (6 + 4 * 3 + 9 * 1) / 22 / 1.277
    assert hltv_rating(14, 18, 22, multi) == round((kill_r + 0.7 * surv_r + mk_r) / 2.7, 2)


def test_rating_with_no_rounds_is_zero():
    assert hltv_rating(0, 0, 0, {}) == 0.0


# --- kill kuralları ---

def test_teamkill_suicide_and_world_are_not_kills():
    df = pd.DataFrame([
        death(10, "a1", "b1", T, CT),
        death(11, "a1", "a2", T, T),       # takım kill'i
        death(12, "a1", "a1", T, T),       # intihar
        death(13, None, "b2", None, CT),   # dünya
    ])
    assert valid_kills(df)["tick"].tolist() == [10]


def test_opening_kill_is_first_kill_of_each_round():
    df = pd.DataFrame([death(50, "b1", "a2", CT, T), death(20, "a1", "b1", T, CT), death(300, "b2", "a1", CT, T)])
    df["round"] = [0, 0, 1]
    first = opening_duels(df)
    assert list(zip(first["round"], first["attacker_steamid"])) == [(0, "a1"), (1, "b2")]


def test_trade_within_five_seconds_counts():
    df = pd.DataFrame([
        death(1000, "b1", "a1", CT, T),                      # a1 ölür
        death(1000 + 4 * TICKRATE, "a2", "b1", T, CT),       # a2 katili 4 sn sonra öldürür
        death(2000, "b2", "a2", CT, T),                      # a2 ölür
        death(2000 + 6 * TICKRATE, "a1", "b2", T, CT),       # 6 sn: trade değil
    ])
    df["round"] = 0
    team_of = {"a1": 0, "a2": 0, "b1": 1, "b2": 1}
    assert traded_deaths(df, team_of) == {(0, "a1")}


# --- roundlar ---

def test_post_round_kill_stays_in_its_round():
    bounds = round_bounds([1000, 2000, 3000], [1200, 2200])
    events = pd.DataFrame({"tick": [500, 1000, 1100, 1300, 2100, 2500, 3100]})
    assert assign_rounds(events, bounds).tolist() == [0, 0, 0, 1, 1, 2, 2]


def test_team_mapping_survives_side_swap():
    sides = sides_for([(100, T), (200, T), (300, CT), (400, CT)])
    sides["round"] = sides["tick"].map({100: 0, 200: 1, 300: 2, 400: 3})
    team_of, side0 = team_groups(sides)
    assert team_of == {"a1": 0, "a2": 0, "b1": 1, "b2": 1}
    assert side0 == {0: T, 1: T, 2: CT, 3: CT}


def test_late_joiner_gets_team_by_round_side():
    sides = sides_for([(100, T), (200, CT)])
    sides = pd.concat([sides, pd.DataFrame([{"tick": 200, "steamid": "yedek", "team_num": CT}])])
    sides["round"] = sides["tick"].map({100: 0, 200: 1})
    team_of, _ = team_groups(sides)
    assert team_of["yedek"] == 0  # ikinci yarıda A ile aynı tarafta


# --- uçtan uca ---

def match(**kw):
    """4 roundluk mini maç; 2. roundtan sonra devre (taraf değişimi)."""
    round_ends = ends([
        (50, None, "draw"),               # ısınma sonu
        (1000, "T", "ct_killed"),         # A (T) kazanır
        (2000, "CT", "t_killed"),         # B (CT) kazanır
        (3000, "CT", "t_killed"),         # A artık CT -> A
        (4000, "CT", "bomb_defused"),     # A
    ])
    deaths = pd.DataFrame([
        death(40, "a1", "b1", T, CT, weapon="knife"),            # ısınma: sayılmaz
        death(500, "a1", "b1", T, CT, headshot=True),
        death(600, "a1", "b2", T, CT, assister="a2"),
        death(1500, "b1", "a1", CT, T),
        death(1700, "b1", "a2", CT, T),
        death(2500, "a1", "b2", CT, T, weapon="m4a1"),
        death(2600, "b1", "a1", T, CT),
        death(3500, "a2", "b1", CT, T),
    ])
    hurts = pd.DataFrame([
        hurt(40, "a1", "b1", T, CT, 100, 0),     # ısınma
        hurt(400, "a1", "b1", T, CT, 30, 70),
        hurt(500, "a1", "b1", T, CT, 120, 0),    # kalan 70 ile sınırlı
        hurt(600, "a1", "b2", T, CT, 100, 0),
    ])
    sides = sides_for([(1000, T), (2000, T), (3000, CT), (4000, CT)])
    args = dict(map_name="de_test", names={s: s.upper() for s in A_TEAM + B_TEAM}, deaths=deaths, hurts=hurts,
                round_ends=round_ends, official_ticks=[1100, 2100, 3100], sides=sides, steamid="a1", match_start=100)
    args.update(kw)
    return build_stats(**args)


def test_score_is_counted_per_team_across_halves():
    s = match()
    assert s["round_sayisi"] == 4
    assert [t["skor"] for t in s["takimlar"]] == [3, 1]
    assert [t["ad"] for t in s["takimlar"]] == ["team_A", "Takım B"]
    assert s["takimlar"][0]["kazandi"] and not s["takimlar"][1]["kazandi"]
    assert [r["kazanan_takim"] for r in s["roundlar"]] == [0, 1, 0, 0]
    assert s["benim_takim"] == 0


def test_warmup_is_excluded_and_player_row():
    s = match()
    me = next(p for p in s["oyuncular"] if p["ben"])
    assert (me["kill"], me["death"], me["assist"]) == (3, 2, 0)
    assert me["adr"] == round((30 + 70 + 100) / 4, 1)
    assert me["hs_yuzde"] == round(100 / 3, 1)
    assert me["acilis_kill"] == 2 and me["acilis_death"] == 1
    assert me["cok_kill"] == {"2": 1, "3": 0, "4": 0, "5": 0}
    # KAST: R1 kill, R2 öldü (trade yok), R3 kill, R4 hayatta
    assert me["kast"] == 75.0
    assert [r["benim_kill"] for r in s["roundlar"]] == [2, 0, 1, 0]
    assert [r["ben_oldum"] for r in s["roundlar"]] == [False, True, True, False]
    assert s["silahlar"] == [{"silah": "ak47", "kill": 2, "hs": 1}, {"silah": "m4a1", "kill": 1, "hs": 0}]
    a2 = next(p for p in s["oyuncular"] if p["steamid"] == "a2")
    assert a2["assist"] == 1


def test_players_sorted_by_team_then_rating():
    s = match()
    teams = [p["takim"] for p in s["oyuncular"]]
    assert teams == sorted(teams)
    for t in (0, 1):
        ratings = [p["rating"] for p in s["oyuncular"] if p["takim"] == t]
        assert ratings == sorted(ratings, reverse=True)
    json.dumps(s, ensure_ascii=False)  # JSON'a yazılabilir


# --- önbellek ---

def test_save_and_load_stats(tmp_path):
    demo = tmp_path / "mac.dem"
    demo.write_bytes(b"x")
    os.utime(demo, (1000, 1000))
    out = save_stats(demo, {"harita": "de_anubis", "takimlar": [{"ad": "Takım A"}]})
    assert out.name == "mac.stats.json"
    assert load_stats(demo)["takimlar"][0]["ad"] == "Takım A"
    os.utime(demo, None)  # demo yenilendi
    os.utime(out, (1000, 1000))
    assert load_stats(demo) is None


def test_load_stats_without_cache(tmp_path):
    assert load_stats(tmp_path / "yok.dem") is None
