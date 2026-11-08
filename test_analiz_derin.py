import math

import pandas as pd
import pytest

import analiz_derin as ad
import stats
from highlights import TICKRATE

ME, MATE, E1, E2 = "me", "mate", "e1", "e2"
T, CT = 2, 3


def death(tick, att, vic, att_team, vic_team, rnd=0, weapon="ak47", hs=False, assister=None, flash=False,
          ax=0.0, ay=0.0, ux=10.0, uy=10.0):
    return {"tick": tick, "round": rnd, "attacker_steamid": att, "attacker_team_num": att_team,
            "user_steamid": vic, "user_team_num": vic_team, "weapon": weapon, "headshot": hs,
            "assister_steamid": assister, "assister_team_num": att_team if assister else None,
            "assistedflash": flash, "attacker_X": ax, "attacker_Y": ay, "user_X": ux, "user_Y": uy}


def hurt(tick, att, vic, att_team=T, vic_team=CT, weapon="ak47", hitgroup="chest", dmg=27, health=73, rnd=0):
    return {"tick": tick, "round": rnd, "attacker_steamid": att, "attacker_team_num": att_team,
            "user_steamid": vic, "user_team_num": vic_team, "weapon": weapon, "hitgroup": hitgroup,
            "dmg_health": dmg, "health": health}


def shots_df(rows):
    return pd.DataFrame(rows, columns=["tick", "silah", "recoil_index"])


# --- harita ---

def test_radar_transform_matches_overview_formula():
    r = ad.RADAR["de_dust2"]
    x, y = ad.to_radar("de_dust2", r["pos_x"] + 440, r["pos_y"] - 880)
    assert (x, y) == pytest.approx((100, 200))
    assert ad.to_radar("de_bilinmeyen", 0, 0) is None


def test_all_competitive_maps_have_radar_values():
    for m in ["de_ancient", "de_anubis", "de_dust2", "de_mirage", "de_inferno", "de_nuke", "de_train",
              "de_vertigo", "de_overpass"]:
        info = ad.radar_info(m)
        assert info["x1"] - info["x0"] == pytest.approx(1024 * info["scale"])
        assert info["y1"] == info["pos_y"]


def test_map_box_without_radar_fits_points_in_a_square():
    box = ad.map_box("de_yok", [0, 100], [0, 50])
    assert box["x1"] - box["x0"] == pytest.approx(box["y1"] - box["y0"])
    assert box["x0"] < 0 and box["x1"] > 100 and box["y0"] < 0 and box["y1"] > 50


def test_occupancy_roundtrip_top_row_is_max_y():
    box = {"x0": 0, "x1": 8, "y0": 0, "y1": 8}
    text = ad.occupancy([0.5, 7.5, 3.5, math.nan, 100], [7.5, 0.5, 3.5, 1, 1], box, n=8)
    assert ad.decode_occupancy(text, n=8) == {(0, 0), (7, 7), (3, 4)}


def test_heat_points_use_my_position_and_link_to_other_player():
    kills = pd.DataFrame([death(100, ME, E1, T, CT, rnd=2, hs=True, ax=1, ay=2, ux=3, uy=4)])
    deaths = pd.DataFrame([death(200, E2, ME, CT, T, rnd=3, ax=5, ay=6, ux=7, uy=8),
                           death(300, ME, ME, T, T, rnd=4, weapon="hegrenade", ax=9, ay=9, ux=9, uy=9)])
    pts = ad.heat_points(kills, deaths, ME)
    assert [(p["tur"], p["round"], p["x"], p["y"], p["rx"], p["ry"], p["hs"]) for p in pts] == [
        ("kill", 3, 1, 2, 3, 4, True), ("olum", 4, 7, 8, 5, 6, False), ("olum", 5, 9, 9, None, None, False)]


# --- utility ---

