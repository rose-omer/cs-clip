"""Tam otomatik akış: yeni demoları izle, sıraya al, CS2/FACEIT kapalıyken tek tek kaydet.

Kullanım:
  python otomatik.py izle [--aralik 30] [--faceit-dk 0] [--temizle] [--mevcutlari-da]
  python otomatik.py durum
  python otomatik.py ekle <demo>
  python otomatik.py faceit [--adet 5]

- İzleyici: İndirilenler ve `demos/` (ya da ayarlar.json → demo_klasorleri) klasörlerine bakar. İlk çalışmada
  klasörde zaten duran demolar "görüldü" sayılır, sıraya girmez (`--mevcutlari-da` ile girer). İndirmesi biten
  (KARARLI_SN boyunca değişmeyen) her yeni demo sıraya eklenir.
- Kuyruk: sıradaki demo yalnız CS2 ve FACEIT kapalıyken, kapandıktan sonra `otomatik_bekle_sn` beklenip
  `kontrol.preflight` geçince `klip.py` ile kaydedilir. CS2 ya da FACEIT açıksa hiçbir şeye dokunulmaz, beklenir.
  Aynı anda tek kayıt: arayüz ve kuyruk `kayit.kilit` dosyasını paylaşır.
- FACEIT: `--faceit-dk N` verilirse N dakikada bir son maçlara bakılır; izleme başladığında var olan maçlar
  indirilmez, yalnız sonra bitenler. Hemen indirmek için: `otomatik.py faceit --adet 5`.
İndirilen demolar doğrudan sıraya eklenir. Durum `otomatik.json` dosyasında; arayüz buradan okur.
"""

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from config import load_config
from demofile import find_csgo_dir
from klip import DEMO_SUFFIXES, demo_id
from kontrol import BLOCKERS, blocking_programs, preflight, running_processes
from onarim import is_repaired_copy

ROOT = Path(__file__).resolve().parent
DURUM_DOSYASI = ROOT / "otomatik.json"
KILIT = ROOT / "kayit.kilit"
KARARLI_SN = 15  # dosya bu kadar süredir değişmiyorsa indirme bitmiş sayılır
ARALIK_SN = 30
SATIR = 40
BASLAYAMAZ = "Kayıt başlayamaz"  # klip.py'nin ön kontrol hatası: demo değil ortam sorunu, sonra tekrar denenir

if os.name == "nt":
    import msvcrt

    def _kilitle(f) -> bool:
        f.seek(0)
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False

    def _birak(f) -> None:
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def _kilitle(f) -> bool:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def _birak(f) -> None:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


class Mesgul(Exception):
    pass


@contextmanager
def kayit_kilidi(yol: Path = KILIT):
    """Süreçler arası kayıt kilidi. Süreç ölürse işletim sistemi kilidi bırakır."""
    f = open(yol, "a+b")
    try:
        if not _kilitle(f):
            raise Mesgul("Başka bir kayıt sürüyor.")
        try:
            yield
        finally:
            _birak(f)
    finally:
        f.close()


def kilit_dolu(yol: Path = KILIT) -> bool:
    try:
        with kayit_kilidi(yol):
            return False
    except Mesgul:
        return True


def simdi_iso(t: float | None = None) -> str:
    return datetime.fromtimestamp(time.time() if t is None else t).isoformat(timespec="seconds")


def izlenen_klasorler(cfg: dict) -> list[Path]:
    return [Path(f) for f in cfg["demo_klasorleri"]] or [Path.home() / "Downloads", ROOT / "demos"]


def demo_bul(klasorler: list[Path]) -> dict[str, Path]:
    """id -> dosya (.dem varsa o). `.part`/`.crdownload` gibi yarım indirmeler uzantıdan elenir."""
    found: dict[str, Path] = {}
    for folder in klasorler:
        if not folder.is_dir():
            continue
        for p in folder.iterdir():
            if p.is_file() and p.name.lower().endswith(DEMO_SUFFIXES) and not is_repaired_copy(p):
                did = demo_id(p)
                if did not in found or p.suffix.lower() == ".dem":
                    found[did] = p
    return found


