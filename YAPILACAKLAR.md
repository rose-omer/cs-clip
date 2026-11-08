# YAPILACAKLAR — CS2 yüklü bilgisayarda kurulum

Kayıt CS Demo Manager (CSDM) ile yapılır. OBS ve CS2'de `-netconport` gerekmez.

## 0. Projeyi al

```bat
git clone https://github.com/rose-omer/cs-clip.git C:\cs-clip
```
Private depo: `rose-omer` hesabıyla giriş gerekir. Yolda Türkçe karakter olmaması önerilir.

## 1. Python ve paketler

- [ ] Python 3.11+ kur (https://www.python.org/downloads/ ya da `winget install Python.Python.3.12`). "py launcher" seçili olsun.
- [ ] `kur.bat` dosyasına çift tıkla: sanal ortam, paketler, `ayarlar.json`, testler. Son satırda `Kurulum tamam.` yazmalı.

## 2. FFmpeg

```bat
winget install Gyan.FFmpeg
```
Araç ffmpeg'i winget klasöründe de bulur; terminali yeniden açmak gerekmez.

## 3. PostgreSQL (CSDM'in veritabanı)

- [ ] `winget install PostgreSQL.PostgreSQL.17`
- [ ] **Türkçe Windows'ta** kurucu `initdb` adımında düşer (`Turkish_Türkiye.1254` dil adı). Veritabanını elle aç:
  ```bat
  "C:\Program Files\PostgreSQL\17\bin\initdb.exe" -D "%LOCALAPPDATA%\csdm-pg\data" -U postgres -W --auth=scram-sha-256 --encoding=UTF8 --locale=C
  ```
  Sorduğu şifreyi bir yere not et (adım 4'te gerekir).
- [ ] Başlatmayı dert etme: `klip.bat` kapalı veritabanını kendisi başlatır (`%LOCALAPPDATA%\csdm-pg\data`; başka yerdeyse `ayarlar.json` → `pg_veri_klasoru`).

## 4. CS Demo Manager

- [ ] Kur: https://github.com/akiver/cs-demo-manager/releases (`CS-Demo-Manager-Setup-*.exe`).
- [ ] Bir kez aç ve kapat (`%USERPROFILE%\.csdm\settings.json` oluşur).
- [ ] O dosyada `database.password` alanına adım 3'teki şifreyi yaz (ya da CSDM'in veritabanı ekranından gir).

## 5. Kontrol

```bat
klip.bat --kontrol
```
`Her şey hazır` yazmalı. Yazmıyorsa listelenen sorunu düzelt.

## 6. İlk kayıt

- [ ] Demoyu indir (FACEIT → maç → demo indir → `.dem.zst`).
- [ ] Önce listeye bak: `klip.bat C:\Users\...\Downloads\mac.dem.zst --sadece-analiz`
- [ ] **FACEIT'ten çık, CS2'yi kapat.** Kayıt CS2'yi kendisi açıp kapatır.
- [ ] `klip.bat C:\Users\...\Downloads\mac.dem.zst --en-iyi 3`
- [ ] Kayıt sırasında klavye ve fareye dokunma.
- [ ] Klipler `klipler\`, montaj `klipler\montaj.mp4`.

Birden çok demo: hepsini bir klasöre koyup `klip.bat <klasör> --en-iyi 3 --temizle`. `--temizle` kaydı biten demoları Geri Dönüşüm Kutusu'na taşır.

## 7. Sorun → çözüm

| Belirti | Çözüm |
|---|---|
| `FACEIT açık` / `CS2 açık` | Programı kapat, komutu tekrar çalıştır |
| `PostgreSQL çalışmıyor ve başlatılamadı` | Adım 3; veri klasörü başka yerdeyse `pg_veri_klasoru` |
| `CSDM ayarları yok` | CS Demo Manager'ı bir kez aç-kapat (adım 4) |
| `Kaydedilemedi: Game error` | CS2 bu demoda çöktü. Elle `playdemo` ile dene; o da çökerse demo kaydedilemiyor |
| `Failed to start Counter-Strike` | FACEIT Anti-Cheat hâlâ çalışıyor olabilir; FACEIT'ten tamamen çık |
| Kamera başka oyuncuda | Oyuncu adı demodakiyle aynı mı? `--sadece-analiz` çıktısına bak |
| HUD tamamen kayboluyor | `ayarlar.json` → `"temiz_hud": false` |
| Klip çok kısa / uzun | `ayarlar.json` → `once_sn`, `sonra_sn` |

## Bilinen sınırlar

- FACEIT açıkken kayıt yapılamaz (CSDM CS2'yi `-insecure` başlatır).
- Kayıt gerçek zamanlıdır ve kareler önce diske yazılır: 40 sn'lik görüntü ≈ 2 dk. Ayrıntı: NOTLAR.md.
- CSDM'in FACEIT'ten otomatik demo indirmesi kapalı; demolar elle ya da `otomatik.py faceit` (FACEIT API anahtarıyla) indirilir.
- Clutch, takımların 5 kişi olduğunu varsayar. Clutch'ı yalnız bombayla kazandıysan klip çıkmaz.
