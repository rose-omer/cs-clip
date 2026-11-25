import io
import time
from pathlib import Path

import pytest

import canli
from config import DEFAULTS
from highlights import TICKRATE


def test_kayit_komutu_ekran_ve_nvenc():
    cmd = canli.kayit_komutu(Path("ffmpeg"), Path("a.mkv"), 60)
    assert "ddagrab=output_idx=0:framerate=60:draw_mouse=0" in cmd
    # kareler duvar saatini taşır: başlangıç saati dosyadan okunur
    assert cmd.index("-use_wallclock_as_timestamps") < cmd.index("lavfi") and "-copyts" in cmd
    assert cmd[cmd.index("-c:v") + 1] == "h264_nvenc"
    assert cmd[cmd.index("-g") + 1] == "60"
    assert cmd[-3:] == ["-f", "matroska", "a.mkv"]
    assert "dshow" not in cmd


def test_kayit_komutu_ses_cihazi():
    cmd = canli.kayit_komutu(Path("ffmpeg"), Path("a.mkv"), ses="Stereo Mix")
    assert "audio=Stereo Mix" in cmd and "aac" in cmd


def test_kayit_komutu_bilinmeyen_kodlayici():
    with pytest.raises(ValueError):
        canli.kayit_komutu(Path("ffmpeg"), Path("a.mkv"), kodlayici="libx264")


class Sonuc:
    def __init__(self, stderr):
        self.stderr = stderr


@pytest.mark.parametrize("cikti,beklenen", [
    ("  Duration: 498756:04:27.40, start: 1795521864.250000, bitrate: N/A", 1795521864.25),
    ("  Duration: 00:00:22.20, start: 0.000000, bitrate: 2717 kb/s", None),  # duvar saati değil
    ("Error opening input file", None)])
def test_video_baslangici(cikti, beklenen):
    assert canli.video_baslangici(Path("ffmpeg"), Path("a.mkv"), calistir=lambda *a, **k: Sonuc(cikti)) == beklenen


DEMO = {1: 1000, 2: 1000 + 90 * TICKRATE, 3: 1000 + 200 * TICKRATE, 4: 1000 + 290 * TICKRATE}


def kayit_roundlari(kayma=500.0, bozuk=0.0):
    """DEMO ile aynı round süreleri; duvar saati `kayma` kadar ileride."""
    return {no: kayma + (t - 1000) / TICKRATE + (bozuk if no == 3 else 0) for no, t in DEMO.items()}


def test_uyum_ayni_mac():
    fark, n = canli.uyum(kayit_roundlari(), DEMO)
    assert n == 3 and fark == pytest.approx(0)


def test_uyum_baska_mac():
    baska = {1: 0.0, 2: 70.0, 3: 140.0, 4: 260.0}
    assert canli.uyum(baska, DEMO)[0] > canli.UYUM_ESIGI


def test_uyum_ortak_round_yok():
    assert canli.uyum({9: 1.0}, DEMO) == (float("inf"), 0)


def oturum(**k):
    o = {"surum": canli.SURUM, "video": "a.mkv", "harita": "de_dust2", "steamid": "765", "baslangic": 400.0,
         "video_baslangic": 490.0, "bitis": 900.0, "roundlar": kayit_roundlari()}
    o.update(k)
    return o


def test_video_araliklari():
    # R2 videoda 500 + 90 - 490 = 100. saniyede başlar; kill round başlangıcından 20 sn sonra.
    t0 = DEMO[2]
    h = {"round": 2, "segments": [[t0 + 17 * TICKRATE, t0 + 22 * TICKRATE]]}
    assert canli.video_araliklari(h, oturum(), DEMO) == [(pytest.approx(117), pytest.approx(122))]


def test_video_araliklari_kayitta_olmayan():
    h = {"round": 2, "segments": [[DEMO[2], DEMO[2] + 64]]}
    assert canli.video_araliklari(h, oturum(roundlar={1: 500.0}), DEMO) is None
    assert canli.video_araliklari(h, oturum(video_baslangic=700.0), DEMO) is None  # kayıt sonra başlamış
    assert canli.video_araliklari(h, oturum(bitis=550.0), DEMO) is None  # kayıt önce bitmiş


def test_oturum_bul_uyan_kaydi_secer(tmp_path):
    canli.oturum_yaz(tmp_path / "a.json", oturum(video="a.mkv", roundlar={1: 0.0, 2: 70.0, 3: 140.0}))
    canli.oturum_yaz(tmp_path / "b.json", oturum(video="b.mkv"))
    canli.oturum_yaz(tmp_path / "c.json", oturum(video="c.mkv", harita="de_mirage"))
    (tmp_path / "bozuk.json").write_text("{", encoding="utf-8")
    f, o = canli.oturum_bul(tmp_path, "de_dust2", DEMO)
    assert f.name == "b.json" and o["roundlar"][2] == pytest.approx(590.0)
    assert canli.oturum_bul(tmp_path, "de_nuke", DEMO) is None


class SahteSurec:
    def __init__(self, returncode=None):
        self.stdin = io.StringIO()
        self.komut = None
        self.returncode = returncode  # None: çalışıyor

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        return 0

    def kill(self):
        pass


