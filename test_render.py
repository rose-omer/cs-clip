import sys
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
    segment_args,
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
    # "C:/k" yalnız Windows'ta mutlak yol; Linux'ta aynı kontrol "/k" ile yapılır.
    root = "C:/k" if sys.platform == "win32" else "/k"
    text = concat_list([Path(f"{root}/a.mp4"), Path(f"{root}/it's.mp4")])
    assert text.splitlines() == [f"file '{root}/a.mp4'", f"file '{root}/it'\\''s.mp4'"]


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
        if cmd[4] == "6320":  # R13'ün ikinci parçası her başlangıçla takılır
            return 1, ["Zaman aşımı: CS2 takıldı, kapatıldı"]
        seq(tmp_path, 1, a, int(cmd[4]))
        return 0, ["Video generated"]

    made = record_demo(demo, clips, "765", "x", out, Path("csdm"), None, 3, 2, True, runner=runner)
    assert [p.name for p in made] == ["x_R05_2K.mp4", "x_R20_3K.mp4"]
    assert [c[3] for c in calls[1:]] == ["100", "5000", "6000", "5680", "9000"]  # 6000 bir de 5 sn erken
    assert not list(tmp_path.glob("sequence-*.mp4"))  # R13'ün yarım parçası ve tek açılış parçası silindi


def test_record_demo_raises_when_game_fails(tmp_path):
    demo = tmp_path / "m.dem"
    demo.write_bytes(b"d")
    with pytest.raises(DemoFailed, match="Game error"):
        record_demo(demo, [H], "765", "x", tmp_path / "k", Path("csdm"), None, 3, 2, True,
                    runner=lambda cmd, env, timeout: (0, ["Starting Counter-Strike...", "Game error"]))


@pytest.mark.skipif(sys.platform != "win32", reason="kill_tree süreç ağacını taskkill ile kapatır (yalnız Windows)")
def test_run_streaming_kills_hung_process():
    from render import TIMEOUT_LINE, run_streaming

    code, lines = run_streaming([sys.executable, "-c", "print('basladi', flush=True); import time; time.sleep(30)"],
                                timeout=2)
    assert lines[0] == "basladi" and lines[-1] == TIMEOUT_LINE and failure(lines) == TIMEOUT_LINE


def test_record_timeout_grows_with_footage():
    from render import START_ALLOWANCE, record_timeout

    assert record_timeout([{**H, "segments": [[0, 640]]}]) == START_ALLOWANCE + 6 * 10


def test_quality_args():
    from render import quality_args
    assert quality_args() == []
    assert quality_args("1440p", 18) == ["--width", "2560", "--height", "1440", "--ffmpeg-crf", "18"]
    assert quality_args("1080p") == ["--width", "1920", "--height", "1080"]
    for bad in (("4k", 0), ("", 99), ("", True)):
        with pytest.raises(SystemExit):
            quality_args(*bad)


def test_quality_reaches_both_csdm_commands():
    q = ["--width", "2560", "--height", "1440"]
    assert video_args(Path("csdm"), Path("d.dem"), "1", [3], 3, 2, True, q)[-4:] == q
    assert segment_args(Path("csdm"), Path("d.dem"), "1", 10, 20, True, q)[-4:] == q
    assert video_args(Path("csdm"), Path("d.dem"), "1", [3], 3, 2, True)[-1] == "--no-player-voices"


# --- takılan parçayı başka başlangıçla yeniden deneme ---------------------

FPS = [1 + 3840 * k for k in range(33)]  # a53a1e7b: 3840 tick'te bir FullPacket


def test_retry_starts_moves_r10_to_previous_fullpacket():
    from render import GOTO_LEAD, fullpacket_before, retry_starts

    # a53a1e7b R10: CSDM 61447'ye atlar -> CS2 61441'deki paketten başlar.
    got = retry_starts(61512, FPS)
    assert got[0] == ("aynı başlangıç", 61512)
    assert got[1][0] == "önceki tam paketten"
    assert fullpacket_before(got[1][1] - GOTO_LEAD, FPS) == 57601
    assert 0 < 61512 - got[1][1] <= TICKRATE  # baştan bir saniyeden az fazlalık
    assert len(got) == 2  # 5 sn erken de 57601'den başlardı: tekrar denenmez


def test_retry_starts_skips_long_extra_lead_and_retries_plainly():
    from render import retry_starts

    # R13: 82443 paket başından 1802 tick sonra; önceki pakete inmek 28 sn fazlalık demek.
    assert retry_starts(82508, FPS) == [("aynı başlangıç", 82508), ("aynı başlangıç, yeniden", 82508)]


def test_retry_starts_without_fullpackets_tries_earlier():
    from render import retry_starts

    assert retry_starts(6000, []) == [("aynı başlangıç", 6000), ("5 sn erken", 6000 - 5 * TICKRATE)]


