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