def test_kaydedici_round_ve_durdurma(tmp_path):
    surec = SahteSurec()
    saatler = iter([100.0, 200.0])  # baslat, durdur

    def popen(cmd, **_):
        surec.komut = cmd
        return surec

    okunan = []

    def baslangic_oku(ffmpeg, video):
        okunan.append(video)
        return 100.25

    k = canli.Kaydedici(Path("ffmpeg"), tmp_path, popen=popen, saat=lambda: next(saatler),
                        baslangic_oku=baslangic_oku)
    f = k.baslat("de_dust2", "765")
    k.round_basladi(1, 150.0)
    k.durdur(dosya=tmp_path / "baska.json")  # başka oturum: dokunmaz
    assert k.aktif
    k.durdur()
    assert not k.aktif and surec.stdin.getvalue() == "q"
    o = canli.oturum_oku(f)
    assert o["video_baslangic"] == 100.25 and okunan == [f.with_suffix(".mkv")]
    assert o["roundlar"] == {1: pytest.approx(150.0 - canli.GSI_GECIKME)}
    assert o["bitis"] == 200.0 and o["video"] == f.with_suffix(".mkv").name
    assert str(f.with_suffix(".mkv")) == surec.komut[-1]
    k.round_basladi(2, 300.0)  # kayıt yokken yok sayılır
    assert canli.oturum_oku(f)["roundlar"].keys() == {1}


def test_kes_eslesen_kayittan_keser(tmp_path, monkeypatch):
    kayitlar, klipler = tmp_path / "kayitlar", tmp_path / "klipler"
    kayitlar.mkdir()
    canli.oturum_yaz(kayitlar / "m.json", oturum(video="m.mkv"))
    t0 = DEMO[2]
    hl = [{"round": 2, "kills": 3, "score": 7.0, "labels": ["3K"], "weapons": ["ak47"],
           "start_tick": t0 + 17 * TICKRATE, "end_tick": t0 + 22 * TICKRATE,
           "segments": [[t0 + 17 * TICKRATE, t0 + 22 * TICKRATE]]},
          {"round": 9, "kills": 2, "score": 5.0, "labels": ["2K"], "weapons": ["awp"],
           "start_tick": 1, "end_tick": 2, "segments": [[1, 2]]}]
    monkeypatch.setattr(canli, "open_demo", lambda p: p)
    monkeypatch.setattr(canli, "round_baslangiclari", lambda d: ("de_dust2", DEMO))
    monkeypatch.setattr(canli, "analyze_player", lambda *a, **k: {
        "harita": "de_dust2", "steamid": "765", "ad": "ben", "varsayilan": True, "highlights": hl})
    komutlar = []

    def calistir(cmd, check):
        komutlar.append(cmd)
        Path(cmd[-1]).write_bytes(b"x")

    cfg = dict(DEFAULTS, canli_klasoru=str(kayitlar), cikti_klasoru=str(klipler))
    demo = tmp_path / "1-abcdef12-3456-7890.dem"
    assert canli.kes(demo, cfg, Path("ffmpeg"), prova=True, calistir=calistir) == []
    assert komutlar == []

    yazilan = canli.kes(demo, cfg, Path("ffmpeg"), calistir=calistir)
    assert [p.name for p in yazilan] == ["dust2_abcdef12_R02_3K_ak47.mp4"]
    assert len(komutlar) == 1
    cmd = komutlar[0]
    assert cmd[cmd.index("-ss") + 1] == "117.000" and cmd[cmd.index("-t") + 1] == "5.000"
    assert cmd[cmd.index("-i") + 1] == str(kayitlar / "m.mkv")
    assert canli.kes(demo, cfg, Path("ffmpeg"), calistir=calistir) == []  # zaten var


def test_kes_uyan_kayit_yoksa_hata(tmp_path, monkeypatch):
    monkeypatch.setattr(canli, "open_demo", lambda p: p)
    monkeypatch.setattr(canli, "round_baslangiclari", lambda d: ("de_dust2", DEMO))
    cfg = dict(DEFAULTS, canli_klasoru=str(tmp_path))
    with pytest.raises(SystemExit, match="uyan kayıt yok"):
        canli.kes(tmp_path / "a.dem", cfg, Path("ffmpeg"))


# --- ffmpeg'in kapanması, maç bitişi, adlar ---

def kaydedici(tmp_path, surecler):
    it = iter(surecler)
    return canli.Kaydedici(Path("ffmpeg"), tmp_path, popen=lambda cmd, **_: next(it), saat=lambda: 100.0,
                           baslangic_oku=lambda *a: 99.0)


