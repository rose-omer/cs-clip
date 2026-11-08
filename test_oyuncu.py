"""Herhangi bir oyuncunun highlight'ları: dosya adları, etiketler, arayüz uçları, klip.py --oyuncu."""

import json
import os
import sys
import threading
import urllib.request

import pandas as pd
import pytest

import analyze
import arayuz
import eniyi
import klip
from demofile import demo_files
from render import clip_filename
from test_arayuz import app, fake_ffmpeg, post_error, post_json, server  # noqa: F401 (fikstürler)

DEFAULT_SID, MERT_SID = "76561198963443734", "76561198877001245"
HL = {"round": 5, "score": 10.0, "labels": ["4K"], "weapons": ["ak47"], "start_tick": 0, "end_tick": 640}


# --- analyze ---

@pytest.mark.parametrize("name, sid, tag", [
    ("Mert_06", "1", "Mert06"), ("Bora.", "1", "Bora"), ("çağrı ğ", "1", "çağrığ"),
    ("~*~", "76561198877001245", "77001245"), ("a" * 30, "1", "a" * 20),
])
def test_player_tag_is_filename_safe(name, sid, tag):
    assert analyze.player_tag(name, sid) == tag


def test_highlights_path_keeps_default_name(tmp_path):
    demo = tmp_path / "1-abc-1-1.dem"
    assert analyze.highlights_path(demo).name == "1-abc-1-1.highlights.json"
    assert analyze.highlights_path(demo, MERT_SID).name == f"1-abc-1-1.highlights.{MERT_SID}.json"
    with pytest.raises(ValueError):
        analyze.highlights_path(demo, "../x")


def test_save_player_default_list_other_dict(tmp_path):
    demo = tmp_path / "m.dem"
    base = {"harita": "de_x", "highlights": [HL]}
    f = analyze.save_player(demo, {**base, "steamid": DEFAULT_SID, "ad": "DuranEnnmi", "varsayilan": True})
    assert f.name == "m.highlights.json" and json.loads(f.read_text(encoding="utf-8")) == [HL]
    g = analyze.save_player(demo, {**base, "steamid": MERT_SID, "ad": "Mert_06", "varsayilan": False})
    assert g.name == f"m.highlights.{MERT_SID}.json"
    assert analyze.read_player(g) == {"oyuncu": "Mert_06", "steamid": MERT_SID, "etiket": "p-Mert06",
                                      "highlights": [HL]}
    assert analyze.read_player(f) == {"highlights": [HL]}


def _kills():
    """İki oyuncunun 2K'sı: 1 (T) ve 2 (CT) aynı roundda."""
    rows = []
    for i, (att, vic, at, vt) in enumerate([("1", "21", 2, 3), ("1", "22", 2, 3), ("2", "11", 3, 2), ("2", "12", 3, 2)]):
        rows.append({"tick": 100 + i * 64, "total_rounds_played": 0, "attacker_steamid": att, "user_steamid": vic,
                     "attacker_team_num": at, "user_team_num": vt, "headshot": False, "penetrated": 0, "noscope": False,
                     "thrusmoke": False, "attackerblind": False, "weapon": "ak47", "user_team_num_": vt})
    return pd.DataFrame(rows)


def test_analyze_all_and_player_use_one_parse(monkeypatch, tmp_path):
    players = pd.DataFrame({"steamid": ["1", "2", "2"], "name": ["DuranEnnmi", "Mert_06", "Mert_06"]})
    calls = []
    monkeypatch.setattr(analyze, "_load", lambda d: calls.append(d) or ("de_x", players, _kills(), 0, None))
    res = analyze.analyze_all(tmp_path / "m.dem", default="duranennmi")
    assert len(calls) == 1
    assert [(p["steamid"], p["ad"], p["varsayilan"], [h["labels"] for h in p["highlights"]]) for p in res["oyuncular"]] \
        == [("1", "DuranEnnmi", True, [["2K", "hızlı"]]), ("2", "Mert_06", False, [["2K", "hızlı"]])]
    r = analyze.analyze_player(tmp_path / "m.dem", "2", default="DuranEnnmi")
    assert (r["steamid"], r["ad"], r["varsayilan"]) == ("2", "Mert_06", False)
    assert analyze.analyze_player(tmp_path / "m.dem", "1", default="DuranEnnmi")["varsayilan"] is True
    with pytest.raises(SystemExit, match="yok"):
        analyze.analyze_player(tmp_path / "m.dem", "kimse")


