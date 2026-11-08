import json

import pytest

from config import DEFAULTS, load_config


def test_missing_file_gives_defaults(tmp_path):
    assert load_config(tmp_path / "yok.json") == DEFAULTS


def test_file_overrides_defaults(tmp_path):
    f = tmp_path / "ayarlar.json"
    f.write_text(json.dumps({"once_sn": 5, "min_skor": 5}), encoding="utf-8")
    cfg = load_config(f)
    assert cfg["once_sn"] == 5
    assert cfg["min_skor"] == 5
    assert cfg["oyuncu"] == DEFAULTS["oyuncu"]


def test_unknown_key_is_rejected(tmp_path):
    f = tmp_path / "ayarlar.json"
    f.write_text(json.dumps({"min_skr": 4}), encoding="utf-8")
    with pytest.raises(SystemExit, match="min_skr"):
        load_config(f)


def test_old_obs_keys_are_ignored(tmp_path):
    f = tmp_path / "ayarlar.json"
    f.write_text(json.dumps({"obs_sifre": "abc", "netcon_port": 2121, "min_skor": 4}), encoding="utf-8")
    cfg = load_config(f)
    assert "obs_sifre" not in cfg and cfg["min_skor"] == 4
