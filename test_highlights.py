import pandas as pd

from highlights import POST_SECONDS, PRE_SECONDS, TICKRATE, find_highlights

ME = "76561198000000001"
ENEMY_TEAM = 2
MY_TEAM = 3


def kill(round_no, tick, victim="e", **flags):
    row = {
        "total_rounds_played": round_no,
        "tick": tick,
        "attacker_steamid": ME,
        "attacker_name": "ben",
        "attacker_team_num": MY_TEAM,
        "user_steamid": victim,
        "user_name": victim,
        "user_team_num": ENEMY_TEAM,
        "weapon": "ak47",
        "headshot": False,
        "penetrated": 0,
        "noscope": False,
        "thrusmoke": False,
        "attackerblind": False,
    }
    row.update(flags)
    return row


def test_ace_ranks_above_single_kill():
    rows = [kill(1, 1000)] + [kill(4, 5000 + i * 300, victim=f"e{i}") for i in range(5)]
    result = find_highlights(pd.DataFrame(rows), ME, min_score=0)
    assert result[0]["round"] == 5  # round 4 played -> round 5 shown
    assert "ACE" in result[0]["labels"]
    assert result[0]["kills"] == 5


def test_teamkill_and_suicide_are_ignored():
    rows = [
        kill(1, 1000, user_team_num=MY_TEAM),
        kill(1, 1100, user_steamid=ME),
    ]
    assert find_highlights(pd.DataFrame(rows), ME, min_score=0) == []


def test_wallbang_and_noscope_get_labels():
    rows = [kill(2, 2000, penetrated=1, noscope=True, weapon="awp")]
    result = find_highlights(pd.DataFrame(rows), ME, min_score=0)
    assert "wallbang" in result[0]["labels"]
    assert "noscope" in result[0]["labels"]


def test_clip_window_covers_kills_with_padding():
    rows = [kill(0, 1000), kill(0, 1500, victim="e2")]
    h = find_highlights(pd.DataFrame(rows), ME, min_score=0)[0]
    assert h["start_tick"] == 1000 - PRE_SECONDS * TICKRATE
    assert h["end_tick"] == 1500 + POST_SECONDS * TICKRATE


def test_kills_before_match_start_are_ignored():
    rows = [kill(0, 100 + i, victim=f"e{i}", weapon="knife") for i in range(3)]
    rows.append(kill(0, 5000, victim="late"))
    result = find_highlights(pd.DataFrame(rows), ME, min_score=0, match_start_tick=3000)
    assert result[0]["kills"] == 1


def other_kill(round_no, tick, attacker_team, victim_team, victim="x"):
    return kill(round_no, tick, victim=victim, user_steamid=victim,
                attacker_steamid="other", attacker_name="other",
                attacker_team_num=attacker_team, user_team_num=victim_team)


def clutch_round(winner):
    # 4 takım arkadaşım ölür (1v5), sonra ben 2 kill alırım.
    rows = [other_kill(3, 1000 + i, ENEMY_TEAM, MY_TEAM, victim=f"m{i}") for i in range(4)]
    rows += [kill(3, 2000, victim="e1"), kill(3, 2500, victim="e2")]
    ends = pd.DataFrame([{"tick": 3000, "winner": winner}])
    return pd.DataFrame(rows), ends


def test_won_clutch_is_labelled_with_enemy_count():
    kills, ends = clutch_round("CT")  # MY_TEAM=3 -> CT
    h = find_highlights(kills, ME, min_score=0, round_ends=ends)[0]
    assert "1v5 clutch" in h["labels"]
    assert h["start_tick"] == 1003 - PRE_SECONDS * TICKRATE  # clutch anından başlar


def test_lost_clutch_gets_no_label():
    kills, ends = clutch_round("T")
    h = find_highlights(kills, ME, min_score=0, round_ends=ends)[0]
    assert not any("clutch" in label for label in h["labels"])


def test_clutch_adds_score():
    kills, won = clutch_round("CT")
    _, lost = clutch_round("T")
    won_score = find_highlights(kills, ME, min_score=0, round_ends=won)[0]["score"]
    lost_score = find_highlights(kills, ME, min_score=0, round_ends=lost)[0]["score"]
    assert won_score > lost_score


def test_far_apart_kills_become_separate_segments():
    gap = 20 * TICKRATE
    rows = [kill(0, 1000), kill(0, 1000 + gap, victim="e2")]
    h = find_highlights(pd.DataFrame(rows), ME, min_score=0)[0]
    pre, post = PRE_SECONDS * TICKRATE, POST_SECONDS * TICKRATE
    assert h["segments"] == [[1000 - pre, 1000 + post], [1000 + gap - pre, 1000 + gap + post]]