# --- adlar ---

def test_clip_filename_player_tag_after_round():
    assert clip_filename("anubis_59cf10f2", HL) == "anubis_59cf10f2_R05_4K_ak47.mp4"
    assert clip_filename("anubis_59cf10f2", HL, "Mert06") == "anubis_59cf10f2_R05_p-Mert06_4K_ak47.mp4"


def test_parse_name_reads_player_tag():
    info = eniyi.parse_name("anubis_59cf10f2_R05_p-Mert06_4K_1-HS_ak47.mp4")
    assert (info["round"], info["oyuncu"], info["etiketler"], info["silahlar"]) == (5, "Mert06", ["4K", "1 HS"], ["ak47"])
    assert eniyi.parse_name("anubis_59cf10f2_R05_4K_ak47.mp4")["oyuncu"] is None
    assert eniyi.parse_name("anubis_59cf10f2_R05_p-Mert06.mp4")["oyuncu"] == "Mert06"
    assert eniyi.parse_name("anubis_59cf10f2_R05_p250.mp4")["silahlar"] == ["p250"]  # silah, oyuncu değil


def test_best_clips_uses_player_files(tmp_path):
    demos, out = tmp_path / "d", tmp_path / "k"
    demos.mkdir(), out.mkdir()
    default = demos / "1-59cf10f2-x-1-1.highlights.json"
    default.write_text(json.dumps([{**HL, "round": 5, "score": 3.0, "labels": ["2K"]}]), encoding="utf-8")
    analyze.save_player(demos / "1-59cf10f2-x-1-1.dem", {"steamid": MERT_SID, "ad": "Mert_06", "varsayilan": False,
                                                          "highlights": [{**HL, "score": 12.5}]})
    for n in ["anubis_59cf10f2_R05_2K.mp4", "anubis_59cf10f2_R05_p-Mert06_4K_ak47.mp4",
              "anubis_59cf10f2_R07_p-Bilinmez_3K.mp4"]:
        (out / n).write_bytes(b"v")
    rows = eniyi.best_clips(out, {"59cf10f2": ("1-59cf10f2-x-1-1", default)})
    got = [(r["ad"], r["skor"], r["tahmini"], r["oyuncu"], r["oyuncu_ad"]) for r in rows]
    assert got == [("anubis_59cf10f2_R05_p-Mert06_4K_ak47.mp4", 12.5, False, "Mert06", "Mert_06"),
                   ("anubis_59cf10f2_R07_p-Bilinmez_3K.mp4", 6.0, True, "Bilinmez", "Bilinmez"),
                   ("anubis_59cf10f2_R05_2K.mp4", 3.0, False, None, None)]
    assert [r["ad"] for r in eniyi.by_player(rows, None)] == ["anubis_59cf10f2_R05_2K.mp4"]
    assert len(eniyi.by_player(rows, "mert06")) == 1 and len(eniyi.by_player(rows, eniyi.ALL_PLAYERS)) == 3


@pytest.mark.parametrize("body, expected", [
    ({}, (True, None)), ({"oyuncu": ""}, (True, None)), ({"oyuncu": "*"}, (True, "*")),
    ({"oyuncu": "Mert06"}, (True, "Mert06")), ({"oyuncu": "../x"}, (False, None)), ({"oyuncu": 3}, (False, None)),
])
def test_parse_player(body, expected):
    assert eniyi.parse_player(body) == expected


def test_demo_files_includes_player_highlights(tmp_path):
    for name in ["m.dem", "m.highlights.json", f"m.highlights.{MERT_SID}.json", f"mx.highlights.{MERT_SID}.json"]:
        (tmp_path / name).write_bytes(b"x")
    assert sorted(p.name for p in demo_files(tmp_path / "m.dem")) == sorted([
        "m.dem", "m.highlights.json", f"m.highlights.{MERT_SID}.json"])


# --- arayüz ---

DID = "1-59cf10f2-x-1-1"


