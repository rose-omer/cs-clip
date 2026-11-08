# Çalışma notları

## 2026-11-02 — ilk gerçek kullanım

### Kurulan araçlar
- Python 3.12 (winget), `.venv` ve paketler. Testler geçiyor.
- OBS Studio 33 + WebSocket (4455, şifresiz), `csklip` profili ve CS2 sahnesi. **Kullanılmadı** (aşağıya bak).
- FFmpeg 9 (winget, Gyan.FFmpeg).
- CS Demo Manager 3.20.1: `%LOCALAPPDATA%\Programs\cs-demo-manager`, ayarlar `%USERPROFILE%\.csdm\settings.json`.
- PostgreSQL 17 (CSDM'in veritabanı). Kurucu, Türkçe dil adı (`Turkish_Türkiye.1254`) yüzünden `initdb`'de düştü.
  Veri klasörü elle açıldı: `%LOCALAPPDATA%\csdm-pg\data` (`--locale=C`). **Windows hizmeti değil**, yeniden başlatınca kapanır:
  ```bat
  "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" -D "%LOCALAPPDATA%\csdm-pg\data" -l "%LOCALAPPDATA%\csdm-pg\log.txt" start
  ```
  Şifre `%TEMP%\csdm-dl\pg.txt` içinde ve CSDM ayarlarında. `psql` kullanıcı PATH'ine eklendi.
- Steam CS2 başlatma seçeneği: `-netconport 2121 -windowed -noborder` (artık gereksiz).
  Eski ayar dosyası yedeği: `Steam\userdata\1003178006\config\localconfig.vdf.bak-csklip`.

### Ne çalıştı, ne çalışmadı
- **Analiz (`klip.py --sadece-analiz`)**: sorunsuz, hızlı.
- **Kayıt (`render.py`, OBS + netcon)**: çalışmadı. CS2 `-netconport` ile konsol portunu açmıyor.
- **Kayıt CSDM ile**: çalıştı. Gereken: demo önce `csdm analyze`, sonra `csdm video --mode player --steamids 76561198963443734 --event kills --rounds ...`.
- **FACEIT Anti-Cheat açıkken** CSDM CS2'yi `-insecure` başlatamıyor ("Erişim engellendi"). Kayıttan önce FACEIT client + servis kapatılmalı.
- **CSDM tuhaflıkları**: `--output` yok sayılıyor, klipler Downloads'a düşüyor; tek parçalı kliplerde `--output-file-name` uygulanmıyor (`sequence-N-tick-A-to-B.mp4`); hata mesajı sadece "Game error".
- **Ancient demosu `1-ed2995bf…`**: CS2'yi her açılışta çökertiyor (elle `playdemo` dahil). Dosya sağlam. Diğer Ancient demosu (`1-2dd01012…`) sorunsuzdu.
- **FACEIT indirme**: CSDM'de kapalı. Demolar Chrome'daki FACEIT oturumundan, maç API'si + imzalı indirme linkiyle indirildi.

### Üretilen klipler
- `klipler/` içinde 40 klip, 10 maçtan (1 maç çöktüğü için yok).
- Kullanılan demolar Geri Dönüşüm Kutusu'na taşındı. Downloads'ta test için `1-59cf10f2…` kaldı.

### Ölçümler (aynı 2 round, 4 parça, ~41 sn görüntü)
| Kodlayıcı | Toplam | Dönüştürme | Boyut |
|---|---|---|---|
| x264 | 135 sn | 38 sn | 48 MB |
| NVENC (`-preset p5 -cq 21`) | 125 sn | 29 sn | 140 MB |

Sonuç: NVENC değmez. Zamanın çoğu CS2 açılışı/yükleme ve kayıtta (kareler TGA olarak diske).
`araclar/olcum.ps1` ile aşama aşama ölçüm denendi ama script hemen çıktı (cmd tırnaklama hatası), sonuç yok.

### Araçlar (`araclar/`)
- `test_nvenc.ps1`, `olcum.ps1`: hız testleri. `olcum.ps1` henüz çalışmıyor (cmd tırnaklama).

## 2026-11-08 — kayıt projeye taşındı (`csdm-kayit` dalı)
- `render.py` baştan yazıldı: OBS/netcon kodu kalktı, kayıt CSDM ile. Demo başına tek CS2 açılışı,
  parçalar tick'e göre round'a atanıyor, aynı round'un parçaları ffmpeg ile (yeniden kodlamadan) birleşiyor.
- `kontrol.py`: kayıt öncesi kontrol (`klip.bat --kontrol`). FACEIT/CS2 açıksa söyler, **kapatmaz**.
  Kapalı PostgreSQL'i başlatır (doğrulandı: 7 sn). Disk boş yer kontrolü.
- Klip zaten varsa atlanır; CS2'yi çökerten demo atlanıp sıradakine geçilir.
- Demo CSDM veritabanında varsa yeniden `csdm analyze` yapılmaz.
- Yeni ayarlar: `once_sn` (3), `sonra_sn` (2), `mac_basi_en_fazla`, `csdm_yolu`, `ffmpeg_yolu`, `pg_veri_klasoru`.
  Eski `obs_*`, `netcon_port`, `yukleme_bekle` yok sayılır.
- Yeni bayraklar: `--kontrol`, `--en-iyi N`, `--temizle` (Geri Dönüşüm Kutusu).
- Klip adı: `harita_maçkodu_Rround_etiketler_silah.mp4`.
- 42 test geçiyor. `--kontrol`, `--prova` ve gerçek kayıt (2026-11-08, 3 klip + montaj) doğrulandı.

### Sıradaki adımlar
2. `olcum.ps1`'i düzelt, aşamaları ölç; CSDM `--recording-system HLAE` dene (TGA'sız kayıt).
3. Downloads izleme modu (yeni demo gelince otomatik kayıt).
4. Steam'deki `-netconport 2121 -windowed -noborder` başlatma seçeneği artık gereksiz; istenirse kaldırılır.
