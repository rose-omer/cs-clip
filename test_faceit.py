import io
import json
import urllib.error

import pytest

import faceit
from config import DEFAULTS


class Yanit(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


class SahteAg:
    """URL -> (kod, gövde). Gerçek ağa hiç çıkmaz; istekleri kaydeder."""

    def __init__(self, yollar):
        self.yollar = yollar
        self.istekler = []

    def __call__(self, req, timeout=None):
        url = req.full_url
        self.istekler.append((req.get_method(), url, dict(req.header_items()), req.data))
        for onek, (kod, govde) in self.yollar.items():
            if url.startswith(onek):
                if kod != 200:
                    raise urllib.error.HTTPError(url, kod, "x", {}, io.BytesIO(b""))
                return Yanit(govde if isinstance(govde, bytes) else json.dumps(govde).encode())
        raise urllib.error.URLError("bilinmeyen adres " + url)


DEMO = "https://demos-europe.faceit-cdn.net/cs2/1-abcd1234-aaaa-1-1.dem.zst"


def ag(download_api=(200, {"payload": {"download_url": "https://imzali.example/d?sig=1"}}), dosya=(200, b"DEMO")):
    return SahteAg({
        f"{faceit.API}/players?nickname=": (200, {"player_id": "pid1"}),
        f"{faceit.API}/players/pid1/history": (200, {"items": [
            {"match_id": "1-abcd1234-aaaa", "status": "finished"},
            {"match_id": "1-iptal", "status": "cancelled"},
            {"match_id": "1-eski", "status": "finished"}]}),
        f"{faceit.API}/matches/1-abcd1234-aaaa": (200, {"demo_url": [DEMO]}),
        f"{faceit.API}/matches/1-eski": (200, {"demo_url": []}),
        faceit.DOWNLOAD_API: download_api,
        "https://imzali.example/": dosya,
        DEMO: dosya,
    })


def test_anahtar_yoksa_acik_hata():
    with pytest.raises(faceit.FaceitHatasi, match="faceit_api_anahtari"):
        faceit.Faceit("")
    with pytest.raises(faceit.FaceitHatasi, match="API anahtarı yok"):
        faceit.son_demolari_indir(dict(DEFAULTS), faceit.Path("."))


def test_son_demolari_indirir(tmp_path):
    a = ag()
    api = faceit.Faceit("gizli", ac=a)
    cfg = {**DEFAULTS, "faceit_kullanici": "Duran Ennmi"}
    got = faceit.son_demolari_indir(cfg, tmp_path, 3, set(), api, yaz=lambda *_: None)
    assert got == [("1-abcd1234-aaaa", tmp_path / "1-abcd1234-aaaa-1-1.dem.zst")]
    assert (tmp_path / "1-abcd1234-aaaa-1-1.dem.zst").read_bytes() == b"DEMO"
    assert not list(tmp_path.glob("*.part"))
    yontem, url, basliklar, govde = a.istekler[0]
    assert url.endswith("nickname=Duran%20Ennmi")
    assert basliklar["Authorization"] == "Bearer gizli"
    post = next(i for i in a.istekler if i[1] == faceit.DOWNLOAD_API)
    assert post[0] == "POST" and json.loads(post[3]) == {"resource_url": DEMO}
    indirme = next(i for i in a.istekler if i[1].startswith("https://imzali.example/"))
    assert "Authorization" not in indirme[2]  # anahtar CDN'e gitmez
    # ikinci kez: dosya zaten var, indirilmez
    again = faceit.son_demolari_indir(cfg, tmp_path, 3, set(), api, yaz=lambda *_: None)
    assert again == [("1-abcd1234-aaaa", None)]
    assert faceit.son_demolari_indir(cfg, tmp_path, 3, {"1-abcd1234-aaaa"}, api, yaz=lambda *_: None) == []


def test_kullanici_bos_ise_oyuncu_adi(tmp_path):
    a = ag()
    faceit.son_demolari_indir(dict(DEFAULTS), tmp_path, 1, {"1-abcd1234-aaaa"}, faceit.Faceit("k", ac=a),
                              yaz=lambda *_: None)
    assert a.istekler[0][1].endswith("nickname=DuranEnnmi")


def test_downloads_api_izni_yoksa_dogrudan_link(tmp_path):
    a = ag(download_api=(403, b""))
    got = faceit.son_demolari_indir(dict(DEFAULTS), tmp_path, 1, set(), faceit.Faceit("k", ac=a),
                                    yaz=lambda *_: None)
    assert got[0][1].read_bytes() == b"DEMO"
    assert any(i[1] == DEMO for i in a.istekler)


def test_dosya_indirilemezse_anlasilir_hata_ve_yarim_dosya_kalmaz(tmp_path):
    a = ag(download_api=(403, b""), dosya=(403, b""))
    with pytest.raises(faceit.FaceitHatasi, match="Downloads API"):
        faceit.son_demolari_indir(dict(DEFAULTS), tmp_path, 1, set(), faceit.Faceit("k", ac=a), yaz=lambda *_: None)
    assert list(tmp_path.iterdir()) == []


def test_gecersiz_anahtar(tmp_path):
    a = SahteAg({f"{faceit.API}/players": (401, b"")})
    with pytest.raises(faceit.FaceitHatasi, match="geçersiz"):
        faceit.son_demolari_indir(dict(DEFAULTS), tmp_path, 1, set(), faceit.Faceit("k", ac=a), yaz=lambda *_: None)


def test_dosya_adi_guvenli():
    assert faceit.dosya_adi(DEMO, "m") == "1-abcd1234-aaaa-1-1.dem.zst"
    assert faceit.dosya_adi("https://x/indir?id=5", "1-m") == "1-m.dem.zst"
    assert faceit.dosya_adi("https://x/..%2F..%2Fa.dem", "1-m") == "1-m.dem.zst"
