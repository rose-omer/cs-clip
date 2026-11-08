"""FACEIT'ten son maç demolarını indirme (resmi FACEIT Data API).

Anahtar ayarlar.json → "faceit_api_anahtari" alanından okunur; kod anahtarı hiçbir yere yazmaz.
Anahtar: developers.faceit.com → App Studio → uygulama → API Keys → "Server side".

Akış: kullanıcı adı → player_id → son maçlar → maç ayrıntısındaki demo_url → (Downloads API ile imzalı link)
→ dosya `.part` olarak indirilir, bitince yeniden adlandırılır. Demolar izlenen klasöre düştüğü için
otomatik kuyruk onları kendiliğinden alır.
"""

import json
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlparse

from klip import DEMO_SUFFIXES

API = "https://open.faceit.com/data/v4"
DOWNLOAD_API = "https://open.faceit.com/download/v2/demos/download-url"
CHUNK = 1 << 20
TIMEOUT = 60

ANAHTAR_YOK = ("FACEIT API anahtarı yok. developers.faceit.com → App Studio → uygulama oluştur → API Keys → "
               "'Server side' anahtar al ve ayarlar.json'a \"faceit_api_anahtari\": \"<anahtar>\" olarak yaz.")


class FaceitHatasi(Exception):
    pass


def _hata_metni(code: int, ne: str) -> str:
    if code == 401:
        return "FACEIT API anahtarı geçersiz (HTTP 401). ayarlar.json → faceit_api_anahtari'yi kontrol et."
    if code == 403:
        return f"FACEIT {ne} için izin vermedi (HTTP 403)."
    if code == 404:
        return f"FACEIT'te bulunamadı: {ne} (HTTP 404)."
    if code == 429:
        return "FACEIT istek sınırı doldu (HTTP 429); birkaç dakika sonra tekrar dene."
    return f"FACEIT hatası: {ne} (HTTP {code})."


class Faceit:
    """Küçük Data API istemcisi. `ac` testlerde taklit edilir (urllib.request.urlopen imzası)."""

    def __init__(self, anahtar: str, ac=urllib.request.urlopen):
        if not (anahtar or "").strip():
            raise FaceitHatasi(ANAHTAR_YOK)
        self.anahtar = anahtar.strip()
        self.ac = ac

    def _ac(self, url: str, veri: dict | None = None, yetki: bool = True):
        headers = {"Accept": "application/json", "User-Agent": "cs-klip"}
        if yetki:
            headers["Authorization"] = f"Bearer {self.anahtar}"
        body = None
        if veri is not None:
            body = json.dumps(veri).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=headers, method="POST" if body else "GET")
        return self.ac(req, timeout=TIMEOUT)

    def _json(self, url: str, ne: str, veri: dict | None = None) -> dict:
        try:
            with self._ac(url, veri) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise FaceitHatasi(_hata_metni(e.code, ne)) from e
        except urllib.error.URLError as e:
            raise FaceitHatasi(f"FACEIT'e ulaşılamadı: {e.reason}") from e
        except ValueError as e:
            raise FaceitHatasi(f"FACEIT'ten geçersiz yanıt: {ne}") from e

    def oyuncu_id(self, kullanici: str) -> str:
        data = self._json(f"{API}/players?nickname={quote(kullanici)}", f"'{kullanici}' adlı oyuncu")
        if not data.get("player_id"):
            raise FaceitHatasi(f"FACEIT'te '{kullanici}' bulunamadı; ayarlar.json → faceit_kullanici.")
        return data["player_id"]

    def son_maclar(self, player_id: str, adet: int) -> list[dict]:
        data = self._json(f"{API}/players/{player_id}/history?game=cs2&offset=0&limit={adet}", "maç geçmişi")
        items = data.get("items") or []
        return [m for m in items if m.get("match_id") and str(m.get("status", "finished")).lower() == "finished"]

    def demo_url(self, match_id: str) -> str | None:
        urls = self._json(f"{API}/matches/{match_id}", f"maç {match_id}").get("demo_url") or []
        return urls[0] if urls else None

    def imzali_link(self, demo_url: str) -> str:
        """Downloads API ile imzalı link; anahtarın bu izni yoksa demo_url'nin kendisi denenir."""
        try:
            data = self._json(DOWNLOAD_API, "demo indirme linki", {"resource_url": demo_url})
        except FaceitHatasi as e:
            if "HTTP 401" in str(e) or "HTTP 403" in str(e) or "HTTP 404" in str(e):
                return demo_url
            raise
        return (data.get("payload") or {}).get("download_url") or demo_url

    def indir(self, url: str, hedef: Path) -> Path:
        part = hedef.with_name(hedef.name + ".part")
        try:
            with self._ac(url, yetki=False) as r, open(part, "wb") as f:
                while chunk := r.read(CHUNK):
                    f.write(chunk)
        except urllib.error.HTTPError as e:
            part.unlink(missing_ok=True)
            if e.code in (401, 403):
                raise FaceitHatasi(
                    "Demo dosyası indirilemedi (HTTP %d). FACEIT demo indirmek için Downloads API izni ister: "
                    "developers.faceit.com'da uygulaman için 'Downloads API' erişimi iste." % e.code) from e
            raise FaceitHatasi(_hata_metni(e.code, "demo dosyası")) from e
        except (urllib.error.URLError, OSError) as e:
            part.unlink(missing_ok=True)
            raise FaceitHatasi(f"Demo indirilemedi: {getattr(e, 'reason', e)}") from e
        if part.stat().st_size == 0:
            part.unlink()
            raise FaceitHatasi("FACEIT boş demo dosyası verdi.")
        part.replace(hedef)
        return hedef


