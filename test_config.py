import json

import pytest

from config import DEFAULTS, load_config


def test_missing_file_gives_defaults(tmp_path):
    assert load_config(tmp_path / "yok.json") == DEFAULTS


def test_file_overrides_defaults(tmp_path):
    f = tmp_path / "ayarlar.json"
    f.write_text(json.dumps({"obs_sifre": "abc", "min_skor": 5}), encoding="utf-8")
    cfg = load_config(f)
    assert cfg["obs_sifre"] == "abc"
    assert cfg["min_skor"] == 5
    assert cfg["oyuncu"] == DEFAULTS["oyuncu"]


def test_unknown_key_is_rejected(tmp_path):
    f = tmp_path / "ayarlar.json"
    f.write_text(json.dumps({"obs_sifr": "yazim hatasi"}), encoding="utf-8")
    with pytest.raises(SystemExit, match="obs_sifr"):
        load_config(f)