class Kuyruk:
    """otomatik.json: görülen demolar, sıra ve çalışan işçinin durumu. Her değişiklik dosyaya yazılır."""

    def __init__(self, dosya: Path = DURUM_DOSYASI):
        self.dosya = Path(dosya)
        self._lock = threading.Lock()

    def oku(self) -> dict:
        try:
            s = json.loads(self.dosya.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            s = {}
        s.setdefault("gorulen", [])
        s.setdefault("kuyruk", [])
        s.setdefault("isci", {})
        return s

    def _yaz(self, s: dict) -> None:
        tmp = self.dosya.with_name(self.dosya.name + ".tmp")
        tmp.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
        for attempt in range(10):  # Windows: arayüz o an okuyorsa kısa süre kilitli olabilir
            try:
                tmp.replace(self.dosya)
                return
            except PermissionError:
                if attempt == 9:
                    raise
                time.sleep(0.1)

    def guncelle(self, fn):
        with self._lock:
            s = self.oku()
            r = fn(s)
            self._yaz(s)
            return r

    def ekle(self, yol: Path, kaynak: str = "izleyici") -> bool:
        """Demoyu sıraya ekler; zaten bekliyor/kaydediliyorsa eklemez."""
        did = demo_id(Path(yol))

        def f(s):
            if did not in s["gorulen"]:
                s["gorulen"].append(did)
            if any(i["id"] == did and i["durum"] in ("bekliyor", "kaydediliyor") for i in s["kuyruk"]):
                return False
            s["kuyruk"] = [i for i in s["kuyruk"] if i["id"] != did]
            s["kuyruk"].append({"id": did, "yol": str(yol), "durum": "bekliyor", "eklendi": simdi_iso(),
                                "kaynak": kaynak, "mesaj": ""})
            return True

        return self.guncelle(f)

    def oge_guncelle(self, did: str, **alanlar) -> None:
        def f(s):
            for i in s["kuyruk"]:
                if i["id"] == did:
                    i.update(alanlar)

        self.guncelle(f)

    def isci_guncelle(self, **alanlar) -> None:
        self.guncelle(lambda s: s["isci"].update(alanlar))


class Izleyici:
    def __init__(self, kuyruk: Kuyruk, klasorler: list[Path], kararli_sn: float = KARARLI_SN,
                 mevcutlari_da: bool = False, saat=time.time):
        self.kuyruk, self.klasorler, self.kararli_sn = kuyruk, klasorler, kararli_sn
        self.mevcutlari_da, self.saat = mevcutlari_da, saat

    def tara(self) -> list[str]:
        """Yeni demoları sıraya ekler, eklenenlerin kimliklerini döner."""
        found = demo_bul(self.klasorler)
        now = self.saat()

        def f(s):
            if not s.get("izleme_basladi"):
                s["izleme_basladi"] = simdi_iso(now)
                if not self.mevcutlari_da:
                    s["gorulen"] = sorted(set(s["gorulen"]) | set(found))
                    return []
            seen = set(s["gorulen"])
            yeni = []
            for did, p in sorted(found.items(), key=lambda kv: kv[1].stat().st_mtime):
                if did in seen:
                    continue
                if now - p.stat().st_mtime < self.kararli_sn:
                    continue  # hâlâ yazılıyor olabilir; sonraki taramada
                s["gorulen"].append(did)
                s["kuyruk"].append({"id": did, "yol": str(p), "durum": "bekliyor", "eklendi": simdi_iso(now),
                                    "kaynak": "izleyici", "mesaj": ""})
                yeni.append(did)
            return yeni

        return self.kuyruk.guncelle(f)


def klip_calistir(yol: Path, satir, ayarlar: Path | None = None, temizle: bool = False) -> int:
    """klip.py'yi ayrı süreçte çalıştırır, her satırı `satir`a verir, çıkış kodunu döner."""
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    cmd = [sys.executable, str(ROOT / "klip.py"), str(yol)]
    if ayarlar:
        cmd += ["--ayarlar", str(ayarlar)]
    if temizle:
        cmd.append("--temizle")
    with subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, text=True,
                          encoding="utf-8", errors="replace",
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)) as p:
        for line in p.stdout:
            if line.strip():
                satir(line.rstrip())
    return p.returncode


