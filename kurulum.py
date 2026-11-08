"""cs-klip kurulumu: yeni bir Windows bilgisayarda kayıt için gereken her şeyi hazırlar.

Kullanım:  python kurulum.py [--prova] [--oyuncu AD] [--test-yok]
kur.bat bunu çağırır. Yalnız standart kütüphane kullanır (sanal ortamdan önce çalışır).

Her adım önce durumu yoklar; zaten hazırsa atlar, bu yüzden tekrar tekrar çalıştırılabilir.
--prova hiçbir şeyi kurmaz, yazmaz, başlatmaz: yalnız ne yapılacağını söyler.

Adımlar: sanal ortam, paketler, ayarlar.json, FFmpeg, PostgreSQL programları, CS Demo Manager,
veritabanı klasörü (initdb --locale=C: Türkçe yerel ayarda kurucunun çökmesini aşar), veritabanını başlatma,
csdm veritabanı, CSDM ayarları (~/.csdm/settings.json), PATH, testler.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "araclar" / "csdm-settings.sablon.json"

FFMPEG_WINGET = "Gyan.FFmpeg"
PG_WINGET = "PostgreSQL.PostgreSQL.17"
# EDB kurucusu: yalnız dosyaları aç, hizmet ve veritabanı kurma (onu biz --locale=C ile yapıyoruz).
PG_OVERRIDE = "--mode unattended --unattendedmodeui none --extract-only 1 --disable-components pgAdmin,stackbuilder"
# winget olmazsa ya da kurucu dosyaları açamazsa: EDB'nin zip dağıtımı (yönetici izni gerekmez).
PG_ZIP_URL = "https://get.enterprisedb.com/postgresql/postgresql-17.11-5-windows-x64-binaries.zip"
PG_TOOLS = ("initdb.exe", "pg_ctl.exe", "pg_isready.exe", "psql.exe", "createdb.exe")
PG_PORT = 5432
CSDM_RELEASE = "https://api.github.com/repos/akiver/cs-demo-manager/releases/latest"
CSDM_ASSET = re.compile(r"^CS-Demo-Manager-Setup-[\d.]+\.exe$")
DB_NAME, DB_USER, DB_HOST = "csdm", "postgres", "127.0.0.1"
USER_AGENT = "cs-klip-kurulum"


class KurulumHatasi(Exception):
    """Adım tamamlanamadı; mesaj kullanıcıya ne yapacağını söyler."""


def same_path(a, b) -> bool:
    return os.path.normcase(os.path.normpath(str(a))) == os.path.normcase(os.path.normpath(str(b)))


def port_in_use(port: int, host: str = DB_HOST) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def conf_port(data_dir: Path) -> int | None:
    """postgresql.conf'taki port (yorum satırı değilse)."""
    try:
        text = (Path(data_dir) / "postgresql.conf").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    hits = re.findall(r"^\s*port\s*=\s*(\d+)", text, re.MULTILINE)
    return int(hits[-1]) if hits else None


def fill_missing(dst: dict, src: dict) -> list[str]:
    """src'de olup dst'de olmayan alanları ekler (var olanlara dokunmaz). Eklenen yollar döner."""
    added = []
    for k, v in src.items():
        if k not in dst:
            dst[k] = json.loads(json.dumps(v))
            added.append(k)
        elif isinstance(v, dict) and isinstance(dst[k], dict):
            added += [f"{k}.{x}" for x in fill_missing(dst[k], v)]
    return added


def sha512_from_latest_yml(text: str, name: str) -> str | None:
    """electron-builder latest.yml içinden dosyanın sha512'si (base64)."""
    m = re.search(rf"url:\s*{re.escape(name)}\s*\n\s*sha512:\s*(\S+)", text)
    return m.group(1) if m else None


def user_path_entries() -> list[str]:
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            value, _ = winreg.QueryValueEx(k, "Path")
    except OSError:
        return []
    return [p for p in str(value).split(";") if p]


def set_user_path(entries: list[str]) -> None:
    import ctypes
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, "Path", 0, winreg.REG_EXPAND_SZ, ";".join(entries))
    # açık programlara (Explorer) haber ver; yeni terminaller yeni PATH'i görür
    ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002, 3000, None)