@pytest.fixture
def demo(app):
    """Analiz edilmiş demo: istatistik + varsayılan oyuncunun highlight'ları önbellekte."""
    a, demos, clips = app
    (demos / f"{DID}.dem").write_bytes(b"d")
    stats = {"oyuncu_steamid": DEFAULT_SID, "oyuncular": [
        {"steamid": DEFAULT_SID, "ad": "DuranEnnmi", "takim": 0}, {"steamid": MERT_SID, "ad": "Mert_06", "takim": 0}]}
    (demos / f"{DID}.stats.json").write_text(json.dumps(stats), encoding="utf-8")
    (demos / f"{DID}.highlights.json").write_text(json.dumps([{**HL, "round": 3, "score": 6.0, "labels": ["3K"]}]),
                                                  encoding="utf-8")
    (clips / "anubis_59cf10f2_R03_3K.mp4").write_bytes(b"v")
    (clips / "anubis_59cf10f2_R05_p-Mert06_4K_ak47.mp4").write_bytes(b"v")
    later = os.path.getmtime(demos / f"{DID}.dem") + 5
    for f in demos.glob("*.json"):
        os.utime(f, (later, later))
    return a, demos, clips


def fake_analyze(monkeypatch, demos):
    calls = []

    def one(demo, who, pre, post, default=None):
        calls.append(who)
        if who in (MERT_SID, "Mert_06"):
            return {"harita": "de_anubis", "steamid": MERT_SID, "ad": "Mert_06", "varsayilan": False, "highlights": [HL]}
        raise SystemExit(f"'{who}' bu demoda yok.")

    monkeypatch.setattr(arayuz, "analyze_player", one)
    return calls


def test_clips_default_unchanged(demo):
    a, demos, _ = demo
    res = a.clips(DID)
    assert [(h["round"], h["klip"]) for h in res["highlightlar"]] == [(3, "/klip/anubis_59cf10f2_R03_3K.mp4")]
    assert res["oyuncu"] == {"steamid": DEFAULT_SID, "ad": "DuranEnnmi", "varsayilan": True}
    assert a.clips(DID, DEFAULT_SID)["highlightlar"] == res["highlightlar"]  # kendi steamid'iyle de aynı
    assert sorted(p.name for p in demos.iterdir()) == sorted([f"{DID}.dem", f"{DID}.stats.json", f"{DID}.highlights.json"])


def test_clips_other_player_analyzed_once_and_cached(demo, monkeypatch):
    a, demos, _ = demo
    calls = fake_analyze(monkeypatch, demos)
    res = a.clips(DID, MERT_SID)
    assert [(h["round"], h["klip"]) for h in res["highlightlar"]] == [(5, "/klip/anubis_59cf10f2_R05_p-Mert06_4K_ak47.mp4")]
    assert res["oyuncu"] == {"steamid": MERT_SID, "ad": "Mert_06", "varsayilan": False, "etiket": "p-Mert06"}
    assert (demos / f"{DID}.highlights.{MERT_SID}.json").exists()
    assert a.clips(DID, MERT_SID)["highlightlar"] == res["highlightlar"] and calls == [MERT_SID]
    # varsayılan oyuncunun dosyası ve klip eşleşmesi bozulmadı
    assert json.loads((demos / f"{DID}.highlights.json").read_text(encoding="utf-8"))[0]["round"] == 3
    assert [h["round"] for h in a.clips(DID)["highlightlar"]] == [3]


def test_clips_endpoint_query_and_unknown_player(server, demo, monkeypatch):
    url, _ = server
    fake_analyze(monkeypatch, demo[1])
    with urllib.request.urlopen(f"{url}/api/demo/{DID}/klipler?oyuncu={MERT_SID}") as r:
        assert json.loads(r.read())["oyuncu"]["ad"] == "Mert_06"
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(f"{url}/api/demo/{DID}/klipler?oyuncu=kimse")
    assert e.value.code == 422 and "yok" in json.loads(e.value.read())["hata"]


def test_everyone_lists_best_moment_per_player(server, demo, monkeypatch):
    url, (a, demos, _) = server
    calls = []

    def all_(d, pre, post, default=None):
        calls.append(d)
        return {"harita": "de_anubis", "oyuncular": [
            {"steamid": DEFAULT_SID, "ad": "DuranEnnmi", "varsayilan": True,
             "highlights": [{**HL, "round": 3, "score": 6.0, "labels": ["3K"]}]},
            {"steamid": MERT_SID, "ad": "Mert_06", "varsayilan": False, "highlights": [HL, {**HL, "round": 9, "score": 3}]},
            {"steamid": "3", "ad": "zayif", "varsayilan": False, "highlights": [{**HL, "score": 1.5}]}]}

    monkeypatch.setattr(arayuz, "analyze_all", all_)
    with urllib.request.urlopen(f"{url}/api/demo/{DID}/herkes") as r:
        rows = json.loads(r.read())["oyuncular"]
    assert [(r["ad"], r["highlight_sayisi"], r["en_iyi"] and r["en_iyi"]["round"], r["en_iyi"] and r["en_iyi"]["klip"])
            for r in rows] == [("Mert_06", 2, 5, "/klip/anubis_59cf10f2_R05_p-Mert06_4K_ak47.mp4"),
                               ("DuranEnnmi", 1, 3, "/klip/anubis_59cf10f2_R03_3K.mp4"), ("zayif", 0, None, None)]
    assert len(calls) == 1 and (demos / f"{DID}.highlights.{MERT_SID}.json").exists()
    # stats'taki herkesin dosyası artık var: ikinci çağrı ayrıştırmaz
    a.everyone(DID)
    assert len(calls) == 1


