import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

import arayuz
from config import DEFAULTS


@pytest.fixture
def app(tmp_path, monkeypatch):
    demos, clips, web = tmp_path / "indirilenler", tmp_path / "klipler", tmp_path / "web"
    for d in (demos, clips, web):
        d.mkdir()
    monkeypatch.setattr(arayuz, "UPLOADS", tmp_path / "demos")
    monkeypatch.setattr(arayuz, "WEB", web)
    (web / "index.html").write_text("<h1>ok</h1>", encoding="utf-8")
    cfg = {**DEFAULTS, "demo_klasorleri": [str(demos)], "cikti_klasoru": str(clips)}
    a = arayuz.App(cfg)
    a.out_dir = clips
    return a, demos, clips


@pytest.fixture
def server(app):
    a = app[0]
    srv = ThreadingHTTPServer(("127.0.0.1", 0), arayuz.make_handler(a))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}", app
    srv.shutdown()


def test_demo_id_strips_archive_suffix():
    assert arayuz.demo_id(arayuz.Path("1-abc-1-1.dem.zst")) == "1-abc-1-1"
    assert arayuz.match_code("1-59cf10f2-9122-1-1") == "59cf10f2"


def test_list_prefers_dem_and_counts_clips(app):
    a, demos, clips = app
    (demos / "1-aaaa1111-x-1-1.dem.zst").write_bytes(b"z")
    (demos / "1-aaaa1111-x-1-1.dem").write_bytes(b"d" * 10)
    (demos / "notlar.txt").write_bytes(b"n")
    (clips / "anubis_aaaa1111_R05_2K.mp4").write_bytes(b"v")
    (clips / "cache_bbbb2222_R01_2K.mp4").write_bytes(b"v")
    rows = a.list_demos()
    assert [(r["id"], r["ad"], r["klip_sayisi"], r["analiz_edildi"]) for r in rows] == [
        ("1-aaaa1111-x-1-1", "1-aaaa1111-x-1-1.dem", 1, False)]


def test_clip_served_with_range(server):
    url, (_, _, clips) = server
    (clips / "a_R01.mp4").write_bytes(bytes(range(100)))
    req = urllib.request.Request(url + "/klip/a_R01.mp4", headers={"Range": "bytes=10-19"})
    with urllib.request.urlopen(req) as r:
        assert r.status == 206
        assert r.headers["Content-Range"] == "bytes 10-19/100"
        assert r.read() == bytes(range(10, 20))


def test_static_and_path_escape(server):
    url, _ = server
    with urllib.request.urlopen(url + "/") as r:
        assert b"ok" in r.read()
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(url + "/klip/..%2F..%2Fsecret.txt")
    assert e.value.code == 404


def test_upload_writes_file(server):
    url, (a, _, _) = server
    req = urllib.request.Request(url + "/api/yukle", data=b"x" * 3000, method="POST",
                                 headers={"X-Dosya-Adi": "mac%201.dem"})
    with urllib.request.urlopen(req) as r:
        assert json.loads(r.read()) == {"id": "mac 1"}
    assert (arayuz.UPLOADS / "mac 1.dem").read_bytes() == b"x" * 3000


def test_upload_rejects_other_files(server):
    url, _ = server
    req = urllib.request.Request(url + "/api/yukle", data=b"x", method="POST", headers={"X-Dosya-Adi": "virus.exe"})
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(req)
    assert e.value.code == 400 and "yüklenebilir" in json.loads(e.value.read())["hata"]


def test_unknown_demo_is_404_json(server):
    url, _ = server
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(url + "/api/demo/yok/klipler")
    assert e.value.code == 404 and "hata" in json.loads(e.value.read())


def post_json(url, obj):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return r.status, json.loads(r.read())


def post_error(url, obj):
    with pytest.raises(urllib.error.HTTPError) as e:
        post_json(url, obj)
    return e.value.code, json.loads(e.value.read())


@pytest.fixture
def fake_ffmpeg(monkeypatch, tmp_path):
    """ffmpeg yerine: concat listesindeki dosyaları bayt bayt birleştirir."""
    calls = []

    def run(cmd, check=False, **kw):
        lst = arayuz.Path(cmd[cmd.index("-i") + 1])
        files = [ln[len("file '"):-1] for ln in lst.read_text(encoding="utf-8").splitlines()]
        out = arayuz.Path(cmd[-1])
        out.write_bytes(b"".join(arayuz.Path(f).read_bytes() for f in files))
        calls.append({"liste": [arayuz.Path(f).name for f in files], "cikti": out.name})

    exe = tmp_path / "ffmpeg.exe"
    exe.write_bytes(b"")
    monkeypatch.setattr(arayuz, "find_ffmpeg", lambda override="": exe)
    monkeypatch.setattr(arayuz.render.subprocess, "run", run)
    return calls


