"""cs-klip arayüzü: demo yükle, istatistikleri ve klipleri tarayıcıda gör.

Kullanım:  python arayuz.py [--port 8765] [--tarayici-acma]
Yalnız bu bilgisayardan erişilir (127.0.0.1). Sayfa arayuz/ klasöründen sunulur.
"""

import argparse
import json
import mimetypes
import os
import re
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import eniyi
import render
from analyze import (TAG_PREFIX, analyze, analyze_all, analyze_player, highlights_path, player_tag, read_player,
                     save_json, save_player)
from config import load_config
from demofile import find_csgo_dir, open_demo
from klip import DEMO_SUFFIXES, clip_prefix
from onarim import is_repaired_copy
from kontrol import find_ffmpeg, preflight
from render import clip_seconds, select_clips

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "arayuz"
UPLOADS = ROOT / "demos"
CHUNK = 1 << 20
LOG_LINES = 40


def demo_id(path: Path) -> str:
    name = path.name
    for s in sorted(DEMO_SUFFIXES, key=len, reverse=True):
        if name.lower().endswith(s):
            return name[: -len(s)]
    return path.stem


def fresh(f: Path, demo: Path) -> bool:
    """Önbellek dosyası demodan yeni mi."""
    return f.exists() and f.stat().st_mtime >= demo.stat().st_mtime


def match_code(did: str) -> str:
    """1-59cf10f2-…-1-1 -> 59cf10f2 (klip adlarındaki maç kodu)."""
    return clip_prefix("x", Path(did + ".dem")).split("_", 1)[1]


