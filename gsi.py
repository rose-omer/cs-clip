"""CS2 Game State Integration (GSI): oyunun kendi gönderdiği durum bilgisini dinler.

GSI Valve'ın resmi özelliğidir: CS2, `game/csgo/cfg/gamestate_integration_*.cfg` dosyasındaki adrese her durum
değişiminde HTTP POST atar. Oyuna eklenti ya da enjeksiyon yoktur; FACEIT açıkken de çalışır.

Bu modül üç iş yapar:
- cfg dosyasını yazar (`cfg_yaz`),
- gelen durumlardan olay çıkarır: maç başladı, round başladı, maç bitti (`Izleyici`),
- yalnız 127.0.0.1'de dinleyen sunucuyu açar (`sunucu`).
"""

import json
import re
import secrets
import time
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Callable

CFG_ADI = "gamestate_integration_csklip.cfg"
YOL = "/gsi"
TOKEN_RE = re.compile(r'"token"\s+"([0-9a-f]+)"')


def cfg_metni(port: int, token: str) -> str:
    """CS2'nin okuduğu GSI cfg dosyası. buffer/throttle 0.1 sn: olay en geç ~0,2 sn sonra gelir."""
    return f'''"cs-klip"
{{
  "uri" "http://127.0.0.1:{port}{YOL}"
  "timeout" "1.1"
  "buffer" "0.1"
  "throttle" "0.1"
  "heartbeat" "10.0"
  "auth"
  {{
    "token" "{token}"
  }}
  "data"
  {{
    "provider" "1"
    "map" "1"
    "round" "1"
    "player_id" "1"
    "player_state" "1"
  }}
}}
'''


def cfg_yolu(csgo_dir: Path) -> Path:
    return Path(csgo_dir) / "cfg" / CFG_ADI


def cfg_token(csgo_dir: Path) -> str | None:
    """Yazılmış cfg'deki token; dosya yoksa None."""
    try:
        m = TOKEN_RE.search(cfg_yolu(csgo_dir).read_text(encoding="utf-8"))
    except OSError:
        return None
    return m.group(1) if m else None


def cfg_yaz(csgo_dir: Path, port: int) -> Path:
    """cfg dosyasını yazar. Var olan token korunur; port değiştiyse dosya güncellenir.

    CS2 cfg'yi yalnız açılışta okur: oyun açıksa değişiklik bir sonraki açılışta geçerli olur.
    """
    f = cfg_yolu(csgo_dir)
    if not f.parent.is_dir():
        raise FileNotFoundError(f"CS2 cfg klasörü yok: {f.parent}")
    token = cfg_token(csgo_dir) or secrets.token_hex(16)
    f.write_text(cfg_metni(port, token), encoding="utf-8")
    return f


@dataclass
class Olay:
    tur: str  # "mac_basladi" | "round_basladi" | "mac_bitti"
    zaman: float  # time.time(), olayın bu bilgisayara geldiği an
    harita: str = ""
    round: int = 0  # round_basladi: 1'den başlayan round numarası
    steamid: str = ""


@dataclass
class Izleyici:
    """Ardışık GSI durumlarından olay çıkarır. Ağdan bağımsızdır, testte doğrudan beslenir."""

    harita: str = ""
    mac_evresi: str = ""  # map.phase: warmup | live | intermission | gameover
    round_evresi: str = ""  # round.phase: freezetime | live | over
    son_durum: float = field(default=0.0)

    def besle(self, durum: dict, simdi: float | None = None) -> list[Olay]:
        simdi = time.time() if simdi is None else simdi
        self.son_durum = simdi
        steamid = str(durum.get("provider", {}).get("steamid", ""))
        harita_bilgisi = durum.get("map")
        olaylar: list[Olay] = []

        if not harita_bilgisi:  # ana menü: maçtan çıkıldı
            if self.mac_evresi == "live":
                olaylar.append(Olay("mac_bitti", simdi, self.harita, steamid=steamid))
            self.harita = self.mac_evresi = self.round_evresi = ""
            return olaylar

        harita = str(harita_bilgisi.get("name", ""))
        mac = str(harita_bilgisi.get("phase", ""))
        rnd = str(durum.get("round", {}).get("phase", ""))

        if harita != self.harita:
            if self.mac_evresi == "live":
                olaylar.append(Olay("mac_bitti", simdi, self.harita, steamid=steamid))
            self.mac_evresi = self.round_evresi = ""
        if mac == "live" and self.mac_evresi != "live":
            olaylar.append(Olay("mac_basladi", simdi, harita, steamid=steamid))
        if mac == "live" and rnd == "live" and self.round_evresi != "live":
            # map.round biten round sayısıdır: oynanan round'un numarası bir fazlası.
            no = int(harita_bilgisi.get("round", 0)) + 1
            olaylar.append(Olay("round_basladi", simdi, harita, no, steamid))
        if mac == "gameover" and self.mac_evresi == "live":
            olaylar.append(Olay("mac_bitti", simdi, harita, steamid=steamid))

        self.harita, self.mac_evresi, self.round_evresi = harita, mac, rnd
        return olaylar


def sunucu(port: int, token: str, izleyici: Izleyici, olay_geldi: Callable[[Olay], None]) -> HTTPServer:
    """GSI sunucusu (yalnız 127.0.0.1). serve_forever() çağıran başlatır."""

    class Isleyici(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802 (http.server adı)
            if self.path != YOL:
                return self._yanit(HTTPStatus.NOT_FOUND)
            try:
                uzunluk = int(self.headers.get("Content-Length", 0))
                durum = json.loads(self.rfile.read(min(uzunluk, 1_000_000)) or b"{}")
            except ValueError:
                return self._yanit(HTTPStatus.BAD_REQUEST)
            if not isinstance(durum, dict) or durum.get("auth", {}).get("token") != token:
                return self._yanit(HTTPStatus.FORBIDDEN)
            for olay in izleyici.besle(durum):
                olay_geldi(olay)
            self._yanit(HTTPStatus.OK)

        def _yanit(self, kod: HTTPStatus) -> None:
            self.send_response(kod)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, *args) -> None:  # her POST'u ekrana basmasın
            pass

    # Tek iş parçacıklı: durumlar geliş sırasıyla işlenir (Izleyici sıraya bağlı).
    return HTTPServer(("127.0.0.1", port), Isleyici)