def test_retry_starts_near_demo_start_has_no_earlier_start():
    from render import retry_starts

    assert [t for _, t in retry_starts(120, FPS)] == [120, 120]


def test_attempts_adds_hlae_last():
    from render import attempts

    got = attempts(61512, FPS, "CS", hlae_fallback=True)
    assert [s for *_, s in got] == ["CS", "CS", "HLAE"] and got[-1][1] == 61512
    assert all(s == "HLAE" for *_, s in attempts(61512, FPS, "HLAE", hlae_fallback=True))


def test_segment_args_recording_system():
    from render import segment_args

    args = segment_args(Path("csdm"), Path("d.dem"), "765", 1, 2, True, system="HLAE")
    assert args[args.index("--recording-system") + 1] == "HLAE"


def test_record_demo_retries_hung_segment_from_earlier_start_and_trims(tmp_path, monkeypatch):
    import render

    demo = tmp_path / "m.dem"
    demo.write_bytes(b"d")
    out = tmp_path / "klipler"
    clips = [{**H, "round": 10, "labels": ["3K"], "segments": [[61512, 61832]]}]
    calls, waits, trims = [], [], []

    def runner(cmd, env, timeout):
        calls.append((cmd[3], cmd[cmd.index("--recording-system") + 1], timeout))
        if cmd[3] == "61512":
            seq(tmp_path, 1, 61512, 61832)  # yarım parça bırakıp takılır
            return 1, ["Zaman aşımı: CS2 takıldı, kapatıldı"]
        seq(tmp_path, 1, int(cmd[3]), int(cmd[4]))
        return 0, ["Video generated"]

    monkeypatch.setattr(render, "trim_lead", lambda p, sec, ff: trims.append((p.name, round(sec, 3))) or p)
    made = record_demo(demo, clips, "765", "x", out, Path("csdm"), Path("ffmpeg"), 3, 2, True, runner=runner,
                       per_segment=True, fullpackets=FPS, wait_game=lambda: waits.append(1) or True)
    assert [c[0] for c in calls] == ["61512", "61474"]
    assert calls[1][2] > calls[0][2]  # daha uzun görüntü, daha uzun süre sınırı
    assert trims == [("sequence-1-tick-61474-to-61832.mp4", round(38 / TICKRATE, 3))]
    assert len(waits) == 2  # her açılıştan önce CS2'nin kapanması beklenir
    assert [p.name for p in made] == ["x_R10_3K.mp4"]
    assert not list(tmp_path.glob("sequence-*.mp4"))


def test_record_demo_does_not_retry_permanent_errors(tmp_path):
    demo = tmp_path / "m.dem"
    demo.write_bytes(b"d")
    calls = []

    def runner(cmd, env, timeout):
        calls.append(cmd)
        return 1, ["Missing demo file"]

    with pytest.raises(DemoFailed, match="Missing demo"):
        record_demo(demo, [{**H, "segments": [[61512, 61832]]}], "765", "x", tmp_path / "k", Path("csdm"), None,
                    3, 2, True, runner=runner, per_segment=True, fullpackets=FPS, hlae_fallback=True)
    assert len(calls) == 1


def test_record_demo_falls_back_to_hlae_after_cs_attempts(tmp_path, monkeypatch):
    import render

    demo = tmp_path / "m.dem"
    demo.write_bytes(b"d")
    systems = []

    def runner(cmd, env, timeout):
        system = cmd[cmd.index("--recording-system") + 1]
        systems.append(system)
        if system == "CS":
            return 1, ["Game error"]
        seq(tmp_path, 1, int(cmd[3]), int(cmd[4]))
        return 0, ["Video generated"]

    made = record_demo(demo, [{**H, "round": 10, "labels": ["3K"], "segments": [[61512, 61832]]}], "765", "x",
                       tmp_path / "k", Path("csdm"), None, 3, 2, True, runner=runner, per_segment=True,
                       fullpackets=FPS, hlae_fallback=True)
    assert systems == ["CS", "CS", "HLAE"]
    assert [p.name for p in made] == ["x_R10_3K.mp4"]


def test_record_demo_does_not_launch_while_cs2_still_open(tmp_path):
    demo = tmp_path / "m.dem"
    demo.write_bytes(b"d")
    calls = []
    with pytest.raises(DemoFailed, match="CS2 kapanmadı"):
        record_demo(demo, [H], "765", "x", tmp_path / "k", Path("csdm"), None, 3, 2, True,
                    runner=lambda cmd, env, timeout: calls.append(cmd) or (0, []), wait_game=lambda: False)
    assert calls == []


def test_record_demo_rejects_unknown_recording_system(tmp_path):
    with pytest.raises(ValueError, match="kayıt sistemi"):
        record_demo(tmp_path / "m.dem", [H], "765", "x", tmp_path, Path("csdm"), None, 3, 2, True, system="OBS")
