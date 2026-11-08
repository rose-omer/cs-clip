import json
import subprocess

import pytest

import paylas
from kontrol import find_ffmpeg
from paylas import Clip, Options


def stats(rating=1.34, adr=91.6, mine=0, score=(13, 9), harita="de_anubis"):
    return {"harita": harita, "benim_takim": mine,
            "takimlar": [{"ad": "A", "skor": score[0]}, {"ad": "B", "skor": score[1]}],
            "oyuncular": [{"ad": "baskasi", "ben": False, "rating": 2, "adr": 1, "kill": 1, "death": 1},
                          {"ad": "DuranEnnmi", "ben": True, "rating": rating, "adr": adr, "kill": 25, "death": 14}]}


def test_frame_size():
    assert paylas.frame_size(False, "1080p") == (1920, 1080)
    assert paylas.frame_size(True, "1080p") == (1080, 1920)
    assert paylas.frame_size(False, "1440p") == (2560, 1440)
    assert paylas.frame_size(True, "1440p") == (1440, 2560)


@pytest.mark.parametrize("labels, weapons, want", [
    (["1v3 clutch", "4K", "1 HS"], ["m4a1_silencer"], "4K · 1v3 CLUTCH"),
    (["ACE", "5 HS", "hızlı"], [], "ACE"),
    (["2K", "wallbang", "smoke arkası"], [], "2K · WALLBANG · SMOKE ARKASI"),
    (["1 HS", "noscope"], ["ssg08"], "NOSCOPE"),
    (["1 HS"], ["awp"], "AWP"),
    (["1 HS"], ["m4a1_silencer"], "M4A1-S"),
    ([], [], ""),
])
def test_clip_label(labels, weapons, want):
    assert paylas.clip_label(labels, weapons) == want


def test_card_single_match_with_stats():
    lines = paylas.card_lines("DuranEnnmi", ["anubis"], [stats()], 3)
    assert lines == [("DuranEnnmi", "ad"), ("ANUBIS", "harita"), ("13 – 9   GALİBİYET", "skor"),
                     ("Rating 1.34   ADR 92   25/14", "bilgi")]


def test_card_score_from_my_side_and_loss():
    lines = paylas.card_lines("x", ["mirage"], [stats(mine=1, score=(13, 9))], 1)
    assert ("9 – 13   MAĞLUBİYET", "skor") in lines


def test_card_without_stats_is_map_and_player():
    assert paylas.card_lines("DuranEnnmi", ["dust2"], [], 2) == [("DuranEnnmi", "ad"), ("DUST2", "harita")]


def test_card_many_matches_averages():
    lines = paylas.card_lines("p", ["anubis", "ancient"], [stats(1.0, 80), stats(1.5, 100)], 5)
    assert lines == [("p", "ad"), ("EN İYİ 5 AN", "harita"), ("ANUBIS · ANCIENT", "bilgi"),
                     ("Ort. rating 1.25   ADR 90   (2 maç)", "kucuk")]


def test_video_kbps():
    # 50 MB / 60 sn ~ 6.6 Mbit/s toplam, ses düşülür
    assert 6000 < paylas.video_kbps(50, 60) < 6700
    assert paylas.video_kbps(1, 600) == paylas.MIN_VIDEO_KBPS


def test_parse_options_defaults_and_values(tmp_path):
    assert paylas.parse_options({}) == Options()
    song = tmp_path / "s.mp3"
    song.write_bytes(b"x")
    o = paylas.parse_options({"dikey": True, "yerlesim": "kirp", "kart": False, "etiket": True,
                              "kalite": "1440p", "crf": 24, "hedef_mb": 50, "muzik": f'"{song}"', "oyun_ses": 0.2})
    assert (o.dikey, o.yerlesim, o.kart, o.kalite, o.crf, o.hedef_mb, o.muzik, o.oyun_ses) == (
        True, "kirp", False, "1440p", 24, 50.0, str(song), 0.2)
    assert o.size == (1440, 2560)
    assert paylas.parse_options({"hedef_mb": 0}).hedef_mb == 0


@pytest.mark.parametrize("body, word", [
    ({"dikey": "evet"}, "dikey"), ({"yerlesim": "x"}, "yerlesim"), ({"kalite": "4k"}, "kalite"),
    ({"crf": 50}, "crf"), ({"crf": 2.5}, "crf"), ({"hedef_mb": -1}, "hedef_mb"),
    ({"muzik": "yok/boyle.mp3"}, "Müzik"), ({"oyun_ses": 5}, "oyun_ses"),
])
def test_parse_options_rejects(body, word):
    with pytest.raises(ValueError, match=word):
        paylas.parse_options(body)