def test_close_kills_share_one_segment():
    rows = [kill(0, 1000), kill(0, 1000 + 4 * TICKRATE, victim="e2")]
    h = find_highlights(pd.DataFrame(rows), ME, min_score=0)[0]
    assert h["segments"] == [[h["start_tick"], h["end_tick"]]]


def test_min_score_filters_plain_single_kill():
    rows = [kill(0, 1000)]
    assert find_highlights(pd.DataFrame(rows), ME, min_score=3) == []


def test_padding_can_be_changed():
    rows = [kill(0, 1000)]
    h = find_highlights(pd.DataFrame(rows), ME, min_score=0, pre_seconds=5, post_seconds=1)[0]
    assert h["segments"] == [[1000 - 5 * TICKRATE, 1000 + TICKRATE]]


# --- bağlam ölçütleri ---

def one(rows, **kw):
    return find_highlights(pd.DataFrame(rows), ME, min_score=0, **kw)[0]


def test_puan_dokumu_toplami_skora_esit_ve_labels_degismez():
    h = one([kill(2, 2000, headshot=True, penetrated=1), kill(2, 2050, victim="e2")])
    assert h["score"] == sum(p for _, p in h["puanlar"])
    assert h["labels"] == ["2K", "1 HS", "wallbang", "hızlı"]  # klip adı için eski biçim
    assert h["ozellikler"] == ["açılış"]


def test_acilis_yalniz_roundun_ilk_killi():
    rows = [other_kill(1, 900, ENEMY_TEAM, MY_TEAM, victim="m1"), kill(1, 1000)]
    assert "açılış" not in one(rows)["ozellikler"]


def test_ekonomi_farki():
    eco = kill(1, 1000, attacker_round_start_equip_value=700, user_round_start_equip_value=4700)
    esit = kill(1, 1100, victim="e2", attacker_round_start_equip_value=700, user_round_start_equip_value=1500)
    h = one([eco, esit])
    assert ["ekonomi farkı", 1.0] in h["puanlar"]


def test_az_can_havada_bomba_zeus():
    h = one([kill(1, 1000, attacker_health=7, attackerinair=True),
             kill(1, 1500, victim="e2", weapon="inferno"),
             kill(1, 2000, victim="e3", weapon="taser")])
    assert {"az can", "havada", "bomba", "zeus"} <= set(h["ozellikler"])
    assert ["havada", 2.0] in h["puanlar"] and ["zeus", 3.0] in h["puanlar"]


def test_olu_oyuncunun_cani_az_can_sayilmaz():
    assert "az can" not in one([kill(1, 1000, attacker_health=0)])["ozellikler"]


def test_collateral():
    h = one([kill(1, 1000), kill(1, 1000, victim="e2")])
    assert ["collateral", 3.0] in h["puanlar"]
    assert "hızlı" not in h["labels"]  # aynı tick'teki ikinci kill bir kez puanlanır


def test_uzatma_ve_maci_bitiren_round():
    ends = pd.DataFrame([{"tick": 900, "winner": "T"}, {"tick": 3000, "winner": "CT"}])
    h = one([kill(25, 2000)], round_ends=ends)  # round 26, CT (MY_TEAM) kazandı, son round
    assert {"uzatma", "maçı bitirdi"} <= set(h["ozellikler"])
    lost = pd.DataFrame([{"tick": 3000, "winner": "T"}])
    assert "maçı bitirdi" not in one([kill(25, 2000)], round_ends=lost)["ozellikler"]
    later = pd.DataFrame([{"tick": 3000, "winner": "CT"}, {"tick": 9000, "winner": "T"}])
    assert "maçı bitirdi" not in one([kill(25, 2000)], round_ends=later)["ozellikler"]


def test_wingman_clutch_takim_boyuna_gore():
    rows = [other_kill(3, 1000, ENEMY_TEAM, MY_TEAM, victim="m1"),
            kill(3, 2000, victim="e1"), kill(3, 2500, victim="e2")]
    ends = pd.DataFrame([{"tick": 3000, "winner": "CT"}])
    assert "1v2 clutch" in one(rows, round_ends=ends, team_size=2)["labels"]
    assert not any("clutch" in lb for lb in one(rows, round_ends=ends)["labels"])  # 5v5'te 4 kişi hâlâ sağ


def test_wingman_uzatmasi_17_round():
    assert "uzatma" in one([kill(16, 2000)], team_size=2)["ozellikler"]  # round 17
    assert "uzatma" not in one([kill(16, 2000)])["ozellikler"]  # 5v5'te round 17 normal süre