class Isci:
    """Sıradaki demoyu, ortam uygunsa kaydeder. `adim()` bir kez bakar; kayıt varsa bitene kadar sürer."""

    def __init__(self, kuyruk: Kuyruk, cfg: dict, kaydet=None, surecler=running_processes, on_kontrol=None,
                 kilit: Path = KILIT, saat=time.time, yaz=print, aralik: float = ARALIK_SN):
        self.kuyruk, self.cfg, self.kilit, self.saat, self.yaz = kuyruk, cfg, kilit, saat, yaz
        self.kaydet = kaydet or (lambda yol, satir: klip_calistir(yol, satir))
        self.surecler = surecler
        self.on_kontrol = on_kontrol or self._preflight
        self.bekle_sn = cfg.get("otomatik_bekle_sn", 120)
        self.aralik = aralik
        self.son_engel: float | None = None
        self.son_durum = ""

    def _preflight(self) -> list[str]:
        csgo = Path(self.cfg["csgo_klasoru"]) if self.cfg["csgo_klasoru"] else find_csgo_dir()
        return preflight(self.cfg, csgo)[1]

    def durum(self, metin: str, **ek) -> str:
        self.kuyruk.isci_guncelle(pid=os.getpid(), nabiz=self.saat(), aralik=self.aralik, durum=metin, **ek)
        if metin != self.son_durum:
            self.yaz(f"[{simdi_iso(self.saat())[11:]}] {metin}")
            self.son_durum = metin
        return metin

    def adim(self) -> str:
        s = self.kuyruk.oku()
        busy = kilit_dolu(self.kilit)
        if not busy:  # önceki işçi yarıda öldüyse "kaydediliyor" kalan iş sıraya döner
            for i in s["kuyruk"]:
                if i["durum"] == "kaydediliyor":
                    self.kuyruk.oge_guncelle(i["id"], durum="bekliyor", mesaj="Yarıda kalmıştı, yeniden denenecek")
                    i["durum"] = "bekliyor"
        oge = next((i for i in s["kuyruk"] if i["durum"] == "bekliyor"), None)
        if oge is None:
            return self.durum("Sıra boş; yeni demo bekleniyor", aktif=None)
        yol = Path(oge["yol"])
        if not yol.exists():
            self.kuyruk.oge_guncelle(oge["id"], durum="hata", mesaj="Dosya artık yok", bitti=simdi_iso())
            return self.durum(f"{oge['id']}: dosya artık yok, atlandı", aktif=None)

        engeller = blocking_programs(self.surecler())
        now = self.saat()
        if engeller:
            self.son_engel = now
            return self.durum("Bekliyor: " + ", ".join(BLOCKERS[e] for e in engeller), aktif=None)
        if self.son_engel is not None and now - self.son_engel < self.bekle_sn:
            kalan = int(self.bekle_sn - (now - self.son_engel))
            return self.durum(f"CS2/FACEIT yeni kapandı; {kalan} sn sonra kayıt başlayacak", aktif=None)
        if busy:
            return self.durum("Bekliyor: başka bir kayıt sürüyor (arayüz)", aktif=None)
        problems = self.on_kontrol()
        if problems:
            return self.durum("Bekliyor: " + problems[0], aktif=None)
        # Ön kontrol sırasında CS2/FACEIT açılmış olabilir: son bir kez bak.
        if engeller := blocking_programs(self.surecler()):
            self.son_engel = self.saat()
            return self.durum("Bekliyor: " + ", ".join(BLOCKERS[e] for e in engeller), aktif=None)
        try:
            with kayit_kilidi(self.kilit):
                return self._kaydet(oge, yol)
        except Mesgul:
            return self.durum("Bekliyor: başka bir kayıt sürüyor (arayüz)", aktif=None)

    def _kaydet(self, oge: dict, yol: Path) -> str:
        did = oge["id"]
        self.kuyruk.oge_guncelle(did, durum="kaydediliyor", mesaj="Kayıt sürüyor", basladi=simdi_iso(self.saat()))
        self.durum(f"Kaydediliyor: {did}", aktif=did, satirlar=[])
        satirlar: list[str] = []
        son_yazim = [0.0]

        def satir(line: str) -> None:
            satirlar.append(line)
            del satirlar[:-SATIR]
            self.yaz(f"  {line}")
            if self.saat() - son_yazim[0] >= 2:  # dosyaya en çok 2 sn'de bir
                son_yazim[0] = self.saat()
                self.kuyruk.isci_guncelle(nabiz=self.saat(), satirlar=list(satirlar))

        try:
            code = self.kaydet(yol, satir)
        except OSError as e:
            code, satirlar[:] = 1, [str(e)]
        son = satirlar[-1] if satirlar else f"çıkış kodu {code}"
        if any(BASLAYAMAZ in ln for ln in satirlar):
            sorun = next((ln.strip(" -") for ln in satirlar if ln.lstrip().startswith("- ")), son)
            self.kuyruk.oge_guncelle(did, durum="bekliyor", mesaj=sorun)
            return self.durum(f"Bekliyor: {sorun}", aktif=None, satirlar=satirlar)
        if code == 0:
            self.kuyruk.oge_guncelle(did, durum="bitti", mesaj=son, bitti=simdi_iso(self.saat()))
            return self.durum(f"Bitti: {did}", aktif=None, satirlar=satirlar)
        self.kuyruk.oge_guncelle(did, durum="hata", mesaj=son, bitti=simdi_iso(self.saat()))
        return self.durum(f"Kaydedilemedi: {did}: {son}", aktif=None, satirlar=satirlar)


