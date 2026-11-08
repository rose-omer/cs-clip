from pathlib import Path

import pytest

from highlights import TICKRATE
from render import (
    DemoFailed,
    assign_parts,
    clip_filename,
    clip_seconds,
    concat_list,
    failure,
    record_demo,
    select_clips,
    video_args,
)

H = {"round": 4, "score": 12.5, "labels": ["1v3 clutch", "4K"], "start_tick": 22116, "end_tick": 25663}


def test_clip_seconds_from_tick_range():
    assert clip_seconds(H) == (25663 - 22116) / TICKRATE


def test_clip_seconds_sums_segments():
    h = {**H, "segments": [[0, 640], [2000, 2320]]}
    assert clip_seconds(h) == 15


def test_select_clips_filters_by_score_and_keeps_demo_order():
    clips = [
        {"round": 11, "score": 10.0, "start_tick": 82194, "end_tick": 84067},
        {"round": 6, "score": 1.0, "start_tick": 36409, "end_tick": 36921},
        H,
    ]
    assert [c["round"] for c in select_clips(clips, min_score=3)] == [4, 11]


def test_select_clips_limit_keeps_best_scores():
    clips = [{"round": r, "score": s, "start_tick": r * 100, "end_tick": r * 100 + 50}
             for r, s in [(1, 4), (2, 9), (3, 5), (4, 7)]]
    assert [c["round"] for c in select_clips(clips, min_score=3, limit=2)] == [2, 4]


def test_clip_filename_is_safe_for_windows_and_adds_weapon():
    name = clip_filename("anubis_59cf10f2", {**H, "labels": ['a/b:c*"d', "smoke arkası"], "weapons": ["ak47", "usp"]})
    assert name == "anubis_59cf10f2_R04_abcd_smoke-arkası_ak47.mp4"


def test_concat_list_escapes_quotes():
    text = concat_list([Path("C:/k/a.mp4"), Path("C:/k/it's.mp4")])
    assert text.splitlines() == ["file 'C:/k/a.mp4'", "file 'C:/k/it'\\''s.mp4'"]


