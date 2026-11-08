"""Kayıt öncesi kontroller: araçlar kurulu mu, veritabanı çalışıyor mu, engel olan program var mı.

Hiçbir programı kapatmaz; yalnız sorunu söyler. Kapalı PostgreSQL'i başlatmayı dener.
"""

import csv
import json
import os
import shutil
import subprocess
from pathlib import Path

MIN_FREE_GB = 10  # CS2 kareleri kayıt sırasında TGA olarak diske yazılır
BLOCKERS = {
    "faceitclient.exe": "FACEIT açık",
    "faceitservice.exe": "FACEIT Anti-Cheat hizmeti çalışıyor",
    "cs2.exe": "CS2 açık",
}
BLOCKER_HINT = {
    "faceitclient.exe": "FACEIT açıkken CS2 demo kaydı için başlatılamaz. FACEIT'ten çık (sistem tepsisi → Quit).",
    "faceitservice.exe": "FACEIT'ten tamamen çıkınca hizmet de durur.",
    "cs2.exe": "Kayıt CS2'yi kendisi açıp kapatır. Oyunu kapatıp tekrar dene.",
}


def local_appdata() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))


def running_processes() -> set[str]:
    """Çalışan programların küçük harfli adları (Windows tasklist)."""
    try:
        out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True,
                             encoding="mbcs", errors="replace", check=True).stdout
    except (OSError, subprocess.CalledProcessError, LookupError):
        return set()
    return {row[0].lower() for row in csv.reader(out.splitlines()) if row}


def blocking_programs(procs: set[str]) -> list[str]:
    return [name for name in BLOCKERS if name in procs]


def find_csdm(override: str = "") -> Path | None:
    candidates = [Path(override)] if override else []
    candidates.append(local_appdata() / "Programs" / "cs-demo-manager" / "csdm.cmd")
    return next((p for p in candidates if p.is_file()), None)


def find_ffmpeg(override: str = "") -> Path | None:
    if override:
        return Path(override) if Path(override).is_file() else None
    if found := shutil.which("ffmpeg"):
        return Path(found)
    # winget yeni terminal açılana kadar PATH'e eklenmez
    pkgs = local_appdata() / "Microsoft" / "WinGet" / "Packages"
    hits = sorted(pkgs.glob("Gyan.FFmpeg*/*/bin/ffmpeg.exe")) if pkgs.is_dir() else []
    return hits[-1] if hits else None


def find_pg_bin() -> Path | None:
    hits = sorted(Path(r"C:\Program Files\PostgreSQL").glob("*/bin/pg_isready.exe"),
                  key=lambda p: int(p.parent.parent.name) if p.parent.parent.name.isdigit() else 0)
    return hits[-1].parent if hits else None


def csdm_database() -> dict | None:
    """CSDM'in veritabanı bağlantısı (~/.csdm/settings.json)."""
    f = Path.home() / ".csdm" / "settings.json"
    try:
        return json.loads(f.read_text(encoding="utf-8"))["database"]
    except (OSError, ValueError, KeyError):
        return None


def pg_env(pg_bin: Path | None, db: dict | None) -> dict:
    """csdm ve psql için ortam: psql PATH'te, şifre PGPASSWORD'de."""
    env = dict(os.environ)
    if pg_bin:
        env["PATH"] = f"{pg_bin}{os.pathsep}{env.get('PATH', '')}"
    if db and db.get("password"):
        env["PGPASSWORD"] = str(db["password"])
    return env


def pg_ready(pg_bin: Path, db: dict) -> bool:
    r = subprocess.run([str(pg_bin / "pg_isready.exe"), "-h", db["hostname"], "-p", str(db["port"])],
                       capture_output=True)
    return r.returncode == 0


def start_pg(pg_bin: Path, data_dir: Path) -> bool:
    if not (data_dir / "PG_VERSION").is_file():
        return False
    # Çıktı borusu yakalanmaz: başlayan postgres süreci boruyu miras alıp açık tutar, run() hiç dönmez.
    r = subprocess.run([str(pg_bin / "pg_ctl.exe"), "-D", str(data_dir), "-l", str(data_dir.parent / "log.txt"),
                        "-w", "-t", "30", "start"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))
    return r.returncode == 0


def demo_in_db(pg_bin: Path, db: dict, demo: Path, env: dict) -> bool:
    """Demo CSDM'e daha önce eklenmiş mi (yeniden analiz etmemek için)."""
    path = str(demo).replace("'", "''")
    r = subprocess.run(
        [str(pg_bin / "psql.exe"), "-h", db["hostname"], "-p", str(db["port"]), "-U", db["username"],
         "-d", db["database"], "-tAc", f"select 1 from matches where demo_path = '{path}' limit 1"],
        capture_output=True, text=True, env=env,
    )
    return r.returncode == 0 and r.stdout.strip() == "1"


def free_gb(path: Path) -> float:
    return shutil.disk_usage(path).free / 1024**3


def preflight(cfg: dict, csgo_dir: Path | None, procs: set[str] | None = None) -> tuple[dict, list[str]]:
    """(araçlar, sorunlar) döner. Sorun listesi boşsa kayıt başlayabilir."""
    problems: list[str] = []
    tools = {
        "csdm": find_csdm(cfg["csdm_yolu"]),
        "ffmpeg": find_ffmpeg(cfg["ffmpeg_yolu"]),
        "pg_bin": find_pg_bin(),
        "db": csdm_database(),
    }
    if tools["csdm"] is None:
        problems.append("CS Demo Manager bulunamadı. Kur: github.com/akiver/cs-demo-manager/releases "
                        "(ya da ayarlar.json → csdm_yolu).")
    if tools["ffmpeg"] is None:
        problems.append("ffmpeg bulunamadı: winget install Gyan.FFmpeg")
    if tools["pg_bin"] is None:
        problems.append("PostgreSQL bulunamadı (CSDM'in veritabanı). YAPILACAKLAR.md → PostgreSQL.")
    elif tools["db"] is None:
        problems.append("CSDM ayarları yok (~/.csdm/settings.json). CS Demo Manager'ı bir kez açıp kapat.")
    elif not pg_ready(tools["pg_bin"], tools["db"]):
        data = Path(cfg["pg_veri_klasoru"]) if cfg["pg_veri_klasoru"] else local_appdata() / "csdm-pg" / "data"
        if start_pg(tools["pg_bin"], data):
            print(f"PostgreSQL başlatıldı ({data}).")
        else:
            problems.append(f"PostgreSQL çalışmıyor ve başlatılamadı ({data}).")

    for name in blocking_programs(running_processes() if procs is None else procs):
        problems.append(f"{BLOCKERS[name]}. {BLOCKER_HINT[name]}")

    if csgo_dir is None or not Path(csgo_dir).is_dir():
        problems.append("CS2 klasörü bulunamadı. ayarlar.json → csgo_klasoru "
                        "(…\\Counter-Strike Global Offensive\\game\\csgo).")
    elif (gb := free_gb(Path(csgo_dir))) < MIN_FREE_GB:
        problems.append(f"CS2 diskinde {gb:.0f} GB boş yer var; kayıt için en az {MIN_FREE_GB} GB gerekir.")

    tools["env"] = pg_env(tools["pg_bin"], tools["db"])
    return tools, problems