def faceit_yokla(kuyruk: Kuyruk, cfg: dict, hedef: Path, adet: int = 5, istemci=None, yaz=print,
                 ilk_kez_indirme: bool = True) -> list[Path]:
    """FACEIT'teki son maçların demolarını indirir; indirilen maçlar otomatik.json'da tutulur (tekrar inmez).

    `ilk_kez_indirme=False` iken ilk yoklamada bulunan maçlar indirilmeden "görüldü" sayılır (izleme modu:
    yalnız izleme başladıktan sonra biten maçlar iner).
    """
    import faceit

    api = istemci or faceit.Faceit(cfg.get("faceit_api_anahtari", ""))
    s = kuyruk.oku()
    if "faceit_indirilen" not in s and not ilk_kez_indirme:
        pid = api.oyuncu_id(cfg.get("faceit_kullanici") or cfg["oyuncu"])
        mids = [m["match_id"] for m in api.son_maclar(pid, adet)]
        kuyruk.guncelle(lambda st: st.__setitem__("faceit_indirilen", mids))
        yaz(f"FACEIT: {len(mids)} eski maç görüldü sayıldı; bundan sonra bitenler indirilecek.")
        return []
    atla = set(s.get("faceit_indirilen", []))
    sonuc = faceit.son_demolari_indir(cfg, hedef, adet, atla, api, yaz)
    if sonuc:
        kuyruk.guncelle(lambda st: st.__setitem__(
            "faceit_indirilen", (st.get("faceit_indirilen", []) + [m for m, _ in sonuc])[-200:]))
    indirilen = [p for _, p in sonuc if p is not None]
    for p in indirilen:  # izleyici hiç çalışmamış olsa da sıraya girsin
        kuyruk.ekle(p, "faceit")
    return indirilen


def ozet(dosya: Path = DURUM_DOSYASI, kilit: Path = KILIT, saat=time.time, son: int = 12) -> dict:
    """Arayüz için kısa durum."""
    s = Kuyruk(dosya).oku()
    isci = s["isci"]
    nabiz = isci.get("nabiz") or 0
    sinir = max(3 * float(isci.get("aralik") or ARALIK_SN), 90)
    calisiyor = bool(nabiz) and (saat() - nabiz < sinir or (isci.get("aktif") is not None and kilit_dolu(kilit)))
    kuyruk = s["kuyruk"]
    return {
        "calisiyor": calisiyor,
        "durum": isci.get("durum", "") if calisiyor else "",
        "aktif": isci.get("aktif") if calisiyor else None,
        "satirlar": (isci.get("satirlar") or [])[-8:] if calisiyor else [],
        "bekleyen": sum(i["durum"] == "bekliyor" for i in kuyruk),
        "kuyruk": [{k: i.get(k) for k in ("id", "durum", "mesaj", "eklendi", "bitti", "kaynak")}
                   for i in reversed(kuyruk[-son:])],
    }


