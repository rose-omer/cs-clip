"""Başa sarınca CS2'yi çökerten demoları onarır: ilk FullPacket'i sağlam demolardaki biçime getirir.

Sorun (NOTLAR.md, "Ancient çökmesi"): CS2 her demonun başında kendiliğinden tick 0'a sarar ve
ilk FullPacket'i ikinci kez uygular. Sağlam demolarda bu paket yalnız `userinfo` tablosu,
Tick ve PacketEntities içerir. Bazı FACEIT demolarında (sunucu kaydı geç başlattığında) aynı
pakette `instancebaseline`/`AnimAssetData` tabloları ve svc_UserCommands da var; CS2 bunları
ikinci kez uygularken engine2.dll'de çöker. Bu tablolar zaten signon'da ve demonun kendi
paketlerinde geliyor; ilk FullPacket'ten çıkarılınca demo sorunsuz oynuyor (CS2'de denendi).

Araç yalnız ilk FullPacket'i değiştirir, diğer her şeyi bayt bayt kopyalar ve yeni dosya yazar.

    python onarim.py <demo.dem> [--cikti onarilmis.dem] [--kontrol]

Yalnız stdlib kullanır (snappy açıcısı dahil).
"""

import argparse
import struct
import sys
from pathlib import Path

MAGIC = b"PBDEMS2\0"
DEM_STOP, DEM_FULLPACKET = 0, 13
COMPRESSED = 64
SVC_USERCOMMANDS = 76
# Sağlam demoların ilk FullPacket'inde yalnız bu tablo var.
FIRST_FULLPACKET_TABLES = {"userinfo"}
REPAIRED_SUFFIX = ".onarilmis.dem"


# --- düşük seviye kodlama -------------------------------------------------

def read_varint(b: bytes, i: int) -> tuple[int, int]:
    r = s = 0
    while True:
        c = b[i]
        i += 1
        r |= (c & 0x7F) << s
        s += 7
        if not c & 0x80:
            return r, i


def write_varint(v: int) -> bytes:
    out = bytearray()
    while True:
        c = v & 0x7F
        v >>= 7
        if v:
            out.append(c | 0x80)
        else:
            out.append(c)
            return bytes(out)


def snappy_decompress(src: bytes) -> bytes:
    n, i = read_varint(src, 0)
    out = bytearray()
    while i < len(src):
        tag = src[i]
        i += 1
        kind = tag & 3
        if kind == 0:
            ln = tag >> 2
            if ln >= 60:
                k = ln - 59
                ln = int.from_bytes(src[i:i + k], "little")
                i += k
            ln += 1
            out += src[i:i + ln]
            i += ln
            continue
        if kind == 1:
            ln = ((tag >> 2) & 7) + 4
            off = ((tag >> 5) << 8) | src[i]
            i += 1
        elif kind == 2:
            ln = (tag >> 2) + 1
            off = int.from_bytes(src[i:i + 2], "little")
            i += 2
        else:
            ln = (tag >> 2) + 1
            off = int.from_bytes(src[i:i + 4], "little")
            i += 4
        if off >= ln:
            out += out[-off:len(out) - off + ln]
        else:
            for _ in range(ln):
                out.append(out[-off])
    if len(out) != n:
        raise ValueError("snappy: boyut tutmuyor")
    return bytes(out)


def pb_fields(b: bytes) -> list[tuple[int, int, object]]:
    """Protobuf alanları (no, tel türü, değer); bilinmeyen alanlar korunur."""
    i, out = 0, []
    while i < len(b):
        key, i = read_varint(b, i)
        no, wt = key >> 3, key & 7
        if wt == 0:
            v, i = read_varint(b, i)
        elif wt == 2:
            ln, i = read_varint(b, i)
            v = b[i:i + ln]
            i += ln
        elif wt == 5:
            v = b[i:i + 4]
            i += 4
        elif wt == 1:
            v = b[i:i + 8]
            i += 8
        else:
            raise ValueError(f"protobuf tel türü {wt}")
        out.append((no, wt, v))
    return out


def pb_encode(fields: list[tuple[int, int, object]]) -> bytes:
    out = bytearray()
    for no, wt, v in fields:
        out += write_varint(no << 3 | wt)
        if wt == 0:
            out += write_varint(v)
        elif wt == 2:
            out += write_varint(len(v)) + v
        else:
            out += v
    return bytes(out)


def pb_get(fields, no):
    return next((v for n, _, v in fields if n == no), None)


def pb_replace(fields, no, value):
    return [(n, wt, value if n == no else v) for n, wt, v in fields]


class BitReader:
    def __init__(self, b: bytes):
        self.b, self.p = b, 0

    def read(self, n: int) -> int:
        q, r = self.p >> 3, self.p & 7
        v = (int.from_bytes(self.b[q:q + ((r + n + 7) >> 3)], "little") >> r) & ((1 << n) - 1)
        self.p += n
        return v

    def ubitvar(self) -> int:
        r = self.read(6)
        if r & 0x30 == 0x10:
            r = (r & 15) | (self.read(4) << 4)
        elif r & 0x30 == 0x20:
            r = (r & 15) | (self.read(8) << 4)
        elif r & 0x30 == 0x30:
            r = (r & 15) | (self.read(28) << 4)
        return r

    def varint(self) -> int:
        r = s = 0
        while True:
            c = self.read(8)
            r |= (c & 0x7F) << s
            s += 7
            if not c & 0x80:
                return r