class App:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.out_dir = (ROOT / cfg["cikti_klasoru"]).resolve()
        self.folders = [Path(f) for f in cfg["demo_klasorleri"]] or [Path.home() / "Downloads", UPLOADS]
        self.locks: dict[str, threading.Lock] = {}
        self.lock = threading.Lock()
        self.job = {"durum": "bos", "mesaj": "", "satirlar": [], "demo": None}
        self.montage_lock = threading.Lock()

    # --- demolar ---
    def demos(self) -> dict[str, Path]:
        """id -> en iyi dosya (.dem varsa o, yoksa arşiv)."""
        found: dict[str, Path] = {}
        for folder in self.folders:
            if not folder.is_dir():
                continue
            for p in folder.iterdir():
                if p.is_file() and p.name.lower().endswith(DEMO_SUFFIXES) and not is_repaired_copy(p):
                    did = demo_id(p)
                    if did not in found or p.suffix.lower() == ".dem":
                        found[did] = p
        return found

    def demo_path(self, did: str) -> Path:
        p = self.demos().get(did)
        if p is None:
            raise ApiError(HTTPStatus.NOT_FOUND, "Demo bulunamadı.")
        return p

    def demo_lock(self, did: str) -> threading.Lock:
        with self.lock:
            return self.locks.setdefault(did, threading.Lock())

    def cached_stats(self, path: Path) -> dict | None:
        f = path.with_name(demo_id(path) + ".stats.json")
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8"))
            except ValueError:
                return None
        return None

    def clip_files(self, did: str) -> list[Path]:
        if not self.out_dir.is_dir():
            return []
        return sorted(self.out_dir.glob(f"*_{match_code(did)}_R*.mp4"))

    def list_demos(self) -> list[dict]:
        rows = []
        for did, p in self.demos().items():
            st = p.stat()
            stats = self.cached_stats(p)
            rows.append({
                "id": did, "ad": p.name, "harita": stats.get("harita") if stats else None,
                "tarih": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                "boyut_mb": round(st.st_size / 1024**2, 1), "analiz_edildi": stats is not None,
                "klip_sayisi": len(self.clip_files(did)),
            })
        return sorted(rows, key=lambda r: r["tarih"], reverse=True)

    def stats(self, did: str) -> dict:
        import stats as st  # ağır içe aktarma; yalnız gerektiğinde

        with self.demo_lock(did):
            demo = open_demo(self.demo_path(did))
            cached = st.load_stats(demo)
            if cached is not None:
                return cached
            result = st.match_stats(demo, self.cfg["oyuncu"])
            st.save_stats(demo, result)
            return result

    def highlights(self, did: str) -> tuple[Path, list[dict]]:
        with self.demo_lock(did):
            demo = open_demo(self.demo_path(did))
            f = highlights_path(demo)
            if fresh(f, demo):
                return demo, json.loads(f.read_text(encoding="utf-8"))
            _, _, hl = analyze(demo, self.cfg["oyuncu"], self.cfg["once_sn"], self.cfg["sonra_sn"])
            save_json(demo, hl)
            return demo, hl

    # --- oyuncular ---
    def default_player(self, did: str) -> dict:
        """Varsayılan oyuncunun {steamid, ad, varsayilan}; istatistik önbelleği yoksa steamid None."""
        stats = self.cached_stats(self.demo_path(did)) or {}
        sid = stats.get("oyuncu_steamid")
        name = next((p.get("ad") for p in stats.get("oyuncular", []) if str(p.get("steamid")) == str(sid)), None)
        return {"steamid": str(sid) if sid else None, "ad": name or self.cfg["oyuncu"], "varsayilan": True}

    def is_default(self, did: str, who: str | None) -> bool:
        if not who:
            return True
        return who.casefold() == str(self.cfg["oyuncu"]).casefold() or who == self.default_player(did)["steamid"]

    def player_highlights(self, did: str, who: str | None) -> dict:
        """{steamid, ad, varsayilan, highlights}. who: ad ya da SteamID64; boşsa varsayılan oyuncu.

        Diğer oyuncular <demo>.highlights.<steamid>.json'da önbelleklenir; varsayılan oyuncunun dosyası değişmez.
        """
        if self.is_default(did, who):
            return {**self.default_player(did), "highlights": self.highlights(did)[1]}
        with self.demo_lock(did):
            demo = open_demo(self.demo_path(did))
            if re.fullmatch(r"\d+", who) and fresh(f := highlights_path(demo, who), demo):
                data = read_player(f)
                if data and "steamid" in data:
                    return {"steamid": str(data["steamid"]), "ad": data.get("oyuncu") or who, "varsayilan": False,
                            "highlights": data["highlights"]}
            r = analyze_player(demo, who, self.cfg["once_sn"], self.cfg["sonra_sn"], default=self.cfg["oyuncu"])
            if not (r["varsayilan"] and fresh(highlights_path(demo), demo)):
                save_player(demo, r)
            return {k: r[k] for k in ("steamid", "ad", "varsayilan", "highlights")}

    def player_clip_files(self, did: str, tag: str | None) -> dict[int, Path]:
        """round -> klip dosyası; tag None ise varsayılan oyuncunun (etiketsiz) klipleri."""
        out = {}
        for p in self.clip_files(did):
            info = eniyi.parse_name(p.name)
            if info and (info["oyuncu"] or "").casefold() == (tag or "").casefold():
                out.setdefault(info["round"], p)
        return out

    def clip_rows(self, did: str, player: dict) -> list[dict]:
        tag = None if player["varsayilan"] else player_tag(player["ad"], player["steamid"])
        files = self.player_clip_files(did, tag)
        rows = []
        for h in sorted(select_clips(player["highlights"], self.cfg["min_skor"]), key=lambda h: h["score"], reverse=True):
            clip = files.get(int(h["round"]))
            rows.append({"round": h["round"], "score": h["score"], "labels": h["labels"], "weapons": h["weapons"],
                         "saniye": round(clip_seconds(h)), "klip": f"/klip/{clip.name}" if clip else None})
        return rows

    def clips(self, did: str, who: str | None = None) -> dict:
        player = self.player_highlights(did, who)
        rows = self.clip_rows(did, player)
        job = dict(self.job) if self.job["demo"] == did else {"durum": "bos", "mesaj": "", "satirlar": []}
        job.pop("demo", None)
        info = {k: player[k] for k in ("steamid", "ad", "varsayilan")}
        if not player["varsayilan"]:
            info["etiket"] = TAG_PREFIX + player_tag(player["ad"], player["steamid"])
        return {"highlightlar": rows, "kayit": job, "oyuncu": info}

    def everyone(self, did: str) -> dict:
        """Maçtaki her oyuncunun en iyi anı (skor eşiğini geçenlerden), en yüksek puan önce."""
        default = self.default_player(did)
        stats = self.cached_stats(self.demo_path(did)) or {}
        known = [str(p["steamid"]) for p in stats.get("oyuncular", []) if p.get("steamid")]
        with self.demo_lock(did):
            demo = open_demo(self.demo_path(did))
            others = [s for s in known if s != default["steamid"]]
            players = None
            if known and default["steamid"] and fresh(highlights_path(demo), demo) \
                    and all(fresh(highlights_path(demo, s), demo) for s in others):
                players = [{**default, "highlights": json.loads(highlights_path(demo).read_text(encoding="utf-8"))}]
                for s in others:
                    data = read_player(highlights_path(demo, s)) or {}
                    players.append({"steamid": s, "ad": data.get("oyuncu") or s, "varsayilan": False,
                                    "highlights": data.get("highlights", [])})
            if players is None:
                res = analyze_all(demo, self.cfg["once_sn"], self.cfg["sonra_sn"], default=self.cfg["oyuncu"])
                players = res["oyuncular"]
                for r in players:
                    if not (r["varsayilan"] and fresh(highlights_path(demo), demo)):
                        save_player(demo, r)
        rows = []
        for p in players:
            shown = self.clip_rows(did, p)
            rows.append({"steamid": p["steamid"], "ad": p["ad"], "varsayilan": p["varsayilan"],
                         "highlight_sayisi": len(shown), "en_iyi": shown[0] if shown else None})
        rows.sort(key=lambda r: (-(r["en_iyi"]["score"] if r["en_iyi"] else -1), str(r["ad"]).casefold()))
        return {"oyuncular": rows}

    # --- en iyi klipler ---
    def best_clips(self) -> list[dict]:
        """Klipler skora göre; demosu ve highlights.json'u duranlar gerçek puanla (analiz başlatılmaz)."""
        by_code = {}
        for did, p in self.demos().items():
            by_code.setdefault(match_code(did), (did, p.parent / f"{did}.highlights.json"))
        return eniyi.best_clips(self.out_dir, by_code)

    def best(self) -> dict:
        return {"klipler": self.best_clips(), "montaj": eniyi.montage_info(self.out_dir)}

    def best_montage(self, count: int, player: str | None = None) -> dict:
        """player: None = varsayılan oyuncunun klipleri, eniyi.ALL_PLAYERS = herkes, yoksa oyuncu etiketi."""
        if not self.montage_lock.acquire(blocking=False):
            raise ApiError(HTTPStatus.CONFLICT, "Montaj sürüyor.")
        try:
            clips = eniyi.by_player(self.best_clips(), player)[:count]
            if not clips:
                raise ApiError(HTTPStatus.CONFLICT, "Montaj için klip yok; önce klip kaydedin.")
            ffmpeg = find_ffmpeg(self.cfg["ffmpeg_yolu"])
            if ffmpeg is None:
                raise ApiError(HTTPStatus.CONFLICT,
                               "Montaj için ffmpeg bulunamadı (winget install Gyan.FFmpeg ya da ayarlarda ffmpeg_yolu).")
            out = self.out_dir / eniyi.MONTAGE_NAME
            part = out.with_name(out.stem + ".part.mp4")  # oynatılan montaj yarım dosyayla bozulmasın
            try:
                render.make_montage([self.out_dir / c["ad"] for c in clips], part, ffmpeg)
                if not part.is_file():
                    raise ApiError(HTTPStatus.INTERNAL_SERVER_ERROR, "Montaj üretilemedi.")
                for attempt in range(10):  # Windows: oynatılırken dosya kısa süre kilitli olabilir
                    try:
                        part.replace(out)
                        break
                    except PermissionError:
                        if attempt == 9:
                            raise ApiError(HTTPStatus.CONFLICT,
                                           "Montaj dosyası kullanımda (oynatılıyor olabilir); videoyu kapatıp tekrar deneyin.")
                        time.sleep(0.3)
            except subprocess.CalledProcessError as e:
                raise ApiError(HTTPStatus.INTERNAL_SERVER_ERROR, f"ffmpeg montajı birleştiremedi (çıkış kodu {e.returncode}).")
            finally:
                part.unlink(missing_ok=True)
            (self.out_dir / eniyi.MONTAGE_META).write_text(
                json.dumps({"adet": len(clips), "oyuncu": player, "klipler": [c["ad"] for c in clips]},
                           ensure_ascii=False, indent=2),
                encoding="utf-8")
            info = eniyi.montage_info(self.out_dir)
            return {"klip": info["klip"], "adet": len(clips), "oyuncu": player, "boyut_mb": info["boyut_mb"],
                    "tarih": info["tarih"]}
        finally:
            self.montage_lock.release()

    # --- kayıt ---
    def start_recording(self, did: str, best: int, player: str | None = None) -> dict:
        """player: ad ya da SteamID64 (klip.py --oyuncu); boşsa ayarlar.json'daki oyuncu."""
        with self.lock:
            if self.job["durum"] == "calisiyor":
                raise ApiError(HTTPStatus.CONFLICT, "Başka bir kayıt sürüyor.")
            path = self.demo_path(did)
            csgo = Path(self.cfg["csgo_klasoru"]) if self.cfg["csgo_klasoru"] else find_csgo_dir()
            _, problems = preflight(self.cfg, csgo)
            if problems:
                raise ApiError(HTTPStatus.CONFLICT, "Kayıt başlayamaz: " + " ".join(problems))
            self.job = {"durum": "calisiyor", "mesaj": "Kayıt başladı", "satirlar": [], "demo": did, "oyuncu": player}
        threading.Thread(target=self._record, args=(path, best, player), daemon=True).start()
        return {"durum": "calisiyor", "oyuncu": player}

    def record_command(self, path: Path, best: int, player: str | None = None) -> list[str]:
        cmd = [sys.executable, str(ROOT / "klip.py"), str(path), "--en-iyi", str(best)]
        return cmd + [f"--oyuncu={player}"] if player else cmd  # '=' ile: '-' ile başlayan ad bayrak sanılmasın

    def _record(self, path: Path, best: int, player: str | None = None) -> None:
        env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
        cmd = self.record_command(path, best, player)
        try:
            with subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                                  text=True, encoding="utf-8", errors="replace",
                                  creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)) as p:
                for line in p.stdout:
                    if line.strip():
                        self.job["satirlar"] = (self.job["satirlar"] + [line.rstrip()])[-LOG_LINES:]
            ok = p.returncode == 0
            self.job.update(durum="bitti" if ok else "hata",
                            mesaj="Kayıt bitti" if ok else (self.job["satirlar"] or ["Kayıt başarısız"])[-1])
        except OSError as e:
            self.job.update(durum="hata", mesaj=str(e))

    # --- yükleme ---
    def upload(self, name: str, length: int, stream) -> dict:
        name = Path(unquote(name)).name
        if not name.lower().endswith(DEMO_SUFFIXES):
            raise ApiError(HTTPStatus.BAD_REQUEST, "Yalnız .dem, .dem.zst, .dem.gz, .dem.bz2 yüklenebilir.")
        UPLOADS.mkdir(exist_ok=True)
        dst, tmp = UPLOADS / name, UPLOADS / (name + ".part")
        left = length
        with open(tmp, "wb") as f:
            while left > 0:
                chunk = stream.read(min(CHUNK, left))
                if not chunk:
                    break
                f.write(chunk)
                left -= len(chunk)
        if left:
            tmp.unlink(missing_ok=True)
            raise ApiError(HTTPStatus.BAD_REQUEST, "Yükleme yarıda kesildi.")
        tmp.replace(dst)
        if UPLOADS not in self.folders:
            self.folders.append(UPLOADS)
        return {"id": demo_id(dst)}