def calistir(cfg: dict, ayarlar: Path | None = None, aralik: float = ARALIK_SN, faceit_dk: float = 0,
             temizle: bool = False, mevcutlari_da: bool = False, dur: threading.Event | None = None,
             yaz=print, dosya: Path = DURUM_DOSYASI) -> None:
    """İzleme döngüsü. `dur` ayarlanınca çıkar (arayüz içinden de çalışır)."""
    dur = dur or threading.Event()
    kuyruk = Kuyruk(dosya)
    klasorler = izlenen_klasorler(cfg)
    izleyici = Izleyici(kuyruk, klasorler, mevcutlari_da=mevcutlari_da)
    isci = Isci(kuyruk, cfg, kaydet=lambda yol, satir: klip_calistir(yol, satir, ayarlar, temizle),
                yaz=yaz, aralik=aralik)
    yaz("Otomatik kayıt: " + ", ".join(str(k) for k in klasorler) + " izleniyor (durdurmak için Ctrl+C).")
    son_faceit = 0.0
    while not dur.is_set():
        if faceit_dk and time.time() - son_faceit >= faceit_dk * 60:
            son_faceit = time.time()
            try:
                for p in faceit_yokla(kuyruk, cfg, klasorler[0], yaz=yaz, ilk_kez_indirme=False):
                    yaz(f"FACEIT'ten indirildi: {p.name}")
            except Exception as e:  # FACEIT erişilemese de kuyruk çalışmaya devam etsin
                yaz(f"FACEIT: {e}")
        try:
            for did in izleyici.tara():
                yaz(f"Sıraya eklendi: {did}")
            isci.adim()
        except Exception as e:  # tek bir bozuk dosya döngüyü durdurmasın
            yaz(f"Hata: {e}")
        dur.wait(aralik)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="cs-klip tam otomatik akış")
    ap.add_argument("--ayarlar", type=Path, default=ROOT / "ayarlar.json")
    sub = ap.add_subparsers(dest="komut", required=True)
    p = sub.add_parser("izle", help="klasörleri izle, yeni demoları sırayla kaydet")
    p.add_argument("--aralik", type=float, default=ARALIK_SN, help="tarama aralığı (sn)")
    p.add_argument("--faceit-dk", type=float, default=0, help="N dakikada bir FACEIT'ten yeni maç demosu indir")
    p.add_argument("--temizle", action="store_true", help="kaydı biten demoyu Geri Dönüşüm Kutusu'na taşı")
    p.add_argument("--mevcutlari-da", action="store_true", help="ilk çalışmada klasörde duran demoları da sıraya al")
    sub.add_parser("durum", help="sırayı göster")
    p = sub.add_parser("ekle", help="demoyu elle sıraya ekle")
    p.add_argument("demo", type=Path)
    p = sub.add_parser("faceit", help="FACEIT'ten son maç demolarını şimdi indir")
    p.add_argument("--adet", type=int, default=5)
    args = ap.parse_args()
    cfg = load_config(args.ayarlar)

    if args.komut == "izle":
        try:
            calistir(cfg, args.ayarlar, args.aralik, args.faceit_dk, args.temizle, args.mevcutlari_da)
        except KeyboardInterrupt:
            pass
    elif args.komut == "durum":
        o = ozet()
        print(("Çalışıyor: " + o["durum"]) if o["calisiyor"] else "İzleyici çalışmıyor.")
        for i in o["kuyruk"]:
            print(f"  {i['durum']:<13} {i['id']}  {i['mesaj'] or ''}")
    elif args.komut == "ekle":
        if not args.demo.is_file() or not args.demo.name.lower().endswith(DEMO_SUFFIXES):
            raise SystemExit(f"Demo dosyası değil: {args.demo}")
        print("Sıraya eklendi." if Kuyruk().ekle(args.demo.resolve(), "elle") else "Zaten sırada.")
    elif args.komut == "faceit":
        import faceit

        try:
            got = faceit_yokla(Kuyruk(), cfg, izlenen_klasorler(cfg)[0], args.adet)
        except faceit.FaceitHatasi as e:
            raise SystemExit(str(e))
        print(f"{len(got)} demo indirildi." + (" İzleyici çalışıyorsa sıraya kendisi alır." if got else ""))


if __name__ == "__main__":
    main()
