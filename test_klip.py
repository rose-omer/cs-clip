from klip import collect_demos, copy_to_csgo, safe_demo_name


def test_safe_demo_name_removes_spaces_and_symbols():
    assert safe_demo_name("mac 2 (final)şı") == "mac_2__final___"


def test_copy_to_csgo_uses_safe_name(tmp_path):
    demo = tmp_path / "mac 2.dem"
    demo.write_bytes(b"x" * 10)
    csgo = tmp_path / "csgo"
    csgo.mkdir()
    cmd = copy_to_csgo(demo, csgo)
    assert cmd == "cs-klip/mac_2"
    assert (csgo / "cs-klip" / "mac_2.dem").read_bytes() == b"x" * 10


def test_collect_demos_prefers_extracted_dem(tmp_path):
    for name in ["a.dem", "a.dem.zst", "b.dem.zst", "notlar.txt"]:
        (tmp_path / name).write_bytes(b"x")
    assert [p.name for p in collect_demos(tmp_path)] == ["a.dem", "b.dem.zst"]
