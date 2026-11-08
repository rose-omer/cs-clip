import json
import os

import pytest

import eniyi


@pytest.mark.parametrize("name, expected", [
    ("anubis_e3c103b2_R11_1v3clutch_4K_hegrenade_m4a1_silencer.mp4",
     ("anubis", "e3c103b2", 11, ["1v3 clutch", "4K"], ["hegrenade", "m4a1_silencer"])),
    ("dust2_a95f6ac2_R09_3K_3-HS_m4a1.mp4", ("dust2", "a95f6ac2", 9, ["3K", "3 HS"], ["m4a1"])),
    ("ancient_a53a1e7b_R05_2K_1-HS_smoke-arkası_m4a1.mp4",
     ("ancient", "a53a1e7b", 5, ["2K", "1 HS", "smoke arkası"], ["m4a1"])),
    ("ancient_2dd01012_R02_2K_1HS_smokearkas_deagle.mp4",
     ("ancient", "2dd01012", 2, ["2K", "1 HS", "smoke arkası"], ["deagle"])),
    ("anubis_e3c103b2_R02_2K_2HS_hzl_mp7.mp4", ("anubis", "e3c103b2", 2, ["2K", "2 HS", "hızlı"], ["mp7"])),
    ("anubis_ddb52137_R19_2K_2HS_wallbang_m4a1_silencer.mp4",
     ("anubis", "ddb52137", 19, ["2K", "2 HS", "wallbang"], ["m4a1_silencer"])),
    ("ancient_2dd01012_R19_1v2clutch_4K_ak47.mp4", ("ancient", "2dd01012", 19, ["1v2 clutch", "4K"], ["ak47"])),
    ("dust2_a95f6ac2_R16_1-HS_noscope_ssg08.mp4", ("dust2", "a95f6ac2", 16, ["1 HS", "noscope"], ["ssg08"])),
    ("mirage_12345678_R03_ACE_1v3-clutch_hızlı_bıçak_knife_t.mp4",
     ("mirage", "12345678", 3, ["ACE", "1v3 clutch", "hızlı", "bıçak"], ["knife_t"])),
    ("cache_3d2d7c71_R10_wallbang_scar20.mp4", ("cache", "3d2d7c71", 10, ["wallbang"], ["scar20"])),
    ("nuke_aaaa1111_R07.mp4", ("nuke", "aaaa1111", 7, [], [])),
    ("cs_office_bbbb2222_R01_2K_usp_silencer_off.mp4", ("cs_office", "bbbb2222", 1, ["2K"], ["usp_silencer_off"])),
])
def test_parse_name(name, expected):
    r = eniyi.parse_name(name)
    assert (r["harita"], r["kod"], r["round"], r["etiketler"], r["silahlar"]) == expected


@pytest.mark.parametrize("name", ["montaj.mp4", "en_iyi_montaj.mp4", "en_iyi_montaj.part.mp4", "notlar.txt",
                                  "anubis_e3c103b2_R11_2K.mkv"])
def test_parse_name_rejects_other_files(name):
    assert eniyi.parse_name(name) is None


@pytest.mark.parametrize("labels, score", [
    (["1v3 clutch", "4K"], 17),  # 10 + 7
    (["3K", "3 HS"], 7.5),
    (["2K", "1 HS", "smoke arkası"], 5),
    (["2K", "2 HS", "hızlı"], 5),
    (["2K", "2 HS", "wallbang"], 6),
    (["1 HS", "noscope"], 3.5),  # kill etiketi yok: 1 kill
    (["wallbang"], 3),
    ([], 1),
    (["ACE"], 16),
    (["ACE", "1v5 clutch", "bıçak", "kör"], 16 + 14 + 3 + 2),
])
def test_estimate_score(labels, score):
    assert eniyi.estimate_score(labels) == score


def test_rank_score_then_newer_first():
    rows = [{"ad": "a", "skor": 5.0, "tarih": "2026-11-02T10:00:00"},
            {"ad": "b", "skor": 7.0, "tarih": "2026-11-01T10:00:00"},
            {"ad": "c", "skor": 5.0, "tarih": "2026-11-03T10:00:00"}]
    assert [r["ad"] for r in eniyi.rank(rows)] == ["b", "c", "a"]


def touch(p, size=1024, mtime=None):
    p.write_bytes(b"v" * size)
    if mtime:
        os.utime(p, (mtime, mtime))
    return p