def test_record_command_and_post_body(server, demo, monkeypatch):
    url, (a, _, _) = server
    started = []
    monkeypatch.setattr(arayuz, "preflight", lambda cfg, csgo: ({}, []))
    monkeypatch.setattr(arayuz, "find_csgo_dir", lambda: None)
    done = threading.Event()
    monkeypatch.setattr(a, "_record", lambda *args: (started.append(args), done.set()))  # gerçek kayıt yok
    status, data = post_json(f"{url}/api/demo/{DID}/kaydet", {"en_iyi": 3, "oyuncu": MERT_SID})
    assert status == 200 and data == {"durum": "calisiyor", "oyuncu": MERT_SID}
    assert done.wait(5)
    assert started[-1][1:] == (3, MERT_SID) and a.job["oyuncu"] == MERT_SID
    cmd = a.record_command(started[-1][0], 3, MERT_SID)
    assert cmd[-3:] == ["--en-iyi", "3", f"--oyuncu={MERT_SID}"]
    assert a.record_command(started[-1][0], 3)[-2:] == ["--en-iyi", "3"]  # varsayılan: eski komut
    assert a.clips(DID)["kayit"]["oyuncu"] == MERT_SID
    a.job["durum"] = "bitti"
    code, err = post_error(f"{url}/api/demo/{DID}/kaydet", {"en_iyi": 3, "oyuncu": 5})
    assert code == 400 and "oyuncu" in err["hata"]


def test_montage_by_player(server, demo, fake_ffmpeg):  # noqa: F811
    url, _ = server
    status, data = post_json(url + "/api/en-iyi/montaj", {"adet": 5})
    assert data["oyuncu"] is None and fake_ffmpeg[-1]["liste"] == ["anubis_59cf10f2_R03_3K.mp4"]
    status, data = post_json(url + "/api/en-iyi/montaj", {"adet": 5, "oyuncu": "Mert06"})
    assert fake_ffmpeg[-1]["liste"] == ["anubis_59cf10f2_R05_p-Mert06_4K_ak47.mp4"]
    status, data = post_json(url + "/api/en-iyi/montaj", {"adet": 5, "oyuncu": "*"})
    assert len(fake_ffmpeg[-1]["liste"]) == 2
    with urllib.request.urlopen(url + "/api/en-iyi") as r:
        assert json.loads(r.read())["montaj"]["oyuncu"] == "*"


# --- klip.py --oyuncu ---

def test_klip_prova_other_player_by_steamid(monkeypatch, tmp_path, capsys):
    demo = tmp_path / "1-59cf10f2-x-1-1.dem"
    demo.write_bytes(b"d")
    seen = []

    def one(d, who, pre, post, default=None):
        seen.append((who, default))
        return {"harita": "de_anubis", "steamid": MERT_SID, "ad": "Mert_06", "varsayilan": False, "highlights": [HL]}

    monkeypatch.setattr(klip, "analyze_player", one)
    monkeypatch.setattr(klip, "find_csgo_dir", lambda: None)
    monkeypatch.setattr(sys, "argv", ["klip.py", str(demo), "--prova", "--oyuncu", MERT_SID,
                                      "--ayarlar", str(tmp_path / "yok.json")])
    klip.main()
    out = capsys.readouterr().out
    assert seen == [(MERT_SID, "DuranEnnmi")]
    assert f"--steamids {MERT_SID}" in out and "anubis_59cf10f2_R05_p-Mert06_4K_ak47.mp4" in out
    assert (tmp_path / f"1-59cf10f2-x-1-1.highlights.{MERT_SID}.json").exists()
    assert not (tmp_path / "1-59cf10f2-x-1-1.highlights.json").exists()  # varsayılan oyuncunun dosyasına dokunmaz
