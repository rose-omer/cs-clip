"""cs-klip arayüzü: demo yükle, istatistikleri ve klipleri tarayıcıda gör.

Kullanım:  python arayuz.py [--port 8765] [--tarayici-acma] [--otomatik]
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
from urllib.parse import unquote, urlparse

import eniyi
import otomatik
import render
from analyze import analyze, save_json
from config import DEFAULTS, load_config, save_config, validate
from demofile import find_csgo_dir, open_demo
from klip import DEMO_SUFFIXES, clip_prefix, demo_id
from onarim import is_repaired_copy
from kontrol import find_ffmpeg, preflight
from render import clip_seconds, select_clips

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "arayuz"
UPLOADS = ROOT / "demos"
CHUNK = 1 << 20
LOG_LINES = 40


def match_code(did: str) -> str:
    """1-59cf10f2-…-1-1 -> 59cf10f2 (klip adlarındaki maç kodu)."""
    return clip_prefix("x", Path(did + ".dem")).split("_", 1)[1]


# Değişince önbellekteki analizler eskir: highlight listesi bu ayarlara, istatistikler oyuncuya bağlı.
HIGHLIGHT_KEYS = ("oyuncu", "once_sn", "sonra_sn")


class App:
    def __init__(self, cfg: dict, settings_path: Path | None = None):
        self.settings_path = Path(settings_path) if settings_path else ROOT / "ayarlar.json"
        self.folders: list[Path] = []
        self.apply_config(cfg)
        self.locks: dict[str, threading.Lock] = {}
        self.lock = threading.Lock()
        self.job = {"durum": "bos", "mesaj": "", "satirlar": [], "demo": None}
        self.montage_lock = threading.Lock()
        self.kilit = otomatik.KILIT  # otomatik kuyrukla paylaşılan kayıt kilidi
        self.oto_dosya = otomatik.DURUM_DOSYASI

    def apply_config(self, cfg: dict) -> None:
        self.cfg = cfg
        self.out_dir = (ROOT / cfg["cikti_klasoru"]).resolve()
        uploaded = UPLOADS in self.folders
        self.folders = [Path(f) for f in cfg["demo_klasorleri"]] or [Path.home() / "Downloads", UPLOADS]
        if uploaded and UPLOADS not in self.folders:
            self.folders.append(UPLOADS)

    # --- ayarlar ---
    def settings(self) -> dict:
        return {"ayarlar": self.cfg, "varsayilan": DEFAULTS, "dosya": str(self.settings_path)}

    def save_settings(self, data) -> dict:
        clean, errors = validate(data)
        if errors:
            raise ApiError(HTTPStatus.BAD_REQUEST, "Bazı ayarlar geçersiz: " + ", ".join(errors), alanlar=errors)
        with self.lock:
            old = self.cfg
            try:
                save_config(self.settings_path, clean)
            except (OSError, ValueError, SystemExit) as e:
                raise ApiError(HTTPStatus.INTERNAL_SERVER_ERROR, f"Ayarlar kaydedilemedi: {e}")
            # Çalışan ayarlar üzerine yalnız değişenler: dosyada olmayan alanlar (ör. demo klasörleri) kaybolmasın.
            cfg = {**old, **clean}
            self.apply_config(cfg)
        stale = [k for k in HIGHLIGHT_KEYS if old[k] != cfg[k]]
        cleared = self.clear_caches(stats=old["oyuncu"] != cfg["oyuncu"]) if stale else 0
        return {**self.settings(), "yeniden_analiz": cleared}

    def clear_caches(self, stats: bool) -> int:
        """Eskiyen analiz önbelleklerini siler; demo açılınca yeniden hesaplanır. Silinen demo sayısı."""
        n = 0
        for did, p in self.demos().items():
            files = [p.parent / f"{did}.highlights.json"] + ([p.parent / f"{did}.stats.json"] if stats else [])
            hit = False
            with self.demo_lock(did):
                for f in files:
                    if f.is_file():
                        f.unlink(missing_ok=True)
                        hit = True
            n += hit
        return n

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
            f = demo.with_suffix(".highlights.json")
            if f.exists() and f.stat().st_mtime >= demo.stat().st_mtime:
                return demo, json.loads(f.read_text(encoding="utf-8"))
            _, _, hl = analyze(demo, self.cfg["oyuncu"], self.cfg["once_sn"], self.cfg["sonra_sn"])
            save_json(demo, hl)
            return demo, hl

    def clips(self, did: str) -> dict:
        _, hl = self.highlights(did)
        files = {re.search(r"_R(\d+)_", p.name).group(1): p for p in self.clip_files(did) if re.search(r"_R(\d+)_", p.name)}
        shown = select_clips(hl, self.cfg["min_skor"])
        rows = []
        for h in sorted(shown, key=lambda h: h["score"], reverse=True):
            clip = files.get(f"{h['round']:02d}")
            rows.append({"round": h["round"], "score": h["score"], "labels": h["labels"], "weapons": h["weapons"],
                         "saniye": round(clip_seconds(h)), "klip": f"/klip/{clip.name}" if clip else None})
        job = dict(self.job) if self.job["demo"] == did else {"durum": "bos", "mesaj": "", "satirlar": []}
        job.pop("demo", None)
        return {"highlightlar": rows, "kayit": job}

    # --- en iyi klipler ---
    def best_clips(self) -> list[dict]:
        """Klipler skora göre; demosu ve highlights.json'u duranlar gerçek puanla (analiz başlatılmaz)."""
        by_code = {}
        for did, p in self.demos().items():
            by_code.setdefault(match_code(did), (did, p.parent / f"{did}.highlights.json"))
        return eniyi.best_clips(self.out_dir, by_code)

    def best(self) -> dict:
        return {"klipler": self.best_clips(), "montaj": eniyi.montage_info(self.out_dir)}

    def best_montage(self, count: int) -> dict:
        if not self.montage_lock.acquire(blocking=False):
            raise ApiError(HTTPStatus.CONFLICT, "Montaj sürüyor.")
        try:
            clips = self.best_clips()[:count]
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
                json.dumps({"adet": len(clips), "klipler": [c["ad"] for c in clips]}, ensure_ascii=False, indent=2),
                encoding="utf-8")
            info = eniyi.montage_info(self.out_dir)
            return {"klip": info["klip"], "adet": len(clips), "boyut_mb": info["boyut_mb"], "tarih": info["tarih"]}
        finally:
            self.montage_lock.release()

    # --- kayıt ---
    def start_recording(self, did: str, best: int) -> dict:
        with self.lock:
            if self.job["durum"] == "calisiyor":
                raise ApiError(HTTPStatus.CONFLICT, "Başka bir kayıt sürüyor.")
            if otomatik.kilit_dolu(self.kilit):
                raise ApiError(HTTPStatus.CONFLICT, "Otomatik kuyruk şu an kayıt yapıyor; bitince tekrar dene.")
            path = self.demo_path(did)
            csgo = Path(self.cfg["csgo_klasoru"]) if self.cfg["csgo_klasoru"] else find_csgo_dir()
            _, problems = preflight(self.cfg, csgo)
            if problems:
                raise ApiError(HTTPStatus.CONFLICT, "Kayıt başlayamaz: " + " ".join(problems))
            self.job = {"durum": "calisiyor", "mesaj": "Kayıt başladı", "satirlar": [], "demo": did}
        threading.Thread(target=self._record, args=(path, best), daemon=True).start()
        return {"durum": "calisiyor"}

    def _record(self, path: Path, best: int) -> None:
        env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
        cmd = [sys.executable, str(ROOT / "klip.py"), str(path), "--en-iyi", str(best),
               "--ayarlar", str(self.settings_path)]
        try:
            with otomatik.kayit_kilidi(self.kilit), subprocess.Popen(
                    cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                    text=True, encoding="utf-8", errors="replace",
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)) as p:
                for line in p.stdout:
                    if line.strip():
                        self.job["satirlar"] = (self.job["satirlar"] + [line.rstrip()])[-LOG_LINES:]
            ok = p.returncode == 0
            self.job.update(durum="bitti" if ok else "hata",
                            mesaj="Kayıt bitti" if ok else (self.job["satirlar"] or ["Kayıt başarısız"])[-1])
        except otomatik.Mesgul:
            self.job.update(durum="hata", mesaj="Otomatik kuyruk şu an kayıt yapıyor; bitince tekrar dene.")
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
    def __init__(self, status: HTTPStatus, message: str, **extra):
        super().__init__(message)
        self.status = status
        self.extra = extra


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
                self.send_json({"hata": str(e), **e.extra}, e.status)
            except SystemExit as e:  # analyze/stats kullanıcıya dönük hataları SystemExit ile verir
                self.send_json({"hata": str(e)}, HTTPStatus.UNPROCESSABLE_ENTITY)
            except Exception as e:  # sunucu çökmesin, hata sayfada görünsün
                self.send_json({"hata": f"Beklenmeyen hata: {e}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

        def do_GET(self):
            path = unquote(urlparse(self.path).path)
            if path == "/api/kontrol":
                def check():
                    csgo = Path(app.cfg["csgo_klasoru"]) if app.cfg["csgo_klasoru"] else find_csgo_dir()
                    problems = preflight(app.cfg, csgo)[1]
                    return {"hazir": not problems, "sorunlar": problems}
                return self.handle_api(check)
            if path == "/api/demolar":
                return self.handle_api(app.list_demos)
            if path == "/api/ayarlar":
                return self.handle_api(app.settings)
            if path == "/api/en-iyi":
                return self.handle_api(app.best)
            if path == "/api/otomatik":
                return self.handle_api(lambda: otomatik.ozet(app.oto_dosya, app.kilit))
            if m := re.fullmatch(r"/api/demo/([^/]+)/klipler", path):
                return self.handle_api(lambda: app.clips(m.group(1)))
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
                        best = int(json.loads(body or b"{}").get("en_iyi", 3))
                    except (ValueError, TypeError, AttributeError):
                        raise ApiError(HTTPStatus.BAD_REQUEST, "en_iyi sayı olmalı.")
                    return app.start_recording(m.group(1), best)
                return self.handle_api(start)
            if path == "/api/ayarlar":
                def save():
                    try:
                        data = json.loads(body or b"{}")
                    except ValueError:
                        raise ApiError(HTTPStatus.BAD_REQUEST, "Geçersiz JSON.")
                    return app.save_settings(data)
                return self.handle_api(save)
            if path == "/api/en-iyi/montaj":
                def montage():
                    try:
                        data = json.loads(body or b"{}")
                    except ValueError:
                        data = None
                    count = eniyi.parse_count(data)
                    if count is None:
                        raise ApiError(HTTPStatus.BAD_REQUEST, f"adet 1 ile {eniyi.MAX_COUNT} arasında bir sayı olmalı.")
                    return app.best_montage(count)
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
    ap.add_argument("--otomatik", action="store_true",
                    help="yeni demoları izle ve CS2/FACEIT kapalıyken sırayla kaydet (otomatik.py izle ile aynı)")
    args = ap.parse_args()

    mimetypes.add_type("video/mp4", ".mp4")
    mimetypes.add_type("text/javascript", ".js")
    app = App(load_config(args.ayarlar), args.ayarlar)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(app))
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Arayüz: {url}  (kapatmak için Ctrl+C)")
    if args.otomatik:
        threading.Thread(target=otomatik.calistir, args=(app.cfg, args.ayarlar), daemon=True).start()
    if not args.tarayici_acma:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