def test_utility_counts_throws_blinds_flash_assists_and_nade_damage():
    throws = pd.DataFrame({"user_steamid": [ME, ME, ME, ME, ME, MATE, ME],
                           "weapon": ["weapon_flashbang", "weapon_flashbang", "weapon_smokegrenade",
                                      "weapon_molotov", "weapon_incgrenade", "weapon_hegrenade", "weapon_ak47"]})
    blinds = pd.DataFrame([
        {"attacker_steamid": ME, "attacker_team_num": T, "user_steamid": E1, "user_team_num": CT, "blind_duration": 2.5},
        {"attacker_steamid": ME, "attacker_team_num": T, "user_steamid": E2, "user_team_num": CT, "blind_duration": 1.5},
        {"attacker_steamid": ME, "attacker_team_num": T, "user_steamid": MATE, "user_team_num": T, "blind_duration": 3.0},
        {"attacker_steamid": ME, "attacker_team_num": T, "user_steamid": ME, "user_team_num": T, "blind_duration": 4.0},
        {"attacker_steamid": MATE, "attacker_team_num": T, "user_steamid": E1, "user_team_num": CT, "blind_duration": 9.0},
    ])
    deaths = pd.DataFrame([death(10, MATE, E1, T, CT, assister=ME, flash=True),
                           death(20, MATE, E2, T, CT, assister=ME, flash=False),
                           death(30, MATE, ME, T, T, assister=ME, flash=True)])  # takım kill'i sayılmaz
    damage = pd.DataFrame({"attacker_steamid": [ME, ME, ME, MATE], "weapon": ["hegrenade", "inferno", "ak47", "hegrenade"],
                           "dmg": [40, 12, 100, 50]})
    u = ad.utility(ME, throws, blinds, deaths, damage, rounds=4)
    assert u["atilan"] == {"flas": 2, "smoke": 1, "molotof": 2, "he": 0, "decoy": 0}
    assert u["atilan_toplam"] == 5 and u["round_basi"] == 1.25
    assert u["flas_asist"] == 1
    assert (u["kor_dusman"], u["kor_dusman_sn"], u["flas_basi_kor_sn"], u["flas_basi_dusman"]) == (2, 4.0, 2.0, 1.0)
    assert (u["kor_takim"], u["kor_takim_sn"]) == (1, 3.0)
    assert u["bomba_hasar"] == {"he": 40, "molotof": 12} and u["bomba_hasar_toplam"] == 52


def test_utility_without_flashes_has_no_per_flash_average():
    empty = pd.DataFrame(columns=["user_steamid", "weapon"])
    blinds = pd.DataFrame(columns=["attacker_steamid", "attacker_team_num", "user_steamid", "user_team_num", "blind_duration"])
    deaths = pd.DataFrame(columns=list(death(0, ME, E1, T, CT)))
    damage = pd.DataFrame(columns=["attacker_steamid", "weapon", "dmg"])
    u = ad.utility(ME, empty, blinds, deaths, damage, rounds=0)
    assert u["flas_basi_kor_sn"] is None and u["round_basi"] == 0.0 and u["atilan_toplam"] == 0


# --- nişan ---

def test_shot_table_names_from_weapon_fire_with_item_def_fallback():
    bullets = pd.DataFrame({"tick": [10, 11, 12, 13], "user_steamid": [ME, ME, ME, MATE],
                            "item_def_index": [7, 61, 9, 7], "recoil_index": [0.0, 0.0, 0.0, 0.0]})
    fires = pd.DataFrame({"tick": [10, 11, 13, 14], "user_steamid": [ME, ME, MATE, ME],
                          "weapon": ["weapon_ak47", "weapon_usp_silencer", "weapon_ak47", "weapon_flashbang"]})
    out = ad.shot_table(bullets, fires, ME)
    assert out["silah"].tolist() == ["ak47", "usp_silencer", "awp"]


def test_aim_accuracy_spray_and_headshots_by_weapon():
    shots = shots_df([(100, "ak47", 0), (106, "ak47", 1), (112, "ak47", 2), (118, "ak47", 3), (124, "ak47", 4),
                      (200, "usp_silencer", 0), (210, "usp_silencer", 0.7)])
    hurts = pd.DataFrame([
        hurt(100, ME, E1, hitgroup="head"), hurt(118, ME, E1), hurt(124, ME, E2),  # ak: 3 isabet (1 sprey dışı)
        hurt(200, ME, E2, weapon="hkp2000", hitgroup="head"),                     # USP-S hasarı hkp2000 görünür
        hurt(150, ME, MATE, vic_team=T),                                           # takım hasarı sayılmaz
        hurt(160, ME, E1, weapon="hegrenade"),                                     # bomba nişan değil
    ])
    kills = pd.DataFrame([death(124, ME, E2, T, CT, hs=False), death(200, ME, E2, T, CT, weapon="usp_silencer", hs=True)])
    a = ad.aim(ME, shots, hurts, kills)
    assert (a["atis"], a["isabetli_atis"], a["isabet_yuzde"]) == (7, 4, 57.1)
    assert (a["sprey_atis"], a["sprey_isabet_yuzde"]) == (2, 100.0)  # recoil_index >= 3, yalnız otomatik silah
    assert (a["ilk_mermi_atis"], a["ilk_mermi_isabet_yuzde"]) == (3, 66.7)
    assert (a["vurus"], a["kafa_vurus"], a["kafa_vurus_yuzde"]) == (4, 2, 50.0)
    by = {w["silah"]: w for w in a["silahlar"]}
    assert set(by) == {"ak47", "usp_silencer"}
    assert (by["ak47"]["atis"], by["ak47"]["isabetli_atis"], by["ak47"]["kafa_yuzde"]) == (5, 3, 33.3)
    assert (by["usp_silencer"]["vurus"], by["usp_silencer"]["kafa"], by["usp_silencer"]["hs_kill_yuzde"]) == (1, 1, 100.0)


