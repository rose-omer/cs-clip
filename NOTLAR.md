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

## 2026-11-08 — arayüz ve 4 yeni demo
- Arayüz (`arayuz.bat`) gerçek demolarla denendi: istatistik, klip oynatma, arayüzden kayıt çalışıyor.
- Yeni demolar: Dust2 `a95f6ac2` ve Anubis `797f8ecc` 3'er klip. Ancient `3dd3d912` "Game error" ile çöktü;
  Ancient `a53a1e7b`'de CS2 10 dk hiç kare yazmadan takıldı, elle kapatıldı.
  Ancient'ta 4 demonun 3'ü kaydedilemedi (yalnız `2dd01012` çalıştı): CS2/CSDM tarafında Ancient'a özgü bir sorun olabilir.
- Kayda süre sınırı eklendi: 180 sn + görüntü süresinin 6 katı; dolarsa csdm ve CS2 kapatılıp sıradaki demoya geçilir.

### Ancient çökmesi — inceleme (2026-11-08)
- Çöken demolar (`3dd3d912`, `a53a1e7b`) sorunsuz Dust2/Anubis demolarıyla aynı sürümde (patch 14196). Demo dosyası sorunu değil.
- 8 çökme dökümünün hepsi Valve'ın kodunda: `engine2.dll+0x10c5b0` / `+0x89222`, `client.dll+0xb01eeb` (access violation).
  CSDM'siz elle `playdemo` de aynı yerde çöküyor → CSDM ya da bizim kod değil.
- `-condebug` günlüğü: demo yüklenir, CS2 kendiliğinden başa sarar ("Demo Skipping: skipping to demo tick 0"),
  ikinci tam güncellemeyi ("non-incremental update") alırken çöker. Dust2 aynı geri sarmayı sorunsuz yapıyor.
- Denendi, işe yaramadı: `cl_demo_predict 0` (TrueView kapalı). Steam dosya doğrulaması: hiçbir dosya bozuk değil.
- hub.tcno.co'daki "type 138" düzeltmesi Temmuz 2026 öncesi demolar ve "Failed to parse message" için; bu sorun değil.
- Sonuç: CS2'nin mevcut sürümünde (ClientVersion 2000942, 4 Kasım 2026) Ancient demolarını geri sararken çıkan bir motor hatası.
  Bizim taraftan çözülemez; CS2 güncellemesini beklemek ya da Valve'a bildirmek gerekiyor. Araç bu demoları atlayıp devam ediyor.
  (Bu sonuç aşağıdaki demo içi incelemeyle düzeltildi: `3dd3d912`'de demo dosyasında somut bir anormallik var.)

### Ancient çökmesi — demo içi inceleme ve onarım (2026-11-08, CS2 açılmadan)
- Demo yapısı (komut türleri, 3840 tick'te bir FullPacket, tick sıçraması, SendTables/ClassInfo) 5 demoda aynı.
- `3dd3d912`'nin ilk FullPacket'i (tick 1, CS2'nin başa sararken yüklediği paket) farklı: içinde `instancebaseline`/
  `AnimAssetData` tabloları ve bir `svc_UserCommands` (76) mesajı var; diğer demolarda tick 1 FullPacket'te yalnız
  `userinfo` tablosu, Tick ve PacketEntities var. Başlıkta da `server_start_tick` 6013 ve `server_count` 5 (Dust2'de 2).
- O `svc_UserCommands` tek girdili ve bayat: slot 0, komut 44, komut tick'i 627, beklenen tick 6014 (fark 5387).
  Sağlam demoların FullPacket'lerindeki 1000+ komut girdisinde fark en çok birkaç tick. Çökme günlüğündeki son satırlar:
  `full command 44 for slot 0 replaces newer baseline 5423` → `Receiving 22.7K non-incremental update` → çökme.
  Dust2 günlüğünde bu "replaces newer baseline" satırı yok. Yani çökmeyi bu bayat komut tetikliyor olmalı.
- Tüm FullPacket taraması (tick farkı > 128): `3dd3d912` 1 (tick 1'de), `59cf10f2` 1 (tick 57601'de, fark 1184; o demo
  kaydedilebildi), `a53a1e7b`, `a95f6ac2`, `797f8ecc` 0.
- `a53a1e7b`'de bu anormallik yok. O demo çökmedi, CSDM'de 10 dk kare yazmadan takıldı; elle `playdemo` ile hiç
  denenmedi, günlüğü yok. Sebebi hâlâ bilinmiyor.
- Aday onarım: `araclar/demo_onar.py <demo.dem>` FullPacket'lerdeki bayat komut girdilerini siler (girdisi kalmayan
  mesajı tamamen), gerisini bayt bayt kopyalar ve `<ad>.onarilmis.dem` yazar. Orijinale dokunmaz. `--kontrol` yalnız bakar.
  `3dd3d912` için doğrulandı: 93002 mesajın yalnız FullPacket@1'i değişti, tablolar ve diğer mesajlar aynı,
  başlık ofsetleri kaydırıldı, demoparser2 iki dosyada da aynı 122 kill'i görüyor.
- Henüz CS2'de denenmedi (kullanıcı maçtaydı). Deneme: CS2 ve FACEIT kapalıyken
  `powershell -ExecutionPolicy Bypass -File araclar\ancient_test.ps1` (açık bir şey görürse kapatmaz, çıkar).
  Çalışırsa sonraki adım: `klip.py` kayıttan önce `find_stale` ile kontrol edip onarılmış kopyadan kaydetsin.
