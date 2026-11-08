"""Derin analiz: harita üstünde kill/ölüm konumları, utility ve nişan metrikleri.

stats.json'a "derin" anahtarıyla eklenir (DERIN_SURUM). Eski json'larda bu anahtar yoktur;
arayüz o zaman "yeniden hesapla" der. Yalnız demoda doğrudan olan veriler kullanılır:

- konumlar: player_death olayındaki X/Y (katil ve kurban), zemin için tüm oyuncuların X/Y'si
- utility: weapon_fire (atılan bombalar), player_blind (kör süresi), player_death.assistedflash,
  player_hurt (el bombası/molotof hasarı)
- nişan: fire_bullets (her mermi, recoil_index), player_hurt (aynı tick'te isabet, hitgroup),
  approximate_spotted_by (time-to-damage; sunucunun radar görüşü, yaklaşık)

Demoda olmayan şeyler (ör. crosshair yerleşimi, counter-strafe) hesaplanmaz.
"""

import base64
import math
import statistics
from collections import Counter

import pandas as pd

from highlights import TICKRATE

DERIN_SURUM = 1

# CS2 radar (overview) dönüşümü: radar_px = (x - pos_x) / scale, radar_py = (pos_y - y) / scale.
# Radar görseli 1024x1024; değerler oyunun resource/overviews/<harita>.txt dosyalarından.
RADAR_PX = 1024
RADAR = {
    "de_ancient": {"pos_x": -2953, "pos_y": 2164, "scale": 5.0},
    "de_anubis": {"pos_x": -2796, "pos_y": 3328, "scale": 5.22},
    "de_dust2": {"pos_x": -2476, "pos_y": 3239, "scale": 4.4},
    "de_mirage": {"pos_x": -3230, "pos_y": 1713, "scale": 5.0},
    "de_inferno": {"pos_x": -2087, "pos_y": 3870, "scale": 4.9},
    "de_nuke": {"pos_x": -3453, "pos_y": 2887, "scale": 7.0},
    "de_train": {"pos_x": -2308, "pos_y": 2078, "scale": 4.082077},
    "de_vertigo": {"pos_x": -3168, "pos_y": 1762, "scale": 4.0},
    "de_overpass": {"pos_x": -4831, "pos_y": 1781, "scale": 5.2},
}

GRID = 128  # zemin ızgarası (GRID x GRID hücre)
ZEMIN_ADIM = 16  # zemin için kaç tick'te bir konum alınır
TTD_PENCERE_SN = 2.0  # time-to-damage: hasardan en fazla bu kadar önce görülmüş olmalı
TTD_BOSLUK = 4  # görüş kaydında bu kadar tick'lik boşluk görüşü bölmez
SPREY_MERMI = 3  # recoil_index >= 3: spreyin 4. mermisi ve sonrası

BOMBA = {  # weapon_fire silah adı -> anahtar
    "weapon_flashbang": "flas", "weapon_smokegrenade": "smoke", "weapon_hegrenade": "he",
    "weapon_molotov": "molotof", "weapon_incgrenade": "molotof", "weapon_decoy": "decoy",
}
BOMBA_HASAR = {"hegrenade": "he", "inferno": "molotof", "molotov": "molotof", "incgrenade": "molotof"}
NISANSIZ = {"knife", "taser", "hegrenade", "inferno", "molotov", "incgrenade", "flashbang", "smokegrenade",
            "decoy", "world", "c4"}
OTOMATIK = {"ak47", "m4a1", "m4a1_silencer", "galilar", "famas", "sg556", "aug", "mac10", "mp9", "mp7", "mp5sd",
            "ump45", "p90", "bizon", "m249", "negev", "cz75a"}
