"""kurulum.py: sahte bir "yeni bilgisayar" üzerinde. Gerçek winget/PostgreSQL/CSDM'e dokunulmaz."""

import base64
import hashlib
import io
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

import kontrol
import kurulum

ROOT = Path(__file__).resolve().parent
PINS = ["demoparser2==0.42.1", "pytest==9.2.0"]


class Makine:
    """Kurulu programların durumu + komutları taklit eden çalıştırıcı."""

    def __init__(self, tmp: Path, ffmpeg=False, pg=False, csdm=True):
        self.tmp = tmp
        self.ffmpeg, self.pg, self.csdm = ffmpeg, pg, csdm
        self.paketler = False
        self.calisiyor = False
        self.db_var = False
        self.komutlar: list[list[str]] = []
        self.parola = None
        self.pg_dir = tmp / "pg" / "17" / "bin"

    def kur_pg(self):
        self.pg_dir.mkdir(parents=True, exist_ok=True)
        for t in kurulum.PG_TOOLS:
            (self.pg_dir / t).write_bytes(b"")
        self.pg = True

    def __call__(self, cmd, **kw):
        self.komutlar.append(cmd)
        exe = Path(cmd[0]).name.lower()
        out, code = "", 0
        if cmd[1:3] == ["-m", "venv"]:
            py = Path(cmd[3]) / "Scripts" / "python.exe"
            py.parent.mkdir(parents=True)
            py.write_bytes(b"")
        elif cmd[1:3] == ["-m", "pip"]:
            self.paketler = True
        elif cmd[1] == "-c":  # paket sürüm yoklaması
            out = "" if self.paketler else "\n".join(cmd[3:])
        elif cmd[1:3] == ["-m", "pytest"]:
            pass
        elif exe == "winget":
            paket = cmd[cmd.index("--id") + 1]
            if paket == kurulum.FFMPEG_WINGET:
                self.ffmpeg = True
            elif paket == kurulum.PG_WINGET:
                self.kur_pg()
        elif exe == "initdb.exe":
            assert "--locale=C" in cmd
            self.parola = Path(cmd[cmd.index("--pwfile") + 1]).read_text(encoding="utf-8").strip()
            data = Path(cmd[cmd.index("-D") + 1])
            data.mkdir(parents=True)
            (data / "PG_VERSION").write_text("17", encoding="utf-8")
            (data / "postgresql.conf").write_text("#port = 5432\n", encoding="utf-8")
        elif exe == "pg_isready.exe":
            code = 0 if self.calisiyor else 2
        elif exe == "psql.exe":
            assert kw["env"]["PGPASSWORD"]
            out = "1" if self.db_var else ""
        elif exe == "createdb.exe":
            self.db_var = True
        else:
            raise AssertionError(f"beklenmeyen komut: {cmd}")
        return subprocess.CompletedProcess(cmd, code, out, "")

    def degistiren(self):
        """Durumu değiştiren komutlar (yoklamalar hariç)."""
        oku = {"pg_isready.exe", "psql.exe"}
        return [c for c in self.komutlar if Path(c[0]).name.lower() not in oku and c[1:2] != ["-c"]]


@pytest.fixture
def ortam(tmp_path, monkeypatch):
    root, home, lad = tmp_path / "cs-klip", tmp_path / "ev", tmp_path / "lad"
    for d in (root, home, lad):
        d.mkdir()
    (root / "requirements.txt").write_text("\n".join(PINS) + "\n", encoding="utf-8")
    shutil.copy(ROOT / "ayarlar.ornek.json", root / "ayarlar.ornek.json")
    m = Makine(tmp_path)
    ffmpeg = tmp_path / "ffmpeg.exe"
    ffmpeg.write_bytes(b"")
    csdm = tmp_path / "csdm.cmd"
    csdm.write_bytes(b"")
    monkeypatch.setattr(kontrol, "find_ffmpeg", lambda o="": ffmpeg if m.ffmpeg else None)
    monkeypatch.setattr(kontrol, "find_csdm", lambda o="": csdm if m.csdm else None)
    monkeypatch.setattr(kontrol, "find_pg_bin", lambda: m.pg_dir if m.pg else None)
    monkeypatch.setattr(kontrol, "PG_ROOT", tmp_path / "pg")

    def start_pg(pg_bin, data):
        m.komutlar.append(["pg_ctl.exe", "start", str(data)])
        m.calisiyor = (data / "PG_VERSION").is_file()
        return m.calisiyor
    monkeypatch.setattr(kontrol, "start_pg", start_pg)
    monkeypatch.setattr(kurulum.shutil, "which", lambda name: "winget.exe" if name == "winget" else None)
    monkeypatch.setattr(kurulum, "port_in_use", lambda port, host="": False)
    path = {"girdiler": [r"C:\Windows"], "yazilan": None}
    monkeypatch.setattr(kurulum, "user_path_entries", lambda: list(path["girdiler"]))
    monkeypatch.setattr(kurulum, "set_user_path", lambda e: path.update(yazilan=e, girdiler=e))
    monkeypatch.setenv("PATH", r"C:\Windows")

    def yeni(**kw):
        return kurulum.Kurulum(root=root, home=home, localappdata=lad, runner=m, sor=lambda _: "", **kw)
    return {"root": root, "home": home, "lad": lad, "m": m, "yeni": yeni, "path": path, "ffmpeg": ffmpeg}