def test_concat_list_makes_relative_paths_absolute(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert concat_list([Path("klipler/a.mp4")]) == f"file '{(tmp_path / 'klipler' / 'a.mp4').as_posix()}'"


def test_video_args_records_all_rounds_in_one_launch():
    args = video_args(Path("csdm.cmd"), Path("d.dem"), "765", [20, 5, 20], 3, 2, clean_hud=True)
    assert args[:3] == ["csdm.cmd", "video", "d.dem"]
    assert args[args.index("--rounds") + 1] == "5,20"
    assert args[args.index("--start-seconds-before") + 1] == "3"
    assert "--no-concatenate-sequences" in args and "--show-only-death-notices" in args
    assert "--no-player-voices" in args


def test_failure_finds_error_line():
    assert failure(["Starting Counter-Strike...", "Game error"]) == "Game error"
    assert failure(["Video generated in C:\\x"]) is None
    assert failure(["Match not found in database. Make sure the demo has been analyzed."])


def seq(tmp, n, a, b):
    p = tmp / f"sequence-{n}-tick-{a}-to-{b}.mp4"
    p.write_bytes(b"v")
    return p


def test_assign_parts_groups_by_nearest_highlight(tmp_path):
    clips = [{**H, "round": 5, "segments": [[1000, 1500], [3000, 3300]]},
             {**H, "round": 9, "segments": [[9000, 9400]]}]
    parts = [seq(tmp_path, 3, 9000, 9400), seq(tmp_path, 1, 1000, 1500), seq(tmp_path, 2, 3001, 3300)]
    got = assign_parts(parts, clips)
    assert [p.name for p in got[0]] == ["sequence-1-tick-1000-to-1500.mp4", "sequence-2-tick-3001-to-3300.mp4"]
    assert [p.name for p in got[1]] == ["sequence-3-tick-9000-to-9400.mp4"]


def test_record_demo_moves_single_parts_and_skips_existing(tmp_path):
    demo = tmp_path / "m.dem"
    demo.write_bytes(b"d")
    out = tmp_path / "klipler"
    out.mkdir()
    clips = [{**H, "round": 5, "labels": ["2K"], "segments": [[1000, 1500]]},
             {**H, "round": 9, "labels": ["3K"], "segments": [[9000, 9400]]}]
    (out / "x_R05_2K.mp4").write_bytes(b"old")
    calls = []

    def runner(cmd, env, timeout):
        calls.append(cmd)
        seq(tmp_path, 1, 9000, 9400)
        return 0, ["Video generated"]

    made = record_demo(demo, clips, "765", "x", out, Path("csdm"), None, 3, 2, True, runner=runner)
    assert [p.name for p in made] == ["x_R09_3K.mp4"]
    assert calls[0][calls[0].index("--rounds") + 1] == "9"
    assert (out / "x_R05_2K.mp4").read_bytes() == b"old"
    assert not list(tmp_path.glob("sequence-*.mp4"))


def test_record_demo_per_segment_launches_once_per_tick_range(tmp_path):
    demo = tmp_path / "m.dem"
    demo.write_bytes(b"d")
    out = tmp_path / "klipler"
    clips = [{**H, "round": 8, "labels": ["3K"], "segments": [[100, 420], [1700, 2020]]},
             {**H, "round": 12, "labels": ["2K"], "segments": [[5000, 5528]]}]
    calls = []

    def runner(cmd, env, timeout):
        calls.append(cmd)
        seq(tmp_path, 1, int(cmd[3]), int(cmd[4]))  # CSDM her açılışta sequence-1 yazar
        return 0, ["Video generated"]

    def fake_join(parts, dst, ffmpeg):
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(b"".join(p.read_bytes() for p in parts))
        for p in parts:
            p.unlink()
        return dst

    import render
    orig = render.join_parts
    render.join_parts = fake_join
    try:
        made = record_demo(demo, clips, "765", "x", out, Path("csdm"), None, 3, 2, True, runner=runner,
                           per_segment=True)
    finally:
        render.join_parts = orig
    assert [c[3:5] for c in calls] == [["100", "420"], ["1700", "2020"], ["5000", "5528"]]
    assert all(c[c.index("--focus-player") + 1] == "765" and "--mode" not in c for c in calls)
    assert all("--no-player-voices" in c for c in calls)
    assert [p.name for p in made] == ["x_R08_3K.mp4", "x_R12_2K.mp4"]


def test_record_demo_falls_back_to_segments_and_keeps_good_clips(tmp_path):
    demo = tmp_path / "m.dem"
    demo.write_bytes(b"d")
    out = tmp_path / "klipler"
    clips = [{**H, "round": 5, "labels": ["2K"], "segments": [[100, 420]]},
             {**H, "round": 13, "labels": ["2K"], "segments": [[5000, 5320], [6000, 6320]]},
             {**H, "round": 20, "labels": ["3K"], "segments": [[9000, 9320]]}]
    calls = []

    def runner(cmd, env, timeout):
        calls.append(cmd)
        if "--mode" in cmd:  # tek açılış: bir parça yazıp takılır
            seq(tmp_path, 2, 100, 420)
            return 1, ["Recording in progress...", "Zaman aşımı: CS2 takıldı, kapatıldı"]
        a = int(cmd[3])
        if a == 6000:  # R13'ün ikinci parçası takılır
            return 1, ["Zaman aşımı: CS2 takıldı, kapatıldı"]
        seq(tmp_path, 1, a, int(cmd[4]))
        return 0, ["Video generated"]

    made = record_demo(demo, clips, "765", "x", out, Path("csdm"), None, 3, 2, True, runner=runner)
    assert [p.name for p in made] == ["x_R05_2K.mp4", "x_R20_3K.mp4"]
    assert [c[3] for c in calls[1:]] == ["100", "5000", "6000", "9000"]
    assert not list(tmp_path.glob("sequence-*.mp4"))  # R13'ün yarım parçası ve tek açılış parçası silindi


def test_record_demo_raises_when_game_fails(tmp_path):
    demo = tmp_path / "m.dem"
    demo.write_bytes(b"d")
    with pytest.raises(DemoFailed, match="Game error"):
        record_demo(demo, [H], "765", "x", tmp_path / "k", Path("csdm"), None, 3, 2, True,
                    runner=lambda cmd, env, timeout: (0, ["Starting Counter-Strike...", "Game error"]))


def test_run_streaming_kills_hung_process():
    import sys
    from render import TIMEOUT_LINE, run_streaming

    code, lines = run_streaming([sys.executable, "-c", "print('basladi', flush=True); import time; time.sleep(30)"],
                                timeout=2)
    assert lines[0] == "basladi" and lines[-1] == TIMEOUT_LINE and failure(lines) == TIMEOUT_LINE


def test_record_timeout_grows_with_footage():
    from render import START_ALLOWANCE, record_timeout

    assert record_timeout([{**H, "segments": [[0, 640]]}]) == START_ALLOWANCE + 6 * 10