def test_aim_with_no_shots_gives_none_percentages():
    a = ad.aim(ME, shots_df([]), pd.DataFrame([hurt(1, E1, ME, CT, T)]), pd.DataFrame(columns=list(death(0, ME, E1, T, CT))))
    assert a["atis"] == 0 and a["isabet_yuzde"] is None and a["sprey_isabet_yuzde"] is None and a["silahlar"] == []


def test_engagement_is_first_gun_damage_per_round_and_victim():
    hurts = pd.DataFrame([hurt(300, ME, E1, rnd=0), hurt(100, ME, E1, rnd=0, weapon="hegrenade"),
                          hurt(200, ME, E1, rnd=0), hurt(250, ME, E2, rnd=0), hurt(900, ME, E1, rnd=1),
                          hurt(50, MATE, E1, rnd=0)])
    first = ad.engagements(ME, hurts)
    assert sorted(zip(first["round"], first["user_steamid"], first["tick"])) == [(0, E1, 200), (0, E2, 250), (1, E1, 900)]


def spotted_rows(victim, ticks, by=(ME,)):
    return [{"tick": t, "steamid": victim, "approximate_spotted_by": list(by)} for t in ticks]


def test_ttd_is_time_from_first_sight_to_first_damage():
    first = pd.DataFrame({"tick": [1000, 2000, 3000, 4000], "round": [0, 1, 2, 3], "user_steamid": [E1, E1, E2, E2]})
    rows = (spotted_rows(E1, range(968, 1001))                   # 32 tick görüş -> 500 ms
            + spotted_rows(E1, range(1960, 1990))                 # hasar anında görmüyor -> sayılmaz
            + spotted_rows(E2, range(3000 - 2 * TICKRATE - 20, 3001))  # pencereden uzun -> sayılmaz
            + spotted_rows(E2, [3990, 3991, 3994, 3995, 3996, 3997, 3998, 3999, 4000])  # 2 tick boşluk tolere
            + spotted_rows(E2, range(3900, 3950), by=(MATE,)))   # başkası görüyor
    ticks = ad.ttd_ticks(ME, first, pd.DataFrame(rows))
    assert ticks == [32, 10]
    s = ad.ttd_summary(ticks)
    assert s["ornek"] == 2 and s["medyan_ms"] == round((500 + 156.25) / 2)
    assert [b["sayi"] for b in s["dagilim"]] == [1, 0, 1, 0, 0]


def test_ttd_summary_empty_and_tick_list():
    assert ad.ttd_summary([])["medyan_ms"] is None
    ticks = ad.ttd_tick_list(pd.DataFrame({"tick": [200]}), window=10)
    assert ticks[0] == 200 - 10 - ad.TTD_BOSLUK - 1 and ticks[-1] == 200


# --- birleştirme / şema ---

def test_build_derin_block_and_refresh_check():
    kills = pd.DataFrame([death(100, ME, E1, T, CT, ax=-1000, ay=1000)])
    deaths = pd.DataFrame([death(100, ME, E1, T, CT, ax=-1000, ay=1000), death(200, E2, ME, CT, T, ux=0, uy=0)])
    hurts = pd.DataFrame([hurt(100, ME, E1)])
    damage = hurts.assign(dmg=27)
    throws = pd.DataFrame({"user_steamid": [ME], "weapon": ["weapon_smokegrenade"]})
    blinds = pd.DataFrame(columns=["attacker_steamid", "attacker_team_num", "user_steamid", "user_team_num", "blind_duration"])
    positions = pd.DataFrame({"X": [-1000.0, 0.0], "Y": [1000.0, 0.0]})
    d = ad.build_derin("de_dust2", ME, 2, kills, deaths, hurts, damage, throws, blinds,
                       shots_df([(100, "ak47", 0)]), [32], positions)
    assert d["surum"] == ad.DERIN_SURUM
    assert d["harita"]["radar"]["scale"] == 4.4 and len(d["harita"]["noktalar"]) == 2
    assert len(ad.decode_occupancy(d["harita"]["zemin"]["bitler"])) == 2
    assert d["utility"]["atilan"]["smoke"] == 1
    assert d["nisan"]["isabet_yuzde"] == 100.0 and d["nisan"]["ttd"]["medyan_ms"] == 500
    assert not ad.needs_refresh({"derin": d})
    assert ad.needs_refresh({"harita": "de_dust2"})  # eski json
    assert ad.needs_refresh({"derin": {"surum": 0, "hata": "x"}})


def test_deep_stats_failure_keeps_basic_stats(monkeypatch):
    def boom(*a, **k):
        raise KeyError("fire_bullets")
    monkeypatch.setattr(ad, "derin_from_parser", boom)
    out = stats.deep_stats(None, "de_dust2", ME, 0, [100, 200], [150])
    assert out["surum"] == 0 and "fire_bullets" in out["hata"]