class BitWriter:
    def __init__(self):
        self.v, self.n = 0, 0

    def write(self, value: int, bits: int) -> None:
        self.v |= (value & ((1 << bits) - 1)) << self.n
        self.n += bits

    def ubitvar(self, x: int) -> None:
        if x < 16:
            self.write(x, 6)
        elif x < 256:
            self.write((x & 15) | 0x10, 6)
            self.write(x >> 4, 4)
        elif x < 4096:
            self.write((x & 15) | 0x20, 6)
            self.write(x >> 4, 8)
        else:
            self.write((x & 15) | 0x30, 6)
            self.write(x >> 4, 28)

    def raw(self, b: bytes) -> None:
        self.write(int.from_bytes(b, "little"), 8 * len(b))

    def bytes(self) -> bytes:
        return self.v.to_bytes((self.n + 7) >> 3, "little")


def net_messages(data: bytes) -> tuple[list[tuple[int, int, int, bytes]], int]:
    """Paket bit akışındaki ağ mesajları: [(tür, başlangıç biti, bitiş biti, gövde)], son mesajın bitişi."""
    r = BitReader(data)
    out = []
    total = len(data) * 8
    while r.p + 8 <= total:
        start = r.p
        t = r.ubitvar()
        n = r.varint()
        if r.p + 8 * n > total:
            raise ValueError("ağ mesajı paketin dışına taşıyor")
        body = r.read(8 * n).to_bytes(n, "little") if n else b""
        out.append((t, start, r.p, body))
    return out, r.p


def copy_bits(w: BitWriter, data: bytes, start: int, end: int) -> None:
    if end > start:
        w.write(BitReader(data[start >> 3:]).read(end - start + (start & 7)) >> (start & 7), end - start)


# --- onarım ---------------------------------------------------------------

def drop_messages(data: bytes, types: set[int]) -> tuple[bytes, int]:
    """Bit akışından verilen türdeki ağ mesajlarını çıkarır: (yeni akış, silinen sayısı)."""
    msgs, _ = net_messages(data)
    if not any(t in types for t, *_ in msgs):
        return data, 0
    w = BitWriter()
    for t, start, stop, _ in msgs:
        if t not in types:
            copy_bits(w, data, start, stop)
    # Eski dolgu bitleri kopyalanmaz: hizalama değiştiği için 8+ bit kalıp sahte mesaj gibi okunabilir.
    # BitWriter son baytı sıfırla tamamlar (< 8 bit kalır, okuyucu orada durur).
    return w.bytes(), sum(t in types for t, *_ in msgs)


def table_name(table: bytes) -> str:
    return (pb_get(pb_fields(table), 1) or b"").decode("utf-8", "replace")


def fullpacket_problems(raw: bytes) -> list[str]:
    """İlk FullPacket'te sağlam demolarda olmayan şeyler."""
    full = pb_fields(raw)
    problems = [f"tablo {table_name(t)}" for no, _, t in pb_fields(pb_get(full, 1) or b"")
                if no == 1 and table_name(t) not in FIRST_FULLPACKET_TABLES]
    data = pb_get(pb_fields(pb_get(full, 2) or b""), 3) or b""
    if any(t == SVC_USERCOMMANDS for t, *_ in net_messages(data)[0]):
        problems.append("svc_UserCommands")
    return problems


def normalize_fullpacket(raw: bytes) -> bytes:
    """Fazla tabloları ve UserCommands mesajını çıkarır; diğer alanlar aynen kalır."""
    full = pb_fields(raw)
    tables = pb_get(full, 1)
    if tables is not None:
        kept = [(no, wt, t) for no, wt, t in pb_fields(tables)
                if no != 1 or table_name(t) in FIRST_FULLPACKET_TABLES]
        full = pb_replace(full, 1, pb_encode(kept))
    packet = pb_get(full, 2)
    if packet is not None:
        pkt = pb_fields(packet)
        data = pb_get(pkt, 3)
        if data is not None:
            full = pb_replace(full, 2, pb_encode(pb_replace(pkt, 3, drop_messages(data, {SVC_USERCOMMANDS})[0])))
    return pb_encode(full)


def first_fullpacket(b: bytes):
    """İlk FullPacket: (mesaj başı, bitişi, tick, açılmış gövde) ya da None."""
    if b[:8] != MAGIC:
        raise ValueError("CS2 demosu değil (PBDEMS2 başlığı yok)")
    i = 16
    while i < len(b):
        start = i
        cmd, i = read_varint(b, i)
        tick, i = read_varint(b, i)
        n, i = read_varint(b, i)
        end = i + n
        c = cmd & ~COMPRESSED
        if c == DEM_FULLPACKET:
            raw = b[i:end]
            return start, end, tick, snappy_decompress(raw) if cmd & COMPRESSED else raw
        if c == DEM_STOP:
            return None
        i = end
    return None


