import shutil
import subprocess

import pytest

from render import make_montage

ffmpeg = shutil.which("ffmpeg")
ffprobe = shutil.which("ffprobe")


@pytest.mark.skipif(ffmpeg is None or ffprobe is None, reason="ffmpeg yok")
def test_montage_joins_clips(tmp_path):
    clips = []
    for i in range(2):
        p = tmp_path / f"c{i}.mp4"
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=d=1:s=64x64:r=30",
                        "-pix_fmt", "yuv420p", str(p)], check=True)
        clips.append(p)
    out = make_montage(clips, tmp_path / "montaj.mp4")
    probe = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(out)],
        capture_output=True, text=True, check=True,
    )
    assert 1.9 <= float(probe.stdout) <= 2.2
    assert not (tmp_path / "montaj.txt").exists()
