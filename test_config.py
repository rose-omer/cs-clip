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


from config import save_config, validate


def test_validate_converts_and_cleans(tmp_path):
    clean, errors = validate({"oyuncu": "  ben ", "min_skor": "4,5", "mac_basi_en_fazla": 3.0, "once_sn": 2,
                              "temiz_hud": False, "demo_klasorleri": [f'"{tmp_path}"', "", str(tmp_path)],
                              "csdm_yolu": ""})
    assert errors == {}
    assert clean == {"oyuncu": "ben", "min_skor": 4.5, "mac_basi_en_fazla": 3, "once_sn": 2, "temiz_hud": False,
                     "demo_klasorleri": [str(tmp_path)], "csdm_yolu": ""}


@pytest.mark.parametrize("data, field", [
    ({"oyuncu": " "}, "oyuncu"),
    ({"min_skor": "abc"}, "min_skor"),
    ({"min_skor": True}, "min_skor"),
    ({"once_sn": 99}, "once_sn"),
    ({"mac_basi_en_fazla": 2.5}, "mac_basi_en_fazla"),
    ({"montaj": "evet"}, "montaj"),
    ({"cikti_klasoru": ""}, "cikti_klasoru"),
    ({"demo_klasorleri": ["C:/yok/boyle/klasor"]}, "demo_klasorleri"),
    ({"demo_klasorleri": [1]}, "demo_klasorleri"),
    ({"ffmpeg_yolu": "C:/yok/ffmpeg.exe"}, "ffmpeg_yolu"),
    ({"csgo_klasoru": "C:/yok"}, "csgo_klasoru"),
    ({"bilinmeyen": 1}, "bilinmeyen"),
])
def test_validate_rejects(data, field):
    _, errors = validate(data)
    assert list(errors) == [field]


def test_validate_pg_folder_needs_pg_version(tmp_path):
    assert "pg_veri_klasoru" in validate({"pg_veri_klasoru": str(tmp_path)})[1]
    (tmp_path / "PG_VERSION").write_text("17", encoding="utf-8")
    assert validate({"pg_veri_klasoru": str(tmp_path)})[1] == {}


def test_save_config_merges_and_drops_obsolete(tmp_path):
    f = tmp_path / "ayarlar.json"
    f.write_text(json.dumps({"obs_sifre": "x", "once_sn": 5, "oyuncu": "a"}), encoding="utf-8")
    cfg = save_config(f, {"oyuncu": "b", "montaj": False})
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data == {"oyuncu": "b", "once_sn": 5, "montaj": False}
    assert cfg["oyuncu"] == "b" and cfg["once_sn"] == 5 and cfg["min_skor"] == DEFAULTS["min_skor"]
    assert not (tmp_path / "ayarlar.json.tmp").exists()