def test_wants_share_only_with_new_fields():
    assert not paylas.wants_share({"adet": 5})
    assert not paylas.wants_share(None)
    assert paylas.wants_share({"adet": 5, "dikey": False})
    assert paylas.wants_share({"paylasim": True})


def test_output_names():
    assert paylas.output_name(Options(dikey=True), "20261108-1200") == "paylas_dikey_1080p_20261108-1200.mp4"
    assert paylas.api_output_name(Options()) == "en_iyi_yatay.mp4"


def test_ff_path_escapes_drive_colon():
    assert paylas.ff_path(r"C:\Windows\Fonts\a.ttf") == r"'C\:/Windows/Fonts/a.ttf'"


def clips2(tmp_path):
    return [Clip(tmp_path / "a.mp4", 5.0, True, "4K · 1v3 CLUTCH", "ANUBIS · R11"),
            Clip(tmp_path / "b.mp4", 3.5, False, "2K", "")]


def test_build_command_inputs_and_filter(tmp_path):
    song = tmp_path / "s.mp3"
    opts = Options(dikey=True, muzik=str(song), crf=22)
    cmd, total = paylas.build_command("ffmpeg", clips2(tmp_path), opts, [("p", "ad"), ("ANUBIS", "harita")],
                                      tmp_path / "font.ttf", tmp_path, tmp_path / "out.mp4")
    assert total == pytest.approx(paylas.CARD_SECONDS + 8.5)
    inputs = [cmd[i + 1] for i, a in enumerate(cmd) if a == "-i"]
    # 2 klip, kart arka planı (ilk klip), kart sesi, sessiz klibe sessizlik, müzik
    assert inputs == [str(tmp_path / "a.mp4"), str(tmp_path / "b.mp4"), str(tmp_path / "a.mp4"),
                      "anullsrc=r=48000:cl=stereo", "anullsrc=r=48000:cl=stereo", str(song)]
    assert cmd[cmd.index("-crf") + 1] == "22" and "-b:v" not in cmd
    graph = (tmp_path / "filtre.txt").read_text(encoding="utf-8")
    assert "concat=n=3:v=1:a=1" in graph
    assert "[4:a]aresample" in graph  # b klibinin sesi sessizlikten
    assert "[3:a]atrim=0:2.5" in graph  # kart sesi
    assert "[5:a]aresample" in graph and "amix=inputs=2" in graph and f"volume={opts.oyun_ses}" in graph
    assert "gblur" in graph  # bulanık yerleşim
    assert (tmp_path / "etiket_0.txt").read_text(encoding="utf-8") == "4K · 1v3 CLUTCH"
    assert (tmp_path / "kart_1.txt").read_text(encoding="utf-8") == "ANUBIS"
    assert not (tmp_path / "alt_1.txt").exists()


def test_build_command_plain_target_size(tmp_path):
    opts = Options(kart=False, etiket=False, hedef_mb=20)
    cmd, total = paylas.build_command("ffmpeg", clips2(tmp_path)[:1], opts, [], tmp_path / "f.ttf", tmp_path,
                                      tmp_path / "o.mp4")
    assert total == 5.0
    assert [cmd[i + 1] for i, a in enumerate(cmd) if a == "-i"] == [str(tmp_path / "a.mp4")]
    assert "-crf" not in cmd and cmd[cmd.index("-b:v") + 1] == f"{paylas.video_kbps(20, 5.0)}k"
    graph = (tmp_path / "filtre.txt").read_text(encoding="utf-8")
    assert "drawtext" not in graph and "pad=1920:1080" in graph and "[acat]anull[aout]" in graph


def test_demo_index(tmp_path):
    (tmp_path / "1-59cf10f2-9122-41c4-1-1.dem.zst").write_bytes(b"z")
    (tmp_path / "1-59cf10f2-9122-41c4-1-1.onarilmis.dem").write_bytes(b"z")
    (tmp_path / "notlar.txt").write_bytes(b"n")
    idx = paylas.demo_index([tmp_path, tmp_path / "yok"])
    assert list(idx) == ["59cf10f2"]
    assert idx["59cf10f2"]["stats"] == tmp_path / "1-59cf10f2-9122-41c4-1-1.stats.json"