class Kurulum:
    def __init__(self, prova: bool = False, root: Path = ROOT, home: Path | None = None,
                 localappdata: Path | None = None, oyuncu: str | None = None, testler: bool = True,
                 sor=input, runner=subprocess.run):
        import kontrol

        self.k = kontrol
        self.prova = prova
        self.root = Path(root)
        self.home = Path(home) if home else Path.home()
        self.lad = Path(localappdata) if localappdata else kontrol.local_appdata()
        self.oyuncu = oyuncu
        self.testler = testler
        self.sor = sor
        self.runner = runner
        self.venv_py = self.root / ".venv" / "Scripts" / "python.exe"
        self.ayarlar = self.root / "ayarlar.json"
        self.csdm_settings = self.home / ".csdm" / "settings.json"
        self.sorunlar: list[str] = []
        self.no = 0
        # adımlar arasında taşınan bilgiler
        self.ffmpeg: Path | None = None
        self.pg_bin: Path | None = None
        self.data_dir: Path | None = None
        self.db: dict = {}
        self.yeni_kume = False
        self.pg_tahmini = False  # provada PostgreSQL henüz kurulu değil: yolu varsayılır, komutlar çalıştırılmaz

    # --- çıktı ---
    def adim(self, baslik: str) -> None:
        self.no += 1
        print(f"\n[{self.no}] {baslik}")

    @staticmethod
    def tamam(msg: str) -> None:
        print(f"  ✓ {msg}")

    def yap(self, msg: str) -> None:
        print(f"  {'(prova) ' if self.prova else ''}→ {msg}")

    @staticmethod
    def uyari(msg: str) -> None:
        print(f"  ! {msg}")

    # --- yardımcılar ---
    def calistir(self, cmd: list, **kw) -> subprocess.CompletedProcess | None:
        """Değişiklik yapan komut: provada yalnız yazdırılır."""
        if self.prova:
            print("    $ " + subprocess.list2cmdline([str(c) for c in cmd]))
            return None
        return self.runner([str(c) for c in cmd], **kw)

    def yokla(self, cmd: list, **kw) -> subprocess.CompletedProcess:
        """Yalnız okuyan komut: provada da çalışır."""
        return self.runner([str(c) for c in cmd], capture_output=True, text=True, errors="replace", **kw)

    def yaz(self, path: Path, text: str, yedek: bool = False) -> None:
        if self.prova:
            print(f"    yazılacak: {path}")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        if yedek and path.exists():
            shutil.copy2(path, path.with_name(path.name + ".yedek"))
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)

    def winget(self, paket: str, *ek: str) -> None:
        if not shutil.which("winget"):
            raise KurulumHatasi("winget yok. Microsoft Store'dan \"Uygulama Yükleyici\"yi (App Installer) kur, "
                                "sonra kur.bat'ı yeniden çalıştır.")
        self.calistir(["winget", "install", "--id", paket, "-e", "--silent", "--accept-package-agreements",
                       "--accept-source-agreements", "--disable-interactivity", *ek])

    def indir(self, url: str, hedef: Path) -> None:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as r, open(hedef, "wb") as f:
            toplam = int(r.headers.get("Content-Length") or 0)
            inen, son = 0, -1
            while chunk := r.read(1 << 20):
                f.write(chunk)
                inen += len(chunk)
                if toplam and (yuzde := inen * 100 // toplam) // 10 != son:
                    son = yuzde // 10
                    print(f"    indiriliyor… %{yuzde} ({inen / 1024**2:.0f}/{toplam / 1024**2:.0f} MB)", flush=True)

    def cfg(self) -> dict:
        from config import load_config

        try:
            return load_config(self.ayarlar)
        except (SystemExit, ValueError) as e:
            raise KurulumHatasi(f"ayarlar.json okunamadı: {e}")

    def csdm_json(self) -> dict | None:
        try:
            return json.loads(self.csdm_settings.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None
        except (OSError, ValueError) as e:
            raise KurulumHatasi(f"{self.csdm_settings} bozuk ({e}). Dosyayı düzelt ya da silip kur.bat'ı yeniden çalıştır.")

    # --- adımlar ---
    def sanal_ortam(self) -> None:
        self.adim("Python sanal ortamı (.venv)")
        if sys.version_info < (3, 11):
            raise KurulumHatasi(f"Python {sys.version.split()[0]} eski; 3.11 ya da yenisi gerekli (winget install Python.Python.3.12).")
        if self.venv_py.is_file():
            self.tamam(f"Zaten var: {self.venv_py.parent.parent}")
            return
        self.yap("Sanal ortam oluşturuluyor")
        self.calistir([sys.executable, "-m", "venv", self.root / ".venv"], check=True)

    def paketler(self) -> None:
        self.adim("Python paketleri (requirements.txt)")
        req = self.root / "requirements.txt"
        pins = [ln.strip() for ln in req.read_text(encoding="utf-8").splitlines() if "==" in ln and not ln.startswith("#")]
        eksik = pins
        if self.venv_py.is_file():
            code = ("import sys, importlib.metadata as m\n"
                    "for p in sys.argv[1:]:\n"
                    "    n, v = p.split('==')\n"
                    "    try: ok = m.version(n) == v\n"
                    "    except m.PackageNotFoundError: ok = False\n"
                    "    ok or print(p)\n")
            r = self.yokla([self.venv_py, "-c", code, *pins])
            eksik = r.stdout.split() if r.returncode == 0 else pins
        if not eksik:
            self.tamam(f"{len(pins)} paket kurulu ve güncel")
            return
        self.yap(f"Kuruluyor: {', '.join(eksik)}")
        self.calistir([self.venv_py, "-m", "pip", "install", "-q", "--disable-pip-version-check", "-r", req], check=True)

    def ayar_dosyasi(self) -> None:
        self.adim("cs-klip ayarları (ayarlar.json)")
        if self.ayarlar.exists():
            self.tamam(f"Zaten var (oyuncu: {self.cfg()['oyuncu']}). Arayüzde Ayarlar sayfasından değiştirilebilir.")
            return
        data = json.loads((self.root / "ayarlar.ornek.json").read_text(encoding="utf-8"))
        ad = (self.oyuncu or "").strip()
        if not ad and not self.prova and sys.stdin and sys.stdin.isatty():
            ad = self.sor("  Demodaki oyuncu adın (boş bırakırsan sonra Ayarlar'dan girersin): ").strip()
        if ad:
            data["oyuncu"] = ad
        self.yap(f"ayarlar.json oluşturuluyor (oyuncu: {data['oyuncu']})")
        self.yaz(self.ayarlar, json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    def ffmpeg_kur(self) -> None:
        self.adim("FFmpeg")
        yol = self.cfg()["ffmpeg_yolu"]
        if found := self.k.find_ffmpeg(yol):
            self.ffmpeg = found
            self.tamam(f"Kurulu: {found}")
            return
        self.yap(f"winget ile kuruluyor ({FFMPEG_WINGET})")
        self.winget(FFMPEG_WINGET)
        if self.prova:
            return
        self.ffmpeg = self.k.find_ffmpeg(yol)
        if not self.ffmpeg:
            raise KurulumHatasi("FFmpeg kurulamadı. Elle: winget install Gyan.FFmpeg")
        self.tamam(f"Kuruldu: {self.ffmpeg}")

    def pg_bul(self) -> Path | None:
        b = self.k.find_pg_bin()
        return b if b and all((b / t).is_file() for t in PG_TOOLS) else None

    def postgresql_kur(self) -> None:
        self.adim("PostgreSQL programları")
        if b := self.pg_bul():
            self.pg_bin = b
            self.tamam(f"Kurulu: {b}")
            return
        hata = None
        if shutil.which("winget"):
            self.yap(f"winget ile kuruluyor ({PG_WINGET}); yalnız dosyalar açılır, Windows hizmeti kurulmaz. "
                     "Yönetici izni (UAC) sorulursa Evet de.")
            try:
                self.winget(PG_WINGET, "--override", PG_OVERRIDE)
            except (OSError, subprocess.SubprocessError) as e:
                hata = e
            if not self.prova and (b := self.pg_bul()):
                self.pg_bin = b
                self.tamam(f"Kuruldu: {b}")
                return
        # yedek yol: zip (yönetici izni gerekmez)
        hedef = self.lad / "csdm-pg"
        self.yap(f"winget kurulumu {'olmadı' if not self.prova else 'olmazsa'}: zip dağıtımı {hedef / 'pgsql'} içine açılıyor")
        if self.prova:
            print(f"    indirilecek: {PG_ZIP_URL}")
            self.pg_bin, self.pg_tahmini = self.k.PG_ROOT / "17" / "bin", True
            return
        hedef.mkdir(parents=True, exist_ok=True)
        zip_yolu = Path(tempfile.gettempdir()) / "cs-klip-postgresql.zip"
        try:
            self.indir(PG_ZIP_URL, zip_yolu)
            with zipfile.ZipFile(zip_yolu) as z:
                uyeler = [m for m in z.namelist() if m.startswith("pgsql/")
                          and not m.startswith(("pgsql/pgAdmin", "pgsql/StackBuilder", "pgsql/doc/"))]
                z.extractall(hedef, uyeler)
        except (OSError, zipfile.BadZipFile) as e:
            raise KurulumHatasi(f"PostgreSQL indirilemedi ({hata or e}). Elle: winget install {PG_WINGET}")
        finally:
            zip_yolu.unlink(missing_ok=True)
        self.pg_bin = self.pg_bul()
        if not self.pg_bin:
            raise KurulumHatasi("PostgreSQL dosyaları açıldı ama programlar bulunamadı.")
        self.tamam(f"Kuruldu: {self.pg_bin}")

    def csdm_kur(self) -> None:
        self.adim("CS Demo Manager")
        yol = self.cfg()["csdm_yolu"]
        if found := self.k.find_csdm(yol):
            self.tamam(f"Kurulu: {found}")
            return
        self.yap("GitHub'dan son sürüm indirilip sessiz kuruluyor (akiver/cs-demo-manager)")
        if self.prova:
            print(f"    sürüm bilgisi: {CSDM_RELEASE}")
            return
        try:
            req = urllib.request.Request(CSDM_RELEASE, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                rel = json.load(r)
            assets = {a["name"]: a["browser_download_url"] for a in rel["assets"]}
            name = next(n for n in assets if CSDM_ASSET.match(n))
            yml_req = urllib.request.Request(assets["latest.yml"], headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(yml_req, timeout=30) as r:
                beklenen = sha512_from_latest_yml(r.read().decode("utf-8", "replace"), name)
        except (OSError, ValueError, KeyError, StopIteration) as e:
            raise KurulumHatasi(f"CS Demo Manager sürüm bilgisi alınamadı ({e}). "
                                "Elle kur: github.com/akiver/cs-demo-manager/releases")
        kurucu = Path(tempfile.gettempdir()) / name
        print(f"    {rel.get('tag_name', '')} indiriliyor: {name}")
        try:
            self.indir(assets[name], kurucu)
            gercek = base64.b64encode(hashlib.sha512(kurucu.read_bytes()).digest()).decode()
            if not beklenen or gercek != beklenen:
                raise KurulumHatasi("CS Demo Manager kurucusunun özeti tutmadı (indirme bozuk olabilir); tekrar dene.")
            self.yap("Kuruluyor (sessiz, yalnız bu kullanıcı için)")
            self.calistir([kurucu, "/S"], check=False)
        except OSError as e:
            raise KurulumHatasi(f"CS Demo Manager indirilemedi/kurulamadı: {e}")
        finally:
            kurucu.unlink(missing_ok=True)
        if not self.k.find_csdm(yol):
            raise KurulumHatasi("CS Demo Manager kuruldu ama csdm.cmd bulunamadı. "
                                "Başka klasöre kurduysan ayarlar.json → csdm_yolu.")
        self.tamam("Kuruldu")

    def varsayilan_veri(self) -> Path:
        d = self.lad / "csdm-pg" / "data"
        # PostgreSQL Windows'ta ASCII dışı (ör. "Ömer") kullanıcı klasörlerinde sorun çıkarabilir
        return d if str(d).isascii() else Path(os.environ.get("SystemDrive", "C:") + "\\") / "csdm-pg" / "data"

    def veritabani_klasoru(self) -> None:
        self.adim("Veritabanı klasörü (initdb --locale=C)")
        cfg = self.cfg()
        self.data_dir = Path(cfg["pg_veri_klasoru"]) if cfg["pg_veri_klasoru"] else self.varsayilan_veri()
        mevcut = (self.csdm_json() or {}).get("database") or {}
        self.db = {"hostname": mevcut.get("hostname") or DB_HOST, "username": mevcut.get("username") or DB_USER,
                   "database": mevcut.get("database") or DB_NAME, "password": str(mevcut.get("password") or "")}
        if (self.data_dir / "PG_VERSION").is_file():
            self.db["port"] = int(mevcut.get("port") or conf_port(self.data_dir) or PG_PORT)
            self.tamam(f"Zaten var: {self.data_dir} (port {self.db['port']})")
            if not self.db["password"]:
                raise KurulumHatasi(
                    f"Veritabanı var ama şifresi CSDM ayarlarında yok ({self.csdm_settings} → database.password). "
                    "Şifreyi oraya yaz; bilmiyorsan veri klasörünü silip kur.bat'ı yeniden çalıştır.")
            return
        if not self.pg_bin:
            raise KurulumHatasi("PostgreSQL programları olmadan veritabanı açılamaz (önceki adıma bak).")
        port = PG_PORT
        while port_in_use(port) and port < PG_PORT + 20:  # başka bir PostgreSQL 5432'yi tutuyor olabilir
            port += 1
        self.db["port"] = port
        if not self.db["password"]:
            self.db["password"] = secrets.token_urlsafe(18)
        self.yeni_kume = True
        self.yap(f"Yeni veritabanı: {self.data_dir} (UTF8, yerel ayar C, port {port})")
        if port != PG_PORT:
            self.uyari(f"{PG_PORT} portu dolu (başka bir PostgreSQL çalışıyor olabilir); {port} kullanılacak.")
        cmd = [self.pg_bin / "initdb.exe", "-D", self.data_dir, "-U", self.db["username"], "--auth=scram-sha-256",
               "--encoding=UTF8", "--locale=C", "--lc-messages=C"]
        if self.prova:
            self.calistir([*cmd, "--pwfile", "<geçici şifre dosyası>"])
            return
        self.data_dir.parent.mkdir(parents=True, exist_ok=True)
        fd, pw = tempfile.mkstemp(prefix="csklip-pg-", suffix=".txt")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(self.db["password"] + "\n")
            # Türkçe sistem dili (Turkish_Türkiye.1254) initdb'yi düşürüyor: ortamı da C yap
            env = dict(os.environ, LC_ALL="C", LANG="C", LC_MESSAGES="C")
            r = self.calistir([*cmd, "--pwfile", pw], capture_output=True, text=True, errors="replace", env=env)
        finally:
            os.unlink(pw)
        if r.returncode != 0:
            raise KurulumHatasi("initdb başarısız:\n    " + (r.stderr or r.stdout).strip().replace("\n", "\n    "))
        if port != PG_PORT:
            with open(self.data_dir / "postgresql.conf", "a", encoding="utf-8") as f:
                f.write(f"\n# cs-klip kurulumu\nport = {port}\n")
        if not same_path(self.data_dir, self.lad / "csdm-pg" / "data") and not cfg["pg_veri_klasoru"]:
            from config import save_config

            save_config(self.ayarlar, {"pg_veri_klasoru": str(self.data_dir)})  # kontrol.py bulsun
        self.tamam("Veritabanı klasörü açıldı")

    def pg_hazir(self) -> bool:
        if self.pg_tahmini:
            return False
        r = self.yokla([self.pg_bin / "pg_isready.exe", "-h", self.db["hostname"], "-p", self.db["port"]])
        return r.returncode == 0

    def veritabani_baslat(self) -> None:
        self.adim("PostgreSQL'i başlatma")
        if not self.pg_bin or not self.db:
            raise KurulumHatasi("Önceki adımlar tamamlanmadı.")
        if self.pg_hazir():
            self.tamam(f"Çalışıyor ({self.db['hostname']}:{self.db['port']})")
            return
        self.yap("Başlatılıyor (pg_ctl; Windows hizmeti değil, kapalıysa klip.bat kendisi başlatır)")
        if self.prova:
            print(f"    $ pg_ctl -D {self.data_dir} -l {self.data_dir.parent / 'log.txt'} -w start")
            return
        if not self.k.start_pg(self.pg_bin, self.data_dir) or not self.pg_hazir():
            raise KurulumHatasi(f"PostgreSQL başlatılamadı. Günlük: {self.data_dir.parent / 'log.txt'}")
        self.tamam("Başlatıldı")

    def psql_env(self) -> dict:
        return self.k.pg_env(self.pg_bin, self.db)

    def veritabani_olustur(self) -> None:
        self.adim(f"CSDM veritabanı ({self.db.get('database', DB_NAME)})")
        if self.prova and not self.pg_hazir():
            self.yap(f"Veritabanı çalışınca yoksa oluşturulacak (createdb {self.db['database']})")
            return
        conn = ["-h", self.db["hostname"], "-p", self.db["port"], "-U", self.db["username"]]
        name = self.db["database"].replace("'", "''")
        r = self.yokla([self.pg_bin / "psql.exe", *conn, "-d", "postgres", "-tAc",
                        f"select 1 from pg_database where datname = '{name}'"], env=self.psql_env())
        if r.returncode != 0:
            raise KurulumHatasi("Veritabanına bağlanılamadı (şifre CSDM ayarlarındakiyle aynı mı?): " + r.stderr.strip())
        if r.stdout.strip() == "1":
            self.tamam("Zaten var")
            return
        self.yap("Oluşturuluyor; tabloları CS Demo Manager ilk bağlantıda kendisi kurar")
        r = self.calistir([self.pg_bin / "createdb.exe", *conn, self.db["database"]],
                          env=self.psql_env(), capture_output=True, text=True, errors="replace")
        if r is not None and r.returncode != 0:
            raise KurulumHatasi("createdb başarısız: " + (r.stderr or r.stdout).strip())

    def csdm_ayarlari(self) -> None:
        self.adim(f"CS Demo Manager ayarları ({self.csdm_settings})")
        template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        mevcut = self.csdm_json()
        data = mevcut if mevcut is not None else json.loads(json.dumps(template))
        degisen = []
        if mevcut is not None and mevcut.get("schemaVersion", 0) <= template["schemaVersion"]:
            # eski kurulumların eksik alanları (yeni sürümün şemasında alan adları değişmiş olabilir: dokunma)
            degisen += [f"eksik alan: {a}" for a in fill_missing(data, template)]
        db = data.setdefault("database", {})
        for k in ("hostname", "port", "username", "database"):
            if self.db.get(k) is not None and db.get(k) != self.db[k]:
                db[k] = self.db[k]
                degisen.append(f"database.{k}")
        if self.db.get("password") and db.get("password") != self.db["password"]:
            db["password"] = self.db["password"]  # CSDM şifreyi düz metin ister
            degisen.append("database.password")
        ff = data.setdefault("video", {}).setdefault("ffmpegSettings", {})
        ffmpeg = self.ffmpeg or self.k.find_ffmpeg(self.cfg()["ffmpeg_yolu"])
        if ffmpeg and not (ff.get("customLocationEnabled") and Path(str(ff.get("customExecutableLocation", ""))).is_file()):
            ff.update(customLocationEnabled=True, customExecutableLocation=str(ffmpeg))
            degisen.append("video.ffmpegSettings (ffmpeg yolu)")
        if mevcut is not None and not degisen:
            self.tamam("Doğru: veritabanı bağlantısı ve ffmpeg yolu ayarlı")
            return
        self.yap(("Oluşturuluyor" if mevcut is None else "Güncelleniyor: " + ", ".join(degisen)))
        if mevcut is not None:
            print(f"    eski dosya yedeklenir: {self.csdm_settings.name}.yedek")
        self.yaz(self.csdm_settings, json.dumps(data, ensure_ascii=False, indent=2), yedek=True)

    def path_ayari(self) -> None:
        self.adim("PATH (psql)")
        if not self.pg_bin:
            raise KurulumHatasi("PostgreSQL programları yok.")
        entries = user_path_entries()
        if any(same_path(os.path.expandvars(e), self.pg_bin) for e in entries) or \
                any(same_path(e, self.pg_bin) for e in os.environ.get("PATH", "").split(os.pathsep) if e):
            self.tamam(f"Zaten PATH'te: {self.pg_bin}")
            return
        self.yap(f"Kullanıcı PATH'ine ekleniyor: {self.pg_bin} (yeni açılan terminallerde geçerli)")
        if not self.prova:
            set_user_path(entries + [str(self.pg_bin)])

    def testleri_calistir(self) -> None:
        self.adim("Testler")
        if not self.testler:
            self.tamam("Atlandı (--test-yok)")
            return
        self.yap("pytest çalışıyor")
        r = self.calistir([self.venv_py, "-m", "pytest", "-q"], cwd=self.root)
        if r is not None and r.returncode != 0:
            raise KurulumHatasi("Testler geçmedi. Çıktıyı geliştiriciye gönder.")

    ADIMLAR = ("sanal_ortam", "paketler", "ayar_dosyasi", "ffmpeg_kur", "postgresql_kur", "csdm_kur",
               "veritabani_klasoru", "veritabani_baslat", "veritabani_olustur", "csdm_ayarlari", "path_ayari",
               "testleri_calistir")
    # bu adımlar başarısız olursa sonrakiler anlamsız
    ZORUNLU = {"sanal_ortam", "paketler"}
    PG_ADIMLARI = {"veritabani_baslat", "veritabani_olustur", "csdm_ayarlari"}
    ATLANAN = {"veritabani_baslat": "PostgreSQL'i başlatma", "veritabani_olustur": "CSDM veritabanı",
               "csdm_ayarlari": "CS Demo Manager ayarları"}

    def calis(self) -> int:
        print("cs-klip kurulumu" + (" — PROVA: hiçbir şey değiştirilmeyecek" if self.prova else ""))
        pg_bozuk = False
        for ad in self.ADIMLAR:
            if ad in self.PG_ADIMLARI and pg_bozuk:
                self.adim(self.ATLANAN[ad])
                self.uyari("Atlandı: önceki veritabanı adımı tamamlanmadı.")
                continue
            try:
                getattr(self, ad)()
            except (KurulumHatasi, subprocess.CalledProcessError, OSError) as e:
                msg = str(e) if isinstance(e, KurulumHatasi) else f"{type(e).__name__}: {e}"
                print(f"  ✗ {msg}")
                self.sorunlar.append(msg)
                if ad in self.ZORUNLU:
                    break
                if ad in ("postgresql_kur", "veritabani_klasoru"):
                    pg_bozuk = True
        print()
        if self.sorunlar:
            print(f"Kurulum {len(self.sorunlar)} sorunla bitti:")
            for s in self.sorunlar:
                print(f"  - {s.splitlines()[0]}")
            print("Sorunu düzeltip kur.bat'ı yeniden çalıştır; tamamlanan adımlar atlanır.")
            return 1
        if self.prova:
            print("Prova bitti. Gerçek kurulum için: kur.bat")
        else:
            print("Kurulum tamam.\n  Arayüz: arayuz.bat   ·   Kayıt öncesi kontrol: klip.bat --kontrol\n"
                  "  Kayıttan önce FACEIT'ten çık ve CS2'yi kapat.")
        return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="cs-klip kurulumu (tekrar çalıştırılabilir)")
    ap.add_argument("--prova", action="store_true", help="hiçbir şeyi değiştirme, yalnız ne yapılacağını yaz")
    ap.add_argument("--oyuncu", help="ayarlar.json yoksa oyuncu adı (sorulmaz)")
    ap.add_argument("--test-yok", action="store_true", help="sondaki testleri çalıştırma")
    args = ap.parse_args()
    if os.name != "nt":
        print("cs-klip yalnız Windows'ta çalışır.")
        return 1
    return Kurulum(prova=args.prova, oyuncu=args.oyuncu, testler=not args.test_yok).calis()


if __name__ == "__main__":
    sys.exit(main())
