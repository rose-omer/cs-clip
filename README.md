# cs-klip

CS2 demosundan senin iyi anlarını bulur ve `.mp4` klip yapar.

Akış: demo (`.dem` / `.dem.zst` / `.gz` / `.bz2`) → analiz → CS2 demoyu oynatır → OBS kaydeder → `klipler/`.

Kurulum ve ilk çalıştırma: **[YAPILACAKLAR.md](YAPILACAKLAR.md)**.

## Komutlar

| Komut | Ne yapar |
|---|---|
| `klip.bat <demo>` | Analiz + klip kaydı + montaj |
| `klip.bat <demo> --sadece-analiz` | Yalnız listeyi gösterir (CS2/OBS gerekmez) |
| `klip.bat <demo> --prova` | CS2/OBS'e gidecek komutları gösterir, kayıt yapmaz |
| `klip.bat <klasör>` | Klasördeki tüm demoları işler |
| `--oyuncu AD` | Başka oyuncunun anları |
| `--min-skor N` | Eşik (varsayılan 3) |

Demo dosyasını `klip.bat` üzerine sürükle-bırak da çalışır.

## Skorlama

| Olay | Puan |
|---|---|
| 1K / 2K / 3K / 4K / ACE | 1 / 3 / 6 / 10 / 16 |
| Kazanılan 1v2 / 1v3 / 1v4 / 1v5 clutch | +4 / +7 / +10 / +14 |
| Headshot (kill başı) | +0.5 |
| Wallbang, noscope, kör iken kill | +2 |
| Smoke arkası | +1.5 |
| Bıçak | +3 |
| 2 sn içinde art arda kill | +1 |

- Isınma ve maç öncesi bıçak kill'leri sayılmaz.
- Takım arkadaşı kill'i ve intihar sayılmaz.
- Kill'ler arasında 8 sn'den uzun boşluk varsa klip parçalara bölünür. OBS boşlukta kaydı duraklatır.
- Klip ilk andan 5 sn önce başlar, son kill'den 3 sn sonra biter.

Sabitler: `highlights.py` başı. Bekleme süreleri: `render.py` başı ve `ayarlar.json`.

## Dosyalar

| Dosya | Görev |
|---|---|
| `klip.py` | Tek giriş noktası |
| `highlights.py` | Skorlama, clutch, klip parçaları |
| `analyze.py` | Demoyu okur (demoparser2) |
| `demofile.py` | Sıkıştırılmış demoyu açar, CS2 klasörünü bulur |
| `render.py` | CS2 konsolu (netcon) + OBS WebSocket + ffmpeg montaj |
| `config.py` | `ayarlar.json` okur |
| `test_*.py` | Testler: `.venv\Scripts\python -m pytest -q` |
