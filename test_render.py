from pathlib import Path

from highlights import TICKRATE
from render import (
    clip_filename,
    clip_seconds,
    concat_list,
    move_when_ready,
    render_clips,
    seek_commands,
    select_clips,
)

H = {"round": 4, "score": 12.5, "labels": ["1v3 clutch", "4K"], "start_tick": 22116, "end_tick": 25663}


def test_seek_commands_jump_to_start_and_follow_player():
    cmds = seek_commands(22116, "DuranEnnmi")
    assert "demo_gototick 22116" in cmds
    assert 'spec_player "DuranEnnmi"' in cmds
    assert cmds.index("demo_gototick 22116") < cmds.index('spec_player "DuranEnnmi"')


def test_seek_commands_also_follow_by_account_id():
    cmds = seek_commands(100, "DuranEnnmi", steamid="76561198963443734")
    assert f"spec_player_by_accountid {76561198963443734 - 76561197960265728}" in cmds


def test_clip_seconds_from_tick_range():
    assert clip_seconds(H) == (25663 - 22116) / TICKRATE


def test_clip_seconds_sums_segments():
    h = {**H, "segments": [[0, 640], [2000, 2320]]}
    assert clip_seconds(h) == 15


def test_segmented_clip_pauses_recording_between_segments(tmp_path):
    con, rec = FakeConsole(), FakeRecorder(tmp_path)
    h = {**H, "segments": [[100, 740], [5000, 5320]]}
    render_clips([h], demo="d", player="p", out_dir=tmp_path / "k", con=con, rec=rec,
                 load_wait=0, clean_hud=False, sleep=lambda s: None)
    assert rec.events == ["start", "pause", "resume", "stop"]
    assert "demo_gototick 100" in con.sent and "demo_gototick 5000" in con.sent


def test_select_clips_filters_by_score_and_keeps_demo_order():
    clips = [
        {"round": 11, "score": 10.0, "start_tick": 82194, "end_tick": 84067},
        {"round": 6, "score": 1.0, "start_tick": 36409, "end_tick": 36921},
        H,
    ]
    assert [c["round"] for c in select_clips(clips, min_score=3)] == [4, 11]


def test_clip_filename_is_safe_for_windows():
    name = clip_filename("mac1", {**H, "labels": ['a/b:c*"d', "smoke arkası"]})
    assert name == "mac1_R04_abcd_smoke-arkası.mp4"


def test_concat_list_escapes_quotes():
    text = concat_list([Path("C:/k/a.mp4"), Path("C:/k/it's.mp4")])
    assert text.splitlines() == ["file 'C:/k/a.mp4'", "file 'C:/k/it'\\''s.mp4'"]


def test_move_when_ready_retries_until_file_is_free(tmp_path):
    src = tmp_path / "obs.mp4"
    src.write_bytes(b"video")
    dst = tmp_path / "out" / "klip.mp4"
    calls = {"n": 0}
    real_replace = Path.replace

    def flaky_replace(self, target):
        calls["n"] += 1
        if calls["n"] < 3:
            raise PermissionError("OBS dosyayı tutuyor")
        return real_replace(self, target)

    Path.replace = flaky_replace
    try:
        move_when_ready(src, dst, sleep=lambda s: None)
    finally:
        Path.replace = real_replace
    assert dst.read_bytes() == b"video"
    assert calls["n"] == 3


class FakeConsole:
    def __init__(self):
        self.sent = []

    def send(self, *cmds):
        self.sent.extend(cmds)


class FakeRecorder:
    def __init__(self, tmp):
        self.tmp = tmp
        self.n = 0
        self.recording = False
        self.events = []

    def start(self):
        assert not self.recording
        self.recording = True
        self.events.append("start")

    def pause(self):
        self.events.append("pause")

    def resume(self):
        self.events.append("resume")

    def stop(self):
        assert self.recording
        self.recording = False
        self.events.append("stop")
        self.n += 1
        f = self.tmp / f"obs{self.n}.mp4"
        f.write_bytes(b"v")
        return f


def test_render_clips_records_each_clip_and_restores_hud(tmp_path):
    con, rec = FakeConsole(), FakeRecorder(tmp_path)
    clips = [H, {**H, "round": 11, "labels": ["4K"], "start_tick": 82194, "end_tick": 84067}]
    out = render_clips(
        clips, demo="cs-klip/mac1", player="DuranEnnmi", out_dir=tmp_path / "klipler",
        con=con, rec=rec, load_wait=0, clean_hud=True, sleep=lambda s: None,
    )
    assert [p.name for p in out] == ["mac1_R04_1v3-clutch_4K.mp4", "mac1_R11_4K.mp4"]
    assert all(p.exists() for p in out)
    assert con.sent[0] == "cl_draw_only_deathnotices 1"
    assert "playdemo cs-klip/mac1" in con.sent
    assert con.sent[-1] == "cl_draw_only_deathnotices 0"
    assert con.sent.count("demo_resume") == 2


def test_render_clips_without_recorder_output_skips_move(tmp_path):
    class DryRecorder(FakeRecorder):
        def stop(self):
            super().stop()
            return None

    out = render_clips(
        [H], demo="d", player="p", out_dir=tmp_path, con=FakeConsole(), rec=DryRecorder(tmp_path),
        load_wait=0, clean_hud=False, sleep=lambda s: None,
    )
    assert out == []
