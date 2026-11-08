import json
import os
import urllib.request

import arayuz
import kariyer


def stats(harita="de_anubis", biz=13, onlar=9, rating=1.05, ben_takim=0, ben=True):
    return {
        "harita": harita, "round_sayisi": biz + onlar, "benim_takim": ben_takim,
        "oyuncu_steamid": "7656",
        "takimlar": [{"ad": "A", "skor": biz if ben_takim == 0 else onlar}, {"ad": "B", "skor": onlar if ben_takim == 0 else biz}],
        "oyuncular": [
            {"steamid": "7656", "ad": "DuranEnnmi", "takim": ben_takim, "kill": 14, "death": 12, "assist": 5, "adr": 66.3,
             "hs_yuzde": 42.9, "kd": 1.17, "kast": 67.8, "rating": rating, "acilis_kill": 3, "acilis_death": 3,
             "cok_kill": {"2": 2, "3": 1, "4": 0, "5": 0}, "ben": ben},
            {"steamid": "1", "ad": "rakip", "takim": 1 - ben_takim, "kill": 20, "death": 10, "rating": 1.4, "ben": False},
        ],
        "roundlar": [], "silahlar": [],
    }


def write(folder, did, data, mtime=None, demo=True):
    f = folder / f"{did}.stats.json"
    f.write_text(json.dumps(data) if not isinstance(data, str) else data, encoding="utf-8")
    if demo:
        d = folder / f"{did}.dem"
        d.write_bytes(b"d")
        if mtime:
            os.utime(d, (mtime, mtime))
    elif mtime:
        os.utime(f, (mtime, mtime))
    return f


def test_match_row_uses_my_team_and_result():
    row = kariyer.match_row(stats(biz=10, onlar=13, ben_takim=1), "x", "2026-11-01T10:00:00", True)
    assert row["skor"] == [10, 13] and row["sonuc"] == "M"
    assert row["rating"] == 1.05 and row["adr"] == 66.3 and row["cok_kill"] == {"2": 2, "3": 1, "4": 0, "5": 0}
    assert kariyer.match_row(stats(biz=12, onlar=12), "x", "t", True)["sonuc"] == "B"


def test_match_row_falls_back_to_steamid_and_skips_unknown_player():
    assert kariyer.match_row(stats(ben=False), "x", "t", True)["ad"] == "DuranEnnmi"
    s = stats(ben=False)
    s["oyuncu_steamid"] = "999"
    assert kariyer.match_row(s, "x", "t", True) is None
    assert kariyer.match_row({"takimlar": []}, "x", "t", True) is None
    assert kariyer.match_row([], "x", "t", True) is None


def test_career_reads_only_existing_stats(app):
    a, demos, _ = app
    write(demos, "1-bbbb-1-1", stats("de_mirage", 13, 5, 1.4), mtime=1_800_000_000)
    write(demos, "1-aaaa-1-1", stats("de_anubis", 9, 13, 0.8), mtime=1_700_000_000)
    write(demos, "1-eski-1-1", stats("de_nuke", 13, 11, 1.1), mtime=1_600_000_000, demo=False)  # demo silinmiş
    write(demos, "1-bozuk-1-1", "{bozuk")
    (demos / "1-yeni-1-1.dem").write_bytes(b"d")  # analiz edilmemiş: dokunulmaz
    before = sorted(p.name for p in demos.iterdir())
    out = a.career()
    assert [r["id"] for r in out["maclar"]] == ["1-eski-1-1", "1-aaaa-1-1", "1-bbbb-1-1"]  # eskiden yeniye
    assert [r["sonuc"] for r in out["maclar"]] == ["G", "M", "G"]
    assert [r["demo_var"] for r in out["maclar"]] == [False, True, True]
    assert out["analiz_bekleyen"] == 1 and out["okunamayan"] == 1
    assert sorted(p.name for p in demos.iterdir()) == before  # hiçbir dosya yazılmadı


def test_career_endpoint(server):
    url, (_, demos, _) = server
    with urllib.request.urlopen(url + "/api/kariyer") as r:
        assert json.loads(r.read()) == {"maclar": [], "analiz_bekleyen": 0, "okunamayan": 0}
    write(demos, "1-cccc-1-1", stats())
    with urllib.request.urlopen(url + "/api/kariyer") as r:
        assert r.headers["Content-Type"].startswith("application/json")
        body = json.loads(r.read())
    assert len(body["maclar"]) == 1
    m = body["maclar"][0]
    assert m["harita"] == "de_anubis" and m["skor"] == [13, 9] and m["kast"] == 67.8 and m["hs_yuzde"] == 42.9


def test_career_does_not_start_analysis(app, monkeypatch):
    a, demos, _ = app
    (demos / "1-dddd-1-1.dem").write_bytes(b"d")
    monkeypatch.setattr(arayuz.App, "stats", lambda *_: (_ for _ in ()).throw(AssertionError("analiz başladı")))
    assert a.career()["maclar"] == []
