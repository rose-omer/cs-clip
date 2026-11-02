import bz2
import gzip

import zstandard

from demofile import CS2_SUBDIR, find_csgo_dir, library_paths, open_demo

DATA = b"PBDEMS2\x00" + b"x" * 1000


def test_plain_dem_is_returned_as_is(tmp_path):
    src = tmp_path / "a.dem"
    src.write_bytes(DATA)
    assert open_demo(src) == src


def test_compressed_demos_are_extracted_next_to_source(tmp_path):
    packers = {
        ".zst": zstandard.ZstdCompressor().compress,
        ".gz": gzip.compress,
        ".bz2": bz2.compress,
    }
    for suffix, pack in packers.items():
        src = tmp_path / f"m{suffix[1:]}.dem{suffix}"
        src.write_bytes(pack(DATA))
        out = open_demo(src)
        assert out == tmp_path / f"m{suffix[1:]}.dem"
        assert out.read_bytes() == DATA


def test_existing_extracted_demo_is_reused(tmp_path):
    src = tmp_path / "m.dem.gz"
    src.write_bytes(gzip.compress(DATA))
    out = open_demo(src)
    out.write_bytes(b"degisti")
    assert open_demo(src).read_bytes() == b"degisti"


VDF = r'''
"libraryfolders"
{
	"0"
	{
		"path"		"C:\\Program Files (x86)\\Steam"
		"apps" { "228980" "1" }
	}
	"1"
	{
		"path"		"D:\\SteamLibrary"
		"apps" { "730" "123" }
	}
}
'''


def test_library_paths_reads_all_paths():
    assert library_paths(VDF) == [r"C:\Program Files (x86)\Steam", r"D:\SteamLibrary"]


def test_find_csgo_dir_picks_library_that_has_cs2(tmp_path):
    steam = tmp_path / "steam"
    lib = tmp_path / "lib"
    (steam / "steamapps").mkdir(parents=True)
    (lib / CS2_SUBDIR).mkdir(parents=True)
    vdf = f'"libraryfolders" {{ "0" {{ "path" "{steam}" }} "1" {{ "path" "{lib}" }} }}'
    (steam / "steamapps" / "libraryfolders.vdf").write_text(vdf.replace("\\", "\\\\"))
    assert find_csgo_dir(steam) == lib / CS2_SUBDIR


def test_find_csgo_dir_returns_none_without_steam(tmp_path):
    assert find_csgo_dir(tmp_path / "yok") is None
