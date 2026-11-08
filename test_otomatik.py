import json
import os
import time

import pytest

import otomatik
from config import DEFAULTS


class Saat:
    def __init__(self, t=1_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


def demo(folder, name, yas=100, now=None):
    p = folder / name
    p.write_bytes(b"d")
    t = (now or time.time()) - yas
    os.utime(p, (t, t))
    return p


@pytest.fixture
def ortam(tmp_path):
    klasor = tmp_path / "Downloads"
    klasor.mkdir()
    kuyruk = otomatik.Kuyruk(tmp_path / "otomatik.json")
    return klasor, kuyruk, tmp_path / "kayit.kilit"


def test_ilk_tarama_mevcutlari_siraya_almaz_sonra_yenileri_alir(ortam):
    klasor, kuyruk, _ = ortam
    demo(klasor, "1-eski0000-a-1-1.dem.zst")
    iz = otomatik.Izleyici(kuyruk, [klasor])
    assert iz.tara() == []
    assert kuyruk.oku()["gorulen"] == ["1-eski0000-a-1-1"]
    demo(klasor, "1-yeni1111-a-1-1.dem.zst")
    assert iz.tara() == ["1-yeni1111-a-1-1"]
    assert iz.tara() == []  # ikinci kez eklenmez
    (klasor / "1-yeni1111-a-1-1.dem").write_bytes(b"x")  # açılmış hâli ayrı maç sayılmaz
    assert iz.tara() == []
    q = kuyruk.oku()["kuyruk"]
    assert [(i["id"], i["durum"]) for i in q] == [("1-yeni1111-a-1-1", "bekliyor")]


def test_mevcutlari_da_ve_yarim_indirmeler(ortam):
    klasor, kuyruk, _ = ortam
    demo(klasor, "1-aaaa0000-a-1-1.dem")
    demo(klasor, "1-bbbb0000-a-1-1.dem.zst.crdownload")
    demo(klasor, "1-cccc0000-a-1-1.dem.part")
    demo(klasor, "1-aaaa0000-a-1-1.onarilmis.dem")
    demo(klasor, "1-dddd0000-a-1-1.dem", yas=1)  # hâlâ yazılıyor
    iz = otomatik.Izleyici(kuyruk, [klasor], mevcutlari_da=True)
    assert iz.tara() == ["1-aaaa0000-a-1-1"]
    os.utime(klasor / "1-dddd0000-a-1-1.dem", (time.time() - 100,) * 2)
    assert iz.tara() == ["1-dddd0000-a-1-1"]


def test_kilit_ozel(tmp_path):
    k = tmp_path / "kayit.kilit"
    assert not otomatik.kilit_dolu(k)
    with otomatik.kayit_kilidi(k):
        assert otomatik.kilit_dolu(k)
        with pytest.raises(otomatik.Mesgul):
            with otomatik.kayit_kilidi(k):
                pass
    assert not otomatik.kilit_dolu(k)


def isci(kuyruk, kilit, saat, procs, problems=(), sonuc=(0, ["2 yeni klip"]), cfg=None):
    calls = []

    def kaydet(yol, satir):
        calls.append(yol)
        assert otomatik.kilit_dolu(kilit)  # kayıt kilit altında
        for line in sonuc[1]:
            satir(line)
        return sonuc[0]

    w = otomatik.Isci(kuyruk, cfg or {**DEFAULTS, "otomatik_bekle_sn": 60}, kaydet=kaydet,
                      surecler=lambda: set(procs), on_kontrol=lambda: list(problems), kilit=kilit,
                      saat=saat, yaz=lambda *_: None)
    return w, calls


def test_cs2_ya_da_faceit_aciksa_bekler_kapaninca_sure_dolunca_kaydeder(ortam):
    klasor, kuyruk, kilit = ortam
    p = demo(klasor, "1-aaaa0000-a-1-1.dem")
    kuyruk.ekle(p)
    saat, procs = Saat(), {"cs2.exe", "explorer.exe"}
    w, calls = isci(kuyruk, kilit, saat, procs)
    assert w.adim() == "Bekliyor: CS2 açık"
    procs.clear()
    procs.add("faceitclient.exe")
    assert w.adim() == "Bekliyor: FACEIT açık"
    procs.clear()
    saat.t += 10
    assert "sn sonra kayıt başlayacak" in w.adim()
    assert calls == []
    saat.t += 60
    assert w.adim() == "Bitti: 1-aaaa0000-a-1-1"
    assert calls == [p]
    item = kuyruk.oku()["kuyruk"][0]
    assert item["durum"] == "bitti" and item["mesaj"] == "2 yeni klip"
    assert w.adim().startswith("Sıra boş")
    assert not otomatik.kilit_dolu(kilit)


def test_on_kontrol_gecmezse_bekler(ortam):
    klasor, kuyruk, kilit = ortam
    kuyruk.ekle(demo(klasor, "1-aaaa0000-a-1-1.dem"))
    w, calls = isci(kuyruk, kilit, Saat(), set(), problems=["ffmpeg bulunamadı"])
    assert w.adim() == "Bekliyor: ffmpeg bulunamadı"
    assert calls == [] and kuyruk.oku()["kuyruk"][0]["durum"] == "bekliyor"


def test_baska_kayit_surerken_dokunmaz(ortam):
    klasor, kuyruk, kilit = ortam
    kuyruk.ekle(demo(klasor, "1-aaaa0000-a-1-1.dem"))
    w, calls = isci(kuyruk, kilit, Saat(), set())
    with otomatik.kayit_kilidi(kilit):
        assert "başka bir kayıt" in w.adim()
    assert calls == []


def test_kayit_hatasi_ve_ortam_hatasi(ortam):
    klasor, kuyruk, kilit = ortam
    kuyruk.ekle(demo(klasor, "1-aaaa0000-a-1-1.dem"))
    kuyruk.ekle(demo(klasor, "1-bbbb0000-a-1-1.dem"))
    w, _ = isci(kuyruk, kilit, Saat(), set(), sonuc=(1, ["  ! 1-aaaa: Game error"]))
    assert w.adim().startswith("Kaydedilemedi")
    w, _ = isci(kuyruk, kilit, Saat(), set(), sonuc=(1, ["", "Kayıt başlayamaz:", "  - CS2 açık. Oyunu kapat."]))
    assert w.adim() == "Bekliyor: CS2 açık. Oyunu kapat."
    q = {i["id"]: i for i in kuyruk.oku()["kuyruk"]}
    assert q["1-aaaa0000-a-1-1"]["durum"] == "hata"
    assert q["1-bbbb0000-a-1-1"]["durum"] == "bekliyor"  # demo değil ortam sorunu: sonra yeniden


def test_yarida_kalan_ve_silinen_dosya(ortam):
    klasor, kuyruk, kilit = ortam
    p = demo(klasor, "1-aaaa0000-a-1-1.dem")
    kuyruk.ekle(p)
    kuyruk.oge_guncelle("1-aaaa0000-a-1-1", durum="kaydediliyor")
    p.unlink()
    w, calls = isci(kuyruk, kilit, Saat(), set())
    assert "dosya artık yok" in w.adim()
    assert kuyruk.oku()["kuyruk"][0]["durum"] == "hata" and calls == []


def test_ekle_tekrar_eklemez(ortam):
    klasor, kuyruk, _ = ortam
    p = demo(klasor, "1-aaaa0000-a-1-1.dem.zst")
    assert kuyruk.ekle(p, "elle") is True
    assert kuyruk.ekle(p, "elle") is False
    kuyruk.oge_guncelle("1-aaaa0000-a-1-1", durum="hata")
    assert kuyruk.ekle(p, "elle") is True  # hatalı iş elle yeniden sıraya alınabilir
    assert len(kuyruk.oku()["kuyruk"]) == 1


def test_ozet(ortam):
    klasor, kuyruk, kilit = ortam
    kuyruk.ekle(demo(klasor, "1-aaaa0000-a-1-1.dem"))
    saat = Saat(time.time())
    o = otomatik.ozet(kuyruk.dosya, kilit, saat)
    assert o["calisiyor"] is False and o["bekleyen"] == 1 and o["kuyruk"][0]["id"] == "1-aaaa0000-a-1-1"
    w, _ = isci(kuyruk, kilit, saat, {"cs2.exe"})
    w.adim()
    o = otomatik.ozet(kuyruk.dosya, kilit, saat)
    assert o["calisiyor"] is True and o["durum"] == "Bekliyor: CS2 açık"
    saat.t += 1000
    assert otomatik.ozet(kuyruk.dosya, kilit, saat)["calisiyor"] is False


class SahteFaceit:
    def __init__(self, maclar):
        self.maclar = maclar
        self.indirilen = []

    def oyuncu_id(self, kullanici):
        return "pid-" + kullanici

    def son_maclar(self, pid, adet):
        return [{"match_id": m, "status": "finished"} for m in self.maclar[:adet]]

    def demo_url(self, mid):
        return f"https://cdn.example/cs2/{mid}-1-1.dem.zst"

    def imzali_link(self, url):
        return url + "?imza=1"

    def indir(self, url, hedef):
        self.indirilen.append(url)
        hedef.write_bytes(b"demo")
        return hedef


def test_faceit_yokla_izleme_modunda_eskileri_indirmez(ortam):
    klasor, kuyruk, _ = ortam
    api = SahteFaceit(["1-eski"])
    cfg = {**DEFAULTS, "faceit_api_anahtari": "x"}
    assert otomatik.faceit_yokla(kuyruk, cfg, klasor, istemci=api, yaz=lambda *_: None, ilk_kez_indirme=False) == []
    assert api.indirilen == []
    api.maclar = ["1-yeni", "1-eski"]
    got = otomatik.faceit_yokla(kuyruk, cfg, klasor, istemci=api, yaz=lambda *_: None, ilk_kez_indirme=False)
    assert [p.name for p in got] == ["1-yeni-1-1.dem.zst"]
    s = kuyruk.oku()
    assert s["faceit_indirilen"] == ["1-eski", "1-yeni"]
    assert [(i["id"], i["kaynak"]) for i in s["kuyruk"]] == [("1-yeni-1-1", "faceit")]
    assert otomatik.faceit_yokla(kuyruk, cfg, klasor, istemci=api, yaz=lambda *_: None) == []  # tekrar inmez


def test_durum_dosyasi_bozuksa_sifirdan_baslar(ortam):
    _, kuyruk, _ = ortam
    kuyruk.dosya.write_text("{bozuk", encoding="utf-8")
    assert kuyruk.oku() == {"gorulen": [], "kuyruk": [], "isci": {}}
    kuyruk.isci_guncelle(durum="x")
    assert json.loads(kuyruk.dosya.read_text(encoding="utf-8"))["isci"] == {"durum": "x"}
