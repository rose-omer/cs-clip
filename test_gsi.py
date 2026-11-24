import json
import threading
import urllib.error
import urllib.request

import pytest

import gsi


def durum(faz="live", rnd="live", no=0, harita="de_dust2", token="t"):
    return {"provider": {"steamid": "765"}, "map": {"name": harita, "phase": faz, "round": no},
            "round": {"phase": rnd}, "auth": {"token": token}}


def test_cfg_metni_adres_ve_token():
    metin = gsi.cfg_metni(8770, "abc")
    assert '"uri" "http://127.0.0.1:8770/gsi"' in metin
    assert '"token" "abc"' in metin


def test_cfg_yaz_token_korunur_port_guncellenir(tmp_path):
    (tmp_path / "cfg").mkdir()
    gsi.cfg_yaz(tmp_path, 8770)
    token = gsi.cfg_token(tmp_path)
    assert token and len(token) == 32
    f = gsi.cfg_yaz(tmp_path, 8771)
    assert gsi.cfg_token(tmp_path) == token
    assert "8771" in f.read_text(encoding="utf-8")


def test_cfg_yaz_cfg_klasoru_yoksa_hata(tmp_path):
    with pytest.raises(FileNotFoundError):
        gsi.cfg_yaz(tmp_path, 8770)


def turler(izleyici, *durumlar):
    out = []
    for i, d in enumerate(durumlar):
        out += [(o.tur, o.round) for o in izleyici.besle(d, simdi=float(i))]
    return out


def test_mac_akisi():
    iz = gsi.Izleyici()
    assert turler(
        iz,
        durum("warmup", "live"),
        durum("live", "freezetime", 0),
        durum("live", "live", 0),
        durum("live", "over", 0),
        durum("live", "freezetime", 1),
        durum("live", "live", 1),
        durum("gameover", "over", 2),
    ) == [("mac_basladi", 0), ("round_basladi", 1), ("round_basladi", 2), ("mac_bitti", 0)]


def test_ayni_durum_tekrar_olay_uretmez():
    iz = gsi.Izleyici()
    turler(iz, durum("live", "live", 0))
    assert turler(iz, durum("live", "live", 0), durum("live", "live", 0)) == []


def test_menuye_donus_ve_harita_degisimi_maci_bitirir():
    iz = gsi.Izleyici()
    turler(iz, durum("live", "live", 3))
    assert turler(iz, {"provider": {}}) == [("mac_bitti", 0)]
    turler(iz, durum("live", "live", 0))
    assert turler(iz, durum("live", "live", 0, harita="de_mirage")) == [
        ("mac_bitti", 0), ("mac_basladi", 0), ("round_basladi", 1)]


def test_isinmada_round_olayi_yok():
    assert turler(gsi.Izleyici(), durum("warmup", "live", 0)) == []


def gonder(port, veri):
    req = urllib.request.Request(f"http://127.0.0.1:{port}/gsi", data=json.dumps(veri).encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def test_sunucu_token_denetler_ve_olay_iletir():
    gelen = []
    srv = gsi.sunucu(0, "dogru", gsi.Izleyici(), gelen.append)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        assert gonder(port, durum(token="yanlis")) == 403
        assert gelen == []
        assert gonder(port, durum(token="dogru")) == 200
        assert [o.tur for o in gelen] == ["mac_basladi", "round_basladi"]
        assert gelen[1].steamid == "765" and gelen[1].harita == "de_dust2"
    finally:
        srv.shutdown()
        srv.server_close()
