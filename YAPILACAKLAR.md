# YAPILACAKLAR — CS2 yüklü bilgisayarda kurulum

Kayıt CS Demo Manager (CSDM) ile yapılır. OBS ve CS2'de `-netconport` gerekmez.

## 1. Kur

- [ ] Projeyi al: `git clone https://github.com/rose-omer/cs-clip.git C:\cs-clip` (ya da ZIP indirip aç).
      Yolda Türkçe karakter olmaması önerilir.
- [ ] `kur.bat`'a çift tıkla. Python, paketler, `ayarlar.json`, FFmpeg, PostgreSQL, CS Demo Manager, veritabanı,
      CSDM ayarları ve PATH sırayla hazırlanır; kurulu olanlar atlanır. Ayrıntı: [README.md → Kurulum](README.md#kurulum).
- [ ] Son satırda `Kurulum tamam.` yazmalı. Sorun yazarsa düzeltip `kur.bat`'ı tekrar çalıştır.
- [ ] Ne yapacağını önce görmek için: `kur.bat --prova` (hiçbir şeyi değiştirmez).

## 2. Kontrol

```bat
klip.bat --kontrol
```
`Her şey hazır` yazmalı. Yazmıyorsa listelenen sorunu düzelt. Oyuncu adı, klip süreleri ve klasörler:
`arayuz.bat` → **Ayarlar**.

## Elle kurulum (kur.bat bir adımda takılırsa)

- **Python**: https://www.python.org/downloads/ (3.11+, "py launcher" seçili).
- **FFmpeg**: `winget install Gyan.FFmpeg`.
- **PostgreSQL**: `winget install PostgreSQL.PostgreSQL.17`. Türkçe Windows'ta kurucu `initdb` adımında düşer
  (`Turkish_Türkiye.1254`); programlar yine de kurulur. Veritabanını elle aç:
  ```bat
  "C:\Program Files\PostgreSQL\17\bin\initdb.exe" -D "%LOCALAPPDATA%\csdm-pg\data" -U postgres -W --auth=scram-sha-256 --encoding=UTF8 --locale=C
  ```
  Sonra `kur.bat`'ı yeniden çalıştır; şifreyi `%USERPROFILE%\.csdm\settings.json` → `database.password`'a yazmış ol.
- **CS Demo Manager**: https://github.com/akiver/cs-demo-manager/releases (`CS-Demo-Manager-Setup-*.exe`).

## 3. İlk kayıt

- [ ] Demoyu indir (FACEIT → maç → demo indir → `.dem.zst`).
- [ ] Önce listeye bak: `klip.bat C:\Users\...\Downloads\mac.dem.zst --sadece-analiz`
- [ ] **FACEIT'ten çık, CS2'yi kapat.** Kayıt CS2'yi kendisi açıp kapatır.
- [ ] `klip.bat C:\Users\...\Downloads\mac.dem.zst --en-iyi 3`
- [ ] Kayıt sırasında klavye ve fareye dokunma.
- [ ] Klipler `klipler\`, montaj `klipler\montaj.mp4`.

Birden çok demo: hepsini bir klasöre koyup `klip.bat <klasör> --en-iyi 3 --temizle`. `--temizle` kaydı biten demoları Geri Dönüşüm Kutusu'na taşır.

## 4. Sorun → çözüm

| Belirti | Çözüm |
|---|---|
| `FACEIT açık` / `CS2 açık` | Programı kapat, komutu tekrar çalıştır |
| `PostgreSQL çalışmıyor ve başlatılamadı` | `kur.bat`'ı çalıştır; günlük `%LOCALAPPDATA%\csdm-pg\log.txt`. Veri klasörü başka yerdeyse Ayarlar → `pg_veri_klasoru` |
| `CSDM ayarları yok` | `kur.bat`'ı çalıştır |
| `Kaydedilemedi: Game error` | CS2 bu demoda çöktü. Elle `playdemo` ile dene; o da çökerse demo kaydedilemiyor |
| `Failed to start Counter-Strike` | FACEIT Anti-Cheat hâlâ çalışıyor olabilir; FACEIT'ten tamamen çık |
| Kamera başka oyuncuda | Oyuncu adı demodakiyle aynı mı? `--sadece-analiz` çıktısına bak |
| HUD tamamen kayboluyor | Ayarlar → Temiz HUD kapalı |
| Klip çok kısa / uzun | Ayarlar → klip öncesi/sonrası süre |

## Bilinen sınırlar

- FACEIT açıkken kayıt yapılamaz (CSDM CS2'yi `-insecure` başlatır).
- Kayıt gerçek zamanlıdır ve kareler önce diske yazılır: 40 sn'lik görüntü ≈ 2 dk. Ayrıntı: NOTLAR.md.
- CSDM'in FACEIT'ten otomatik demo indirmesi kapalı; demolar elle ya da `otomatik.py faceit` (FACEIT API anahtarıyla) indirilir.
- Clutch, takımların 5 kişi olduğunu varsayar. Clutch'ı yalnız bombayla kazandıysan klip çıkmaz.