def dosyalar(*klasorler):
    return sorted(p for d in klasorler for p in Path(d).rglob("*"))


def test_prova_changes_nothing_on_fresh_machine(ortam, capsys):
    m = ortam["m"]
    m.csdm = False
    once = dosyalar(ortam["root"], ortam["home"], ortam["lad"])
    assert ortam["yeni"](prova=True, oyuncu="ben").calis() == 0
    assert dosyalar(ortam["root"], ortam["home"], ortam["lad"]) == once
    assert m.komutlar == []  # hiçbir şey çalıştırılmadı (yoklanacak program da yok)
    assert ortam["path"]["yazilan"] is None
    out = capsys.readouterr().out
    for parca in ("-m venv", "winget install --id Gyan.FFmpeg", f"--id {kurulum.PG_WINGET}", "--extract-only 1",
                  "--locale=C", "github.com/repos/akiver/cs-demo-manager", "yazılacak:", "settings.json"):
        assert parca in out, parca


def test_fresh_install_then_rerun_is_noop(ortam, capsys):
    m, root, home = ortam["m"], ortam["root"], ortam["home"]
    assert ortam["yeni"](oyuncu="Arkadas").calis() == 0

    assert json.loads((root / "ayarlar.json").read_text(encoding="utf-8"))["oyuncu"] == "Arkadas"
    data = ortam["lad"] / "csdm-pg" / "data"
    assert (data / "PG_VERSION").is_file() and m.calisiyor and m.db_var
    s = json.loads((home / ".csdm" / "settings.json").read_text(encoding="utf-8"))
    sablon = json.loads(kurulum.TEMPLATE.read_text(encoding="utf-8"))
    assert set(s) == set(sablon) and s["schemaVersion"] == sablon["schemaVersion"]
    assert s["database"] == {"hostname": "127.0.0.1", "port": 5432, "username": "postgres",
                             "password": m.parola, "database": "csdm"}
    assert len(m.parola) >= 20
    assert s["video"]["ffmpegSettings"]["customLocationEnabled"] is True
    assert s["video"]["ffmpegSettings"]["customExecutableLocation"] == str(ortam["ffmpeg"])
    assert ortam["path"]["yazilan"] == [r"C:\Windows", str(m.pg_dir)]
    assert not list(Path(kurulum.tempfile.gettempdir()).glob("csklip-pg-*"))  # şifre dosyası silindi
    adlar = [Path(c[0]).name.lower() for c in m.degistiren()]
    assert adlar.count("winget") == 2 and "initdb.exe" in adlar and "createdb.exe" in adlar

    # ikinci çalıştırma: her şey kurulu, hiçbir şey değişmez
    capsys.readouterr()
    m.komutlar.clear()
    once = (home / ".csdm" / "settings.json").read_bytes()
    ortam["path"]["yazilan"] = None
    assert ortam["yeni"]().calis() == 0
    assert [c for c in m.degistiren() if c[1:3] != ["-m", "pytest"]] == []
    assert (home / ".csdm" / "settings.json").read_bytes() == once
    assert not (home / ".csdm" / "settings.json.yedek").exists()
    assert ortam["path"]["yazilan"] is None
    out = capsys.readouterr().out
    assert "→" not in out.replace("→ pytest", "")


def test_existing_csdm_settings_are_completed_not_replaced(ortam):
    m, home = ortam["m"], ortam["home"]
    m.ffmpeg = True
    m.kur_pg()
    f = home / ".csdm" / "settings.json"
    f.parent.mkdir()
    f.write_text(json.dumps({"schemaVersion": 13, "ui": {"locale": "en"},
                             "database": {"hostname": "127.0.0.1", "port": 5432, "username": "postgres",
                                          "password": "", "database": "csdm"}}), encoding="utf-8")
    assert ortam["yeni"](oyuncu="x", testler=False).calis() == 0
    s = json.loads(f.read_text(encoding="utf-8"))
    assert s["ui"]["locale"] == "en"  # kullanıcının ayarı korunur
    assert s["ui"]["theme"] == "dark" and "playback" in s  # eksikler şablondan
    assert s["database"]["password"] == m.parola
    assert json.loads((home / ".csdm" / "settings.json.yedek").read_text(encoding="utf-8"))["ui"] == {"locale": "en"}


