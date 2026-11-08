"""ayarlar.json okuma. Dosya yoksa varsayılanlar kullanılır."""

import json
from pathlib import Path

DEFAULTS = {
    "oyuncu": "DuranEnnmi",
    "min_skor": 3,
    "mac_basi_en_fazla": 0,  # maç başına en iyi N an; 0 = eşiği geçen hepsi
    "once_sn": 3,  # ilk kill'den önce kaydedilecek süre
    "sonra_sn": 2,  # son kill'den sonra kaydedilecek süre
    "temiz_hud": True,  # yalnız kill akışı görünür
    "kayit_cozunurluk": "",  # "1080p" | "1440p"; boşsa CSDM'in ayarı
    "kayit_crf": 0,  # 14-35 (düşük = daha iyi, büyük dosya); 0 = CSDM'in ayarı
    "montaj": True,  # klipleri tek videoda birleştir
    "cikti_klasoru": "klipler",
    "csgo_klasoru": "",  # boşsa Steam'den bulunur
    "csdm_yolu": "",  # boşsa %LOCALAPPDATA%\Programs\cs-demo-manager\csdm.cmd
    "ffmpeg_yolu": "",  # boşsa PATH ve winget klasörü aranır
    "pg_veri_klasoru": "",  # boşsa %LOCALAPPDATA%\csdm-pg\data
    "demo_klasorleri": [],  # arayüzün demo aradığı klasörler; boşsa İndirilenler + demos/
    "otomatik_bekle_sn": 120,  # otomatik kayıt: CS2/FACEIT kapandıktan sonra bu kadar bekle
    "faceit_api_anahtari": "",  # FACEIT Data API anahtarı (developers.faceit.com); otomatik.py faceit
    "faceit_kullanici": "",  # FACEIT kullanıcı adı; boşsa "oyuncu"
}

# OBS/netcon dönemi ayarları: eski ayarlar.json bozulmasın diye yok sayılır.
OBSOLETE = {"obs_host", "obs_port", "obs_sifre", "netcon_port", "yukleme_bekle"}


def load_config(path: Path) -> dict:
    cfg = dict(DEFAULTS)
    if not Path(path).exists():
        return cfg
    user = json.loads(Path(path).read_text(encoding="utf-8"))
    unknown = sorted(set(user) - set(DEFAULTS) - OBSOLETE)
    if unknown:
        raise SystemExit(f"{path}: bilinmeyen ayar: {', '.join(unknown)}")
    cfg.update({k: v for k, v in user.items() if k not in OBSOLETE})
    return cfg


# --- arayüzden düzenleme: doğrulama ve kaydetme ---
NUMBERS = {  # alan: (en az, en çok, yalnız tam sayı mı)
    "min_skor": (0, 100, False),
    "mac_basi_en_fazla": (0, 50, True),
    "once_sn": (0, 30, False),
    "sonra_sn": (0, 30, False),
}
BOOLS = ("temiz_hud", "montaj")
DIRS = ("csgo_klasoru", "pg_veri_klasoru")  # boş olabilir; doluysa var olmalı
FILES = ("csdm_yolu", "ffmpeg_yolu")
MAX_DEMO_FOLDERS = 20


def clean_path(value) -> str:
    """Yapıştırılan yoldaki boşlukları ve Explorer'ın "Yol olarak kopyala" tırnaklarını atar."""
    return str(value).strip().strip('"').strip()


def validate(data, check_paths: bool = True) -> tuple[dict, dict]:
    """(temiz değerler, alan -> hata mesajı). Yalnız gelen alanlar döner; eksik alan hata değildir."""
    if not isinstance(data, dict):
        return {}, {"_": "Ayarlar bir JSON nesnesi olmalı."}
    clean, errors = {}, {}
    for key in sorted(set(data) - set(DEFAULTS)):
        errors[key] = "Bilinmeyen ayar."
    for key, value in data.items():
        if key not in DEFAULTS:
            continue
        if key == "oyuncu":
            name = str(value).strip() if isinstance(value, (str, int)) and not isinstance(value, bool) else ""
            if not name:
                errors[key] = "Oyuncu adı boş olamaz (demodaki ad ya da SteamID64)."
            elif len(name) > 64:
                errors[key] = "Oyuncu adı en fazla 64 karakter olabilir."
            else:
                clean[key] = name
        elif key in NUMBERS:
            lo, hi, whole = NUMBERS[key]
            if isinstance(value, str):
                try:
                    value = float(value.replace(",", ".")) if value.strip() else None
                except ValueError:
                    value = None
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value != value:
                errors[key] = "Sayı olmalı."
            elif whole and value != int(value):
                errors[key] = "Tam sayı olmalı."
            elif not lo <= value <= hi:
                errors[key] = f"{lo} ile {hi} arasında olmalı."
            else:
                clean[key] = int(value) if whole or value == int(value) else float(value)
        elif key in BOOLS:
            if not isinstance(value, bool):
                errors[key] = "Açık ya da kapalı (true/false) olmalı."
            else:
                clean[key] = value
        elif key == "cikti_klasoru":
            path = clean_path(value) if isinstance(value, str) else ""
            if not path:
                errors[key] = "Klip klasörü boş olamaz."
            elif check_paths and Path(path).exists() and not Path(path).is_dir():
                errors[key] = "Bu yol bir dosya, klasör değil."
            else:
                clean[key] = path
        elif key == "demo_klasorleri":
            if isinstance(value, str):  # arayüzdeki metin kutusu: her satıra bir klasör
                value = value.splitlines()
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                errors[key] = "Klasör listesi olmalı."
                continue
            paths = list(dict.fromkeys(p for p in (clean_path(v) for v in value) if p))
            missing = [p for p in paths if check_paths and not Path(p).is_dir()]
            if len(paths) > MAX_DEMO_FOLDERS:
                errors[key] = f"En fazla {MAX_DEMO_FOLDERS} klasör."
            elif missing:
                errors[key] = "Klasör bulunamadı: " + ", ".join(missing)
            else:
                clean[key] = paths
        elif key in DIRS or key in FILES:
            path = clean_path(value) if isinstance(value, str) else None
            if path is None:
                errors[key] = "Yol metin olmalı."
            elif path and check_paths and key in DIRS and not Path(path).is_dir():
                errors[key] = "Klasör bulunamadı."
            elif path and check_paths and key == "pg_veri_klasoru" and not (Path(path) / "PG_VERSION").is_file():
                errors[key] = "PostgreSQL veri klasörü değil (içinde PG_VERSION yok)."
            elif path and check_paths and key in FILES and not Path(path).is_file():
                errors[key] = "Dosya bulunamadı."
            else:
                clean[key] = path
    return clean, errors


def save_config(path: Path, changes: dict) -> dict:
    """Doğrulanmış değişiklikleri dosyaya yazar (varsayılandan farklı olmasa da), yeni ayarları döner.

    Dosyadaki eski (OBS dönemi) alanlar atılır. Yazma atomik: yarım dosya kalmaz.
    """
    path = Path(path)
    current = {}
    if path.exists():
        current = {k: v for k, v in json.loads(path.read_text(encoding="utf-8")).items() if k in DEFAULTS}
    current.update(changes)
    ordered = {k: current[k] for k in DEFAULTS if k in current}
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return load_config(path)
