"""CS2 demosundaki bayat oyuncu komutlarını temizleyip onarılmış bir kopya yazar.

Sorun (NOTLAR.md, "Ancient çökmesi"): bazı FACEIT demolarında bir FullPacket'in içindeki
svc_UserCommands mesajında eski bir komut var (ör. tick 627, olması gereken ~6014). CS2 demo
başında kendiliğinden tick 0'a sararken bu FullPacket'i yükler, konsola
"full command 44 for slot 0 replaces newer baseline 5423" yazar ve ardından çöker.

Bu araç yalnız FullPacket'lerdeki bayat komut girdilerini çıkarır (girdisi kalmayan mesajı
siler), diğer her şeyi bayt bayt aynen kopyalar. Orijinal dosyaya dokunmaz.

    python araclar/demo_onar.py <demo.dem> [--cikti onarilmis.dem] [--kontrol]

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
# Komutun yürütüldüğü tick ile bekleneni arasındaki fark bundan büyükse bayat sayılır.
# Sağlam demolarda fark en çok birkaç tick; çöken demoda 5387.
STALE_TICKS = 128


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

def stale_entry(entry: bytes, limit: int = STALE_TICKS) -> bool:
    """UserCommands girdisi: alan 4 = beklenen tick, alan 5 = komutun tick'i."""
    f = pb_get_all(entry)
    return 4 in f and 5 in f and abs(f[4] - f[5]) > limit


def pb_get_all(b: bytes) -> dict:
    return {no: v for no, wt, v in pb_fields(b) if wt == 0}


def clean_usercommands(body: bytes, limit: int = STALE_TICKS) -> tuple[bytes | None, list[dict]]:
    """Bayat girdileri çıkarır. Dönen gövde None ise mesaj tamamen silinmeli."""
    fields = pb_fields(body)
    removed = [pb_get_all(v) for no, wt, v in fields if no == 1 and wt == 2 and stale_entry(v, limit)]
    if not removed:
        return body, []
    kept = [(no, wt, v) for no, wt, v in fields if not (no == 1 and wt == 2 and stale_entry(v, limit))]
    has_entries = any(no == 1 for no, _, _ in kept)
    return (pb_encode(kept) if has_entries else None), removed


def clean_packet_data(data: bytes, limit: int = STALE_TICKS) -> tuple[bytes, list[dict]]:
    """Ağ mesajı bit akışından bayat komutları temizler; değişiklik yoksa aynı baytları döner."""
    msgs, end = net_messages(data)
    w = BitWriter()
    removed_all = []
    changed = False
    for t, start, stop, body in msgs:
        if t == SVC_USERCOMMANDS:
            new, removed = clean_usercommands(body, limit)
            if removed:
                changed = True
                removed_all += removed
                if new is not None:
                    w.ubitvar(t)
                    for byte in write_varint(len(new)):
                        w.write(byte, 8)
                    w.raw(new)
                continue
        copy_bits(w, data, start, stop)
    if not changed:
        return data, []
    # Eski dolgu bitleri kopyalanmaz: hizalama değiştiği için 8+ bit kalıp sahte mesaj gibi okunabilir.
    # BitWriter son baytı sıfırla tamamlar (< 8 bit kalır, okuyucu orada durur).
    return w.bytes(), removed_all


def clean_fullpacket(raw: bytes, limit: int = STALE_TICKS) -> tuple[bytes, list[dict]]:
    full = pb_fields(raw)
    packet = pb_get(full, 2)
    if packet is None:
        return raw, []
    pkt = pb_fields(packet)
    data = pb_get(pkt, 3)
    if data is None:
        return raw, []
    new_data, removed = clean_packet_data(data, limit)
    if not removed:
        return raw, []
    return pb_encode(pb_replace(full, 2, pb_encode(pb_replace(pkt, 3, new_data)))), removed


def repair(b: bytes, limit: int = STALE_TICKS) -> tuple[bytes, list[tuple[int, dict]]]:
    """Demo baytlarını onarır: (yeni baytlar, [(tick, silinen girdi)]). Değişiklik yoksa aynı baytlar."""
    if b[:8] != MAGIC:
        raise ValueError("CS2 demosu değil (PBDEMS2 başlığı yok)")
    off1, off2 = struct.unpack_from("<ii", b, 8)
    out = bytearray(b[:16])
    i = 16
    removed_all = []
    delta = 0
    while i < len(b):
        start = i
        cmd, i = read_varint(b, i)
        tick, i = read_varint(b, i)
        n, i = read_varint(b, i)
        end = i + n
        c = cmd & ~COMPRESSED
        if c == DEM_FULLPACKET:
            raw = b[i:end]
            if cmd & COMPRESSED:
                raw = snappy_decompress(raw)
            new, removed = clean_fullpacket(raw, limit)
            if removed:
                # Yeni mesaj sıkıştırılmadan yazılır (CS2 bunu destekler; dosyada zaten var).
                chunk = write_varint(c) + write_varint(tick) + write_varint(len(new)) + new
                delta += len(chunk) - (end - start)
                out += chunk
                removed_all += [(tick, r) for r in removed]
                i = end
                continue
        out += b[start:end]
        i = end
        if c == DEM_STOP:
            out += b[i:]  # Stop'tan sonrası (FileInfo vb.) aynen
            break
    if not removed_all:
        return b, []
    struct.pack_into("<ii", out, 8, off1 + delta if off1 > 0 else off1, off2 + delta if off2 > 0 else off2)
    return bytes(out), removed_all


def find_stale(b: bytes, limit: int = STALE_TICKS) -> list[tuple[int, dict]]:
    """Değiştirmeden yalnız bayat komutları listeler."""
    return repair(b, limit)[1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("demo", type=Path)
    ap.add_argument("--cikti", type=Path, help="varsayılan: <ad>.onarilmis.dem")
    ap.add_argument("--kontrol", action="store_true", help="yalnız bayat komut var mı bak, dosya yazma")
    a = ap.parse_args(argv)
    if a.demo.suffix.lower() != ".dem":
        sys.exit("Açılmış .dem dosyası ver (önce klip.py --sadece-analiz ile açılır).")
    data = a.demo.read_bytes()
    new, removed = repair(data)
    for tick, r in removed:
        print(f"  FullPacket@{tick}: bayat komut slot {r.get(3, 0)}, komut {r.get(2)}, tick {r.get(5)} (beklenen {r.get(4)})")
    if not removed:
        print(f"{a.demo.name}: bayat komut yok, onarım gerekmiyor.")
        return 0
    if a.kontrol:
        print(f"{a.demo.name}: {len(removed)} bayat komut var.")
        return 1
    out = a.cikti or a.demo.with_name(a.demo.name[:-4] + ".onarilmis.dem")
    if out.resolve() == a.demo.resolve():
        sys.exit("Çıktı orijinalin üstüne yazılamaz.")
    tmp = out.with_suffix(".part")
    tmp.write_bytes(new)
    tmp.replace(out)
    print(f"{len(removed)} bayat komut temizlendi -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