# fire_bullets.item_def_index -> silah (weapon_fire ile eşleşmeyen atışlar için yedek)
ITEM_DEF = {
    1: "deagle", 2: "elite", 3: "fiveseven", 4: "glock", 7: "ak47", 8: "aug", 9: "awp", 10: "famas",
    11: "g3sg1", 13: "galilar", 14: "m249", 16: "m4a1", 17: "mac10", 19: "p90", 23: "mp5sd", 24: "ump45",
    25: "xm1014", 26: "bizon", 27: "mag7", 28: "negev", 29: "sawedoff", 30: "tec9", 31: "taser",
    32: "hkp2000", 33: "mp7", 34: "mp9", 35: "nova", 36: "p250", 38: "scar20", 39: "sg556", 40: "ssg08",
    60: "m4a1_silencer", 61: "usp_silencer", 63: "cz75a", 64: "revolver",
}


def _s(col: pd.Series) -> pd.Series:
    return col.astype(str)


def _enemy(df: pd.DataFrame, a: str = "attacker", u: str = "user") -> pd.Series:
    """Saldıran ile kurban farklı takımda (ve kendisi değil)."""
    return (df[f"{a}_team_num"] != df[f"{u}_team_num"]) & (_s(df[f"{a}_steamid"]) != _s(df[f"{u}_steamid"]))


def _r(x: float, n: int = 1) -> float:
    return round(float(x), n)


def _pct(a: int, b: int) -> float | None:
    return _r(100 * a / b) if b else None


def _silah(name) -> str:
    return str(name or "").removeprefix("weapon_")


# --- harita ---

def radar_info(map_name: str) -> dict | None:
    r = RADAR.get(str(map_name))
    if r is None:
        return None
    size = RADAR_PX * r["scale"]
    return {**r, "px": RADAR_PX, "x0": r["pos_x"], "x1": r["pos_x"] + size, "y0": r["pos_y"] - size, "y1": r["pos_y"]}


def to_radar(map_name: str, x: float, y: float) -> tuple[float, float] | None:
    """Dünya koordinatı -> radar pikseli (0..1024); harita bilinmiyorsa None."""
    r = RADAR.get(str(map_name))
    if r is None:
        return None
    return (x - r["pos_x"]) / r["scale"], (r["pos_y"] - y) / r["scale"]


def map_box(map_name: str, xs: list[float], ys: list[float]) -> dict:
    """Zemin ve noktaların çizildiği kare alan (dünya koordinatı). Radar biliniyorsa radarla aynı."""
    r = radar_info(map_name)
    if r is not None:
        return {"x0": r["x0"], "x1": r["x1"], "y0": r["y0"], "y1": r["y1"]}
    if not xs:
        return {"x0": -1.0, "x1": 1.0, "y0": -1.0, "y1": 1.0}
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    half = max(max(xs) - min(xs), max(ys) - min(ys), 1.0) * 0.55
    return {"x0": cx - half, "x1": cx + half, "y0": cy - half, "y1": cy + half}


