"""ayarlar.json okuma. Dosya yoksa varsayılanlar kullanılır."""

import json
from pathlib import Path

DEFAULTS = {
    "oyuncu": "DuranEnnmi",
    "min_skor": 3,
    "obs_host": "localhost",
    "obs_port": 4455,
    "obs_sifre": "",
    "netcon_port": 2121,
    "csgo_klasoru": "",  # boşsa Steam'den bulunur
    "yukleme_bekle": 40,  # playdemo sonrası bekleme (sn)
    "temiz_hud": True,  # yalnız kill akışı görünür
    "montaj": True,  # klipleri tek videoda birleştir (ffmpeg gerekir)
    "cikti_klasoru": "klipler",
}


def load_config(path: Path) -> dict:
    cfg = dict(DEFAULTS)
    if not Path(path).exists():
        return cfg
    user = json.loads(Path(path).read_text(encoding="utf-8"))
    unknown = sorted(set(user) - set(DEFAULTS))
    if unknown:
        raise SystemExit(f"{path}: bilinmeyen ayar: {', '.join(unknown)}")
    cfg.update(user)
    return cfg
