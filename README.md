# cs-klip

CS2 demosundan senin iyi anlarını bulur ve `.mp4` klip yapar.

Akış: demo (`.dem` / `.dem.zst` / `.gz` / `.bz2`) → analiz → CS Demo Manager demoyu CS2'de **bir kez** açıp anları kaydeder → parçalar birleştirilip `klipler/` klasörüne adlandırılır.

Kurulum: **[YAPILACAKLAR.md](YAPILACAKLAR.md)**. Bilinen sorunlar ve ölçümler: [NOTLAR.md](NOTLAR.md).

## Arayüz

`arayuz.bat` → tarayıcıda `http://127.0.0.1:8765/` açılır (yalnız bu bilgisayardan erişilir).

- Solda İndirilenler ve `demos/` klasöründeki demolar; sürükle-bırak ile demo yüklenebilir.
- Demo seçince maç istatistikleri: skor, rating, ADR, K/D/A, KAST, HS%, açılış kill'leri, iki takımın skor tablosu, round çizelgesi, silahlar.
- Highlight listesi ve kaydedilmiş klipler sayfada oynatılır. "Klipleri kaydet" kaydı arka planda başlatır (FACEIT ve CS2 kapalı olmalı).
- İlk açılışta istatistik hesaplanır ve demonun yanına `.stats.json` olarak saklanır; sonraki açılışlar anında.

## Komutlar

| Komut | Ne yapar |
|---|---|
| `klip.bat <demo>` | Analiz + klip kaydı + montaj |
| `klip.bat <klasör>` | Klasördeki tüm demoları işler |
| `klip.bat <demo> --sadece-analiz` | Yalnız listeyi gösterir (CS2 gerekmez) |
| `klip.bat <demo> --prova` | Kaydetmeden çalışacak komutu ve klip adlarını gösterir |
| `klip.bat --kontrol` | Kayıt öncesi kontrol: araçlar, veritabanı, FACEIT/CS2 açık mı, disk |
| `--en-iyi N` | Maç başına yalnız en iyi N an |
| `--temizle` | Kaydı biten demoyu Geri Dönüşüm Kutusu'na taşır |
| `--oyuncu AD` | Başka oyuncunun anları |
| `--min-skor N` | Eşik (varsayılan 3) |

Demo dosyasını `klip.bat` üzerine sürükle-bırak da çalışır.

Kayıttan önce **FACEIT ve CS2 kapalı olmalı**. Araç bunları kapatmaz, yalnız söyler. Kapalı PostgreSQL'i kendisi başlatır.
Klibi hazır olan round atlanır; yarıda kalan iş aynı komutla sürdürülür. CS2'yi çökerten demo atlanır, sıradakine geçilir.

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
- Kill'ler arasında 8 sn'den uzun boşluk varsa klip parçalara bölünür; parçalar birleştirilir.
- Klip ilk andan 3 sn önce başlar, son kill'den 2 sn sonra biter (`once_sn`, `sonra_sn`).

## Dosyalar

| Dosya | Görev |
|---|---|
| `klip.py` | Tek giriş noktası |
| `highlights.py` | Skorlama, clutch, klip parçaları |
| `analyze.py` | Demoyu okur (demoparser2) |
| `demofile.py` | Sıkıştırılmış demoyu açar, CS2 klasörünü bulur, Geri Dönüşüm Kutusu |
| `render.py` | CSDM ile kayıt, parçaları round'a atama, birleştirme, montaj |
| `kontrol.py` | Kayıt öncesi kontroller, PostgreSQL başlatma |
| `stats.py` | Maç istatistikleri (rating, ADR, KAST, round çizelgesi) |
| `arayuz.py`, `arayuz/` | Yerel web arayüzü: sunucu ve sayfa |
| `config.py` | `ayarlar.json` okur |
| `araclar/` | Hız ölçüm script'leri |
| `test_*.py` | Testler: `.venv\Scripts\python -m pytest -q` |
