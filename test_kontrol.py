import kontrol
from config import DEFAULTS


def test_blocking_programs_lists_faceit_and_cs2():
    procs = {"explorer.exe", "cs2.exe", "faceitclient.exe"}
    assert set(kontrol.blocking_programs(procs)) == {"cs2.exe", "faceitclient.exe"}


def test_preflight_reports_blockers_without_touching_them(tmp_path, monkeypatch):
    monkeypatch.setattr(kontrol, "find_csdm", lambda o: tmp_path / "csdm.cmd")
    monkeypatch.setattr(kontrol, "find_ffmpeg", lambda o: tmp_path / "ffmpeg.exe")
    monkeypatch.setattr(kontrol, "find_pg_bin", lambda: tmp_path)
    monkeypatch.setattr(kontrol, "csdm_database", lambda: {"hostname": "h", "port": 1, "password": "p"})
    monkeypatch.setattr(kontrol, "pg_ready", lambda b, d: True)
    monkeypatch.setattr(kontrol, "free_gb", lambda p: 100)
    tools, problems = kontrol.preflight(DEFAULTS, tmp_path, procs={"faceitservice.exe"})
    assert len(problems) == 1 and "FACEIT" in problems[0]
    assert tools["env"]["PGPASSWORD"] == "p"


def test_preflight_is_clean_when_ready(tmp_path, monkeypatch):
    monkeypatch.setattr(kontrol, "find_csdm", lambda o: tmp_path / "csdm.cmd")
    monkeypatch.setattr(kontrol, "find_ffmpeg", lambda o: tmp_path / "ffmpeg.exe")
    monkeypatch.setattr(kontrol, "find_pg_bin", lambda: tmp_path)
    monkeypatch.setattr(kontrol, "csdm_database", lambda: {"hostname": "h", "port": 1})
    monkeypatch.setattr(kontrol, "pg_ready", lambda b, d: True)
    monkeypatch.setattr(kontrol, "free_gb", lambda p: 100)
    assert kontrol.preflight(DEFAULTS, tmp_path, procs=set())[1] == []


def test_preflight_tries_to_start_stopped_database(tmp_path, monkeypatch):
    started = []
    monkeypatch.setattr(kontrol, "find_csdm", lambda o: tmp_path / "csdm.cmd")
    monkeypatch.setattr(kontrol, "find_ffmpeg", lambda o: tmp_path / "ffmpeg.exe")
    monkeypatch.setattr(kontrol, "find_pg_bin", lambda: tmp_path)
    monkeypatch.setattr(kontrol, "csdm_database", lambda: {"hostname": "h", "port": 1})
    monkeypatch.setattr(kontrol, "pg_ready", lambda b, d: False)
    monkeypatch.setattr(kontrol, "start_pg", lambda b, d: started.append(d) or True)
    monkeypatch.setattr(kontrol, "free_gb", lambda p: 100)
    cfg = {**DEFAULTS, "pg_veri_klasoru": str(tmp_path / "data")}
    assert kontrol.preflight(cfg, tmp_path, procs=set())[1] == []
    assert started == [tmp_path / "data"]
