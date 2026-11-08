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
