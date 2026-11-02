# YAPILACAKLAR — CS2 yüklü bilgisayarda

Durum: analiz kısmı gerçek bir FACEIT demosunda doğrulandı. Kayıt kısmı (CS2 + OBS) sahte konsol ve sahte kayıt cihazıyla test edildi. Gerçek CS2 ve OBS ile **ilk kez bu bilgisayarda** çalışacak. Adım 6'daki ilk deneme bu yüzden önemli.

## 0. Bu bilgisayardan taşı

- [ ] `cs-klip` klasörünü kopyala (USB, Drive ya da zip). Şunları **alma**: `.venv`, `demos`, `klipler`, `__pycache__`, `.pytest_cache`.
  Zip için (PowerShell, `cs-klip`in bir üst klasöründe):
  ```powershell
  Compress-Archive -Path cs-klip\* -DestinationPath cs-klip.zip -Force
  ```
  Zip'e `.venv` girerse hedefte sil. `kur.bat` yeniden oluşturur.

## 1. Python

- [ ] Python 3.11 ya da üstünü kur: https://www.python.org/downloads/
  - Kurulumda "py launcher" ve "Add python.exe to PATH" seçili olsun.
- [ ] Kontrol: `py --version`

## 2. Kurulum

- [ ] `cs-klip\kur.bat` dosyasına çift tıkla.
  - Sanal ortamı oluşturur ve paketleri kurar.
  - `ayarlar.json` dosyasını oluşturur.
  - Testleri çalıştırır.
- [ ] Son satırda `Kurulum tamam.` yazmalı. Test hatası olursa çıktının tamamını Claude'a gönder.

## 3. OBS Studio

- [ ] OBS'i kur: https://obsproject.com (sürüm 28 ya da üstü; WebSocket içinde gelir).
- [ ] Araçlar → **WebSocket Sunucu Ayarları**:
  - [ ] "WebSocket sunucusunu etkinleştir" seçili.
  - [ ] Port: `4455`.
  - [ ] "Bağlantı bilgilerini göster" → şifreyi kopyala.
- [ ] `ayarlar.json` dosyasını aç. Şifreyi `"obs_sifre": ""` içine yaz.
- [ ] Sahneye kaynak ekle: **Oyun Yakalama** → Mod: "Belirli bir pencereyi yakala" → `cs2.exe`.
- [ ] Ayarlar → Çıkış:
  - [ ] Kayıt biçimi: **mp4** (ya da "Hybrid MP4").
  - [ ] Kayıt yolu: istediğin bir klasör. Araç dosyayı oradan `klipler/` klasörüne taşır.
- [ ] Ayarlar → Video: çözünürlük ve FPS'i oyununla aynı yap (ör. 1920x1080, 60).
- [ ] Ayarlar → Ses: masaüstü sesi açık olsun (oyun sesi kliplere girsin).

## 4. CS2

- [ ] Steam → CS2 → sağ tık → Özellikler → Genel → **Başlatma Seçenekleri**:
  ```
  -netconport 2121
  ```
  (Başka seçeneklerin varsa sonuna boşlukla ekle.)
- [ ] CS2'yi bir kez aç ve kapat.
- [ ] Önerilen: oyunu **pencereli tam ekran** modunda çalıştır. OBS yakalaması daha güvenilir olur.

## 5. Kuru deneme (CS2 ve OBS gerekmez)

- [ ] Demoyu indir (FACEIT → maç → "Watch demo" → `.dem.zst`).
- [ ] Analiz:
  ```bat
  klip.bat C:\Users\...\Downloads\mac.dem.zst --sadece-analiz
  ```
  Highlight listesi görünmeli. `.zst` dosyası aynı klasöre `.dem` olarak açılır (~270 MB).
- [ ] Prova (gidecek komutları gösterir, kayıt yapmaz):
  ```bat
  klip.bat C:\Users\...\Downloads\mac.dem.zst --prova
  ```

## 6. İlk gerçek kayıt

- [ ] OBS'i aç.
- [ ] CS2'yi aç. **Ana menüde** bekle (maça girme).
- [ ] Önce yalnız en iyi 1–2 klipi dene:
  ```bat
  klip.bat C:\Users\...\Downloads\mac.dem.zst --min-skor 10
  ```
- [ ] Kayıt sırasında klavye ve fareye dokunma. CS2 penceresi önde kalsın.
- [ ] Sonucu kontrol et (`klipler\` klasörü):
  - [ ] Klip doğru anda mı başlıyor? Olmuyorsa tablo 1'e bak.
  - [ ] Kamera senin POV'unda mı? Olmuyorsa tablo 1'e bak.
  - [ ] Görüntü siyah mı? OBS Oyun Yakalama ayarına bak (adım 3).
- [ ] Sorun yoksa tüm klipler:
  ```bat
  klip.bat C:\Users\...\Downloads\mac.dem.zst
  ```
- [ ] Montaj (`klipler\montaj.mp4`) için ffmpeg gerekir. İsteğe bağlı kurulum:
  ```bat
  winget install Gyan.FFmpeg
  ```
  Kurulumdan sonra terminali yeniden aç.

## 7. Ayar tablosu (sorun → çözüm)

**Tablo 1**

| Belirti | Çözüm |
|---|---|
| `CS2 konsoluna bağlanılamadı` | CS2 açık değil ya da `-netconport 2121` eksik (adım 4) |
| `OBS'e bağlanılamadı` | OBS kapalı, WebSocket kapalı ya da şifre yanlış (adım 3) |
| `OBS zaten kayıtta` | OBS'te kaydı durdur |
| `CS2 klasörü bulunamadı` | `ayarlar.json` → `"csgo_klasoru": "D:\\SteamLibrary\\steamapps\\common\\Counter-Strike Global Offensive\\game\\csgo"` |
| İlk klip yükleme ekranıyla başlıyor | `ayarlar.json` → `yukleme_bekle` değerini artır (40 → 60) |
| Klip başında donma/atlama | `render.py` → `SEEK_WAIT = 3` değerini 5 yap |
| Kamera başka oyuncuda | Oyuncu adı demodakiyle aynı mı? `--sadece-analiz` çıktısındaki adı kullan |
| HUD tamamen kayboluyor | `ayarlar.json` → `"temiz_hud": false` |
| `PermissionError` (taşıma) | OBS dosyayı geç bırakıyor. `render.py` → `MOVE_TRIES` artır |
| `Montaj atlandı: ffmpeg bulunamadı` | Adım 6'daki winget komutu |

## 8. Claude'a geri bildirim

İlk gerçek kayıttan sonra şunları gönder:
- [ ] `klip.bat` çıktısının tamamı.
- [ ] `cs-klip\konsol.log` (CS2 konsolunun kaydı; komut hataları burada görünür).
- [ ] Bir klibin başı doğru mu, kamera doğru mu (kısa not).
- [ ] Hata varsa tam metni.

## Bilinen sınırlar

- `-netconport` Valve'ın resmi belgesinde yok. Bir CS2 güncellemesi kaldırabilir. Bu olursa alternatif: HLAE ya da CS Demo Manager.
- Kayıt gerçek zamanlıdır. 9 klip ≈ 4–5 dakika sürer.
- Clutch, takımların 5 kişi olduğunu varsayar. Erken çıkan oyuncu olursa clutch etiketi kaçabilir.
- Clutch'ı yalnız bombayla (kill almadan) kazandıysan klip çıkmaz.
