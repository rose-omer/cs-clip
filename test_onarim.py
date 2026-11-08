import struct

import pytest

import onarim as d


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


def table(name, items=1):
    item = d.pb_encode([(1, 2, b"k"), (2, 2, b"veri")])
    return d.pb_encode([(1, 2, name.encode()), *[(2, 2, item)] * items])


def fullpacket(msgs, tables=("userinfo",)):
    st = d.pb_encode([(1, 2, table(n)) for n in tables])
    packet = d.pb_encode([(3, 2, bitstream(msgs))])
    return d.pb_encode([(1, 2, st), (2, 2, packet)])


def demo(*chunks, tail=b"FILEINFO"):
    body = bytearray()
    for cmd, tick, raw in chunks:
        body += d.write_varint(cmd) + d.write_varint(tick) + d.write_varint(len(raw)) + raw
    body += d.write_varint(0) + d.write_varint(5) + d.write_varint(0)
    off = 16 + len(body)
    return d.MAGIC + struct.pack("<ii", off, off - 2) + bytes(body) + tail


HEALTHY_FP = fullpacket([(4, b"\x08\x01"), (55, b"ents" * 50)])
BAD_FP = fullpacket([(4, b"\x08\x01"), (55, b"ents" * 50), (76, b"komut")],
                    tables=("instancebaseline", "userinfo", "AnimAssetData"))
LATER_FP = fullpacket([(4, b"\x08\x02"), (76, b"komut")], tables=("instancebaseline", "AnimAssetData"))


def read_chunk(b, i):
    cmd, i = d.read_varint(b, i)
    tick, i = d.read_varint(b, i)
    n, i = d.read_varint(b, i)
    return cmd, tick, b[i:i + n], i + n


def test_net_messages_roundtrip_unaligned_bits():
    msgs = [(4, b"\x01\x02"), (55, b"x" * 300), (76, b"abc")]
    assert [(t, body) for t, _, _, body in d.net_messages(bitstream(msgs))[0]] == msgs


def test_drop_messages_keeps_other_bodies():
    data, n = d.drop_messages(bitstream([(4, b"\x01"), (76, b"abc"), (55, b"x" * 30)]), {76})
    assert n == 1 and [(t, body) for t, _, _, body in d.net_messages(data)[0]] == [(4, b"\x01"), (55, b"x" * 30)]


def test_fullpacket_problems():
    assert d.fullpacket_problems(HEALTHY_FP) == []
    assert d.fullpacket_problems(BAD_FP) == ["tablo instancebaseline", "tablo AnimAssetData", "svc_UserCommands"]


def test_repair_normalizes_only_first_fullpacket():
    src = demo((7, 1, b"paket"), (d.DEM_FULLPACKET | d.COMPRESSED, 1, snappy_literal(BAD_FP)),
               (d.DEM_FULLPACKET, 3841, LATER_FP))
    out, problems = d.repair(src)
    assert problems == ["tablo instancebaseline", "tablo AnimAssetData", "svc_UserCommands"]
    assert out.endswith(b"FILEINFO")
    delta = len(out) - len(src)
    assert struct.unpack_from("<ii", out, 8) == tuple(v + delta for v in struct.unpack_from("<ii", src, 8))

    cmd, tick, raw, i = read_chunk(out, 16)
    assert (cmd, tick, raw) == (7, 1, b"paket")
    cmd, tick, raw, i = read_chunk(out, i)
    assert (cmd, tick) == (d.DEM_FULLPACKET, 1)  # sıkıştırılmadan yazıldı
    assert raw == HEALTHY_FP
    cmd, tick, raw, i = read_chunk(out, i)
    # sonraki paketlerde tablolar kalır, yalnız UserCommands çıkar
    assert (cmd, tick) == (d.DEM_FULLPACKET, 3841)
    assert raw == fullpacket([(4, b"\x08\x02")], tables=("instancebaseline", "AnimAssetData"))
    assert d.find_problems(out) == []


def test_repair_keeps_later_fullpacket_without_usercommands_byte_identical():
    plain = fullpacket([(4, b"\x08\x02")], tables=("instancebaseline",))
    src = demo((d.DEM_FULLPACKET, 1, BAD_FP), (d.DEM_FULLPACKET | d.COMPRESSED, 3841, snappy_literal(plain)))
    out, _ = d.repair(src)
    assert out.endswith(d.write_varint(d.DEM_FULLPACKET | d.COMPRESSED) + d.write_varint(3841)
                        + d.write_varint(len(snappy_literal(plain))) + snappy_literal(plain)
                        + d.write_varint(0) + d.write_varint(5) + d.write_varint(0) + b"FILEINFO")


def test_repair_leaves_healthy_demo_untouched():
    src = demo((d.DEM_FULLPACKET, 1, HEALTHY_FP), (d.DEM_FULLPACKET, 3841, LATER_FP))
    out, problems = d.repair(src)
    assert out is src and problems == []


def test_repair_rejects_non_demo():
    with pytest.raises(ValueError):
        d.repair(b"HL2DEMO\0" + b"\0" * 16)


def test_snappy_decompress_handles_copies():
    # "abcd" literal + 4 bayt geriden 8 baytlık (çakışan) kopya -> "abcdabcdabcd"
    src = d.write_varint(12) + bytes([3 << 2]) + b"abcd" + bytes([((8 - 4) << 2) | 1, 4])
    assert d.snappy_decompress(src) == b"abcdabcdabcd"


def test_ensure_repaired_writes_copy_once_and_keeps_original(tmp_path):
    src = demo((d.DEM_FULLPACKET, 1, BAD_FP))
    p = tmp_path / "mac.dem"
    p.write_bytes(src)
    got, problems = d.ensure_repaired(p)
    assert got == tmp_path / "mac.onarilmis.dem" and problems
    assert p.read_bytes() == src and d.find_problems(got.read_bytes()) == []
    mtime = got.stat().st_mtime_ns
    assert d.ensure_repaired(p)[0] == got and got.stat().st_mtime_ns == mtime
    assert d.ensure_repaired(got) == (got, [])


def test_ensure_repaired_skips_healthy(tmp_path):
    p = tmp_path / "mac.dem"
    p.write_bytes(demo((d.DEM_FULLPACKET, 1, HEALTHY_FP)))
    assert d.ensure_repaired(p) == (p, [])
    assert not (tmp_path / "mac.onarilmis.dem").exists()


def test_main_kontrol_does_not_write(tmp_path):
    p = tmp_path / "mac.dem"
    p.write_bytes(demo((d.DEM_FULLPACKET, 1, BAD_FP)))
    assert d.main([str(p), "--kontrol"]) == 1
    assert not (tmp_path / "mac.onarilmis.dem").exists()
    assert d.main([str(p)]) == 0 and (tmp_path / "mac.onarilmis.dem").exists()