def test_best_clips_endpoint(server):
    url, (a, demos, clips) = server
    (demos / "1-a95f6ac2-x-1-1.dem").write_bytes(b"d")
    (demos / "1-a95f6ac2-x-1-1.highlights.json").write_text(json.dumps(
        [{"round": 9, "score": 21.0, "labels": ["3K", "3 HS"], "weapons": ["m4a1"]}]), encoding="utf-8")
    (clips / "dust2_a95f6ac2_R09_3K_3-HS_m4a1.mp4").write_bytes(b"a")
    (clips / "anubis_e3c103b2_R11_1v3clutch_4K_hegrenade_m4a1_silencer.mp4").write_bytes(b"b")
    (clips / "montaj.mp4").write_bytes(b"m")
    with urllib.request.urlopen(url + "/api/en-iyi") as r:
        data = json.loads(r.read())
    assert data["montaj"] is None
    assert [(c["ad"], c["skor"], c["tahmini"], c["demo"]) for c in data["klipler"]] == [
        ("dust2_a95f6ac2_R09_3K_3-HS_m4a1.mp4", 21.0, False, "1-a95f6ac2-x-1-1"),
        ("anubis_e3c103b2_R11_1v3clutch_4K_hegrenade_m4a1_silencer.mp4", 17.0, True, None)]
    assert set(data["klipler"][1]) == {"ad", "klip", "harita", "kod", "round", "etiketler", "silahlar", "skor",
                                       "tahmini", "demo", "tarih", "boyut_mb"}


def test_best_montage_builds_in_score_order(server, fake_ffmpeg):
    url, (a, _, clips) = server
    (clips / "dust2_a95f6ac2_R05_2K_m4a1.mp4").write_bytes(b"2K|")
    (clips / "dust2_a95f6ac2_R09_3K_3-HS_m4a1.mp4").write_bytes(b"3K|")
    (clips / "anubis_e3c103b2_R11_1v3clutch_4K_hegrenade_m4a1_silencer.mp4").write_bytes(b"clutch|")
    (clips / "en_iyi_montaj.mp4").write_bytes(b"eski")
    status, data = post_json(url + "/api/en-iyi/montaj", {"adet": 2})
    assert status == 200
    assert (data["klip"], data["adet"]) == ("/klip/en_iyi_montaj.mp4", 2)
    assert set(data) == {"klip", "adet", "boyut_mb", "tarih"}
    assert fake_ffmpeg == [{"liste": ["anubis_e3c103b2_R11_1v3clutch_4K_hegrenade_m4a1_silencer.mp4",
                                      "dust2_a95f6ac2_R09_3K_3-HS_m4a1.mp4"], "cikti": "en_iyi_montaj.part.mp4"}]
    assert (clips / "en_iyi_montaj.mp4").read_bytes() == b"clutch|3K|"
    assert sorted(p.name for p in clips.iterdir() if not p.name.startswith(("dust2", "anubis"))) == [
        "en_iyi_montaj.json", "en_iyi_montaj.mp4"]  # geçici liste ve .part kalmadı
    with urllib.request.urlopen(url + "/api/en-iyi") as r:
        listed = json.loads(r.read())
    assert listed["montaj"]["adet"] == 2 and len(listed["klipler"]) == 3  # montaj listeye girmez
    status, data = post_json(url + "/api/en-iyi/montaj", {})  # varsayılan 10, olan kadar
    assert data["adet"] == 3


@pytest.mark.parametrize("body", [{"adet": 0}, {"adet": 51}, {"adet": "x"}])
def test_best_montage_bad_count(server, fake_ffmpeg, body):
    url, _ = server
    code, data = post_error(url + "/api/en-iyi/montaj", body)
    assert code == 400 and "adet" in data["hata"]


def test_best_montage_without_clips_or_ffmpeg(server, fake_ffmpeg, monkeypatch):
    url, (_, _, clips) = server
    code, data = post_error(url + "/api/en-iyi/montaj", {"adet": 3})
    assert code == 409 and "klip yok" in data["hata"]
    (clips / "dust2_a95f6ac2_R05_2K_m4a1.mp4").write_bytes(b"v")
    monkeypatch.setattr(arayuz, "find_ffmpeg", lambda override="": None)
    code, data = post_error(url + "/api/en-iyi/montaj", {"adet": 3})
    assert code == 409 and "ffmpeg" in data["hata"]
    assert not fake_ffmpeg


def test_best_montage_busy(server, fake_ffmpeg):
    url, (a, _, clips) = server
    (clips / "dust2_a95f6ac2_R05_2K_m4a1.mp4").write_bytes(b"v")
    a.montage_lock.acquire()
    try:
        code, data = post_error(url + "/api/en-iyi/montaj", {"adet": 3})
    finally:
        a.montage_lock.release()
    assert code == 409 and data["hata"] == "Montaj sürüyor."
