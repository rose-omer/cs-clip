"""Highlight kliplerini CS2 (netcon) + OBS (WebSocket) ile .mp4 olarak kaydeder."""

import re
import shutil
import socket
import subprocess
import threading
import time
from pathlib import Path

from highlights import TICKRATE

SEEK_WAIT = 3  # demo_gototick sonrası yüklenme payı (sn)
MOVE_TRIES = 20  # OBS dosyayı bırakana kadar deneme sayısı (0.5 sn arayla)


STEAMID64_BASE = 76561197960265728


def follow_commands(player: str, steamid: str | None = None) -> list[str]:
    """Kamerayı oyuncuya kilitler; hesap no. ile komut da gönderilir (adla çalışmazsa)."""
    cmds = [f'spec_player "{player}"']
    if steamid:
        cmds.append(f"spec_player_by_accountid {int(steamid) - STEAMID64_BASE}")
    return cmds


def seek_commands(tick: int, player: str, steamid: str | None = None) -> list[str]:
    """Tick'e atlayıp oyuncuyu izlemeye alan konsol komutları."""
    return ["demo_pause", f"demo_gototick {tick}", *follow_commands(player, steamid)]


def segments(h: dict) -> list[list[int]]:
    """Klibin kaydedilecek tick aralıkları (eski JSON'da tek aralık)."""
    return h.get("segments") or [[h["start_tick"], h["end_tick"]]]


def clip_seconds(h: dict) -> float:
    return sum(end - start for start, end in segments(h)) / TICKRATE


def select_clips(highlights: list[dict], min_score: float) -> list[dict]:
    """Skoru yeten klipleri demo sırasına göre döner (geri sarmayı azaltır)."""
    chosen = [h for h in highlights if h["score"] >= min_score]
    return sorted(chosen, key=lambda h: h["start_tick"])


def clip_filename(demo_stem: str, h: dict) -> str:
    labels = "_".join(re.sub(r'[<>:"/\\|?*]', "", label).replace(" ", "-") for label in h["labels"])
    return f"{demo_stem}_R{h['round']:02d}_{labels}.mp4" if labels else f"{demo_stem}_R{h['round']:02d}.mp4"


def concat_list(paths: list[Path]) -> str:
    """ffmpeg concat demuxer listesi."""
    return "\n".join("file '" + p.as_posix().replace("'", "'\\''") + "'" for p in paths)


def move_when_ready(src: Path, dst: Path, sleep=time.sleep) -> None:
    """OBS dosyayı kapatana kadar bekleyip taşır."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(MOVE_TRIES):
        try:
            src.replace(dst)
            return
        except PermissionError:
            if attempt == MOVE_TRIES - 1:
                raise
            sleep(0.5)


class Console:
    """CS2 -netconport üzerinden konsol komutu gönderir.

    CS2'nin konsol çıktısı arka planda okunup log dosyasına yazılır; okunmazsa
    TCP tamponu dolar ve oyun takılabilir.
    """

    def __init__(self, port: int, log_path: Path = Path("konsol.log")):
        try:
            self.sock = socket.create_connection(("127.0.0.1", port), timeout=5)
        except OSError as e:
            raise SystemExit(
                f"CS2 konsoluna bağlanılamadı (port {port}): {e}\n"
                f"CS2 açık mı? Başlatma seçeneklerinde '-netconport {port}' var mı?"
            ) from e
        self.sock.settimeout(None)
        self.log = open(log_path, "ab")
        threading.Thread(target=self._drain, daemon=True).start()

    def _drain(self) -> None:
        try:
            while chunk := self.sock.recv(65536):
                self.log.write(chunk)
                self.log.flush()
        except OSError:
            pass  # bağlantı kapandı; okunacak bir şey kalmadı

    def send(self, *cmds: str) -> None:
        for cmd in cmds:
            self.sock.sendall((cmd + "\n").encode())
            time.sleep(0.2)


class ObsRecorder:
    def __init__(self, host: str, port: int, password: str):
        import obsws_python as obs

        try:
            self.client = obs.ReqClient(host=host, port=port, password=password, timeout=5)
        except Exception as e:  # obsws bağlantı/kimlik hatalarını tek mesajda topla
            raise SystemExit(
                f"OBS'e bağlanılamadı ({host}:{port}): {e}\n"
                "OBS açık mı? Araçlar → WebSocket Sunucu Ayarları etkin mi? Şifre doğru mu?"
            ) from e
        if self.client.get_record_status().output_active:
            raise SystemExit("OBS zaten kayıtta. Kaydı durdurup tekrar dene.")

    def start(self) -> None:
        self.client.start_record()

    def pause(self) -> None:
        self.client.pause_record()

    def resume(self) -> None:
        self.client.resume_record()

    def stop(self) -> Path | None:
        return Path(self.client.stop_record().output_path)


class PrintConsole:
    """Prova: komutları yalnız ekrana yazar."""

    def send(self, *cmds: str) -> None:
        for cmd in cmds:
            print(f"  [cs2] {cmd}")


class PrintRecorder:
    def start(self) -> None:
        print("  [obs] kayıt başla")

    def pause(self) -> None:
        print("  [obs] kayıt duraklat")

    def resume(self) -> None:
        print("  [obs] kayıt sürdür")

    def stop(self) -> None:
        print("  [obs] kayıt dur")
        return None


def render_clips(
    clips: list[dict],
    demo: str,
    player: str,
    out_dir: Path,
    con,
    rec,
    load_wait: float,
    clean_hud: bool,
    sleep=time.sleep,
    steamid: str | None = None,
) -> list[Path]:
    """Klipleri sırayla kaydeder; oluşan dosyaların yollarını döner."""
    stem = Path(demo).name
    done: list[Path] = []
    if clean_hud:
        con.send("cl_draw_only_deathnotices 1")
    con.send("demo_timescale 1", f"playdemo {demo}")
    sleep(load_wait)

    for i, h in enumerate(clips, 1):
        print(f"[{i}/{len(clips)}] R{h['round']} {', '.join(h['labels'])} ({clip_seconds(h):.0f} sn)")
        for j, (start, end) in enumerate(segments(h)):
            con.send(*seek_commands(start, player, steamid))
            sleep(SEEK_WAIT)
            con.send("demo_resume", *follow_commands(player, steamid))
            if j == 0:
                rec.start()
            else:
                rec.resume()
            sleep((end - start) / TICKRATE)
            if j < len(segments(h)) - 1:
                rec.pause()  # demo, sonraki seek'teki demo_pause ile durur
        src = rec.stop()
        con.send("demo_pause")
        if src is None:
            continue
        dst = Path(out_dir) / clip_filename(stem, h)
        move_when_ready(src, dst, sleep=sleep)
        done.append(dst)
        print(f"   -> {dst}")

    con.send("disconnect")
    if clean_hud:
        con.send("cl_draw_only_deathnotices 0")
    return done


def make_montage(paths: list[Path], out: Path) -> Path | None:
    """Klipleri ffmpeg ile tek videoda birleştirir; ffmpeg yoksa None."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None or not paths:
        return None
    lst = out.with_suffix(".txt")
    lst.write_text(concat_list(paths), encoding="utf-8")
    subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)],
        check=True,
    )
    lst.unlink()
    return out
