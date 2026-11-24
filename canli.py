"""Canlı kayıt: oynarken ekranı kaydeder, maç bitince demoyla en iyi anları keser.

CS2'ye dokunulmaz. FACEIT açık kalabilir:
- Görüntü: FFmpeg `ddagrab` (Windows Desktop Duplication) + NVENC. Oyun sürecine enjeksiyon yok,
  kodlama ekran kartının ayrı yongasında yapılır.
- Zaman: CS2'nin resmi GSI'si her round'un başladığı anı bildirir (gsi.py). Bu an demodaki
  `round_freeze_end` tick'iyle eşlenir; böylece demodaki her tick'in videodaki saniyesi bilinir.

Kullanım:
  python canli.py kur              # CS2 cfg klasörüne GSI dosyasını yazar (bir kez; CS2'yi yeniden aç)
  python canli.py izle             # açık kaldıkça her maçı kaydeder (kayitlar/)
  python canli.py kes <demo>       # demonun en iyi anlarını o maçın kaydından keser (klipler/)

Her kayıt üç dosyadır: `<tarih>_<harita>.mkv` (ham görüntü; her kare kendi duvar saatini taşır), aynı adlı
`.json` (oturum: video başlangıç saati, round başlangıç saatleri, harita, SteamID) ve `.log` (ffmpeg hataları).
"""

import argparse
import json
import re
import statistics
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import gsi
import otomatik
from analyze import analyze_player, player_tag
from config import CANLI_KODLAYICILAR, load_config
from demofile import find_csgo_dir, open_demo
from highlights import TICKRATE
from klip import clip_prefix
from kontrol import find_ffmpeg
from render import clip_filename, join_parts, segments, select_clips

KODLAYICILAR = CANLI_KODLAYICILAR
# Sabit kalite (VBR + CQ 23); 1080p60 oyun görüntüsünde ~10-25 Mbps. Anahtar kare saniyede bir:
# yeniden kodlamadan kesim en fazla 1 sn erken başlar.
KALITE = ["-preset", "p4", "-rc", "vbr", "-cq", "23", "-b:v", "0", "-maxrate", "40M", "-bufsize", "80M"]
DURDURMA_GECIKMESI = 8  # maç bitince son kill'in sonrası da girsin
SESSIZLIK_SN = 60  # bu kadar süre GSI gelmezse (CS2 kapandı/çöktü) kayıt durur
BEKCI_SN = 3  # ffmpeg'in kendiliğinden kapanıp kapanmadığına bu aralıkla bakılır
GSI_GECIKME = 0.1  # cfg'deki buffer: olay bu kadar geç gelir
UYUM_ESIGI = 2.0  # demo ile kayıt arasındaki round süresi farkının ortancası (sn); üstü başka maç sayılır
SURUM = 1


# --- kayıt ---

def kayit_komutu(ffmpeg: Path, cikti: Path, fps: int = 60, kodlayici: str = "h264_nvenc", ses: str = "") -> list[str]:
    """Ana ekranı kaydeden ffmpeg komutu. ses: DirectShow ses cihazı adı (boşsa sessiz).

    Her kare geldiği anın duvar saatini taşır (-use_wallclock_as_timestamps + -copyts): videonun başlangıç
    saati dosyanın kendisinden okunur (video_baslangici), tahmin gerekmez.
    """
    if kodlayici not in KODLAYICILAR:
        raise ValueError(f"kodlayıcı {kodlayici!r}; olabilecekler: {', '.join(KODLAYICILAR)}")
    saat = ["-use_wallclock_as_timestamps", "1"]
    cmd = [str(ffmpeg), "-hide_banner", "-loglevel", "error", "-nostats",
           *saat, "-f", "lavfi", "-i", f"ddagrab=output_idx=0:framerate={fps}:draw_mouse=0"]
    if ses:
        cmd += [*saat, "-f", "dshow", "-i", f"audio={ses}"]
    cmd += ["-copyts", "-c:v", kodlayici, *KALITE, "-g", str(fps)]
    if ses:
        cmd += ["-c:a", "aac", "-b:a", "160k"]
    return cmd + ["-f", "matroska", str(cikti)]


START_RE = re.compile(r"start: (\d+\.\d+)")


