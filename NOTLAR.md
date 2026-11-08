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
  (Bu sonuç yanlış çıktı: sorun demonun ilk FullPacket'inde, aşağıya bak.)

### Ancient çökmesi — demo içi inceleme ve çözüm (2026-11-08)
- Demo yapısı (komut türleri, 3840 tick'te bir FullPacket, tick sıçraması, SendTables/ClassInfo) 5 demoda aynı.
  Yükleme sırası (spawn group) da sebep değil: Anubis'te de gökyüzü kutusu 8. sırada ve sorunsuz.
- Çöken `3dd3d912`'nin ilk FullPacket'i (tick 1; CS2 her demonun başında tick 0'a sararken bunu ikinci kez uygular)
  farklı: içinde `instancebaseline`/`AnimAssetData` tabloları ve bir `svc_UserCommands` (76) mesajı var. Sağlam
  demolarda (Dust2, Anubis, diğer Ancient) bu pakette yalnız `userinfo` tablosu, Tick ve PacketEntities var.
  Başlıkta `server_start_tick` 6013, `server_count` 5 (Dust2'de 2): sunucu kaydı geç ve harita yenilemeleri sonrası başlatmış.
- CS2'de denenen varyantlar (`-condebug` + elle `playdemo`):
  - Yalnız bayat `svc_UserCommands` girdisini silmek (komut tick'i 627, beklenen 6014): yine `engine2.dll+0x10c5b0`'da çöktü.
  - İlk FullPacket'i tamamen silmek: çökmedi ama başa sarma 3841'deki pakete gidip takıldı.
  - İlk FullPacket'i sağlam biçime getirmek (yalnız `userinfo`, UserCommands yok): "Demo Skipping finished at tick 0",
    demo sorunsuz oynuyor. **Çözüm bu.**
- `a53a1e7b` (diğer "bozuk" Ancient) elle `playdemo` ile sorunsuz oynuyor; ilk FullPacket'i de sağlam. CSDM ile
  tek açılışta yine takıldı (eklenti yüklendi, oynatma hiç başlamadı; süre sınırı kapattı). Parça parça: 6 parçanın
  4'ü kaydedildi → R05 2K ve R10 3K klipleri çıktı. R13'ün ilk parçasında (tick 82508) CS2 ayrı açılışta da takıldı;
  R13 (skor 3, glock 2K) kaydedilemedi.
- Bu yüzden `record_demo` artık: tek açılış çöker/takılırsa yarım parçaları silip her parçayı ayrı açılışta dener;
  parça parça kayıtta bir klibin parçası başarısız olursa yalnız o klip atlanır (parçaları silinir), diğerleri kalır.
- CSDM ile kayıt: başa sarma artık geçiyor, CSDM 46081'e atlayıp ilk klibi kaydediyor, ama bir sonraki klibe
  (47690) atlarken yine `engine2.dll+0x10c5b0`'da çöküyor (CSDM eklenti günlüğü: `game\bin\win64\csdm.log`).
  Sonraki FullPacket'lerden UserCommands'ı silmek de işe yaramadı. Aynı parça (47755–48075) ayrı bir CS2
  açılışında, tek atlamayla sorunsuz kaydedildi. Yani bu demoda CS2 ilk atlamada sağlam, ikincide çöküyor.
- Kod: `onarim.py` ilk FullPacket'te fazlalık varsa ilk paketi sağlam biçime getirir, diğer FullPacket'lerden
  UserCommands'ı çıkarır (yalnız TrueView kullanıyor, CSDM zaten kapatıyor), gerisini bayt bayt kopyalayıp
  `<ad>.onarilmis.dem` yazar. Sağlam demolara dokunmaz. `klip.py` kayıttan önce bunu kendisi yapar ve onarılmış
  demoyu **her tick aralığı ayrı CS2 açılışında** kaydeder (`csdm video <demo> <başlangıç> <bitiş> --focus-player`);
  sağlam demolar eskisi gibi tek açılışta. Arayüz ve klasör taraması kopyayı ayrı maç saymaz, `--temizle` kopyayı da
  çöpe atar. Elle: `python onarim.py <demo.dem> [--kontrol]`.
- CSDM veritabanında aynı yolun eski hâli kayıtlıysa `csdm video` "Match not found in database" der; bu artık hata
  sayılıyor, demo yeniden analiz edilip kayıt bir kez daha deneniyor. Deneme betiği: `araclar\ancient_test.ps1`.
- CSDM CLI `playback.launchParameters` ayarını kullanmıyor; `--cfg "con_logfile ..."` de dosya yazmadı.
  CS2 tarafını görmek için elle `steam.exe -applaunch 730 -condebug -novid -insecure +playdemo <demo>` kullan.

### Takılan round'lar — a53a1e7b R10 (2026-11-08)
- **R10 3K kaydedildi** (`ancient_a53a1e7b_R10_3K_3-HS_m4a1.mp4`, 16,7 sn, 2 parça). Tek açılış yine takıldı; parça
  parça kayıtta 1. parça ilk denemede, 2. parça (tick 63995) ilk denemede takılıp **aynı başlangıçla düz tekrarda** çıktı.
- Takılma demonun yapısından değil: FullPacket'ler 5 demoda da 3840 tick'te bir, R10'un yüklendiği 61441'deki paket
  sağlam demolardakilerle aynı biçimde (tablosuz, Tick + PacketEntities + UserCommands). Her pakette 10 svc_UserCommands
  var; sağlam Dust2/Anubis'te de aynı.
- CSDM eklentisi (3.20.1) her satırda `csdm.log`'u açıp kapatıyor, yani günlük eksik kalmaz. Takılan açılışta günlük
  `CreateInterface ... EntitySubclassUtilsV001`'de bitiyor: `ClientFullyConnect` ve "Demo playback started" hiç yok.
  Yani CS2 **demoyu yüklerken/oynatmaya başlamadan** takılıyor; `demo_gototick`'e hiç gelmiyor. Başarılı açılışta sıra:
  `ClientFullyConnect` → `[1] Demo playback started` → `[96] demo_gototick <başlangıç-65>` → `startmovie` → `quit`.
  Takılma rastgele görünüyor (aynı parça bir açılışta takılıyor, sonrakinde çıkıyor).
- CSDM tek aralık kaydında `demo_gototick <başlangıç - 65>` yapar (kurulum tick'i başlangıç - 64); action tick'i en az 96.
- `render.py`: parça parça kayıtta CS2 takılır ya da çökerse ("Game error") parça yeniden denenir:
  aynı başlangıç → önceki FullPacket'ten (atlama hedefi paketin 33 tick önüne çekilir) → 5 sn erken → (alternatif
  yoksa) aynı başlangıçla bir kez daha → HLAE kuruluysa HLAE ile. Fazladan baş kısım ffmpeg ile kesilir (yeniden
  kodlama, en fazla 12 sn). Her CS2 açılışından önce önceki CS2'nin kapanması beklenir (30 sn; **kapatmaz**).
  Kalıcı hatalar (demo yok, veritabanında yok) tekrar denenmez. FullPacket tick'leri `onarim.fullpacket_ticks`.
- **HLAE** (kurulmadı): `ayarlar.json → "kayit_sistemi": "HLAE"` ya da kuruluysa CS takılınca son çare. CSDM HLAE'yi
  `%USERPROFILE%\.csdm\hlae\hlae.exe`'de arar (ya da CSDM ayarlarında özel konum). Kurulum: CS Demo Manager →
  Settings → Video → HLAE → Install; ya da github.com/advancedfx/advancedfx/releases → `hlae_<sürüm>.zip`
  (v2.193.0: 9,1 MB) bu klasöre açılır. `klip.bat --kontrol` HLAE seçiliyken kurulu değilse söyler.
- **CSDM'siz kendi yol** (`playdemo` + `demo_gototick` + `startmovie`): CS2'de belirli tick'te komut çalıştırma yok
  (CSDM eklentisi ya da HLAE `mirv_cmd` gerekir), netcon da çalışmıyor; otomatik yapılamıyor. `araclar\elle_kayit.ps1`
  CS2'yi `-condebug +playdemo` ile açıp yazılacak komutları gösterir (elle kayıt ve takılmanın yerini
  `game\csgo\console.log`'da görmek için).
- Yan bulgu: `~/.csdm/settings.json` → `video.outputFolderPath` bozuk kodlanmış (`C:\yazÄ±lÄ±m\...`); CSDM'in klipleri
  Downloads'a yazmasının sebebi büyük olasılıkla bu. Düzeltilmedi.
