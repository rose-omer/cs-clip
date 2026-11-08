import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent / "araclar"))
import demo_onar as d  # noqa: E402


def entry(cmd, slot, expected, actual):
    inner = d.pb_encode([(1, 2, b"\x08\x01")])  # komut verisi (içeriği önemsiz)
    return d.pb_encode([(1, 2, inner), (2, 0, cmd), (3, 0, slot), (4, 0, expected), (5, 0, actual)])


def usercommands(*entries):
    return d.pb_encode([(1, 2, e) for e in entries])


def bitstream(msgs):
    w = d.BitWriter()
    for t, body in msgs:
        w.ubitvar(t)
        for byte in d.write_varint(len(body)):
            w.write(byte, 8)
        w.raw(body)
    return w.bytes()


def snappy_literal(b):
    """Testler için en basit snappy: tek literal blok."""
    n = len(b) - 1
    head = bytes([n << 2]) if n < 60 else bytes([61 << 2]) + n.to_bytes(2, "little")
    return d.write_varint(len(b)) + head + b


def fullpacket(msgs):
    packet = d.pb_encode([(3, 2, bitstream(msgs))])
    return d.pb_encode([(1, 2, b"\x0a\x00"), (2, 2, packet)])


def demo(*chunks, tail=b"FILEINFO"):
    body = bytearray()
    for cmd, tick, raw in chunks:
        body += d.write_varint(cmd) + d.write_varint(tick) + d.write_varint(len(raw)) + raw
    body += d.write_varint(0) + d.write_varint(5) + d.write_varint(0)
    off = 16 + len(body)
    return d.MAGIC + struct.pack("<ii", off, off - 2) + bytes(body) + tail


STALE = entry(44, 0, 6014, 627)
FRESH = entry(9262, 1, 9854, 9850)


def test_net_messages_roundtrip_unaligned_bits():
    msgs = [(4, b"\x01\x02"), (55, b"x" * 300), (76, b"abc")]
    got = [(t, body) for t, _, _, body in d.net_messages(bitstream(msgs))[0]]
    assert got == msgs


def test_clean_usercommands_drops_only_stale_entries():
    body, removed = d.clean_usercommands(usercommands(STALE, FRESH))
    assert [r[5] for r in removed] == [627]
    assert body == usercommands(FRESH)


def test_clean_usercommands_drops_message_when_all_stale():
    assert d.clean_usercommands(usercommands(STALE))[0] is None


def test_repair_removes_stale_command_from_compressed_fullpacket():
    fp = fullpacket([(4, b"\x08\x01"), (55, b"ents" * 50), (76, usercommands(STALE))])
    other = (7, 2, b"paket")
    src = demo((d.DEM_FULLPACKET | d.COMPRESSED, 1, snappy_literal(fp)), other)
    out, removed = d.repair(src)
    assert [(t, r[2]) for t, r in removed] == [(1, 44)]
    assert out.endswith(b"FILEINFO") and b"paket" in out
    # başlık ofsetleri boyut farkı kadar kaydı
    delta = len(out) - len(src)
    assert struct.unpack_from("<ii", out, 8) == tuple(v + delta for v in struct.unpack_from("<ii", src, 8))
    # onarılmış FullPacket sıkıştırılmamış yazıldı ve içinde UserCommands yok
    cmd, i = d.read_varint(out, 16)
    tick, i = d.read_varint(out, i)
    n, i = d.read_varint(out, i)
    assert (cmd, tick) == (d.DEM_FULLPACKET, 1)
    full = d.pb_fields(out[i:i + n])
    data = d.pb_get(d.pb_fields(d.pb_get(full, 2)), 3)
    assert [t for t, *_ in d.net_messages(data)[0]] == [4, 55]
    assert d.pb_get(full, 1) == b"\x0a\x00"
    assert d.find_stale(out) == []


def test_repair_leaves_healthy_demo_untouched():
    src = demo((d.DEM_FULLPACKET, 1, fullpacket([(4, b"\x08\x01"), (76, usercommands(FRESH))])))
    out, removed = d.repair(src)
    assert out is src and removed == []


def test_repair_rejects_non_demo():
    with pytest.raises(ValueError):
        d.repair(b"HL2DEMO\0" + b"\0" * 16)


def test_snappy_decompress_handles_copies():
    # "abcd" literal + 1 baytlık ofsetle 8 baytlık kopya (çakışan) -> "abcdabcdabcd"
    src = d.write_varint(12) + bytes([3 << 2]) + b"abcd" + bytes([((8 - 4) << 2) | 1, 4])
    assert d.snappy_decompress(src) == b"abcdabcdabcd"


def test_main_writes_new_file_and_keeps_original(tmp_path):
    src = demo((d.DEM_FULLPACKET, 1, fullpacket([(76, usercommands(STALE))])))
    p = tmp_path / "mac.dem"
    p.write_bytes(src)
    assert d.main([str(p), "--kontrol"]) == 1
    assert not (tmp_path / "mac.onarilmis.dem").exists()
    assert d.main([str(p)]) == 0
    assert p.read_bytes() == src
    assert d.find_stale((tmp_path / "mac.onarilmis.dem").read_bytes()) == []