def occupancy(xs, ys, box: dict, n: int = GRID) -> str:
    """Konumların düştüğü hücreler: n*n bit, satır satır (üst satır = en büyük y), base64."""
    bits = bytearray((n * n + 7) // 8)
    w, h = box["x1"] - box["x0"], box["y1"] - box["y0"]
    for x, y in zip(xs, ys):
        if x is None or y is None or math.isnan(x) or math.isnan(y):
            continue
        cx = int((x - box["x0"]) / w * n)
        cy = int((box["y1"] - y) / h * n)
        if 0 <= cx < n and 0 <= cy < n:
            i = cy * n + cx
            bits[i >> 3] |= 1 << (i & 7)
    return base64.b64encode(bytes(bits)).decode("ascii")


def decode_occupancy(text: str, n: int = GRID) -> set[tuple[int, int]]:
    """occupancy() tersine: dolu (sütun, satır) hücreleri."""
    raw = base64.b64decode(text)
    return {(i % n, i // n) for i in range(n * n) if raw[i >> 3] >> (i & 7) & 1}


def heat_points(kills: pd.DataFrame, deaths: pd.DataFrame, steamid: str) -> list[dict]:
    """Oyuncunun kill (kendi konumu + kurban) ve ölüm (kendi konumu + katil) noktaları."""
    out = []
    for r in kills.itertuples():
        out.append({"tur": "kill", "round": int(r.round) + 1, "x": _r(r.attacker_X), "y": _r(r.attacker_Y),
                    "rx": _r(r.user_X), "ry": _r(r.user_Y), "silah": str(r.weapon), "hs": bool(r.headshot)})
    for r in deaths.itertuples():
        killer = None if pd.isna(r.attacker_X) or str(r.attacker_steamid) == steamid else (r.attacker_X, r.attacker_Y)
        out.append({"tur": "olum", "round": int(r.round) + 1, "x": _r(r.user_X), "y": _r(r.user_Y),
                    "rx": _r(killer[0]) if killer else None, "ry": _r(killer[1]) if killer else None,
                    "silah": str(r.weapon), "hs": bool(r.headshot)})
    out.sort(key=lambda p: (p["round"], p["tur"]))
    return out


# --- utility ---

def utility(steamid: str, throws: pd.DataFrame, blinds: pd.DataFrame, deaths: pd.DataFrame,
            damage: pd.DataFrame, rounds: int) -> dict:
    """throws: weapon_fire (bomba atışları), blinds: player_blind, deaths: maç içi player_death,
    damage: rakibe verilen, kalan canla sınırlı hasar (stats.enemy_damage; dmg sütunu)."""
    mine = throws[_s(throws["user_steamid"]) == steamid]
    thrown = Counter(BOMBA[w] for w in mine["weapon"] if w in BOMBA)
    my_blinds = blinds[(_s(blinds["attacker_steamid"]) == steamid) & (_s(blinds["user_steamid"]) != steamid)]
    enemy = my_blinds[my_blinds["attacker_team_num"] != my_blinds["user_team_num"]]
    team = my_blinds[my_blinds["attacker_team_num"] == my_blinds["user_team_num"]]
    dur_e = float(enemy["blind_duration"].clip(lower=0).sum())
    flash_assists = deaths[(_s(deaths["assister_steamid"]) == steamid) & deaths["assistedflash"].astype(bool)
                           & _enemy(deaths)]
    mydmg = damage[_s(damage["attacker_steamid"]) == steamid]
    nade = mydmg[mydmg["weapon"].isin(BOMBA_HASAR)]
    nade_dmg = Counter()
    for w, d in zip(nade["weapon"], nade["dmg"]):
        nade_dmg[BOMBA_HASAR[w]] += float(d)
    flashes = thrown.get("flas", 0)
    return {
        "atilan": {k: thrown.get(k, 0) for k in ("flas", "smoke", "molotof", "he", "decoy")},
        "atilan_toplam": sum(thrown.values()),
        "round_basi": _r(sum(thrown.values()) / rounds, 2) if rounds else 0.0,
        "flas_asist": len(flash_assists),
        "kor_dusman": len(enemy),
        "kor_dusman_sn": _r(dur_e, 1),
        "flas_basi_kor_sn": _r(dur_e / flashes, 2) if flashes else None,
        "flas_basi_dusman": _r(len(enemy) / flashes, 2) if flashes else None,
        "kor_takim": len(team),
        "kor_takim_sn": _r(float(team["blind_duration"].clip(lower=0).sum()), 1),
        "bomba_hasar": {k: round(nade_dmg.get(k, 0.0)) for k in ("he", "molotof")},
        "bomba_hasar_toplam": round(sum(nade_dmg.values())),
    }


# --- nişan ---

def shot_table(bullets: pd.DataFrame, fires: pd.DataFrame, steamid: str) -> pd.DataFrame:
    """Oyuncunun mermileri: tick, silah, recoil_index. fire_bullets'a weapon_fire'dan silah adı eklenir."""
    b = bullets[_s(bullets["user_steamid"]) == steamid][["tick", "item_def_index", "recoil_index"]].copy()
    f = fires[_s(fires["user_steamid"]) == steamid][["tick", "weapon"]].copy()
    f["weapon"] = f["weapon"].map(_silah)
    f = f[~f["weapon"].isin(NISANSIZ) & ~f["weapon"].str.startswith("knife")].drop_duplicates("tick")
    b = b.merge(f, on="tick", how="left")
    fallback = b["item_def_index"].map(lambda i: ITEM_DEF.get(int(i)) if pd.notna(i) else None)
    b["silah"] = b["weapon"].where(b["weapon"].notna(), fallback).fillna("?")
    b = b[~b["silah"].isin(NISANSIZ)]
    return b[["tick", "silah", "recoil_index"]].sort_values("tick").reset_index(drop=True)


def aim(steamid: str, shots: pd.DataFrame, hurts: pd.DataFrame, kills: pd.DataFrame) -> dict:
    """shots: shot_table(); hurts: maç içi player_hurt; kills: geçerli kill'ler.

    İsabet: aynı tick'te rakibe player_hurt (CS2'de isabet atışla aynı tick'te gelir).
    """
    mine = hurts[(_s(hurts["attacker_steamid"]) == steamid) & _enemy(hurts) & ~hurts["weapon"].isin(NISANSIZ)
                 & ~hurts["weapon"].astype(str).str.startswith("knife")]
    hit_ticks = set(mine["tick"].astype(int))
    # player_hurt silah adı bazen taban sınıftır (USP-S -> hkp2000); aynı tick'teki mermininkini kullan
    shot_weapon = dict(zip(shots["tick"].astype(int), shots["silah"]))
    mine = mine.assign(silah=[shot_weapon.get(int(t), str(w)) for t, w in zip(mine["tick"], mine["weapon"])])
    shots = shots.copy()
    shots["isabet"] = shots["tick"].astype(int).isin(hit_ticks)
    spray = shots[shots["silah"].isin(OTOMATIK) & (shots["recoil_index"] >= SPREY_MERMI)]
    first = shots[shots["recoil_index"] < 1]

    my_kills = kills[_s(kills["attacker_steamid"]) == steamid]
    rows = []
    for w in sorted(set(shots["silah"]) | set(mine["silah"])):
        s = shots[shots["silah"] == w]
        h = mine[mine["silah"] == w]
        k = my_kills[my_kills["weapon"].astype(str) == w]
        head = int((h["hitgroup"].astype(str) == "head").sum())
        hk = int(k["headshot"].astype(bool).sum())
        rows.append({
            "silah": w, "atis": len(s), "isabetli_atis": int(s["isabet"].sum()),
            "isabet_yuzde": _pct(int(s["isabet"].sum()), len(s)),
            "vurus": len(h), "kafa": head, "kafa_yuzde": _pct(head, len(h)),
            "kill": len(k), "hs_kill": hk, "hs_kill_yuzde": _pct(hk, len(k)),
        })
    rows.sort(key=lambda r: (-r["vurus"], -r["atis"], r["silah"]))
    head = int((mine["hitgroup"].astype(str) == "head").sum())
    return {
        "atis": len(shots), "isabetli_atis": int(shots["isabet"].sum()),
        "isabet_yuzde": _pct(int(shots["isabet"].sum()), len(shots)),
        "ilk_mermi_atis": len(first), "ilk_mermi_isabet_yuzde": _pct(int(first["isabet"].sum()), len(first)),
        "sprey_atis": len(spray), "sprey_isabet_yuzde": _pct(int(spray["isabet"].sum()), len(spray)),
        "vurus": len(mine), "kafa_vurus": head, "kafa_vurus_yuzde": _pct(head, len(mine)),
        "silahlar": rows,
    }


def engagements(steamid: str, hurts: pd.DataFrame) -> pd.DataFrame:
    """Her (round, rakip) için oyuncunun ona ilk silah hasarı: tick, round, user_steamid."""
    mine = hurts[(_s(hurts["attacker_steamid"]) == steamid) & _enemy(hurts) & ~hurts["weapon"].isin(NISANSIZ)
                 & ~hurts["weapon"].astype(str).str.startswith("knife")]
    first = mine.sort_values("tick", kind="stable").groupby(["round", "user_steamid"], as_index=False).head(1)
    return first[["tick", "round", "user_steamid"]].reset_index(drop=True)


def ttd_ticks(steamid: str, first_hits: pd.DataFrame, spotted: pd.DataFrame,
              window: int = int(TTD_PENCERE_SN * TICKRATE), gap: int = TTD_BOSLUK) -> list[int]:
    """Görmeye başlamadan ilk hasara kadar geçen tick'ler (her çatışma için).

    spotted: tick, steamid (görülen), approximate_spotted_by (görenlerin listesi).
    Hasar anında görmüyorsa (duvar arkası/smoke) ya da pencereden önce de görüyorsa çatışma sayılmaz.
    """
    me = str(steamid)
    seen: dict[str, set[int]] = {}
    for tick, sid, by in zip(spotted["tick"], spotted["steamid"], spotted["approximate_spotted_by"]):
        if by is not None and len(by) and me in {str(x) for x in by}:
            seen.setdefault(str(sid), set()).add(int(tick))
    out = []
    for r in first_hits.itertuples():
        ticks = seen.get(str(r.user_steamid), set())
        t, hit = int(r.tick), int(r.tick)
        last = next((x for x in range(hit, hit - gap - 1, -1) if x in ticks), None)
        if last is None:
            continue
        t = last
        while True:
            prev = next((x for x in range(t - 1, t - gap - 2, -1) if x in ticks), None)
            if prev is None:
                break
            t = prev
            if hit - t >= window:
                break
        if hit - t >= window:
            continue  # uzun süredir görüyordu: tepki süresi değil
        out.append(hit - t)
    return out


def ttd_summary(ticks: list[int]) -> dict:
    ms = [t * 1000 / TICKRATE for t in ticks]
    if not ms:
        return {"ornek": 0, "medyan_ms": None, "ortalama_ms": None, "dagilim": []}
    edges = [(0, 250), (250, 500), (500, 750), (750, 1000), (1000, None)]
    return {
        "ornek": len(ms), "medyan_ms": round(statistics.median(ms)), "ortalama_ms": round(statistics.fmean(ms)),
        "dagilim": [{"alt": a, "ust": b, "sayi": sum(1 for m in ms if m >= a and (b is None or m < b))}
                    for a, b in edges],
    }


def ttd_tick_list(first_hits: pd.DataFrame, window: int = int(TTD_PENCERE_SN * TICKRATE)) -> list[int]:
    """approximate_spotted_by için okunacak tick'ler (her çatışmanın öncesindeki pencere)."""
    ticks = set()
    for t in first_hits["tick"].astype(int):
        ticks.update(range(max(t - window - TTD_BOSLUK - 1, 0), t + 1))
    return sorted(ticks)


# --- birleştirme ---

def build_derin(map_name: str, steamid: str, rounds: int, kills: pd.DataFrame, deaths: pd.DataFrame,
                hurts: pd.DataFrame, damage: pd.DataFrame, throws: pd.DataFrame, blinds: pd.DataFrame,
                shots: pd.DataFrame, ttd: list[int], positions: pd.DataFrame) -> dict:
    """Ayrıştırılmış tablolardan "derin" bloğu. Tablolar maç içiyle (ısınma hariç) sınırlı olmalı;
    kills/deaths/hurts'te round (0 tabanlı) sütunu olmalı. positions: X, Y (zemin için)."""
    my_kills = kills[_s(kills["attacker_steamid"]) == steamid]
    my_deaths = deaths[_s(deaths["user_steamid"]) == steamid]
    points = heat_points(my_kills, my_deaths, steamid)
    xs = [float(x) for x in positions["X"]] if len(positions) else []
    ys = [float(y) for y in positions["Y"]] if len(positions) else []
    box = map_box(map_name, xs + [p["x"] for p in points], ys + [p["y"] for p in points])
    radar = radar_info(map_name)
    notes = ["Time-to-damage, sunucunun radar görüşüne (approximate_spotted_by) dayanır; yaklaşık bir değerdir."]
    if radar is None:
        notes.append(f"{map_name} için radar tablosu yok; zemin oyuncu konumlarından ölçeklendi.")
    return {
        "surum": DERIN_SURUM,
        "harita": {
            "ad": map_name, "radar": radar, "kutu": {k: _r(v) for k, v in box.items()},
            "zemin": {"n": GRID, "bitler": occupancy(xs, ys, box)} if xs else None,
            "noktalar": points,
        },
        "utility": utility(steamid, throws, blinds, deaths, damage, rounds),
        "nisan": aim(steamid, shots, hurts, kills) | {"ttd": ttd_summary(ttd)},
        "notlar": notes,
    }


# --- demo ---

DERIN_EVENTS = ["player_death", "player_hurt", "player_blind", "weapon_fire", "fire_bullets"]


def derin_from_parser(parser, map_name: str, steamid: str, match_start: int, bounds: list[float],
                      rounds: int, end_tick: int | None = None) -> dict:
    """demoparser2 ayrıştırıcısından derin analiz. bounds: stats.round_bounds() çıktısı."""
    from stats import assign_rounds, enemy_damage, valid_kills  # döngüsel içe aktarma olmasın

    ev = dict(parser.parse_events(DERIN_EVENTS, player=["X", "Y", "team_num"]))
    empty = pd.DataFrame({"tick": pd.Series(dtype="int64")})

    def in_match(name: str) -> pd.DataFrame:
        df = ev.get(name, empty)
        df = df[df["tick"] >= match_start].copy()
        if end_tick is not None:
            df = df[df["tick"] <= end_tick]
        df["round"] = assign_rounds(df, bounds) if len(df) else pd.Series(dtype="int64")
        return df

    deaths = in_match("player_death")
    deaths = deaths[deaths["user_steamid"].notna()]
    hurts = in_match("player_hurt")
    kills = valid_kills(deaths)
    damage = enemy_damage(hurts)
    fires = in_match("weapon_fire")
    shots = shot_table(in_match("fire_bullets"), fires, steamid)

    first = engagements(steamid, hurts)
    spot_ticks = ttd_tick_list(first)
    spotted = parser.parse_ticks(["approximate_spotted_by"], ticks=spot_ticks) if spot_ticks else \
        pd.DataFrame(columns=["tick", "steamid", "approximate_spotted_by"])
    ttd = ttd_ticks(steamid, first, spotted)

    last = end_tick if end_tick is not None else int(hurts["tick"].max() if len(hurts) else match_start)
    pos_ticks = list(range(match_start, last + 1, ZEMIN_ADIM))
    positions = parser.parse_ticks(["X", "Y", "is_alive", "team_num"], ticks=pos_ticks) if pos_ticks else \
        pd.DataFrame(columns=["X", "Y", "is_alive", "team_num"])
    if len(positions):
        positions = positions[positions["is_alive"].astype(bool) & positions["team_num"].isin([2, 3])]
    return build_derin(map_name, steamid, rounds, kills, deaths, hurts, damage, fires, in_match("player_blind"),
                       shots, ttd, positions)


def needs_refresh(stats: dict | None) -> bool:
    """Eski (derin analizi olmayan ya da eski sürüm) stats.json mu?"""
    if not stats:
        return True
    d = stats.get("derin")
    return not isinstance(d, dict) or d.get("surum", 0) < DERIN_SURUM or "hata" in d
