from pathlib import Path

from demofile import demo_files
from klip import clip_prefix, collect_demos


def test_collect_demos_prefers_extracted_dem(tmp_path):
    for name in ["a.dem", "a.dem.zst", "b.dem.zst", "notlar.txt"]:
        (tmp_path / name).write_bytes(b"x")
    assert [p.name for p in collect_demos(tmp_path)] == ["a.dem", "b.dem.zst"]


def test_clip_prefix_uses_map_and_match_code():
    assert clip_prefix("de_anubis", Path("1-59cf10f2-9122-41c4-89bc-2b28c64e0637-1-1.dem")) == "anubis_59cf10f2"
    assert clip_prefix("de_cache", Path("mac.dem")) == "cache_mac"


def test_demo_files_lists_dem_archive_and_json(tmp_path):
    for name in ["m.dem", "m.dem.zst", "m.highlights.json", "baska.dem"]:
        (tmp_path / name).write_bytes(b"x")
    assert sorted(p.name for p in demo_files(tmp_path / "m.dem")) == ["m.dem", "m.dem.zst", "m.highlights.json"]