def video_baslangici(ffmpeg: Path, video: Path, calistir=subprocess.run) -> float | None:
    """Kaydın ilk karesinin duvar saati (time.time() cinsinden); okunamazsa None."""
    try:
        r = calistir([str(ffmpeg), "-hide_banner", "-i", str(video)], capture_output=True, text=True,
                     encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = START_RE.search(r.stderr or "")
    deger = float(m.group(1)) if m else 0.0
    return deger if deger > 1e9 else None  # 1e9: 2001 sonrası; değilse duvar saati değil


def oturum_yaz(dosya: Path, oturum: dict) -> None:
    tmp = dosya.with_name(dosya.name + ".tmp")
    tmp.write_text(json.dumps(oturum, ensure_ascii=False, indent=1), encoding="utf-8")
    for deneme in range(20):  # Windows: başka biri (kes, arayüz) o an okuyorsa yerine yazma kısa süre reddedilir
        try:
            tmp.replace(dosya)
            return
        except PermissionError:
            if deneme == 19:
                raise
            time.sleep(0.05)


def oturum_oku(dosya: Path) -> dict | None:
    try:
        o = json.loads(Path(dosya).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(o, dict) or o.get("surum") != SURUM:
        return None
    o["roundlar"] = {int(k): float(v) for k, v in o.get("roundlar", {}).items()}
    return o


class Kaydedici:
    """Tek ffmpeg kaydını ve oturum dosyasını yönetir. Aynı anda tek kayıt."""

    def __init__(self, ffmpeg: Path, klasor: Path, fps: int = 60, kodlayici: str = "h264_nvenc", ses: str = "",
                 popen=subprocess.Popen, saat=time.time, baslangic_oku=video_baslangici):
        self.ffmpeg, self.klasor, self.fps, self.kodlayici, self.ses = ffmpeg, Path(klasor), fps, kodlayici, ses
        self.popen, self.saat, self.baslangic_oku = popen, saat, baslangic_oku
        self.surec = None
        self.oturum: dict = {}
        self.dosya: Path | None = None
        self.basarisiz = False  # ffmpeg bu maçta kendiliğinden kapandı: maç bitene kadar yeniden denenmez
        self.bekleyen: threading.Timer | None = None  # maç bitti, kayıt birkaç saniye sonra kapanacak
        self.kilit = threading.Lock()

    @property
    def aktif(self) -> bool:
        return self.surec is not None

    @property
    def bitiyor(self) -> bool:
        """Maç bitti, kayıt gecikmeli kapanmayı bekliyor."""
        return self.bekleyen is not None

    def gecikmeli_durdur(self, gecikme: float) -> None:
        """Maç bitince son anlar da girsin diye kaydı gecikmeyle kapatır. Arada maç yeniden başlarsa baslat karar verir."""
        with self.kilit:
            if self.surec is None:
                return
            if self.bekleyen is not None:
                self.bekleyen.cancel()
            self.bekleyen = threading.Timer(gecikme, self.durdur, args=(self.dosya,))
            self.bekleyen.daemon = True
            self.bekleyen.start()

    def baslat(self, harita: str, steamid: str) -> Path | None:
        eski = None
        try:
            with self.kilit:
                if self.surec is not None:
                    if self.bekleyen is None or self.oturum.get("harita") == harita:
                        # Süren maç ya da kapanmadan aynı haritaya geri dönüş (yeniden bağlanma): kayıt sürer.
                        self._bekleyeni_iptal()
                        return self.dosya
                    # Önceki maç bitti, kapanmasını beklerken yeni harita başladı: eskisini arka planda kapat.
                    eski = self._ayir()
                return self._ac(harita, steamid)
        finally:
            if eski is not None:
                threading.Thread(target=self._kapat, args=eski, daemon=True).start()

    def _bekleyeni_iptal(self) -> None:
        if self.bekleyen is not None:
            self.bekleyen.cancel()
            self.bekleyen = None

    def _ac(self, harita: str, steamid: str) -> Path | None:
        """Yeni kaydı açar. Kilit tutulurken çağrılır."""
        if self.basarisiz:
            return None
        self.klasor.mkdir(parents=True, exist_ok=True)
        ad = f"{datetime.now():%Y%m%d-%H%M%S}_{dosya_adi(harita)}"
        video, self.dosya = self.klasor / f"{ad}.mkv", self.klasor / f"{ad}.json"
        self.oturum = {"surum": SURUM, "video": video.name, "harita": harita, "steamid": steamid,
                       "baslangic": self.saat(), "video_baslangic": None, "bitis": None, "roundlar": {}}
        oturum_yaz(self.dosya, self.oturum)
        # ffmpeg hataları dosyaya: boru dolarsa ffmpeg takılır.
        with open(self.dosya.with_suffix(".log"), "w", encoding="utf-8") as gunluk:
            self.surec = self.popen(kayit_komutu(self.ffmpeg, video, self.fps, self.kodlayici, self.ses),
                                    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=gunluk,
                                    text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        print(f"Kayıt başladı: {video}")
        return self.dosya

    def round_basladi(self, no: int, zaman: float) -> None:
        with self.kilit:
            if self.surec is None:
                return
            # Yeniden başlatmada (mp_restartgame) aynı numara tekrar gelir; sonuncusu geçerli.
            self.oturum["roundlar"][no] = zaman - GSI_GECIKME
            oturum_yaz(self.dosya, self.oturum)

    def denetle(self) -> bool:
        """ffmpeg kendiliğinden kapandıysa (NVENC yok, ses cihazı yanlış…) kaydı bitirip hatayı yazar.

        True: kayıt kapandı. Bekçi birkaç saniyede bir çağırır; yoksa maç boyunca boş kayıt "sürer".
        """
        with self.kilit:
            surec = self.surec
            if surec is None or surec.poll() is None:
                return False
            self.surec, dosya, oturum = None, self.dosya, self.oturum
            self.basarisiz = True
            oturum["bitis"] = self.saat()
            oturum_yaz(dosya, oturum)
        print(f"  ! Kayıt durdu: ffmpeg kapandı (çıkış kodu {surec.returncode}). Bu maç kaydedilmeyecek."
              + gunluk_ozeti(dosya))
        return True

    def mac_bitti(self) -> None:
        """Yeni maçta ffmpeg yeniden denenebilir."""
        with self.kilit:
            self.basarisiz = False

    def durdur(self, dosya: Path | None = None) -> None:
        """Kaydı kapatır. dosya verilirse yalnız o oturum hâlâ sürüyorsa (gecikmeli durdurma yeni maçı kesmesin)."""
        with self.kilit:
            if self.surec is None or (dosya is not None and dosya != self.dosya):
                return
            parca = self._ayir()
        self._kapat(*parca)

    def _ayir(self) -> tuple:
        """Süren kaydı Kaydedici'den ayırır (kilit tutulurken): yeni kayıt hemen açılabilir, eskisi sonra kapatılır."""
        self._bekleyeni_iptal()
        # Yerel kopyalar: ffmpeg beklenirken yeni maç başlarsa self.dosya / self.oturum değişir.
        surec, self.surec, dosya, oturum = self.surec, None, self.dosya, self.oturum
        oturum["bitis"] = self.saat()
        oturum_yaz(dosya, oturum)
        return surec, dosya, oturum

    def _kapat(self, surec, dosya: Path, oturum: dict) -> None:
        """Ayrılmış kaydın ffmpeg'ini düzgün kapatır ve videonun başlangıç saatini yazar."""
        try:
            surec.stdin.write("q")  # ffmpeg'i düzgün kapatır; mkv yarıda kesilse de okunur
            surec.stdin.flush()
            surec.wait(timeout=15)
        except (OSError, ValueError, subprocess.TimeoutExpired):
            surec.kill()
        video = dosya.with_name(oturum["video"])
        oturum["video_baslangic"] = self.baslangic_oku(self.ffmpeg, video)
        oturum_yaz(dosya, oturum)
        print(f"Kayıt bitti: {video}" + gunluk_ozeti(dosya))


def dosya_adi(harita: str) -> str:
    """Harita adından dosya adı: workshop/123/de_x -> workshop_123_de_x."""
    return re.sub(r"[^\w.-]+", "_", harita).strip("._") or "harita"


def gunluk_ozeti(oturum_dosyasi: Path, satir: int = 5) -> str:
    """ffmpeg günlüğünün son satırları (boşsa boş metin)."""
    f = Path(oturum_dosyasi).with_suffix(".log")
    try:
        son = f.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-satir:]
    except OSError:
        return ""
    return "".join(f"\n  ffmpeg: {s}" for s in son)


def izle(cfg: dict, ffmpeg: Path, csgo_dir: Path, sure: float = 0) -> None:
    """GSI'yi dinler; maç başlayınca kaydı açar, bitince kapatır. sure > 0 ise o kadar saniye sonra çıkar (deneme)."""
    token = gsi.cfg_token(csgo_dir)
    if token is None:
        raise SystemExit(f"GSI dosyası yok: {gsi.cfg_yolu(csgo_dir)}. Önce: python canli.py kur")
    kaydedici = Kaydedici(ffmpeg, Path(cfg["canli_klasoru"]), cfg["canli_fps"], cfg["canli_kodlayici"],
                          cfg["canli_ses"])
    izleyici = gsi.Izleyici()
    try:
        srv = gsi.sunucu(cfg["canli_port"], token, izleyici, lambda o: olay_isle(o, kaydedici))
    except OSError as e:
        raise SystemExit(f"GSI portu {cfg['canli_port']} açılamadı ({e}). canli.bat zaten açık olabilir; "
                         "değilse ayarlardan canli_port'u değiştirip canli.bat kur çalıştır.")
    baslangic = time.time()

    def bekci() -> None:
        while True:
            time.sleep(BEKCI_SN)
            kaydedici.denetle()
            if kaydedici.aktif and izleyici.son_durum and time.time() - izleyici.son_durum > SESSIZLIK_SN:
                print("  CS2'den haber yok; kayıt durduruldu.")
                kaydedici.durdur()
            if sure and time.time() - baslangic > sure:
                srv.shutdown()
                return

    threading.Thread(target=bekci, daemon=True).start()
    print(f"CS2 bekleniyor (GSI: 127.0.0.1:{cfg['canli_port']}). Çıkmak için Ctrl+C.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
        kaydedici.durdur()


def olay_isle(o: gsi.Olay, kaydedici: Kaydedici, kayit_suruyor=None) -> None:
    """GSI olayına göre kaydı açar, round saatini yazar, maç bitince kaydı kapatır.

    CSDM ile demo kaydı sürerken (arayüz ya da otomatik kuyruk; ortak kayıt kilidi) CS2 demoyu oynatır ve GSI
    yine durum gönderir: o sırada ekran kaydı açılmaz.
    """
    if kayit_suruyor is None:
        kayit_suruyor = lambda: otomatik.kilit_dolu(otomatik.KILIT)  # noqa: E731
    if o.tur == "mac_bitti":
        kaydedici.mac_bitti()
        kaydedici.gecikmeli_durdur(DURDURMA_GECIKMESI)
        return
    # Kapanmayı bekleyen kayıt varken maç yeniden başladıysa baslat karar verir: aynı harita sürer, yenisi ayrı kayıt.
    if not kaydedici.aktif or kaydedici.bitiyor:
        if kayit_suruyor():
            return
        kaydedici.baslat(o.harita, o.steamid)
    if o.tur == "round_basladi" and kaydedici.aktif:  # kayıt yoksa (ffmpeg kapandı) round yazılmaz
        print(f"  R{o.round:02d} başladı")
        kaydedici.round_basladi(o.round, o.zaman)


# --- demo ile eşleme ve kesim ---

def round_baslangiclari(demo: Path) -> tuple[str, dict[int, int]]:
    """(harita, {round no: donma süresinin bittiği tick}). Isınma ve yeniden başlatmada sonuncusu kalır."""
    from demoparser2 import DemoParser

    parser = DemoParser(str(demo))
    df = parser.parse_event("round_freeze_end", other=["total_rounds_played"])
    out: dict[int, int] = {}
    for r in df.sort_values("tick").itertuples():
        out[int(r.total_rounds_played) + 1] = int(r.tick)
    return parser.parse_header().get("map_name", "?"), out


def uyum(kayit_roundlari: dict[int, float], demo_roundlari: dict[int, int]) -> tuple[float, int]:
    """(ortanca fark sn, karşılaştırılan round sayısı). Ardışık round sürelerini kayıt ile demoda karşılaştırır."""
    ortak = sorted(set(kayit_roundlari) & set(demo_roundlari))
    farklar = [abs((kayit_roundlari[b] - kayit_roundlari[a]) - (demo_roundlari[b] - demo_roundlari[a]) / TICKRATE)
               for a, b in zip(ortak, ortak[1:]) if b == a + 1]
    return (statistics.median(farklar), len(farklar)) if farklar else (float("inf"), 0)


def oturum_bul(klasor: Path, harita: str, demo_roundlari: dict[int, int]) -> tuple[Path, dict] | None:
    """Demoya uyan kayıt: aynı harita, round süreleri uyuyor (en az 2 karşılaştırma, fark UYUM_ESIGI altında).

    Birden çok kayıt uyarsa (maç bölünmüş kaydedilmiş) en çok round'u kapsayan seçilir, eşitlikte farkı küçük olan.
    """
    adaylar = []
    for f in sorted(Path(klasor).glob("*.json")):
        o = oturum_oku(f)
        if o is None or o.get("harita") != harita:
            continue
        fark, n = uyum(o["roundlar"], demo_roundlari)
        if n >= 2 and fark <= UYUM_ESIGI:
            adaylar.append((-n, fark, f, o))
    if not adaylar:
        return None
    _, _, f, o = min(adaylar, key=lambda a: a[:2])
    return f, o


def video_araliklari(h: dict, oturum: dict, demo_roundlari: dict[int, int]) -> list[tuple[float, float]] | None:
    """Klibin tick aralıklarının videodaki saniyeleri; round kayıtta yoksa ya da kayıt dışına taşıyorsa None."""
    no = h["round"]
    if no not in oturum["roundlar"] or no not in demo_roundlari:
        return None
    sifir = oturum["roundlar"][no] - oturum["video_baslangic"] - demo_roundlari[no] / TICKRATE
    out = [(sifir + a / TICKRATE, sifir + b / TICKRATE) for a, b in segments(h)]
    uzunluk = (oturum["bitis"] - oturum["video_baslangic"]) if oturum.get("bitis") else None
    if out[0][0] < 0 or (uzunluk is not None and out[-1][1] > uzunluk):
        return None
    return out


def kesim_komutu(ffmpeg: Path, ham: Path, bas: float, bit: float, cikti: Path) -> list[str]:
    """Yeniden kodlamadan kesim; başlangıç önceki anahtar kareye (en fazla 1 sn) yuvarlanır."""
    return [str(ffmpeg), "-y", "-loglevel", "error", "-ss", f"{bas:.3f}", "-i", str(ham), "-t", f"{bit - bas:.3f}",
            "-c", "copy", "-avoid_negative_ts", "make_zero", "-movflags", "+faststart", str(cikti)]


def kes(demo_yolu: Path, cfg: dict, ffmpeg: Path, oturum_dosyasi: Path | None = None, prova: bool = False,
        calistir=subprocess.run) -> list[Path]:
    """Demonun en iyi anlarını eşleşen kayıttan keser; kesilen klipleri döner."""
    demo = open_demo(demo_yolu)
    harita, demo_roundlari = round_baslangiclari(demo)
    if oturum_dosyasi:
        oturum = oturum_oku(oturum_dosyasi)
        if oturum is None:
            raise SystemExit(f"Oturum dosyası okunamadı: {oturum_dosyasi}")
        kaynak = Path(oturum_dosyasi)
    else:
        bulunan = oturum_bul(Path(cfg["canli_klasoru"]), harita, demo_roundlari)
        if bulunan is None:
            raise SystemExit(f"Bu demoya ({harita}) uyan kayıt yok: {cfg['canli_klasoru']}")
        kaynak, oturum = bulunan
    ham = kaynak.with_name(oturum["video"])
    if oturum.get("video_baslangic") is None:  # kayıt düzgün kapanmadı
        oturum["video_baslangic"] = video_baslangici(ffmpeg, ham)
        if oturum["video_baslangic"] is None:
            raise SystemExit(f"Kaydın başlangıç saati okunamadı: {ham}")
    fark, n = uyum(oturum["roundlar"], demo_roundlari)
    print(f"Kayıt: {kaynak.name} ({n} round karşılaştırıldı, fark {fark:.2f} sn)")

    # Görüntü kaydı yapanın gözünden: oyuncu GSI'deki SteamID.
    r = analyze_player(demo, oturum["steamid"], cfg["once_sn"], cfg["sonra_sn"], default=cfg["oyuncu"])
    etiket = "" if r["varsayilan"] else player_tag(r["ad"], r["steamid"])
    klipler = select_clips(r["highlights"], cfg["min_skor"], cfg["mac_basi_en_fazla"])
    cikti_klasoru = Path(cfg["cikti_klasoru"])
    onek = clip_prefix(harita, demo)
    yazilan = []
    for h in klipler:
        hedef = cikti_klasoru / clip_filename(onek, h, etiket)
        araliklar = video_araliklari(h, oturum, demo_roundlari)
        if araliklar is None:
            print(f"  atlandı (kayıtta yok): R{h['round']:02d} {', '.join(h['labels'])}")
            continue
        if hedef.exists():
            print(f"  zaten var: {hedef.name}")
            continue
        sureler = ", ".join(f"{a:.1f}-{b:.1f} sn" for a, b in araliklar)
        print(f"  R{h['round']:02d} skor {h['score']:.1f} [{sureler}] -> {hedef.name}")
        if prova:
            continue
        cikti_klasoru.mkdir(parents=True, exist_ok=True)
        parcalar = [hedef.with_name(f"{hedef.stem}.parca{i}.mp4") for i in range(len(araliklar))]
        for (a, b), p in zip(araliklar, parcalar):
            calistir(kesim_komutu(ffmpeg, ham, a, b, p), check=True)
        yazilan.append(join_parts(parcalar, hedef, ffmpeg))
    return yazilan


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Canlı kayıt: oynarken kaydet, demoyla en iyi anları kes")
    ap.add_argument("--ayarlar", type=Path, default=Path(__file__).with_name("ayarlar.json"))
    alt = ap.add_subparsers(dest="komut", required=True)
    p_kur = alt.add_parser("kur", help="CS2 cfg klasörüne GSI dosyasını yazar")
    p_kur.add_argument("--kontrol", action="store_true",
                       help="yazmadan bak: güncelse çıkış 0, yazılması gerekiyorsa 1, CS2 yoksa 2")
    p_izle = alt.add_parser("izle", help="maçları kaydeder (Ctrl+C ile çık)")
    p_izle.add_argument("--sure", type=float, default=0, help="bu kadar saniye sonra çık (deneme)")
    p_kes = alt.add_parser("kes", help="demonun en iyi anlarını kayıttan keser")
    p_kes.add_argument("demo", type=Path)
    p_kes.add_argument("--kayit", type=Path, help="oturum .json dosyası (yoksa demoya uyan bulunur)")
    p_kes.add_argument("--prova", action="store_true", help="kesmeden ne yapılacağını göster")
    args = ap.parse_args()

    cfg = load_config(args.ayarlar)
    csgo_dir = Path(cfg["csgo_klasoru"]) if cfg["csgo_klasoru"] else find_csgo_dir()
    if args.komut in ("kur", "izle") and (csgo_dir is None or not (csgo_dir / "cfg").is_dir()):
        print("CS2 klasörü bulunamadı. ayarlar.json → csgo_klasoru (…\\game\\csgo).", file=sys.stderr)
        raise SystemExit(2)
    if args.komut == "kur":
        if args.kontrol:
            guncel = gsi.cfg_guncel(csgo_dir, cfg["canli_port"])
            print(f"GSI dosyası {'güncel' if guncel else 'yazılmalı'}: {gsi.cfg_yolu(csgo_dir)}")
            raise SystemExit(0 if guncel else 1)
        f = gsi.cfg_yaz(csgo_dir, cfg["canli_port"])
        print(f"GSI dosyası yazıldı: {f}\nCS2 açıksa kapatıp yeniden aç.")
        return
    ffmpeg = find_ffmpeg(cfg["ffmpeg_yolu"])
    if ffmpeg is None:
        raise SystemExit("ffmpeg bulunamadı: winget install Gyan.FFmpeg (ya da ayarlar.json → ffmpeg_yolu)")
    if args.komut == "izle":
        izle(cfg, ffmpeg, csgo_dir, args.sure)
    else:
        kes(args.demo, cfg, ffmpeg, args.kayit, args.prova)


if __name__ == "__main__":
    main()