def dosya_adi(demo_url: str, match_id: str) -> str:
    """Demo URL'sinin son parçası (1-<maç>-1-1.dem.zst); uymuyorsa maç kimliğinden üretilir."""
    name = Path(urlparse(demo_url).path).name
    if name.lower().endswith(DEMO_SUFFIXES) and "/" not in name and "\\" not in name and not name.startswith("."):
        return name
    return f"{match_id}.dem.zst"


def son_demolari_indir(cfg: dict, hedef: Path, adet: int = 5, atla: set[str] | None = None,
                       istemci: Faceit | None = None, yaz=print) -> list[tuple[str, Path | None]]:
    """Son `adet` maçın demosunu `hedef` klasörüne indirir.

    `atla`: daha önce indirilmiş maç kimlikleri (indirilmez). Dönüş: (maç kimliği, dosya ya da None) — None,
    maçın demosu olmadığı ya da dosya zaten klasörde olduğu anlamına gelir; ikisi de yeniden denenmez.
    """
    api = istemci or Faceit(cfg.get("faceit_api_anahtari", ""))
    kullanici = cfg.get("faceit_kullanici") or cfg["oyuncu"]
    atla = atla or set()
    pid = api.oyuncu_id(kullanici)
    hedef.mkdir(parents=True, exist_ok=True)
    mevcut = {p.name.lower() for p in hedef.iterdir()}
    sonuc = []
    for m in api.son_maclar(pid, adet):
        mid = m["match_id"]
        if mid in atla:
            continue
        url = api.demo_url(mid)
        if not url:
            yaz(f"  {mid}: demo yok (FACEIT henüz yüklememiş olabilir)")
            continue  # sonra tekrar denensin
        ad = dosya_adi(url, mid)
        dem = ad[: -len(Path(ad).suffix)] if not ad.lower().endswith(".dem") else ad
        if ad.lower() in mevcut or dem.lower() in mevcut:
            yaz(f"  {mid}: zaten var ({ad})")
            sonuc.append((mid, None))
            continue
        yaz(f"  {mid}: indiriliyor → {hedef / ad}")
        sonuc.append((mid, api.indir(api.imzali_link(url), hedef / ad)))
    return sonuc