def test_share_info_and_meta(tmp_path):
    d = tmp_path / paylas.SHARE_DIR
    d.mkdir()
    out = d / "en_iyi_dikey.mp4"
    out.write_bytes(b"v")
    paylas.write_meta(out, [{"ad": "a.mp4"}], Options(dikey=True))
    [info] = paylas.share_info(tmp_path)
    assert info["klip"] == "/klip/paylasim/en_iyi_dikey.mp4" and info["adet"] == 1 and info["dikey"]
    assert info["secenekler"]["dikey"] is True


ffmpeg = find_ffmpeg()


@pytest.mark.skipif(ffmpeg is None or paylas.find_ffprobe(ffmpeg or "x") is None or paylas.find_font() is None,
                    reason="ffmpeg / yazı tipi yok")
@pytest.mark.parametrize("opts", [Options(dikey=True), Options(dikey=True, yerlesim="kirp", hedef_mb=2),
                                  Options(kart=False)])
def test_make_share_video_real(tmp_path, opts):
    clip_dir = tmp_path / "klipler"
    clip_dir.mkdir()
    names = ["anubis_59cf10f2_R11_1v3clutch_4K_m4a1.mp4", "anubis_59cf10f2_R04_3K_awp.mp4"]
    for k, name in enumerate(names):  # biri sessiz
        audio = ["-f", "lavfi", "-i", "sine=f=440:d=1.2"] if k == 0 else []
        subprocess.run([str(ffmpeg), "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                        "testsrc=d=1.2:s=320x180:r=30", *audio, "-pix_fmt", "yuv420p", "-shortest",
                        str(clip_dir / name)], check=True)
    song = tmp_path / "muzik.wav"
    subprocess.run([str(ffmpeg), "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=220:d=1",
                    str(song)], check=True)
    opts.muzik = str(song)
    rows = [{"ad": n, "harita": "anubis", "kod": "59cf10f2", "round": 11, "etiketler": ["4K"], "silahlar": []}
            for n in names]
    out = tmp_path / "paylasim" / "v.mp4"
    got = paylas.make_share_video(rows, clip_dir, out, ffmpeg, opts, "DuranEnnmi", {"59cf10f2": stats()})
    assert got == out and out.is_file() and not out.with_name("v.part.mp4").exists()
    probe = subprocess.run([str(paylas.find_ffprobe(ffmpeg)), "-v", "error", "-show_entries",
                            "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", str(out)],
                           capture_output=True, text=True, check=True)
    data = json.loads(probe.stdout)
    video = next(s for s in data["streams"] if s["codec_type"] == "video")
    assert (video["width"], video["height"]) == opts.size and video["r_frame_rate"] == "60/1"
    assert any(s["codec_type"] == "audio" for s in data["streams"])
    want = 2.4 + (paylas.CARD_SECONDS if opts.kart else 0)
    assert want - 0.2 <= float(data["format"]["duration"]) <= want + 0.3
    assert sorted(p.name for p in clip_dir.iterdir()) == sorted(names)  # klipler değişmedi


def test_make_share_video_dry_run_and_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(paylas, "find_ffprobe", lambda f: tmp_path / "ffprobe.exe")
    monkeypatch.setattr(paylas, "probe", lambda fp, p: (4.0, True))
    monkeypatch.setattr(paylas, "find_font", lambda: tmp_path / "f.ttf")
    rows = [{"ad": "a.mp4", "harita": "dust2", "kod": "k", "round": 3, "etiketler": ["2K"], "silahlar": []}]
    cmd = paylas.make_share_video(rows, tmp_path, tmp_path / "o.mp4", "ffmpeg", Options(), "p", dry_run=True)
    assert cmd[0] == "ffmpeg" and "# filtre:" in cmd and not (tmp_path / "o.mp4").exists()
    with pytest.raises(ValueError, match="klip yok"):
        paylas.make_share_video([], tmp_path, tmp_path / "o.mp4", "ffmpeg", Options(), "p")
    calls = []

    def boom(cmd, check):
        calls.append(cmd)
        raise subprocess.CalledProcessError(1, cmd)

    with pytest.raises(subprocess.CalledProcessError):
        paylas.make_share_video(rows, tmp_path, tmp_path / "o.mp4", "ffmpeg", Options(), "p", runner=boom)
    assert calls and not (tmp_path / "o.part.mp4").exists()
