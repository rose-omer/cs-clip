"""Demo dosyasını açma ve CS2 kurulumunu bulma."""

import bz2
import gzip
import re
import shutil
import sys
from pathlib import Path

import zstandard

CS2_SUBDIR = Path("steamapps/common/Counter-Strike Global Offensive/game/csgo")

_OPENERS = {
    ".zst": lambda f: zstandard.ZstdDecompressor().stream_reader(f),
    ".gz": lambda f: gzip.GzipFile(fileobj=f),
    ".bz2": lambda f: bz2.BZ2File(f),
}


def open_demo(path: Path) -> Path:
    """Sıkıştırılmış demoyu yanına açar ve .dem yolunu döner; açılmışsa yeniden açmaz."""
    path = Path(path)
    opener = _OPENERS.get(path.suffix.lower())
    if opener is None:
        return path
    out = path.with_suffix("")  # mac.dem.zst -> mac.dem
    if out.suffix.lower() != ".dem":
        out = out.with_suffix(".dem")
    if out.exists() and out.stat().st_size > 0:
        return out
    tmp = out.with_suffix(".dem.part")
    with open(path, "rb") as f, opener(f) as src, open(tmp, "wb") as dst:
        shutil.copyfileobj(src, dst, 1 << 20)
    tmp.replace(out)
    return out


def library_paths(vdf_text: str) -> list[str]:
    """libraryfolders.vdf içindeki kütüphane yolları."""
    raw = re.findall(r'"path"\s+"((?:[^"\\]|\\.)*)"', vdf_text)
    return [p.replace("\\\\", "\\") for p in raw]


def steam_root() -> Path | None:
    """Kayıt defterinden Steam klasörü (yalnız Windows)."""
    if sys.platform != "win32":
        return None
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            return Path(winreg.QueryValueEx(key, "SteamPath")[0])
    except OSError:
        return None


def find_csgo_dir(root: Path | None = None) -> Path | None:
    """CS2'nin game/csgo klasörü; bulunamazsa None."""
    root = root or steam_root()
    if root is None:
        return None
    candidates = [root]
    vdf = root / "steamapps" / "libraryfolders.vdf"
    if vdf.exists():
        candidates += [Path(p) for p in library_paths(vdf.read_text(encoding="utf-8", errors="replace"))]
    for lib in candidates:
        if (lib / CS2_SUBDIR).is_dir():
            return lib / CS2_SUBDIR
    return None


def demo_files(demo: Path) -> list[Path]:
    """Bir demoya ait dosyalar: açılmış .dem, sıkıştırılmış hâli, highlight ve istatistik JSON'u."""
    demo = Path(demo)
    base = demo.with_suffix("")  # mac.dem -> mac
    names = [demo.name, *(base.name + ".dem" + s for s in _OPENERS), base.name + ".highlights.json",
             base.name + ".stats.json"]
    return [p for n in dict.fromkeys(names) if (p := demo.parent / n).exists()]


def to_recycle_bin(paths: list[Path]) -> bool:
    """Dosyaları Geri Dönüşüm Kutusu'na taşır (kalıcı silmez). Yalnız Windows."""
    paths = [Path(p).resolve() for p in paths if Path(p).exists()]
    if not paths or sys.platform != "win32":
        return False
    import ctypes
    from ctypes import wintypes

    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT), ("pFrom", wintypes.LPCWSTR),
                    ("pTo", wintypes.LPCWSTR), ("fFlags", ctypes.c_ushort), ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", ctypes.c_void_p), ("lpszProgressTitle", wintypes.LPCWSTR)]

    fo_delete, allow_undo, no_ui = 3, 0x40, 0x10 | 0x04 | 0x400  # NOCONFIRMATION | SILENT | NOERRORUI
    op = SHFILEOPSTRUCTW(wFunc=fo_delete, pFrom="\0".join(map(str, paths)) + "\0", fFlags=allow_undo | no_ui)
    return ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op)) == 0 and not op.fAnyOperationsAborted