def find_problems(b: bytes) -> list[str]:
    """Değiştirmeden ilk FullPacket'teki sorunları listeler (boşsa onarım gerekmez)."""
    fp = first_fullpacket(b)
    return fullpacket_problems(fp[3]) if fp else []


def drop_usercommands(raw: bytes) -> bytes:
    """FullPacket'ten svc_UserCommands mesajlarını çıkarır (yalnız TrueView tahmini kullanır)."""
    full = pb_fields(raw)
    packet = pb_get(full, 2)
    if packet is None:
        return raw
    pkt = pb_fields(packet)
    data = pb_get(pkt, 3)
    if data is None:
        return raw
    new, n = drop_messages(data, {SVC_USERCOMMANDS})
    return pb_encode(pb_replace(full, 2, pb_encode(pb_replace(pkt, 3, new)))) if n else raw


def repair(b: bytes) -> tuple[bytes, list[str]]:
    """Demo baytlarını onarır: (yeni baytlar, sorunlar). Sorun yoksa aynı baytlar döner.

    İlk FullPacket sağlam biçime getirilir. Diğer FullPacket'lerden svc_UserCommands çıkarılır:
    bu demolarda geri sarınca eski komutlar yenilerin yerine geçiyor ve CS2 çöküyor
    (CSDM bir klipten sonrakine atlarken). Diğer her şey bayt bayt aynı kalır.
    """
    fp = first_fullpacket(b)
    problems = fullpacket_problems(fp[3]) if fp else []
    if not problems:
        return b, []
    out = bytearray(b[:16])
    i, first, delta = 16, True, 0
    offsets = struct.unpack_from("<ii", b, 8)
    moved = [0, 0]
    while i < len(b):
        start = i
        cmd, i = read_varint(b, i)
        tick, i = read_varint(b, i)
        n, i = read_varint(b, i)
        end = i + n
        c = cmd & ~COMPRESSED
        chunk = b[start:end]
        if c == DEM_FULLPACKET:
            raw = b[i:end]
            raw = snappy_decompress(raw) if cmd & COMPRESSED else raw
            new = normalize_fullpacket(raw) if first else drop_usercommands(raw)
            first = False
            if new is not raw:
                # Değişen mesaj sıkıştırılmadan yazılır (CS2 bunu destekler; dosyada zaten var).
                chunk = write_varint(DEM_FULLPACKET) + write_varint(tick) + write_varint(len(new)) + new
        for k, off in enumerate(offsets):
            if off > start:
                moved[k] = delta + len(chunk) - (end - start)
        delta += len(chunk) - (end - start)
        out += chunk
        i = end
        if c == DEM_STOP:
            out += b[i:]  # Stop'tan sonrası (FileInfo vb.) aynen
            break
    # Başlıktaki iki ofset (FileInfo vb.) dosya sonuna yakın; önlerindeki değişiklik kadar kayar.
    struct.pack_into("<ii", out, 8, *(off + m if off > 16 else off for off, m in zip(offsets, moved)))
    return bytes(out), problems


def is_repaired_copy(path: Path) -> bool:
    """Bu aracın yazdığı kopya mı (demo listelerinde ayrı maç gibi görünmesin)."""
    return Path(path).name.lower().endswith(REPAIRED_SUFFIX)


def repaired_path(demo: Path) -> Path:
    demo = Path(demo)
    return demo.with_name(demo.name[:-4] + REPAIRED_SUFFIX)


def ensure_repaired(demo: Path) -> tuple[Path, list[str]]:
    """Gerekirse onarılmış kopyayı yazar (varsa yeniden yazmaz): (kaydedilecek demo, sorunlar)."""
    demo = Path(demo)
    if is_repaired_copy(demo):
        return demo, []
    out = repaired_path(demo)
    data = demo.read_bytes()
    new, problems = repair(data)
    if not problems:
        return demo, []
    if not (out.exists() and out.stat().st_size == len(new)):
        tmp = out.with_suffix(".part")
        tmp.write_bytes(new)
        tmp.replace(out)
    return out, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("demo", type=Path)
    ap.add_argument("--cikti", type=Path, help="varsayılan: <ad>.onarilmis.dem")
    ap.add_argument("--kontrol", action="store_true", help="yalnız sorun var mı bak, dosya yazma")
    a = ap.parse_args(argv)
    if a.demo.suffix.lower() != ".dem":
        sys.exit("Açılmış .dem dosyası ver (önce klip.py --sadece-analiz ile açılır).")
    data = a.demo.read_bytes()
    new, problems = repair(data)
    if not problems:
        print(f"{a.demo.name}: ilk FullPacket sağlam, onarım gerekmiyor.")
        return 0
    print(f"{a.demo.name}: ilk FullPacket'te fazlalık: {', '.join(problems)}")
    if a.kontrol:
        return 1
    out = a.cikti or repaired_path(a.demo)
    if out.resolve() == a.demo.resolve():
        sys.exit("Çıktı orijinalin üstüne yazılamaz.")
    tmp = out.with_suffix(".part")
    tmp.write_bytes(new)
    tmp.replace(out)
    print(f"Onarıldı -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