def test_best_clips_uses_real_scores_and_skips_other_files(tmp_path):
    clips = tmp_path / "klipler"
    (clips / "eski").mkdir(parents=True)
    touch(clips / "eski" / "anubis_e3c103b2_R01_ACE_ak47.mp4")
    touch(clips / "montaj.mp4")
    touch(clips / "en_iyi_montaj.mp4")
    touch(clips / "anubis_e3c103b2_R11_1v3clutch_4K_hegrenade_m4a1_silencer.mp4", mtime=1_700_000_000)
    touch(clips / "dust2_a95f6ac2_R09_3K_3-HS_m4a1.mp4", 1024**2 * 3, mtime=1_700_000_100)
    touch(clips / "dust2_a95f6ac2_R05_2K_m4a1.mp4")
    hl = tmp_path / "1-a95f6ac2-x-1-1.highlights.json"
    hl.write_text(json.dumps([{"round": 9, "score": 20.5, "labels": ["3K", "3 HS", "wallbang"],
                               "weapons": ["m4a1", "deagle"]}]), encoding="utf-8")
    rows = eniyi.best_clips(clips, {"a95f6ac2": ("1-a95f6ac2-x-1-1", hl), "e3c103b2": ("1-e3c103b2-y-1-1", None)})
    assert [(r["ad"], r["skor"], r["tahmini"], r["demo"]) for r in rows] == [
        ("dust2_a95f6ac2_R09_3K_3-HS_m4a1.mp4", 20.5, False, "1-a95f6ac2-x-1-1"),
        ("anubis_e3c103b2_R11_1v3clutch_4K_hegrenade_m4a1_silencer.mp4", 17.0, True, "1-e3c103b2-y-1-1"),
        ("dust2_a95f6ac2_R05_2K_m4a1.mp4", 3.0, True, "1-a95f6ac2-x-1-1"),  # json'da round yok: tahmin
    ]
    top = rows[0]
    assert top["etiketler"] == ["3K", "3 HS", "wallbang"] and top["silahlar"] == ["m4a1", "deagle"]
    assert top["klip"] == "/klip/dust2_a95f6ac2_R09_3K_3-HS_m4a1.mp4"
    assert (top["harita"], top["kod"], top["round"], top["boyut_mb"]) == ("dust2", "a95f6ac2", 9, 3.0)
    assert len(top["tarih"]) == 19 and "T" in top["tarih"]


def test_best_clips_without_demo(tmp_path):
    touch(tmp_path / "ancient_a53a1e7b_R05_2K_1-HS_smoke-arkası_m4a1.mp4")
    (row,) = eniyi.best_clips(tmp_path)
    assert row["demo"] is None and row["tahmini"] is True and row["skor"] == 5.0
    assert eniyi.best_clips(tmp_path / "yok") == []


def test_broken_highlights_json_falls_back_to_estimate(tmp_path):
    touch(tmp_path / "dust2_a95f6ac2_R09_3K_3-HS_m4a1.mp4")
    hl = tmp_path / "d.highlights.json"
    hl.write_text("{bozuk", encoding="utf-8")
    (row,) = eniyi.best_clips(tmp_path, {"a95f6ac2": ("d", hl)})
    assert row["tahmini"] is True and row["skor"] == 7.5 and row["demo"] == "d"


def test_montage_info(tmp_path):
    assert eniyi.montage_info(tmp_path) is None
    touch(tmp_path / "en_iyi_montaj.mp4", 1024**2 * 2)
    assert eniyi.montage_info(tmp_path)["adet"] is None
    (tmp_path / "en_iyi_montaj.json").write_text('{"adet": 4}', encoding="utf-8")
    info = eniyi.montage_info(tmp_path)
    assert (info["klip"], info["adet"], info["boyut_mb"]) == ("/klip/en_iyi_montaj.mp4", 4, 2.0)


@pytest.mark.parametrize("body, n", [({}, 10), ({"adet": 1}, 1), ({"adet": 50}, 50), ({"adet": 0}, None),
                                     ({"adet": 51}, None), ({"adet": "5"}, None), ({"adet": True}, None),
                                     ({"adet": 2.5}, None), ([], None), (None, None)])
def test_parse_count(body, n):
    assert eniyi.parse_count(body) == n