def test_existing_cluster_password_from_csdm_settings(ortam):
    m, home, lad = ortam["m"], ortam["home"], ortam["lad"]
    m.ffmpeg = True
    m.kur_pg()
    data = lad / "csdm-pg" / "data"
    data.mkdir(parents=True)
    (data / "PG_VERSION").write_text("17", encoding="utf-8")
    (data / "postgresql.conf").write_text("port = 5433\n", encoding="utf-8")
    assert ortam["yeni"](oyuncu="x", testler=False).calis() == 1  # şifre bilinmiyor
    assert not (home / ".csdm" / "settings.json").exists()
    assert not any(Path(c[0]).name == "initdb.exe" for c in m.komutlar)

    f = home / ".csdm" / "settings.json"
    f.parent.mkdir()
    f.write_text(json.dumps({"database": {"password": "gizli"}}), encoding="utf-8")
    m.komutlar.clear()
    assert ortam["yeni"](testler=False).calis() == 0
    s = json.loads(f.read_text(encoding="utf-8"))
    assert s["database"]["password"] == "gizli" and s["database"]["port"] == 5433  # port postgresql.conf'tan


def test_busy_port_moves_new_cluster(ortam, monkeypatch):
    m = ortam["m"]
    m.ffmpeg = True
    m.kur_pg()
    monkeypatch.setattr(kurulum, "port_in_use", lambda port, host="": port == 5432)
    assert ortam["yeni"](oyuncu="x", testler=False).calis() == 0
    data = ortam["lad"] / "csdm-pg" / "data"
    assert kurulum.conf_port(data) == 5433
    s = json.loads((ortam["home"] / ".csdm" / "settings.json").read_text(encoding="utf-8"))
    assert s["database"]["port"] == 5433


def test_missing_winget_reports_and_continues(ortam, monkeypatch):
    monkeypatch.setattr(kurulum.shutil, "which", lambda name: None)
    m = ortam["m"]
    m.kur_pg()
    k = ortam["yeni"](oyuncu="x", testler=False)
    assert k.calis() == 1
    assert len(k.sorunlar) == 1 and "winget" in k.sorunlar[0]  # yalnız FFmpeg; diğer adımlar sürdü
    assert m.db_var


def test_csdm_download_checks_hash(ortam, monkeypatch):
    m = ortam["m"]
    m.csdm = False
    kurucu = b"kurucu"
    sha = base64.b64encode(hashlib.sha512(kurucu).digest()).decode()
    name = "CS-Demo-Manager-Setup-3.20.1.exe"
    yml = {"dogru": f"files:\n  - url: {name}\n    sha512: {sha}\n    size: 6\n",
           "yanlis": f"files:\n  - url: {name}\n    sha512: AAAA\n    size: 6\n"}
    secim = {"yml": "yanlis"}

    class Yanit(io.BytesIO):
        headers = {}

        def __enter__(self):
            return self

    def urlopen(req, timeout=0):
        url = req.full_url
        if url == kurulum.CSDM_RELEASE:
            return Yanit(json.dumps({"tag_name": "v3.20.1", "assets": [
                {"name": name, "browser_download_url": "https://x/setup.exe"},
                {"name": "latest.yml", "browser_download_url": "https://x/latest.yml"}]}).encode())
        if url.endswith("latest.yml"):
            return Yanit(yml[secim["yml"]].encode())
        return Yanit(kurucu)
    monkeypatch.setattr(kurulum.urllib.request, "urlopen", urlopen)

    k = ortam["yeni"]()
    with pytest.raises(kurulum.KurulumHatasi, match="özeti"):
        k.csdm_kur()
    assert m.komutlar == []

    secim["yml"] = "dogru"
    m.komutlar.clear()
    orijinal = m.__call__

    def kur(cmd, **kw):
        if Path(cmd[0]).name == name:
            m.csdm = True
            assert cmd[1] == "/S"
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return orijinal(cmd, **kw)
    k.runner = kur
    k.csdm_kur()
    assert m.csdm


def test_helpers():
    assert kurulum.sha512_from_latest_yml("files:\n  - url: a.exe\n    sha512: XYZ==\n", "a.exe") == "XYZ=="
    assert kurulum.sha512_from_latest_yml("files: []", "a.exe") is None
    dst = {"a": 1, "b": {"c": 2}}
    assert kurulum.fill_missing(dst, {"a": 9, "b": {"c": 9, "d": 3}, "e": [1]}) == ["b.d", "e"]
    assert dst == {"a": 1, "b": {"c": 2, "d": 3}, "e": [1]}
    if os.name == "nt":  # Windows yolları büyük/küçük harf duyarsız
        assert kurulum.same_path(r"C:\A\b\\", "c:/a/B")


def test_template_has_no_personal_data():
    s = kurulum.TEMPLATE.read_text(encoding="utf-8")
    d = json.loads(s)
    assert d["database"]["password"] == "" and d["steamApiKey"] == "" and d["faceitApiKey"] == ""
    assert "Users" not in s and d["video"]["playerVoicesEnabled"] is False
