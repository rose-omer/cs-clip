"""Paylaşılabilir video: kliplerden LinkedIn / TikTok / Reels'e hazır MP4 (CS2 gerekmez, yalnız ffmpeg).

Kullanım:
  python paylas.py --dikey --en-iyi 5                  # en iyi 5 klip, 9:16, açılış kartı + etiketler
  python paylas.py --en-iyi 10 --kalite 1440p --hedef-mb 80
  python paylas.py klipler/a.mp4 klipler/b.mp4 --dikey --yerlesim kirp --muzik sarki.mp3
  python paylas.py --dikey --en-iyi 3 --prova           # ffmpeg komutunu göster, üretme

Her klip yeniden kodlanır: istenen boyuta getirilir (yatay 16:9 ya da dikey 9:16; dikeyde oyun
görüntüsü ortadan kırpılır ya da bulanık arka planın ortasına yerleşir), köşesine "4K · 1v3 CLUTCH"
gibi etiket yazılır. Başa harita / skor / rating / ADR / oyuncu adlı 2-3 sn'lik açılış kartı gelir
(istatistikler demonun .stats.json'undan; yoksa yalnız harita ve oyuncu). Müzik verilirse oyun sesi
kısılıp altına karıştırılır. Çıktı klipler/paylasim/ altına yeni adla yazılır; klipler değişmez.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from pathlib import Path

import eniyi
from config import load_config
from kontrol import find_ffmpeg
from onarim import is_repaired_copy

ROOT = Path(__file__).resolve().parent
SHARE_DIR = "paylasim"  # çıktı klasörünün alt klasörü; eniyi.best_clips alt klasörlere bakmaz
FPS = 60
QUALITIES = {"1080p": 1080, "1440p": 1440}  # kısa kenar
LAYOUTS = ("bulanik", "kirp")
CARD_SECONDS = 2.5
DEFAULT_CRF = 20
CRF_RANGE = (14, 35)
AUDIO_KBPS = 192
MIN_VIDEO_KBPS = 400
MAX_TARGET_MB = 4000
FONT_CANDIDATES = ("segoeuib.ttf", "bahnschrift.ttf", "arialbd.ttf", "arial.ttf")
ACCENT = "0xFF9B2F"
SPECIAL_LABELS = ("wallbang", "noscope", "smoke arkası", "kör", "bıçak")
DEMO_SUFFIXES = (".dem", ".dem.zst", ".dem.gz", ".dem.bz2")


@dataclass
class Options:
    dikey: bool = False
    yerlesim: str = "bulanik"  # dikeyde: bulanik (bulanık arka plan) | kirp (ortadan kırp)
    kart: bool = True
    etiket: bool = True
    muzik: str = ""  # müzik dosyasının yolu; boşsa yok
    oyun_ses: float = 0.35  # müzik varken oyun sesi çarpanı
    muzik_ses: float = 0.8
    kalite: str = "1080p"
    crf: int = DEFAULT_CRF
    hedef_mb: float = 0  # >0 ise CRF yerine bu boyuta göre bit hızı

    @property
    def size(self) -> tuple[int, int]:
        return frame_size(self.dikey, self.kalite)


# Arayüz / API için: bu alanlardan biri gövdede varsa montaj paylaşım videosu olarak yeniden kodlanır.
OPTION_KEYS = tuple(f.name for f in fields(Options))


@dataclass
class Clip:
    path: Path
    duration: float
    has_audio: bool
    label: str = ""
    sublabel: str = ""


# --- saf yardımcılar ---

def frame_size(vertical: bool, quality: str) -> tuple[int, int]:
    """(genişlik, yükseklik): 1080p yatay 1920x1080, dikey 1080x1920; 1440p 2560x1440 / 1440x2560."""
    short = QUALITIES[quality]
    long = short * 16 // 9
    return (short, long) if vertical else (long, short)


def clip_label(labels: list[str], weapons: list[str] | None = None) -> str:
    """Köşe etiketi: "4K · 1v3 CLUTCH · WALLBANG". Kill/özel etiket yoksa silah ("AWP")."""
    parts = []
    kills = next((lb for lb in labels if lb == "ACE" or re.fullmatch(r"\dK", lb)), None)
    if kills:
        parts.append(kills)
    for lb in labels:
        if m := re.fullmatch(r"1v(\d) clutch", lb):
            parts.append(f"1v{m.group(1)} CLUTCH")
    parts += [lb.upper() for lb in labels if lb in SPECIAL_LABELS]
    if not parts and weapons:
        parts.append(weapon_name(weapons[0]))
    return " · ".join(parts)


def weapon_name(w: str) -> str:
    w = w.lower()
    pretty = {"m4a1_silencer": "M4A1-S", "m4a1": "M4A4", "usp_silencer": "USP-S", "ak47": "AK-47",
              "hegrenade": "HE", "ssg08": "SSG 08", "deagle": "DEAGLE"}
    if w.startswith("knife") or w == "bayonet":
        return "BIÇAK"
    return pretty.get(w, w.replace("_", " ").upper())


def clip_sublabel(row: dict) -> str:
    return f"{row['harita'].upper()} · R{row['round']}" if row.get("harita") else ""


def my_row(stats: dict) -> dict | None:
    return next((p for p in stats.get("oyuncular", []) if p.get("ben")), None)


def card_lines(player: str, maps: list[str], stats: list[dict], count: int) -> list[tuple[str, str]]:
    """Açılış kartının satırları: (metin, biçim). biçim: ad | harita | skor | bilgi | kucuk.

    maps: kliplerin haritaları (sırayla, tekrarsız); stats: bulunan .stats.json'lar (maç başına).
    """
    lines = [(player, "ad")]
    if len(maps) <= 1 and len(stats) <= 1:
        lines.append(((maps[0] if maps else (stats[0]["harita"] if stats else "")).removeprefix("de_").upper(),
                      "harita"))
        if stats:
            s = stats[0]
            mine = s.get("benim_takim", 0)
            teams = s.get("takimlar") or []
            if len(teams) == 2:
                a, b = teams[mine]["skor"], teams[1 - mine]["skor"]
                result = "GALİBİYET" if a > b else "MAĞLUBİYET" if a < b else "BERABERE"
                lines.append((f"{a} – {b}   {result}", "skor"))
            me = my_row(s)
            if me:
                lines.append((f"Rating {me['rating']:.2f}   ADR {me['adr']:.0f}   {me['kill']}/{me['death']}", "bilgi"))
    else:
        lines.append((f"EN İYİ {count} AN", "harita"))
        lines.append((" · ".join(m.removeprefix("de_").upper() for m in maps), "bilgi"))
        mine = [r for s in stats if (r := my_row(s))]
        if mine:
            rating = sum(r["rating"] for r in mine) / len(mine)
            adr = sum(r["adr"] for r in mine) / len(mine)
            lines.append((f"Ort. rating {rating:.2f}   ADR {adr:.0f}   ({len(mine)} maç)", "kucuk"))
    return [ln for ln in lines if ln[0]]


def video_kbps(target_mb: float, seconds: float, audio_kbps: int = AUDIO_KBPS) -> int:
    """Hedef dosya boyutu için video bit hızı (kbit/s); %3 kap payı düşülür."""
    total_kbits = target_mb * 8 * 1024 * 0.97
    return max(MIN_VIDEO_KBPS, int(total_kbits / max(seconds, 0.1) - audio_kbps))


def parse_options(body: dict) -> Options:
    """API gövdesinden seçenekler; geçersiz değerde ValueError (Türkçe mesaj)."""
    o = Options()
    if not isinstance(body, dict):
        return o
    for key in ("dikey", "kart", "etiket"):
        if key in body:
            if not isinstance(body[key], bool):
                raise ValueError(f"{key} true/false olmalı.")
            setattr(o, key, body[key])
    if "yerlesim" in body:
        if body["yerlesim"] not in LAYOUTS:
            raise ValueError(f"yerlesim {' / '.join(LAYOUTS)} olmalı.")
        o.yerlesim = body["yerlesim"]
    if "kalite" in body:
        if body["kalite"] not in QUALITIES:
            raise ValueError(f"kalite {' / '.join(QUALITIES)} olmalı.")
        o.kalite = body["kalite"]
    if "crf" in body:
        c = body["crf"]
        if isinstance(c, bool) or not isinstance(c, int) or not CRF_RANGE[0] <= c <= CRF_RANGE[1]:
            raise ValueError(f"crf {CRF_RANGE[0]} ile {CRF_RANGE[1]} arasında bir tam sayı olmalı.")
        o.crf = c
    if "hedef_mb" in body and body["hedef_mb"] not in (None, 0, ""):
        m = body["hedef_mb"]
        if isinstance(m, bool) or not isinstance(m, (int, float)) or not 1 <= m <= MAX_TARGET_MB:
            raise ValueError(f"hedef_mb 1 ile {MAX_TARGET_MB} arasında olmalı.")
        o.hedef_mb = float(m)
    for key in ("oyun_ses", "muzik_ses"):
        if key in body:
            v = body[key]
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 2:
                raise ValueError(f"{key} 0 ile 2 arasında olmalı.")
            setattr(o, key, float(v))
    if body.get("muzik"):
        if not isinstance(body["muzik"], str):
            raise ValueError("muzik bir dosya yolu olmalı.")
        p = Path(body["muzik"].strip().strip('"'))
        if not p.is_file():
            raise ValueError(f"Müzik dosyası bulunamadı: {p}")
        o.muzik = str(p)
    return o


def wants_share(body) -> bool:
    """Gövdede paylaşım seçeneği var mı (yoksa eski hızlı montaj)."""
    return isinstance(body, dict) and (body.get("paylasim") is True or any(k in body for k in OPTION_KEYS))


def output_name(opts: Options, stamp: str | None = None) -> str:
    """Komut satırı için yeni ad (üzerine yazmaz): paylas_dikey_1080p_20261108-153000.mp4"""
    stamp = stamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"paylas_{'dikey' if opts.dikey else 'yatay'}_{opts.kalite}_{stamp}.mp4"


def api_output_name(opts: Options) -> str:
    """Arayüz montajı için sabit ad (her seferinde yenisi üzerine yazılır)."""
    return f"en_iyi_{'dikey' if opts.dikey else 'yatay'}.mp4"


# --- ffmpeg filtre grafiği ---

def ff_path(p: Path | str) -> str:
    """drawtext seçeneği için yol: C:/x -> 'C\\:/x' (iki nokta seçenek ayırıcısı)."""
    s = Path(p).as_posix().replace("\\", "/").replace(":", r"\:").replace("'", r"'\''")
    return f"'{s}'"


def find_font() -> Path | None:
    fonts = Path(r"C:\Windows\Fonts")
    return next((fonts / f for f in FONT_CANDIDATES if (fonts / f).is_file()), None)


def _fit(w: int, h: int, opts: Options, src: str, out: str, n: int) -> str:
    """Kaynağı w x h'ye getiren zincir (çıkışı [out])."""
    if not opts.dikey:
        return (f"[{src}]scale={w}:{h}:force_original_aspect_ratio=decrease,"
                f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1[{out}]")
    if opts.yerlesim == "kirp":
        return f"[{src}]scale=-2:{h},crop={w}:{h},setsar=1[{out}]"
    sw, sh = w // 4 // 2 * 2, h // 4 // 2 * 2  # bulanıklığı küçük karede yap: hızlı
    return (f"[{src}]split[bg{n}][fg{n}];"
            f"[bg{n}]scale=-2:{sh},crop={sw}:{sh},gblur=sigma=12,eq=brightness=-0.12:saturation=0.8,"
            f"scale={w}:{h},setsar=1[bb{n}];"
            f"[fg{n}]scale={w}:-2,setsar=1[ff{n}];"
            f"[bb{n}][ff{n}]overlay=(W-w)/2:(H-h)/2[{out}]")


def _text(textfile: str, font: Path, size: int, x: str, y: str, color: str = "white", box: str = "") -> str:
    return (f"drawtext=fontfile={ff_path(font)}:textfile={ff_path(textfile)}:expansion=none:"
            f"fontsize={size}:fontcolor={color}:x={x}:y={y}" + (f":{box}" if box else ""))


def label_position(w: int, h: int, opts: Options) -> tuple[str, str, int]:
    """Etiketin x, y ifadesi ve yazı boyu."""
    u = min(w, h) / 1080
    if not opts.dikey:
        return str(int(48 * u)), str(int(44 * u)), int(50 * u)
    if opts.yerlesim == "bulanik":
        video_top = (h - w * 9 / 16) / 2
        return "(w-text_w)/2", str(int(video_top - 200 * u)), int(64 * u)
    return "(w-text_w)/2", str(int(h * 0.14)), int(64 * u)


def build_filter(clips: list[Clip], opts: Options, lines: list[tuple[str, str]], font: Path,
                 workdir: Path, n_inputs: dict) -> tuple[str, float]:
    """filter_complex metni ve toplam süre.

    n_inputs: {"kart_bg": giriş, "kart_ses": giriş, "sessiz": {klip sırası: giriş}, "muzik": giriş}.
    """
    w, h = opts.size
    u = min(w, h) / 1080
    parts, segs = [], []
    total = 0.0

    def write(name: str, text: str) -> str:
        f = workdir / name
        f.write_text(text, encoding="utf-8")
        return str(f)

    if opts.kart and lines:
        bg = n_inputs["kart_bg"]
        frames = round(CARD_SECONDS * FPS)
        fill = Options(dikey=opts.dikey, yerlesim="kirp", kalite=opts.kalite)  # kart arka planı hep tam dolu
        parts.append(f"[{bg}:v]trim=end_frame=1,setpts=PTS-STARTPTS[kc0]")
        parts.append(_fit(w, h, fill, "kc0", "kc1", 900))
        styles = {"ad": (96, "white"), "harita": (72, ACCENT), "skor": (60, "white"),
                  "bilgi": (46, "0xE6E6E6"), "kucuk": (36, "0xB4B4B4")}
        gap = 34 * u
        heights = [styles[s][0] * u for _, s in lines]
        y = h / 2 - (sum(heights) + gap * (len(lines) - 1)) / 2
        draws = []
        for k, (text, style) in enumerate(lines):
            size, color = styles[style]
            tf = write(f"kart_{k}.txt", text)
            draws.append(_text(tf, font, int(size * u), "(w-text_w)/2", str(int(y)), color))
            if style == "ad":  # adın altında turuncu çizgi
                draws.append(f"drawbox=x=(iw-{int(120 * u)})/2:y={int(y + heights[k] + gap * 0.35)}:"
                             f"w={int(120 * u)}:h={max(2, int(6 * u))}:color={ACCENT}:t=fill")
            y += heights[k] + gap
        parts.append(
            f"[kc1]gblur=sigma={int(18 * u)},eq=brightness=-0.32:saturation=0.55,"
            f"loop=loop={frames - 1}:size=1:start=0,setpts=N/{FPS}/TB,fps={FPS},"
            + ",".join(draws)
            + f",fade=t=in:st=0:d=0.3,fade=t=out:st={CARD_SECONDS - 0.35:.2f}:d=0.35,format=yuv420p[vk]")
        parts.append(f"[{n_inputs['kart_ses']}:a]atrim=0:{CARD_SECONDS},asetpts=PTS-STARTPTS[ak]")
        segs.append("[vk][ak]")
        total += CARD_SECONDS

    lx, ly, lsize = label_position(w, h, opts)
    box = f"box=1:boxcolor=black@0.55:boxborderw={int(lsize * 0.35)}"
    for i, c in enumerate(clips):
        parts.append(_fit(w, h, opts, f"{i}:v", f"f{i}", i))
        chain = f"[f{i}]fps={FPS},trim=duration={c.duration:.3f},setpts=PTS-STARTPTS"
        if opts.etiket and c.label:
            alpha = "alpha='min(1,t/0.4)'"
            chain += "," + _text(write(f"etiket_{i}.txt", c.label), font, lsize, lx, ly, "white", box) + f":{alpha}"
            if c.sublabel:
                sub_y = f"{ly}+{int(lsize * 1.55)}"
                chain += "," + _text(write(f"alt_{i}.txt", c.sublabel), font, int(lsize * 0.55),
                                     lx, sub_y, "0xDDDDDD", "shadowcolor=black@0.7:shadowx=2:shadowy=2") + f":{alpha}"
        parts.append(chain + f",format=yuv420p[v{i}]")
        src = f"{i}:a" if c.has_audio else f"{n_inputs['sessiz'][i]}:a"
        parts.append(f"[{src}]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{c.duration:.3f},"
                     f"apad=whole_dur={c.duration:.3f},asetpts=PTS-STARTPTS[a{i}]")
        segs.append(f"[v{i}][a{i}]")
        total += c.duration

    parts.append("".join(segs) + f"concat=n={len(segs)}:v=1:a=1[vout][acat]")
    if opts.muzik:
        m = n_inputs["muzik"]
        fade = max(0.0, total - 2.5)
        parts.append(f"[{m}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total:.3f},"
                     f"volume={opts.muzik_ses},afade=t=in:d=1,afade=t=out:st={fade:.3f}:d=2.5[mu]")
        parts.append(f"[acat]volume={opts.oyun_ses}[ga]")
        parts.append("[ga][mu]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
                     "alimiter=limit=0.95[aout]")
    else:
        parts.append("[acat]anull[aout]")
    return ";\n".join(parts), total


def build_command(ffmpeg: Path | str, clips: list[Clip], opts: Options, lines: list[tuple[str, str]],
                  font: Path, workdir: Path, out: Path) -> tuple[list[str], float]:
    """Tek ffmpeg komutu (filtre grafiği workdir/filtre.txt'de) ve toplam süre."""
    cmd = [str(ffmpeg), "-y", "-hide_banner", "-loglevel", "error", "-stats"]
    for c in clips:
        cmd += ["-i", str(c.path)]
    idx: dict = {"sessiz": {}}

    def add(name, args: list[str], key=None):
        nonlocal cmd
        n = sum(a == "-i" for a in cmd)
        cmd += args
        if key is None:
            idx[name] = n
        else:
            idx[name][key] = n

    silence = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    if opts.kart and lines:
        first = clips[0]
        add("kart_bg", ["-ss", f"{first.duration * 0.4:.2f}", "-i", str(first.path)])
        add("kart_ses", silence)
    for i, c in enumerate(clips):
        if not c.has_audio:
            add("sessiz", silence, i)
    if opts.muzik:
        add("muzik", ["-stream_loop", "-1", "-i", str(opts.muzik)])
    graph, total = build_filter(clips, opts, lines, font, workdir, idx)
    script = workdir / "filtre.txt"
    script.write_text(graph, encoding="utf-8")
    cmd += ["-/filter_complex", str(script), "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", str(FPS)]
    if opts.hedef_mb:
        kbps = video_kbps(opts.hedef_mb, total)
        cmd += ["-b:v", f"{kbps}k", "-maxrate", f"{int(kbps * 1.5)}k", "-bufsize", f"{kbps * 2}k"]
    else:
        cmd += ["-crf", str(opts.crf)]
    cmd += ["-c:a", "aac", "-b:a", f"{AUDIO_KBPS}k", "-ar", "48000", "-movflags", "+faststart",
            "-t", f"{total:.3f}", str(out)]
    return cmd, total


# --- dosyalar ---

def find_ffprobe(ffmpeg: Path | str) -> Path | None:
    p = Path(ffmpeg)
    cand = p.with_name(p.name.lower().replace("ffmpeg", "ffprobe"))
    if cand.is_file():
        return cand
    found = shutil.which("ffprobe")
    return Path(found) if found else None


def probe(ffprobe: Path | str, path: Path) -> tuple[float, bool]:
    """(video süresi sn, ses var mı)."""
    r = subprocess.run([str(ffprobe), "-v", "error", "-show_entries", "stream=codec_type,duration:format=duration",
                        "-of", "json", str(path)], capture_output=True, text=True, encoding="utf-8", check=True)
    data = json.loads(r.stdout)
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    if video is None:
        raise ValueError(f"{path.name}: görüntü yok")
    dur = float(video.get("duration") or data.get("format", {}).get("duration") or 0)
    return dur, any(s.get("codec_type") == "audio" for s in streams)


def demo_index(folders: list[Path]) -> dict[str, dict]:
    """maç kodu -> {"id", "highlights", "stats"} (demo klasörlerindeki demolardan; analiz başlatılmaz)."""
    out: dict[str, dict] = {}
    for folder in folders:
        if not Path(folder).is_dir():
            continue
        for p in Path(folder).iterdir():
            name = p.name.lower()
            suffix = next((s for s in sorted(DEMO_SUFFIXES, key=len, reverse=True) if name.endswith(s)), None)
            if not p.is_file() or suffix is None or is_repaired_copy(p):
                continue
            did = p.name[: -len(suffix)]
            code = (did.split("-")[1] if did.count("-") >= 2 else did)[:8]
            out.setdefault(code, {"id": did, "highlights": p.parent / f"{did}.highlights.json",
                                  "stats": p.parent / f"{did}.stats.json"})
    return out


def read_json(path: Path | None) -> dict | None:
    if path is None or not Path(path).is_file():
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def replace_retry(part: Path, out: Path, tries: int = 10, wait: float = 0.3) -> None:
    """Windows: oynatılan dosya kısa süre kilitli olabilir; olmazsa PermissionError."""
    for attempt in range(tries):
        try:
            part.replace(out)
            return
        except PermissionError:
            if attempt == tries - 1:
                raise
            time.sleep(wait)


def write_meta(out: Path, rows: list[dict], opts: Options) -> None:
    out.with_suffix(".json").write_text(json.dumps(
        {"adet": len(rows), "klipler": [r["ad"] for r in rows], "secenekler": asdict(opts)},
        ensure_ascii=False, indent=2), encoding="utf-8")


def share_info(out_dir: Path) -> list[dict]:
    """Arayüzün ürettiği paylaşım videoları (dikey / yatay), yeni önce."""
    d = Path(out_dir) / SHARE_DIR
    rows = []
    for vertical in (True, False):
        f = d / api_output_name(Options(dikey=vertical))
        if not f.is_file():
            continue
        meta = read_json(f.with_suffix(".json")) or {}
        st = f.stat()
        rows.append({"klip": f"/klip/{SHARE_DIR}/{f.name}", "adet": meta.get("adet"), "dikey": vertical,
                     "secenekler": meta.get("secenekler"), "boyut_mb": round(st.st_size / 1024**2, 1),
                     "tarih": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")})
    return sorted(rows, key=lambda r: r["tarih"], reverse=True)


def make_share_video(rows: list[dict], clip_dir: Path, out: Path, ffmpeg: Path | str, opts: Options,
                     player: str, stats_by_code: dict[str, dict] | None = None, dry_run: bool = False,
                     runner=subprocess.run) -> Path | list[str]:
    """Klip satırlarından (eniyi.clip_row biçimi) paylaşım videosu üretir; dry_run'da komutu döner.

    Önce out'un yanına .part.mp4 yazılır, bitince yerine taşınır.
    """
    if not rows:
        raise ValueError("Video için klip yok.")
    ffprobe = find_ffprobe(ffmpeg)
    if ffprobe is None:
        raise ValueError("ffprobe bulunamadı (ffmpeg ile birlikte gelir).")
    font = find_font()
    if font is None and (opts.kart or opts.etiket):
        raise ValueError("Yazı tipi bulunamadı (C:\\Windows\\Fonts).")
    stats_by_code = stats_by_code or {}
    clips = []
    for r in rows:
        path = Path(r.get("yol") or Path(clip_dir) / r["ad"])
        dur, has_audio = probe(ffprobe, path)
        clips.append(Clip(path, dur, has_audio, clip_label(r.get("etiketler", []), r.get("silahlar", [])),
                          clip_sublabel(r)))
    maps = list(dict.fromkeys(r["harita"] for r in rows if r.get("harita")))
    codes = list(dict.fromkeys(r.get("kod") for r in rows if r.get("kod")))
    stats = [stats_by_code[c] for c in codes if stats_by_code.get(c)]
    me = next((m for s in stats if (m := my_row(s))), None)
    lines = card_lines(me["ad"] if me else player, maps, stats, len(rows)) if opts.kart else []

    out = Path(out)
    part = out.with_name(out.stem + ".part.mp4")
    with tempfile.TemporaryDirectory(prefix="paylas_") as tmp:
        cmd, _ = build_command(ffmpeg, clips, opts, lines, font, Path(tmp), part)
        if dry_run:
            return cmd + ["# filtre:", (Path(tmp) / "filtre.txt").read_text(encoding="utf-8")]
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            runner(cmd, check=True)
            replace_retry(part, out)
        finally:
            part.unlink(missing_ok=True)
    return out


def rows_for_paths(paths: list[Path], index: dict[str, dict]) -> list[dict]:
    rows = []
    for p in paths:
        p = Path(p)
        info = eniyi.parse_name(p.name)
        demo = index.get(info["kod"]) if info else None
        real = eniyi._read_highlights(demo["highlights"]) if demo else None
        row = eniyi.clip_row(p, (demo["id"], demo["highlights"]) if demo else None, real)
        row = row or {"ad": p.name, "harita": "", "kod": "", "round": 0, "etiketler": [], "silahlar": []}
        rows.append(row | {"yol": str(p.resolve())})
    return rows


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kliplerden sosyal medyaya hazır video")
    ap.add_argument("klipler", type=Path, nargs="*", help="klip dosyaları (verilmezse --en-iyi)")
    ap.add_argument("--en-iyi", type=int, default=5, help="en iyi N klip (klip verilmezse; varsayılan 5)")
    ap.add_argument("--dikey", action="store_true", help="9:16 dikey (TikTok / Reels / Shorts)")
    ap.add_argument("--yerlesim", choices=LAYOUTS, default="bulanik",
                    help="dikeyde: bulanik = bulanık arka plan, kirp = ortadan kırp")
    ap.add_argument("--kartsiz", action="store_true", help="açılış kartı olmasın")
    ap.add_argument("--etiketsiz", action="store_true", help="kliplerde köşe etiketi olmasın")
    ap.add_argument("--muzik", type=Path, help="arka plan müziği (mp3, m4a, wav…)")
    ap.add_argument("--oyun-ses", type=float, default=0.35, help="müzik varken oyun sesi (0-2, varsayılan 0.35)")
    ap.add_argument("--muzik-ses", type=float, default=0.8, help="müzik sesi (0-2, varsayılan 0.8)")
    ap.add_argument("--kalite", choices=list(QUALITIES), default="1080p")
    ap.add_argument("--crf", type=int, default=DEFAULT_CRF, help=f"kalite (düşük = iyi, {CRF_RANGE[0]}-{CRF_RANGE[1]})")
    ap.add_argument("--hedef-mb", type=float, default=0, help="yaklaşık dosya boyutu (MB); CRF yerine")
    ap.add_argument("--cikti", type=Path, help="çıktı dosyası (varsayılan klipler/paylasim/paylas_….mp4)")
    ap.add_argument("--ayarlar", type=Path, default=ROOT / "ayarlar.json")
    ap.add_argument("--prova", action="store_true", help="üretmeden ffmpeg komutunu göster")
    args = ap.parse_args()

    cfg = load_config(args.ayarlar)
    out_dir = (ROOT / cfg["cikti_klasoru"]).resolve()
    try:
        opts = parse_options({"dikey": args.dikey, "yerlesim": args.yerlesim, "kart": not args.kartsiz,
                              "etiket": not args.etiketsiz, "muzik": str(args.muzik) if args.muzik else "",
                              "oyun_ses": args.oyun_ses, "muzik_ses": args.muzik_ses, "kalite": args.kalite,
                              "crf": args.crf, "hedef_mb": args.hedef_mb})
    except ValueError as e:
        raise SystemExit(str(e))
    folders = [Path(f) for f in cfg["demo_klasorleri"]] or [Path.home() / "Downloads", ROOT / "demos"]
    index = demo_index(folders)
    if args.klipler:
        missing = [p for p in args.klipler if not p.is_file()]
        if missing:
            raise SystemExit("Klip bulunamadı: " + ", ".join(map(str, missing)))
        rows = rows_for_paths(args.klipler, index)
    else:
        by_code = {c: (d["id"], d["highlights"]) for c, d in index.items()}
        rows = eniyi.best_clips(out_dir, by_code)[: max(1, args.en_iyi)]
        if not rows:
            raise SystemExit(f"{out_dir} içinde klip yok.")
    ffmpeg = find_ffmpeg(cfg["ffmpeg_yolu"])
    if ffmpeg is None:
        raise SystemExit("ffmpeg bulunamadı (winget install Gyan.FFmpeg ya da ayarlarda ffmpeg_yolu).")
    stats = {c: s for c, d in index.items() if (s := read_json(d["stats"]))}
    out = args.cikti or out_dir / SHARE_DIR / output_name(opts)

    print(f"{len(rows)} klip · {'dikey 9:16' if opts.dikey else 'yatay 16:9'} {opts.kalite}"
          f"{' · ' + opts.yerlesim if opts.dikey else ''}{' · müzik' if opts.muzik else ''}")
    for r in rows:
        print(f"  {r['ad']}  [{clip_label(r.get('etiketler', []), r.get('silahlar', []))}]")
    try:
        result = make_share_video(rows, out_dir, out, ffmpeg, opts, cfg["oyuncu"], stats, dry_run=args.prova)
    except (ValueError, subprocess.CalledProcessError) as e:
        raise SystemExit(f"Video üretilemedi: {e}")
    if args.prova:
        print("\n" + " ".join(result))
        return
    print(f"\nHazır: {result} ({result.stat().st_size / 1024**2:.1f} MB)")


if __name__ == "__main__":
    main()