def test_ffmpeg_kendiliginden_kapanirsa_kayit_biter_ve_mac_boyunca_yeniden_denenmez(tmp_path, capsys):
    s = SahteSurec()
    k = kaydedici(tmp_path, [s, SahteSurec()])
    f = k.baslat("de_dust2", "765")
    f.with_suffix(".log").write_text("Cannot load nvcuda.dll\n", encoding="utf-8")
    assert not k.denetle()  # çalışıyor
    s.returncode = 1
    assert k.denetle() and not k.aktif
    assert "nvcuda" in capsys.readouterr().out
    assert canli.oturum_oku(f)["bitis"] == 100.0
    assert k.baslat("de_dust2", "765") is None  # aynı maçta yeniden denenmez
    k.mac_bitti()
    assert k.baslat("de_dust2", "765") is not None  # yeni maçta denenir


def test_durdurma_yeni_oturumu_bozmaz(tmp_path):
    """ffmpeg kapanırken yeni maç başlasa da başlangıç saati eski oturuma yazılır."""
    eski_surec = SahteSurec()
    k = kaydedici(tmp_path, [eski_surec, SahteSurec()])
    eski = k.baslat("de_dust2", "765")

    def bekle(timeout=None):  # ffmpeg kapanırken yeni maç başlıyor
        k.baslat("de_mirage", "765")
        return 0

    eski_surec.wait = bekle
    k.durdur()
    assert canli.oturum_oku(eski)["video_baslangic"] == 99.0
    yeni = k.dosya
    assert yeni != eski and canli.oturum_oku(yeni)["video_baslangic"] is None and k.aktif


def test_olay_isle_demo_kaydi_surerken_ekran_kaydi_acmaz(tmp_path):
    k = kaydedici(tmp_path, [SahteSurec()])
    o = canli.gsi.Olay("mac_basladi", 1.0, "de_dust2", steamid="765")
    canli.olay_isle(o, k, kayit_suruyor=lambda: True)
    assert not k.aktif
    canli.olay_isle(o, k, kayit_suruyor=lambda: False)
    assert k.aktif


@pytest.mark.parametrize("harita,ad", [("de_dust2", "de_dust2"), ("workshop/123/de_x", "workshop_123_de_x"),
                                       ("", "harita"), ("..", "harita")])
def test_dosya_adi(harita, ad):
    assert canli.dosya_adi(harita) == ad


def test_oturum_bul_en_cok_roundu_kapsayani_secer(tmp_path):
    # Maç iki kayda bölünmüş: kısa parçanın farkı biraz daha küçük olsa da uzun olan seçilir.
    kisa = {no: t for no, t in kayit_roundlari().items() if no <= 3}
    uzun = kayit_roundlari(bozuk=0.4)
    canli.oturum_yaz(tmp_path / "kisa.json", oturum(video="kisa.mkv", roundlar=kisa))
    canli.oturum_yaz(tmp_path / "uzun.json", oturum(video="uzun.mkv", roundlar=uzun))
    f, _ = canli.oturum_bul(tmp_path, "de_dust2", DEMO)
    assert f.name == "uzun.json"


def test_mac_bitince_ayni_haritaya_donus_kaydi_surdurur(tmp_path):
    """Yeniden bağlanma: maç bitti olayından sonra gecikmeli kapanma beklenirken aynı harita yeniden başlar."""
    s = SahteSurec()
    k = kaydedici(tmp_path, [s])
    f = k.baslat("de_dust2", "765")
    canli.olay_isle(canli.gsi.Olay("mac_bitti", 1.0, "de_dust2"), k, kayit_suruyor=lambda: False)
    assert k.bitiyor
    canli.olay_isle(canli.gsi.Olay("mac_basladi", 2.0, "de_dust2", steamid="765"), k, kayit_suruyor=lambda: False)
    assert not k.bitiyor and k.aktif and k.dosya == f and s.stdin.getvalue() == ""  # kapanmadı, aynı kayıt


def test_mac_bitince_yeni_harita_ayri_kayit_acar(tmp_path):
    eski_surec, yeni_surec = SahteSurec(), SahteSurec()
    k = kaydedici(tmp_path, [eski_surec, yeni_surec])
    eski = k.baslat("de_dust2", "765")
    canli.olay_isle(canli.gsi.Olay("mac_bitti", 1.0, "de_dust2"), k, kayit_suruyor=lambda: False)
    canli.olay_isle(canli.gsi.Olay("mac_basladi", 2.0, "de_mirage", steamid="765"), k, kayit_suruyor=lambda: False)
    assert k.aktif and not k.bitiyor and k.surec is yeni_surec and k.dosya != eski
    for _ in range(100):  # eski kayıt arka planda kapanır
        if canli.oturum_oku(eski)["video_baslangic"] is not None:
            break
        time.sleep(0.02)
    assert eski_surec.stdin.getvalue() == "q" and canli.oturum_oku(eski)["video_baslangic"] == 99.0


def test_gecikmeli_durdurma_kaydi_kapatir(tmp_path):
    s = SahteSurec()
    k = kaydedici(tmp_path, [s])
    k.baslat("de_dust2", "765")
    k.gecikmeli_durdur(0.01)
    zamanlayici = k.bekleyen
    zamanlayici.join(timeout=5)  # aktif, "q" yazılmadan False olur; durdur() bitene kadar bekle
    assert not zamanlayici.is_alive()
    assert not k.aktif and not k.bitiyor and s.stdin.getvalue() == "q"