class ApiError(Exception):
    def __init__(self, status: HTTPStatus, message: str):
        super().__init__(message)
        self.status = status


def make_handler(app: App):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *args):  # sessiz; hatalar yine yazılır
            pass

        def send_json(self, obj, status=HTTPStatus.OK):
            body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def handle_api(self, fn):
            try:
                self.send_json(fn())
            except ApiError as e:
                self.send_json({"hata": str(e)}, e.status)
            except SystemExit as e:  # analyze/stats kullanıcıya dönük hataları SystemExit ile verir
                self.send_json({"hata": str(e)}, HTTPStatus.UNPROCESSABLE_ENTITY)
            except Exception as e:  # sunucu çökmesin, hata sayfada görünsün
                self.send_json({"hata": f"Beklenmeyen hata: {e}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

        def do_GET(self):
            url = urlparse(self.path)
            path = unquote(url.path)
            who = (parse_qs(url.query).get("oyuncu") or [""])[0].strip() or None
            if path == "/api/kontrol":
                def check():
                    csgo = Path(app.cfg["csgo_klasoru"]) if app.cfg["csgo_klasoru"] else find_csgo_dir()
                    problems = preflight(app.cfg, csgo)[1]
                    return {"hazir": not problems, "sorunlar": problems}
                return self.handle_api(check)
            if path == "/api/demolar":
                return self.handle_api(app.list_demos)
            if path == "/api/en-iyi":
                return self.handle_api(app.best)
            if m := re.fullmatch(r"/api/demo/([^/]+)/klipler", path):
                return self.handle_api(lambda: app.clips(m.group(1), who))
            if m := re.fullmatch(r"/api/demo/([^/]+)/herkes", path):
                return self.handle_api(lambda: app.everyone(m.group(1)))
            if m := re.fullmatch(r"/api/demo/([^/]+)", path):
                return self.handle_api(lambda: app.stats(m.group(1)))
            if path.startswith("/klip/"):
                return self.send_file(app.out_dir, path[len("/klip/"):])
            return self.send_file(WEB, path.lstrip("/") or "index.html")

        def do_POST(self):
            path = unquote(urlparse(self.path).path)
            length = int(self.headers.get("Content-Length") or 0)
            if path == "/api/yukle":
                name = self.headers.get("X-Dosya-Adi", "")
                return self.handle_api(lambda: app.upload(name, length, self.rfile))
            body = self.rfile.read(length) if length else b"{}"
            if m := re.fullmatch(r"/api/demo/([^/]+)/kaydet", path):
                def start():
                    try:
                        data = json.loads(body or b"{}")
                        best = int(data.get("en_iyi", 3))
                    except (ValueError, TypeError, AttributeError):
                        raise ApiError(HTTPStatus.BAD_REQUEST, "en_iyi sayı olmalı.")
                    player = data.get("oyuncu") or None
                    if player is not None and (not isinstance(player, str) or not player.strip() or len(player) > 64):
                        raise ApiError(HTTPStatus.BAD_REQUEST, "oyuncu bir ad ya da SteamID olmalı.")
                    return app.start_recording(m.group(1), best, player.strip() if player else None)
                return self.handle_api(start)
            if path == "/api/en-iyi/montaj":
                def montage():
                    try:
                        data = json.loads(body or b"{}")
                    except ValueError:
                        data = None
                    count = eniyi.parse_count(data)
                    if count is None:
                        raise ApiError(HTTPStatus.BAD_REQUEST, f"adet 1 ile {eniyi.MAX_COUNT} arasında bir sayı olmalı.")
                    ok, player = eniyi.parse_player(data)
                    if not ok:
                        raise ApiError(HTTPStatus.BAD_REQUEST, "oyuncu geçersiz.")
                    return app.best_montage(count, player)
                return self.handle_api(montage)
            self.send_json({"hata": "Bulunamadı."}, HTTPStatus.NOT_FOUND)

        def send_file(self, base: Path, rel: str):
            f = (base / rel).resolve()
            if base.resolve() not in f.parents or not f.is_file():
                return self.send_json({"hata": "Dosya bulunamadı."}, HTTPStatus.NOT_FOUND)
            size = f.stat().st_size
            start, end = 0, size - 1
            rng = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
            if rng and (rng.group(1) or rng.group(2)):
                if rng.group(1):
                    start = int(rng.group(1))
                    end = min(int(rng.group(2)), size - 1) if rng.group(2) else size - 1
                else:  # son N bayt
                    start = max(size - int(rng.group(2)), 0)
                if start > end:
                    self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                self.send_response(HTTPStatus.PARTIAL_CONTENT)
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            else:
                self.send_response(HTTPStatus.OK)
            ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            if ctype.startswith("text/") or ctype.endswith(("javascript", "json")):
                ctype += "; charset=utf-8"
            self.send_header("Content-Type", ctype)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(end - start + 1))
            self.end_headers()
            try:
                with open(f, "rb") as fh:
                    fh.seek(start)
                    left = end - start + 1
                    while left > 0 and (chunk := fh.read(min(CHUNK, left))):
                        self.wfile.write(chunk)
                        left -= len(chunk)
            except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                pass  # tarayıcı videoyu atladı/kapattı

    return Handler


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="cs-klip arayüzü")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--ayarlar", type=Path, default=ROOT / "ayarlar.json")
    ap.add_argument("--tarayici-acma", action="store_true", help="tarayıcıyı otomatik açma")
    args = ap.parse_args()

    mimetypes.add_type("video/mp4", ".mp4")
    mimetypes.add_type("text/javascript", ".js")
    app = App(load_config(args.ayarlar))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(app))
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Arayüz: {url}  (kapatmak için Ctrl+C)")
    if not args.tarayici_acma:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
