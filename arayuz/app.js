/* cs-klip arayüzü — derleme adımı yok, dış bağımlılık yok. */
(() => {
  'use strict';

  const ORNEK_MODU = new URLSearchParams(location.search).get('ornek') === '1';
  // ornek.json'un gömülü kopyası (index.html çift tıklanınca fetch çalışmazsa kullanılır).
  // Güncellemek için ornek.json ile aynı içerik buraya tek satır olarak yazılır.
  const ORNEK_GOMULU = /*ORNEK_BASLA*/{"kontrol":{"hazir":false,"sorunlar":["FACEIT açık — kayıttan önce FACEIT istemcisini kapatın."]},"demolar":[{"id":"1-59cf10f2-8a41-4c3e-b0d7-2f61e9a8c512-1-1","ad":"1-59cf10f2-8a41-4c3e-b0d7-2f61e9a8c512-1-1.dem.zst","harita":"de_anubis","tarih":"2026-11-08T15:18:00","boyut_mb":151.2,"analiz_edildi":true,"klip_sayisi":3},{"id":"1-0b7e33a9-51d2-4f08-9c6e-a4d18e7f0233-1-1","ad":"1-0b7e33a9-51d2-4f08-9c6e-a4d18e7f0233-1-1.dem.gz","harita":"de_mirage","tarih":"2026-11-06T21:42:00","boyut_mb":238.7,"analiz_edildi":true,"klip_sayisi":0},{"id":"1-c41a9e07-7b3f-45d1-8e22-91f0b5d6ac48-1-1","ad":"1-c41a9e07-7b3f-45d1-8e22-91f0b5d6ac48-1-1.dem","harita":null,"tarih":"2026-11-03T19:05:00","boyut_mb":312.4,"analiz_edildi":false,"klip_sayisi":0}],"demo":{"1-59cf10f2-8a41-4c3e-b0d7-2f61e9a8c512-1-1":{"harita":"de_anubis","round_sayisi":22,"takimlar":[{"ad":"Takım A","skor":13,"kazandi":true},{"ad":"Takım B","skor":9,"kazandi":false}],"benim_takim":0,"oyuncu_steamid":"76561198963443734","oyuncular":[{"steamid":"76561198963443734","ad":"DuranEnnmi","takim":0,"kill":14,"death":12,"assist":5,"adr":66.3,"hs_yuzde":42.9,"kd":1.17,"kast":67.8,"rating":1.05,"acilis_kill":3,"acilis_death":3,"cok_kill":{"2":2,"3":2,"4":0,"5":0},"ben":true},{"steamid":"76561198104523311","ad":"kaanzz","takim":0,"kill":26,"death":19,"assist":8,"adr":117.2,"hs_yuzde":54.3,"kd":1.37,"kast":79.3,"rating":1.61,"acilis_kill":0,"acilis_death":4,"cok_kill":{"2":4,"3":1,"4":0,"5":0},"ben":false},{"steamid":"76561198877001245","ad":"Mert_06","takim":0,"kill":23,"death":15,"assist":5,"adr":108.7,"hs_yuzde":42.2,"kd":1.53,"kast":86.4,"rating":1.6,"acilis_kill":3,"acilis_death":0,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198230984410","ad":"swagg3r","takim":0,"kill":15,"death":20,"assist":5,"adr":64.4,"hs_yuzde":56.8,"kd":0.75,"kast":59.7,"rating":0.83,"acilis_kill":1,"acilis_death":0,"cok_kill":{"2":1,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561199012347766","ad":"ozii","takim":0,"kill":11,"death":10,"assist":3,"adr":59.2,"hs_yuzde":50.6,"kd":1.1,"kast":77.7,"rating":1.02,"acilis_kill":4,"acilis_death":4,"cok_kill":{"2":1,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198341200987","ad":"n1ghtfall","takim":1,"kill":20,"death":18,"assist":3,"adr":104.7,"hs_yuzde":33.3,"kd":1.11,"kast":72.4,"rating":1.29,"acilis_kill":2,"acilis_death":3,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198455109823","ad":"Bora.","takim":1,"kill":20,"death":21,"assist":2,"adr":91.8,"hs_yuzde":38.9,"kd":0.95,"kast":63.1,"rating":1.1,"acilis_kill":4,"acilis_death":2,"cok_kill":{"2":2,"3":1,"4":0,"5":0},"ben":false},{"steamid":"76561198199887432","ad":"zeuS_tr","takim":1,"kill":9,"death":18,"assist":3,"adr":54.6,"hs_yuzde":58.2,"kd":0.5,"kast":57.4,"rating":0.59,"acilis_kill":4,"acilis_death":1,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198600123554","ad":"Krampus","takim":1,"kill":10,"death":14,"assist":8,"adr":58.7,"hs_yuzde":53.1,"kd":0.71,"kast":63.4,"rating":0.8,"acilis_kill":1,"acilis_death":4,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198777321009","ad":"leviathan","takim":1,"kill":17,"death":18,"assist":3,"adr":89.2,"hs_yuzde":54.4,"kd":0.94,"kast":70.6,"rating":1.11,"acilis_kill":1,"acilis_death":1,"cok_kill":{"2":1,"3":0,"4":0,"5":0},"ben":false}],"roundlar":[{"no":1,"kazanan_takim":1,"benim_kill":3,"ben_oldum":false,"neden":"ct_win"},{"no":2,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"bomb_exploded"},{"no":3,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":4,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"bomb_exploded"},{"no":5,"kazanan_takim":0,"benim_kill":1,"ben_oldum":false,"neden":"t_win"},{"no":6,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"bomb_defused"},{"no":7,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":8,"kazanan_takim":1,"benim_kill":1,"ben_oldum":true,"neden":"ct_win"},{"no":9,"kazanan_takim":1,"benim_kill":1,"ben_oldum":true,"neden":"bomb_defused"},{"no":10,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":11,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":12,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"ct_win"},{"no":13,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"bomb_defused"},{"no":14,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"bomb_defused"},{"no":15,"kazanan_takim":0,"benim_kill":2,"ben_oldum":false,"neden":"bomb_defused"},{"no":16,"kazanan_takim":1,"benim_kill":0,"ben_oldum":false,"neden":"t_win"},{"no":17,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"target_saved"},{"no":18,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":19,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"ct_win"},{"no":20,"kazanan_takim":1,"benim_kill":3,"ben_oldum":false,"neden":"bomb_exploded"},{"no":21,"kazanan_takim":1,"benim_kill":2,"ben_oldum":true,"neden":"t_win"},{"no":22,"kazanan_takim":0,"benim_kill":1,"ben_oldum":true,"neden":"ct_win"}],"silahlar":[{"silah":"m4a1_silencer","kill":6,"hs":3},{"silah":"glock","kill":3,"hs":1},{"silah":"ak47","kill":3,"hs":1},{"silah":"awp","kill":1,"hs":1},{"silah":"mp9","kill":1,"hs":0}]},"1-0b7e33a9-51d2-4f08-9c6e-a4d18e7f0233-1-1":{"harita":"de_mirage","round_sayisi":23,"takimlar":[{"ad":"Takım A","skor":10,"kazandi":false},{"ad":"Takım B","skor":13,"kazandi":true}],"benim_takim":0,"oyuncu_steamid":"76561198963443734","oyuncular":[{"steamid":"76561198963443734","ad":"DuranEnnmi","takim":0,"kill":19,"death":16,"assist":7,"adr":81.7,"hs_yuzde":47.4,"kd":1.19,"kast":79.1,"rating":1.27,"acilis_kill":4,"acilis_death":4,"cok_kill":{"2":4,"3":1,"4":1,"5":0},"ben":true},{"steamid":"76561198104523311","ad":"kaanzz","takim":0,"kill":19,"death":17,"assist":3,"adr":79.2,"hs_yuzde":52.7,"kd":1.12,"kast":77.1,"rating":1.21,"acilis_kill":3,"acilis_death":1,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198877001245","ad":"Mert_06","takim":0,"kill":21,"death":18,"assist":8,"adr":105.3,"hs_yuzde":35.2,"kd":1.17,"kast":69.6,"rating":1.31,"acilis_kill":2,"acilis_death":4,"cok_kill":{"2":1,"3":1,"4":0,"5":0},"ben":false},{"steamid":"76561198230984410","ad":"swagg3r","takim":0,"kill":14,"death":22,"assist":5,"adr":72.6,"hs_yuzde":53.2,"kd":0.64,"kast":50.8,"rating":0.7,"acilis_kill":4,"acilis_death":1,"cok_kill":{"2":1,"3":1,"4":0,"5":0},"ben":false},{"steamid":"76561199012347766","ad":"ozii","takim":0,"kill":11,"death":19,"assist":6,"adr":45.3,"hs_yuzde":57.7,"kd":0.58,"kast":56.2,"rating":0.62,"acilis_kill":4,"acilis_death":0,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198341200987","ad":"n1ghtfall","takim":1,"kill":26,"death":20,"assist":5,"adr":111.1,"hs_yuzde":35.9,"kd":1.3,"kast":78.1,"rating":1.52,"acilis_kill":5,"acilis_death":4,"cok_kill":{"2":4,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198455109823","ad":"Bora.","takim":1,"kill":22,"death":20,"assist":5,"adr":107.7,"hs_yuzde":44.8,"kd":1.1,"kast":76.1,"rating":1.35,"acilis_kill":0,"acilis_death":4,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198199887432","ad":"zeuS_tr","takim":1,"kill":13,"death":11,"assist":7,"adr":59.9,"hs_yuzde":45.2,"kd":1.18,"kast":75.9,"rating":1.07,"acilis_kill":5,"acilis_death":4,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198600123554","ad":"Krampus","takim":1,"kill":14,"death":14,"assist":8,"adr":73.8,"hs_yuzde":51.6,"kd":1.0,"kast":72.2,"rating":1.06,"acilis_kill":0,"acilis_death":0,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198777321009","ad":"leviathan","takim":1,"kill":17,"death":19,"assist":3,"adr":82.4,"hs_yuzde":40.8,"kd":0.89,"kast":72.0,"rating":1.06,"acilis_kill":5,"acilis_death":0,"cok_kill":{"2":1,"3":0,"4":0,"5":0},"ben":false}],"roundlar":[{"no":1,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"bomb_exploded"},{"no":2,"kazanan_takim":1,"benim_kill":3,"ben_oldum":true,"neden":"target_saved"},{"no":3,"kazanan_takim":1,"benim_kill":0,"ben_oldum":false,"neden":"bomb_defused"},{"no":4,"kazanan_takim":1,"benim_kill":1,"ben_oldum":true,"neden":"target_saved"},{"no":5,"kazanan_takim":0,"benim_kill":2,"ben_oldum":false,"neden":"bomb_exploded"},{"no":6,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"target_saved"},{"no":7,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"bomb_defused"},{"no":8,"kazanan_takim":1,"benim_kill":2,"ben_oldum":true,"neden":"bomb_defused"},{"no":9,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":10,"kazanan_takim":1,"benim_kill":1,"ben_oldum":true,"neden":"ct_win"},{"no":11,"kazanan_takim":1,"benim_kill":0,"ben_oldum":false,"neden":"ct_win"},{"no":12,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"ct_win"},{"no":13,"kazanan_takim":0,"benim_kill":1,"ben_oldum":false,"neden":"bomb_defused"},{"no":14,"kazanan_takim":0,"benim_kill":1,"ben_oldum":true,"neden":"target_saved"},{"no":15,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"bomb_defused"},{"no":16,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"bomb_exploded"},{"no":17,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"target_saved"},{"no":18,"kazanan_takim":1,"benim_kill":2,"ben_oldum":true,"neden":"t_win"},{"no":19,"kazanan_takim":0,"benim_kill":4,"ben_oldum":true,"neden":"ct_win"},{"no":20,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"ct_win"},{"no":21,"kazanan_takim":1,"benim_kill":2,"ben_oldum":false,"neden":"bomb_exploded"},{"no":22,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"target_saved"},{"no":23,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"t_win"}],"silahlar":[{"silah":"m4a1_silencer","kill":7,"hs":3},{"silah":"awp","kill":4,"hs":2},{"silah":"ak47","kill":4,"hs":2},{"silah":"deagle","kill":3,"hs":1},{"silah":"usp_silencer","kill":1,"hs":1}]},"1-c41a9e07-7b3f-45d1-8e22-91f0b5d6ac48-1-1":{"harita":"de_inferno","round_sayisi":20,"takimlar":[{"ad":"Takım A","skor":13,"kazandi":true},{"ad":"Takım B","skor":7,"kazandi":false}],"benim_takim":0,"oyuncu_steamid":"76561198963443734","oyuncular":[{"steamid":"76561198963443734","ad":"DuranEnnmi","takim":0,"kill":17,"death":11,"assist":2,"adr":84.9,"hs_yuzde":47.1,"kd":1.55,"kast":82.1,"rating":1.38,"acilis_kill":0,"acilis_death":4,"cok_kill":{"2":4,"3":0,"4":1,"5":0},"ben":true},{"steamid":"76561198104523311","ad":"kaanzz","takim":0,"kill":16,"death":9,"assist":7,"adr":89.1,"hs_yuzde":61.2,"kd":1.78,"kast":80.0,"rating":1.42,"acilis_kill":0,"acilis_death":1,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198877001245","ad":"Mert_06","takim":0,"kill":21,"death":20,"assist":6,"adr":115.9,"hs_yuzde":38.0,"kd":1.05,"kast":77.2,"rating":1.4,"acilis_kill":0,"acilis_death":4,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198230984410","ad":"swagg3r","takim":0,"kill":7,"death":13,"assist":8,"adr":40.6,"hs_yuzde":32.6,"kd":0.54,"kast":55.9,"rating":0.6,"acilis_kill":1,"acilis_death":1,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561199012347766","ad":"ozii","takim":0,"kill":19,"death":12,"assist":3,"adr":111.1,"hs_yuzde":53.8,"kd":1.58,"kast":89.9,"rating":1.59,"acilis_kill":5,"acilis_death":2,"cok_kill":{"2":1,"3":1,"4":0,"5":0},"ben":false},{"steamid":"76561198341200987","ad":"n1ghtfall","takim":1,"kill":14,"death":19,"assist":7,"adr":76.2,"hs_yuzde":59.7,"kd":0.74,"kast":61.1,"rating":0.88,"acilis_kill":2,"acilis_death":4,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198455109823","ad":"Bora.","takim":1,"kill":15,"death":11,"assist":2,"adr":87.2,"hs_yuzde":60.4,"kd":1.36,"kast":80.6,"rating":1.29,"acilis_kill":4,"acilis_death":3,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198199887432","ad":"zeuS_tr","takim":1,"kill":11,"death":13,"assist":4,"adr":51.0,"hs_yuzde":40.9,"kd":0.85,"kast":68.1,"rating":0.87,"acilis_kill":0,"acilis_death":1,"cok_kill":{"2":1,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198600123554","ad":"Krampus","takim":1,"kill":13,"death":19,"assist":3,"adr":67.6,"hs_yuzde":43.6,"kd":0.68,"kast":62.6,"rating":0.81,"acilis_kill":2,"acilis_death":0,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198777321009","ad":"leviathan","takim":1,"kill":13,"death":18,"assist":6,"adr":72.1,"hs_yuzde":54.4,"kd":0.72,"kast":65.9,"rating":0.89,"acilis_kill":0,"acilis_death":4,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false}],"roundlar":[{"no":1,"kazanan_takim":1,"benim_kill":1,"ben_oldum":false,"neden":"ct_win"},{"no":2,"kazanan_takim":0,"benim_kill":2,"ben_oldum":false,"neden":"t_win"},{"no":3,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"bomb_exploded"},{"no":4,"kazanan_takim":1,"benim_kill":0,"ben_oldum":false,"neden":"bomb_defused"},{"no":5,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"bomb_exploded"},{"no":6,"kazanan_takim":1,"benim_kill":1,"ben_oldum":false,"neden":"ct_win"},{"no":7,"kazanan_takim":0,"benim_kill":2,"ben_oldum":false,"neden":"bomb_exploded"},{"no":8,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"ct_win"},{"no":9,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"t_win"},{"no":10,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":11,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":12,"kazanan_takim":1,"benim_kill":4,"ben_oldum":true,"neden":"ct_win"},{"no":13,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"bomb_defused"},{"no":14,"kazanan_takim":0,"benim_kill":2,"ben_oldum":false,"neden":"bomb_defused"},{"no":15,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"bomb_defused"},{"no":16,"kazanan_takim":1,"benim_kill":1,"ben_oldum":true,"neden":"t_win"},{"no":17,"kazanan_takim":1,"benim_kill":1,"ben_oldum":true,"neden":"t_win"},{"no":18,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"bomb_defused"},{"no":19,"kazanan_takim":0,"benim_kill":2,"ben_oldum":true,"neden":"bomb_defused"},{"no":20,"kazanan_takim":0,"benim_kill":1,"ben_oldum":true,"neden":"target_saved"}],"silahlar":[{"silah":"ak47","kill":7,"hs":3},{"silah":"m4a1_silencer","kill":4,"hs":2},{"silah":"deagle","kill":3,"hs":1},{"silah":"famas","kill":2,"hs":1},{"silah":"glock","kill":1,"hs":1}]}},"klipler":{"1-59cf10f2-8a41-4c3e-b0d7-2f61e9a8c512-1-1":{"highlightlar":[{"round":15,"score":8.0,"labels":["1v2 clutch","2K","2 HS"],"weapons":["m4a1_silencer"],"saniye":12,"klip":"/klip/anubis_59cf10f2_R15_1v2-clutch.mp4"},{"round":20,"score":7.5,"labels":["3K","3 HS"],"weapons":["famas","m4a1_silencer"],"saniye":16,"klip":"/klip/anubis_59cf10f2_R20_3k.mp4"},{"round":1,"score":6,"labels":["3K"],"weapons":["ak47","galilar"],"saniye":22,"klip":"/klip/anubis_59cf10f2_R1_3k.mp4"},{"round":21,"score":3.5,"labels":["2K","1 HS"],"weapons":["famas","mp9"],"saniye":14,"klip":null},{"round":5,"score":1.5,"labels":["1 HS"],"weapons":["awp"],"saniye":14,"klip":null}],"kayit":{"durum":"bos","mesaj":"","satirlar":[]}},"1-0b7e33a9-51d2-4f08-9c6e-a4d18e7f0233-1-1":{"highlightlar":[{"round":19,"score":13.0,"labels":["4K","3 HS","hızlı"],"weapons":["deagle","famas","m4a1_silencer"],"saniye":15,"klip":null},{"round":2,"score":7.5,"labels":["3K","3 HS"],"weapons":["ak47","deagle","galilar"],"saniye":18,"klip":null},{"round":8,"score":4.0,"labels":["2K","2 HS"],"weapons":["ak47","deagle"],"saniye":10,"klip":null},{"round":18,"score":3.5,"labels":["2K","1 HS"],"weapons":["deagle","m4a1_silencer"],"saniye":18,"klip":null},{"round":5,"score":3,"labels":["2K"],"weapons":["ak47"],"saniye":18,"klip":null}],"kayit":{"durum":"bos","mesaj":"","satirlar":[]}},"1-c41a9e07-7b3f-45d1-8e22-91f0b5d6ac48-1-1":{"highlightlar":[{"round":7,"score":11.0,"labels":["1v3 clutch","2K","2 HS"],"weapons":["tec9"],"saniye":21,"klip":null},{"round":12,"score":10.5,"labels":["4K","1 HS"],"weapons":["ak47","galilar"],"saniye":19,"klip":null},{"round":2,"score":8.5,"labels":["1v2 clutch","2K","smoke arkası"],"weapons":["ak47"],"saniye":19,"klip":null},{"round":14,"score":5.5,"labels":["2K","2 HS","smoke arkası"],"weapons":["deagle","m4a1_silencer"],"saniye":10,"klip":null},{"round":19,"score":3.5,"labels":["2K","1 HS"],"weapons":["m4a1_silencer","mp9"],"saniye":11,"klip":null}],"kayit":{"durum":"bos","mesaj":"","satirlar":[]}}}}/*ORNEK_BITIR*/;

  const UZANTI = /\.dem(\.(zst|gz|bz2))?$/i;
  const YOKLAMA_MS = 2000;

  const NEDEN = {
    t_win: "T'ler rakibi eledi",
    ct_win: "CT'ler rakibi eledi",
    bomb_exploded: 'Bomba patladı',
    bomb_defused: 'Bomba imha edildi',
    target_saved: 'Süre doldu, hedef korundu',
    time_ran_out: 'Süre doldu',
    t_surrender: "T'ler teslim oldu",
    ct_surrender: "CT'ler teslim oldu",
    terrorists_surrender: "T'ler teslim oldu",
    cts_surrender: "CT'ler teslim oldu",
    draw: 'Berabere',
  };
  const SILAH = {
    ak47: 'AK-47', m4a1: 'M4A4', m4a1_silencer: 'M4A1-S', awp: 'AWP', deagle: 'Desert Eagle',
    usp_silencer: 'USP-S', glock: 'Glock-18', hkp2000: 'P2000', p250: 'P250', tec9: 'Tec-9',
    fiveseven: 'Five-SeveN', cz75a: 'CZ75-Auto', elite: 'Dual Berettas', revolver: 'R8',
    galilar: 'Galil AR', famas: 'FAMAS', sg556: 'SG 553', aug: 'AUG', ssg08: 'SSG 08',
    scar20: 'SCAR-20', g3sg1: 'G3SG1', mac10: 'MAC-10', mp9: 'MP9', mp7: 'MP7', mp5sd: 'MP5-SD',
    ump45: 'UMP-45', p90: 'P90', bizon: 'PP-Bizon', nova: 'Nova', xm1014: 'XM1014',
    mag7: 'MAG-7', sawedoff: 'Sawed-Off', m249: 'M249', negev: 'Negev', taser: 'Zeus x27',
    knife: 'Bıçak', hegrenade: 'El bombası', inferno: 'Molotof', molotov: 'Molotof',
    incgrenade: 'Yangın bombası', world: 'Dünya',
  };

  const durum = {
    demolar: [],
    kontrol: null,
    seciliId: null,
    stats: null,
    klipler: null,
    istekNo: 0,
    yoklamaZaman: null,
    sira: { anahtar: 'rating', azalan: true },
    yuklemeKuyrugu: [],
    yukleniyor: false,
  };

  /* ---------------- yardımcılar ---------------- */
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const sayi = (x, ondalik = 0) => (x == null || isNaN(x)) ? '–'
    : Number(x).toLocaleString('tr-TR', { minimumFractionDigits: ondalik, maximumFractionDigits: ondalik });
  const bekle = (ms) => new Promise((r) => setTimeout(r, ms));
  const kopya = (x) => JSON.parse(JSON.stringify(x));

  function haritaAd(h) {
    if (!h) return null;
    const ad = String(h).replace(/^(de|cs|ar)_/, '').replace(/_/g, ' ');
    return ad.charAt(0).toUpperCase() + ad.slice(1); // harita adları İngilizce ('inferno' → 'Inferno')
  }
  function tarihYaz(t) {
    if (!t) return '';
    const d = new Date(t);
    if (isNaN(d)) return String(t);
    const s = { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' };
    if (d.getFullYear() !== new Date().getFullYear()) s.year = 'numeric';
    return d.toLocaleString('tr-TR', s);
  }
  const silahAd = (s) => SILAH[s] || String(s || '?').replace(/^weapon_/, '');
  const nedenAd = (n) => NEDEN[n] || String(n || 'bilinmiyor').replace(/_/g, ' ');
  function ratingSinif(r) { return r >= 1.1 ? 'r-iyi' : r < 0.9 ? 'r-kotu' : 'r-orta'; }
  function esik(deger, iyi, kotu) { return deger == null ? '' : deger >= iyi ? 'iyi' : deger < kotu ? 'kotu' : ''; }

  /* ---------------- API ---------------- */
  async function api(yol, secenek = {}) {
    if (ORNEK_MODU) return ornekApi(yol, secenek);
    let yanit;
    try {
      yanit = await fetch(yol, {
        method: secenek.method || 'GET',
        headers: secenek.body ? { 'Content-Type': 'application/json' } : undefined,
        body: secenek.body,
        cache: 'no-store',
      });
    } catch {
      throw new Error('Sunucuya ulaşılamadı. cs-klip sunucusu çalışıyor mu?');
    }
    const metin = await yanit.text();
    let veri = null;
    try { veri = metin ? JSON.parse(metin) : null; } catch { /* JSON değil */ }
    if (!yanit.ok) {
      const h = new Error((veri && veri.hata) || `Sunucu hatası (HTTP ${yanit.status}).`);
      h.status = yanit.status;
      throw h;
    }
    if (veri === null && metin) throw new Error('Sunucudan geçersiz yanıt geldi.');
    return veri;
  }
  const demoYol = (id, ek = '') => `/api/demo/${encodeURIComponent(id)}${ek}`;

  function yukleXhr(dosya, ilerleme) {
    if (ORNEK_MODU) return ornekYukleme(dosya, ilerleme);
    return new Promise((coz, red) => {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/api/yukle');
      xhr.setRequestHeader('X-Dosya-Adi', encodeURIComponent(dosya.name));
      xhr.setRequestHeader('Content-Type', 'application/octet-stream');
      xhr.upload.onprogress = (e) => { if (e.lengthComputable) ilerleme(e.loaded, e.total); };
      xhr.onload = () => {
        let veri = null;
        try { veri = JSON.parse(xhr.responseText); } catch { /* boş */ }
        if (xhr.status >= 200 && xhr.status < 300) coz(veri || {});
        else red(new Error((veri && veri.hata) || `Yükleme başarısız (HTTP ${xhr.status}).`));
      };
      xhr.onerror = () => red(new Error('Yükleme sırasında bağlantı koptu.'));
      xhr.onabort = () => red(new Error('Yükleme iptal edildi.'));
      xhr.send(dosya);
    });
  }

  /* ---------------- örnek mod (ağ yok) ---------------- */
  let ornekVeri = null;
  let ornekSoz = null;
  function ornekYukle() {
    if (!ornekSoz) ornekSoz = ornekOku();
    return ornekSoz;
  }
  async function ornekOku() {
    if (location.protocol.startsWith('http')) {
      try {
        const r = await fetch('ornek.json', { cache: 'no-store' });
        if (r.ok) ornekVeri = await r.json();
      } catch { /* gömülü kopyaya düş */ }
    }
    if (!ornekVeri) {
      if (!ORNEK_GOMULU) throw new Error('Örnek veri bulunamadı.');
      ornekVeri = kopya(ORNEK_GOMULU);
    }
    ornekVeri.isler = {};
    return ornekVeri;
  }

  const ORNEK_LOG = [
    'Kayıt öncesi kontrol: tamam',
    'CS Demo Manager başlatılıyor…',
    'CS2 açılıyor (-insecure, 1920x1080)…',
    'Demo yüklendi, oyuncu POV: DuranEnnmi',
    'Round {r} kaydediliyor ({i}/{n})…',
    'FFmpeg: NVENC h264 kodlama',
    'Klip yazıldı: {k}',
    'CS2 kapatılıyor',
    'Bitti: {n} klip kaydedildi',
  ];

  function ornekIsIlerlet(id) {
    const v = ornekVeri;
    const is = v.isler[id];
    const k = v.klipler[id];
    if (!is || k.kayit.durum !== 'calisiyor') return;
    const sirali = [...k.highlightlar].sort((a, b) => b.score - a.score);
    const hedef = is.enIyi > 0 ? sirali.slice(0, is.enIyi) : sirali;
    is.adim++;
    const satir = (s, h, i) => s.replace('{r}', h ? h.round : '?').replace('{i}', i + 1)
      .replace('{n}', hedef.length).replace('{k}', h ? `${(v.demo[id].harita || 'demo').replace('de_', '')}_R${h.round}.mp4` : '');
    if (is.adim <= 4) k.kayit.satirlar.push(satir(ORNEK_LOG[is.adim - 1]));
    else {
      const i = is.adim - 5;
      if (i < hedef.length) {
        k.kayit.satirlar.push(satir(ORNEK_LOG[4], hedef[i], i), satir(ORNEK_LOG[5]), satir(ORNEK_LOG[6], hedef[i], i));
        if (!hedef[i].klip) hedef[i].klip = `/klip/ornek_R${hedef[i].round}.mp4`;
      } else {
        k.kayit.satirlar.push(satir(ORNEK_LOG[7]), satir(ORNEK_LOG[8]));
        k.kayit.durum = 'bitti';
        k.kayit.mesaj = `${hedef.length} klip kaydedildi.`;
        const d = v.demolar.find((x) => x.id === id);
        if (d) d.klip_sayisi = k.highlightlar.filter((h) => h.klip).length;
        delete v.isler[id];
      }
    }
    k.kayit.satirlar = k.kayit.satirlar.slice(-40);
  }

  async function ornekApi(yol, { method = 'GET', body } = {}) {
    const v = await ornekYukle();
    await bekle(120);
    const hata = (status, mesaj) => Object.assign(new Error(mesaj), { status });
    if (yol === '/api/kontrol') return kopya(v.kontrol);
    if (yol === '/api/demolar') return kopya(v.demolar);
    const m = yol.match(/^\/api\/demo\/([^/]+)(\/klipler|\/kaydet)?$/);
    if (!m) throw hata(404, 'Bulunamadı.');
    const id = decodeURIComponent(m[1]);
    const demo = v.demolar.find((d) => d.id === id);
    if (!demo || !v.demo[id]) throw hata(404, 'Demo bulunamadı.');
    if (!m[2]) {
      if (!demo.analiz_edildi) {
        await bekle(3500); // ilk analizi taklit et
        demo.analiz_edildi = true;
        demo.harita = v.demo[id].harita;
      }
      return kopya(v.demo[id]);
    }
    const k = v.klipler[id];
    if (m[2] === '/klipler') {
      ornekIsIlerlet(id);
      return kopya(k);
    }
    if (method !== 'POST') throw hata(405, 'Geçersiz istek.');
    if (k.kayit.durum === 'calisiyor') throw hata(409, 'Bu demo için kayıt zaten sürüyor.');
    const enIyi = Number(JSON.parse(body || '{}').en_iyi) || 0;
    k.kayit = { durum: 'calisiyor', mesaj: 'Kayıt başladı.', satirlar: [] };
    v.isler[id] = { adim: 0, enIyi };
    return { durum: 'calisiyor' };
  }

  async function ornekYukleme(dosya, ilerleme) {
    const v = await ornekYukle();
    const toplam = dosya.size || 1;
    for (let i = 1; i <= 20; i++) { await bekle(60); ilerleme(toplam * i / 20, toplam); }
    const kaynak = v.demolar[v.demolar.length - 1].id;
    const id = 'ornek-' + Date.now();
    v.demolar.unshift({
      id, ad: dosya.name, harita: null, tarih: new Date().toISOString().slice(0, 19),
      boyut_mb: Math.round(dosya.size / 1e5) / 10, analiz_edildi: false, klip_sayisi: 0,
    });
    v.demo[id] = kopya(v.demo[kaynak]);
    v.klipler[id] = kopya(v.klipler[kaynak]);
    v.klipler[id].highlightlar.forEach((h) => { h.klip = null; });
    return { id };
  }

  /* ---------------- kontrol ---------------- */
  async function kontrolYenile() {
    try {
      durum.kontrol = await api('/api/kontrol');
    } catch (e) {
      durum.kontrol = { hazir: false, sorunlar: [e.message], ulasilamadi: true };
    }
    kontrolCiz();
    kayitUyariCiz();
  }
  function kontrolCiz() {
    const k = durum.kontrol;
    const kutu = $('kontrol');
    if (!k) return;
    const sorunlar = k.sorunlar || [];
    if (k.hazir && !sorunlar.length) {
      kutu.className = 'kontrol hazir';
      kutu.innerHTML = '<span class="nokta"></span>Kayıt hazır';
    } else {
      kutu.className = 'kontrol sorun';
      kutu.innerHTML = `<span class="nokta"></span>${k.hazir ? 'Kayıt hazır, uyarılar var' : 'Kayıt için dikkat'}`
        + (sorunlar.length ? `<ul>${sorunlar.map((s) => `<li>${esc(s)}</li>`).join('')}</ul>` : '');
    }
  }

  /* ---------------- demo listesi ---------------- */
  async function demolariYenile() {
    try {
      durum.demolar = (await api('/api/demolar')) || [];
      listeCiz();
    } catch (e) {
      $('demolar').innerHTML = `<li class="liste-bos" style="color:var(--kotu)">${esc(e.message)}</li>`;
    }
  }
  function listeCiz() {
    const ul = $('demolar');
    if (!durum.demolar.length) {
      ul.innerHTML = '<li class="liste-bos">Henüz demo yok. Yukarıdan bir .dem dosyası yükle.</li>';
      return;
    }
    ul.innerHTML = durum.demolar.map((d) => {
      const ad = haritaAd(d.harita);
      const rozet = [];
      if (d.analiz_edildi) rozet.push('<span class="rozet yesil">analiz edildi</span>');
      else rozet.push('<span class="rozet">analiz bekliyor</span>');
      if (d.klip_sayisi > 0) rozet.push(`<span class="rozet sari">${d.klip_sayisi} klip</span>`);
      return `<li data-id="${esc(d.id)}" class="${d.id === durum.seciliId ? 'secili' : ''}" title="${esc(d.ad)}">
        <div class="demo-ust">
          <span class="demo-harita ${ad ? '' : 'bilinmiyor'}">${esc(ad || 'Bilinmeyen harita')}</span>
          <span class="demo-boyut">${sayi(d.boyut_mb, 0)} MB</span>
        </div>
        <div class="demo-tarih">${esc(tarihYaz(d.tarih))}</div>
        <div class="rozetler">${rozet.join('')}</div>
      </li>`;
    }).join('');
  }

  /* ---------------- yükleme ---------------- */
  function dosyalariAl(liste) {
    const dosyalar = [...liste];
    const gecersiz = dosyalar.filter((f) => !UZANTI.test(f.name));
    durum.yuklemeKuyrugu.push(...dosyalar.filter((f) => UZANTI.test(f.name)));
    if (gecersiz.length) {
      yuklemeDurum(gecersiz.map((f) => f.name).join(', '), 0,
        'Desteklenmeyen dosya: yalnızca .dem, .dem.zst, .dem.gz, .dem.bz2', true);
    }
    kuyruguIsle();
  }
  function yuklemeDurum(ad, oran, metin, hata = false) {
    $('yukleme').hidden = false;
    $('yukleme').classList.toggle('hata', hata);
    $('yuklemeAd').textContent = ad;
    $('yuklemeCubuk').style.width = `${Math.round(oran * 100)}%`;
    $('yuklemeYuzde').textContent = metin;
  }
  async function kuyruguIsle() {
    if (durum.yukleniyor) return;
    durum.yukleniyor = true;
    let sonId = null;
    while (durum.yuklemeKuyrugu.length) {
      const f = durum.yuklemeKuyrugu.shift();
      const bas = Date.now();
      const kalan = durum.yuklemeKuyrugu.length;
      yuklemeDurum(f.name, 0, 'Yükleniyor…');
      try {
        const sonuc = await yukleXhr(f, (yuklenen, toplam) => {
          const sn = (Date.now() - bas) / 1000;
          const hiz = sn > 0.3 ? ` · ${sayi(yuklenen / 1048576 / sn, 0)} MB/sn` : '';
          yuklemeDurum(f.name, yuklenen / toplam,
            `%${Math.floor(yuklenen / toplam * 100)} · ${sayi(yuklenen / 1048576, 0)} / ${sayi(toplam / 1048576, 0)} MB${hiz}`
            + (kalan ? ` · sırada ${kalan}` : ''));
        });
        yuklemeDurum(f.name, 1, 'Yüklendi ✓');
        sonId = sonuc && sonuc.id;
      } catch (e) {
        yuklemeDurum(f.name, 0, e.message, true);
      }
    }
    durum.yukleniyor = false;
    await demolariYenile();
    if (sonId) demoSec(sonId);
  }

  /* ---------------- demo seçimi ---------------- */
  function demoSec(id) {
    if (location.hash.slice(1) !== encodeURIComponent(id)) location.hash = encodeURIComponent(id);
    else demoAc(id);
  }
  function hashtenAc() {
    const id = decodeURIComponent(location.hash.slice(1));
    if (id) demoAc(id);
  }

  async function demoAc(id) {
    const no = ++durum.istekNo;
    yoklamaDurdur();
    durum.seciliId = id;
    durum.stats = null;
    durum.klipler = null;
    listeCiz();
    const demo = durum.demolar.find((d) => d.id === id);
    const ilk = !demo || !demo.analiz_edildi;
    const ana = $('ana');
    ana.innerHTML = `<div class="yukleniyor"><div class="donen"></div>
      <h2>${ilk ? 'Demo analiz ediliyor…' : 'İstatistikler yükleniyor…'}</h2>
      <p>${ilk ? 'İlk analiz 20–40 saniye sürebilir. Sonrakiler anında açılır.' : ''}</p>
      <p id="gecenSure" class="mac-alt"></p></div>`;
    ana.scrollTop = 0;
    const bas = Date.now();
    const sayac = setInterval(() => {
      const el = $('gecenSure');
      if (!el) return;
      const sn = Math.floor((Date.now() - bas) / 1000);
      el.textContent = sn >= 2 ? `${sn} sn${sn > 60 ? ' — hâlâ çalışıyor, büyük demolar daha uzun sürebilir' : ''}` : '';
    }, 1000);
    let stats;
    try {
      stats = await api(demoYol(id));
    } catch (e) {
      if (no !== durum.istekNo) return;
      ana.innerHTML = `<div class="hata-kutu"><h2>Demo açılamadı</h2><p>${esc(e.message)}</p>
        <button class="dugme ikincil" id="tekrarDene">Tekrar dene</button></div>`;
      $('tekrarDene').onclick = () => demoAc(id);
      return;
    } finally {
      clearInterval(sayac);
    }
    if (no !== durum.istekNo) return;
    durum.stats = stats;
    anaCiz();
    if (ilk) demolariYenile();
    klipleriYukle(id, no);
  }

  /* ---------------- ana görünüm ---------------- */
  function benBul(s) {
    return (s.oyuncular || []).find((o) => o.ben)
      || (s.oyuncular || []).find((o) => String(o.steamid) === String(s.oyuncu_steamid)) || null;
  }

  function anaCiz() {
    const s = durum.stats;
    const ben = benBul(s);
    const biz = s.benim_takim ?? (ben ? ben.takim : 0);
    const takimlar = s.takimlar || [];
    const bizT = takimlar[biz] || { skor: 0 };
    const onlarT = takimlar[1 - biz] || { skor: 0 };
    const sonuc = bizT.skor > onlarT.skor ? ['galibiyet', 'Galibiyet'] : bizT.skor < onlarT.skor ? ['maglubiyet', 'Mağlubiyet'] : ['berabere', 'Berabere'];
    const demo = durum.demolar.find((d) => d.id === durum.seciliId);

    $('ana').innerHTML = `<div class="icerik">
      <section class="kart mac-baslik">
        <div>
          <div class="mac-harita">${esc(haritaAd(s.harita) || 'Bilinmeyen harita')}</div>
          <div class="mac-alt">${s.round_sayisi ?? (s.roundlar || []).length} round${demo ? ' · ' + esc(tarihYaz(demo.tarih)) : ''}</div>
        </div>
        <div class="mac-skor">
          <div class="skor"><span class="${sonuc[0]}">${bizT.skor}</span><span class="tire">–</span><span>${onlarT.skor}</span></div>
          <div class="sonuc ${sonuc[0]}">${sonuc[1]}</div>
        </div>
      </section>
      ${ben ? oyuncuKartlari(ben, s) : '<section class="kart"><p class="bos-not">Bu demoda oyuncu bulunamadı (oyuncu_steamid eşleşmedi).</p></section>'}
      <section class="kart"><h3>Skor tablosu <span class="ek">Sıralamak için başlığa tıkla</span></h3>
        <div class="tablolar" id="tablolar"></div></section>
      <div class="ikili">
        <section class="kart"><h3>Roundlar</h3>${zamanCiz(s, biz)}</section>
        <section class="kart"><h3>Silahlar <span class="ek">${ben ? ben.kill + ' kill' : ''}</span></h3>${silahCiz(s.silahlar || [])}</section>
      </div>
      <section class="kart" id="hlBolum">
        <h3>Highlight'lar ve klipler <span class="ek" id="hlOzet"></span></h3>
        <div class="kayit-ust">
          <button class="dugme" id="kaydetDugme">Klipleri kaydet</button>
          <label>En iyi
            <select id="enIyi"><option value="3">3</option><option value="5">5</option><option value="0">Hepsi</option></select>
          </label>
        </div>
        <div id="kayitUyari"></div>
        <div id="kayitDurum"></div>
        <pre class="log" id="log" hidden></pre>
        <div class="hl-liste" id="hlListe"><p class="bos-not"><span class="donen kucuk"></span> Highlight'lar yükleniyor…</p></div>
      </section>
    </div>`;
    tablolariCiz();
    kayitUyariCiz();
    $('kaydetDugme').onclick = kaydet;
    $('tablolar').onclick = (e) => {
      const th = e.target.closest('th[data-k]');
      if (!th) return;
      const k = th.dataset.k;
      durum.sira = durum.sira.anahtar === k ? { anahtar: k, azalan: !durum.sira.azalan } : { anahtar: k, azalan: k !== 'ad' };
      tablolariCiz();
    };
  }

  function oyuncuKartlari(o, s) {
    const hepsi = s.oyuncular || [];
    const sira = (k) => 1 + hepsi.filter((x) => (x[k] ?? -1) > (o[k] ?? -1)).length;
    const fark = o.kill - o.death;
    const ck = o.cok_kill || {};
    const ckHtml = [['2', '2K'], ['3', '3K'], ['4', '4K'], ['5', 'ACE']].map(([k, ad]) =>
      `<span class="${ck[k] ? 'var' : ''}">${ad} <b>${ck[k] || 0}</b></span>`).join('');
    const kart = (ad, deger, alt = '', sinif = '') =>
      `<div class="stat ${sinif}"><div class="stat-ad">${ad}</div><div class="stat-deger">${deger}</div>${alt ? `<div class="stat-alt">${alt}</div>` : ''}</div>`;
    const ac = (o.acilis_kill ?? 0) - (o.acilis_death ?? 0);
    return `<section class="kart">
      <h3><span class="oyuncu-ad">${esc(o.ad)}</span> <span class="ek">${esc(o.steamid)}</span></h3>
      <div class="kartlar">
        <div class="stat rating"><div class="stat-ad">Rating</div>
          <span class="rating-rozet buyuk ${ratingSinif(o.rating)}">${sayi(o.rating, 2)}</span>
          <div class="stat-alt">Lobide ${sira('rating')}. / ${hepsi.length}</div></div>
        ${kart('ADR', sayi(o.adr, 1), `Lobide ${sira('adr')}. / ${hepsi.length}`, esik(o.adr, 85, 65))}
        ${kart('K / D / A', `${o.kill}<small> / </small>${o.death}<small> / </small>${o.assist}`,
          `<span class="${fark > 0 ? 'renk-iyi' : fark < 0 ? 'renk-kotu' : ''}">${fark > 0 ? '+' : ''}${fark}</span> fark`)}
        ${kart('K/D', sayi(o.kd, 2), '', esik(o.kd, 1.1, 0.9))}
        ${kart('HS %', `${sayi(o.hs_yuzde, 1)}<small>%</small>`, '', esik(o.hs_yuzde, 50, 30))}
        ${kart('KAST %', `${sayi(o.kast, 1)}<small>%</small>`, '', esik(o.kast, 75, 65))}
        ${kart('Açılış', `${o.acilis_kill ?? 0}<small> / </small>${o.acilis_death ?? 0}`, 'kill / ölüm', ac > 0 ? 'iyi' : ac < 0 ? 'kotu' : '')}
        <div class="stat"><div class="stat-ad">Çoklu kill</div><div class="cok-kill">${ckHtml}</div></div>
      </div>
    </section>`;
  }

  const SUTUNLAR = [
    ['ad', 'Oyuncu'], ['kill', 'K'], ['death', 'D'], ['assist', 'A'],
    ['adr', 'ADR'], ['hs_yuzde', 'HS%'], ['kast', 'KAST%'], ['rating', 'Rating'],
  ];
  function tablolariCiz() {
    const s = durum.stats;
    const ben = benBul(s);
    const biz = s.benim_takim ?? (ben ? ben.takim : 0);
    const { anahtar, azalan } = durum.sira;
    const sirala = (a, b) => {
      const x = a[anahtar], y = b[anahtar];
      const c = anahtar === 'ad' ? String(x).localeCompare(String(y), 'tr') : (x ?? -1) - (y ?? -1);
      return azalan ? -c : c;
    };
    const takimSira = [biz, 1 - biz];
    $('tablolar').innerHTML = takimSira.map((t) => {
      const takim = (s.takimlar || [])[t] || { ad: `Takım ${t + 1}`, skor: '' };
      const oyuncular = (s.oyuncular || []).filter((o) => o.takim === t).sort(sirala);
      const renk = takim.kazandi ? 'galibiyet' : (s.takimlar || []).some((x) => x.kazandi) ? 'maglubiyet' : 'berabere';
      return `<div>
        <div class="takim-baslik"><span class="takim-skor ${renk}">${esc(takim.skor)}</span><b>${esc(takim.ad)}</b>
          <span class="etiket">${t === biz ? 'senin takımın' : 'rakip'}</span></div>
        <div class="tablo-sar"><table>
          <thead><tr>${SUTUNLAR.map(([k, ad]) =>
            `<th data-k="${k}" class="${k === anahtar ? 'siralı' + (azalan ? '' : ' artan') : ''}">${ad}</th>`).join('')}</tr></thead>
          <tbody>${oyuncular.map((o) => `<tr class="${o.ben ? 'ben' : ''}">
            <td class="oyuncu-hucre" title="${esc(o.steamid)}">${esc(o.ad)}</td>
            <td>${o.kill}</td><td>${o.death}</td><td>${o.assist}</td>
            <td class="${esikRenk(o.adr, 85, 65)}">${sayi(o.adr, 1)}</td>
            <td>${sayi(o.hs_yuzde, 0)}%</td>
            <td class="${esikRenk(o.kast, 75, 65)}">${sayi(o.kast, 1)}%</td>
            <td><span class="rating-rozet ${ratingSinif(o.rating)}">${sayi(o.rating, 2)}</span></td>
          </tr>`).join('')}</tbody>
        </table></div></div>`;
    }).join('');
  }
  function esikRenk(d, iyi, kotu) { const e = esik(d, iyi, kotu); return e ? 'renk-' + e : ''; }

  function zamanCiz(s, biz) {
    const roundlar = [...(s.roundlar || [])].sort((a, b) => a.no - b.no);
    if (!roundlar.length) return '<p class="bos-not">Round bilgisi yok.</p>';
    const parca = [];
    roundlar.forEach((r) => {
      const kazandik = r.kazanan_takim === biz;
      const ipucu = [`Round ${r.no} — ${kazandik ? 'kazandınız' : 'kaybettiniz'}`, nedenAd(r.neden)];
      if (r.benim_kill) ipucu.push(`${r.benim_kill} kill`);
      if (r.ben_oldum) ipucu.push('Öldün');
      parca.push(`<div class="rnd"><div class="rnd-kutu ${kazandik ? 'biz' : 'onlar'}" data-ipucu="${esc(ipucu.join('\n'))}">
${r.benim_kill ? r.benim_kill : ''}</div>
        <div class="rnd-olum">${r.ben_oldum ? '✕' : ''}</div><div class="rnd-no">${r.no}</div></div>`);
      // devre arası 12'den sonra; uzatmada 24'ten sonra her 3 roundda bir
      const ara = r.no === 12 || (r.no >= 24 && (r.no - 24) % 3 === 0);
      if (ara && r.no !== roundlar[roundlar.length - 1].no) parca.push('<div class="ayrac" title="Devre arası"></div>');
    });
    return `<div class="zaman">${parca.join('')}</div>
      <div class="lejant">
        <span><i style="background:var(--iyi)"></i>Kazandınız</span>
        <span><i style="background:var(--kotu)"></i>Kaybettiniz</span>
        <span><b>2</b> senin kill sayın</span>
        <span><span style="color:var(--kotu)">✕</span> öldün</span>
      </div>`;
  }

  function silahCiz(silahlar) {
    if (!silahlar.length) return '<p class="bos-not">Bu maçta kill yok.</p>';
    const liste = [...silahlar].sort((a, b) => b.kill - a.kill);
    const enCok = Math.max(...liste.map((x) => x.kill), 1);
    return `<div class="silahlar">${liste.map((x) => {
      const hs = Math.min(x.hs || 0, x.kill);
      return `<div class="silah-satir" title="${esc(silahAd(x.silah))}: ${x.kill} kill, ${hs} headshot">
        <span class="silah-ad">${esc(silahAd(x.silah))}</span>
        <div class="silah-bar"><div class="hs" style="width:${hs / enCok * 100}%"></div><div class="govde" style="width:${(x.kill - hs) / enCok * 100}%"></div></div>
        <span class="silah-sayi"><b>${x.kill}</b>${hs ? ` · ${hs}` : ''}</span></div>`;
    }).join('')}</div>
    <div class="lejant"><span><i style="background:var(--vurgu)"></i>headshot</span><span><i style="background:#6b7487"></i>diğer</span></div>`;
  }

  /* ---------------- highlight + kayıt ---------------- */
  async function klipleriYukle(id, no) {
    try {
      const k = await api(demoYol(id, '/klipler'));
      if (no !== durum.istekNo) return;
      durum.klipler = k;
      highlightCiz();
      kayitDurumCiz();
      if (k.kayit && k.kayit.durum === 'calisiyor') yoklamaBaslat(id, no);
    } catch (e) {
      if (no !== durum.istekNo) return;
      $('hlListe').innerHTML = `<div class="mesaj hata">Highlight'lar alınamadı: ${esc(e.message)}</div>`;
    }
  }

  function highlightCiz() {
    const liste = $('hlListe');
    if (!liste || !durum.klipler) return;
    const hl = [...(durum.klipler.highlightlar || [])].sort((a, b) => b.score - a.score);
    const klipli = hl.filter((h) => h.klip).length;
    $('hlOzet').textContent = `${hl.length} highlight · ${klipli} klip`;
    if (!hl.length) {
      liste.innerHTML = '<p class="bos-not">Bu maçta öne çıkan an bulunamadı.</p>';
      return;
    }
    liste.innerHTML = hl.map((h) => {
      const etiketler = (h.labels || []).map((l) => {
        const sinif = /clutch/i.test(l) ? 'clutch' : /^(\dK|ACE)$/i.test(l) ? 'kill' : '';
        return `<span class="etk ${sinif}">${esc(l)}</span>`;
      }).join('');
      return `<div class="hl">
        <div class="hl-round"><small>ROUND</small>${esc(h.round)}</div>
        <div>
          <div class="hl-etiketler">${etiketler || '<span class="etk">—</span>'}</div>
          <div class="hl-silah">${(h.weapons || []).map((w) => esc(silahAd(w))).join(', ')}</div>
        </div>
        <div class="hl-sag"><b>${sayi(h.score, 1)}</b>puan · ${esc(h.saniye ?? '?')} sn</div>
        ${!h.klip ? '<div class="hl-klip-yok">Klip henüz kaydedilmedi.</div>'
          : ORNEK_MODU // örnek modda ağ isteği yapılmaz: video kaynaksız gösterilir
            ? `<div class="hl-video"><video controls preload="none"></video><div class="hl-klip-yok" style="margin-top:6px">Örnek mod: ${esc(h.klip)} (dosya yok)</div></div>`
            : `<div class="hl-video"><video controls preload="metadata" src="${esc(h.klip)}"></video></div>`}
      </div>`;
    }).join('');
    liste.querySelectorAll('video').forEach((v) => v.addEventListener('error', () => {
      if (v.dataset.hata) return;
      v.dataset.hata = '1';
      const not = document.createElement('div');
      not.className = 'hl-klip-yok';
      not.style.marginTop = '6px';
      not.textContent = ORNEK_MODU ? 'Örnek modda klip dosyası yok.' : 'Klip dosyası yüklenemedi.';
      v.after(not);
    }));
  }

  function kayitUyariCiz() {
    const kutu = $('kayitUyari');
    if (!kutu) return;
    const k = durum.kontrol;
    const sorunlar = (k && k.sorunlar) || [];
    let html = '<div class="uyari bilgi">Kayıt CS2\'yi açar ve demoyu oynatır; bitene kadar bilgisayarı kullanma. '
      + 'Başlamadan önce FACEIT ve CS2 kapalı olmalı.</div>';
    if (sorunlar.length) html += `<div class="uyari"><b>Kayıt öncesi kontrol:</b><ul>${sorunlar.map((s) => `<li>${esc(s)}</li>`).join('')}</ul></div>`;
    kutu.innerHTML = html;
  }

  function kayitDurumCiz(ekHata) {
    const kutu = $('kayitDurum');
    if (!kutu) return;
    const kayit = (durum.klipler && durum.klipler.kayit) || { durum: 'bos' };
    const calisiyor = kayit.durum === 'calisiyor';
    $('kaydetDugme').disabled = calisiyor;
    $('kaydetDugme').textContent = calisiyor ? 'Kayıt sürüyor…' : 'Klipleri kaydet';
    $('enIyi').disabled = calisiyor;
    let html = '';
    if (calisiyor) html = `<div class="mesaj surer"><span class="donen kucuk"></span> ${esc(kayit.mesaj || 'Kayıt sürüyor…')}</div>`;
    else if (kayit.durum === 'bitti') html = `<div class="mesaj basari">${esc(kayit.mesaj || 'Kayıt tamamlandı.')}</div>`;
    else if (kayit.durum === 'hata') html = `<div class="mesaj hata">Kayıt başarısız: ${esc(kayit.mesaj || 'bilinmeyen hata')}</div>`;
    if (ekHata) html += `<div class="mesaj hata">${esc(ekHata)}</div>`;
    kutu.innerHTML = html;
    const log = $('log');
    const satirlar = kayit.satirlar || [];
    log.hidden = !(satirlar.length && (calisiyor || kayit.durum === 'hata' || kayit.durum === 'bitti'));
    const altta = log.scrollHeight - log.scrollTop - log.clientHeight < 30;
    log.textContent = satirlar.join('\n');
    if (altta || calisiyor) log.scrollTop = log.scrollHeight;
  }

  async function kaydet() {
    const id = durum.seciliId;
    const no = durum.istekNo;
    const dugme = $('kaydetDugme');
    dugme.disabled = true;
    const enIyi = Number($('enIyi').value);
    try {
      const sonuc = await api(demoYol(id, '/kaydet'), { method: 'POST', body: JSON.stringify({ en_iyi: enIyi }) });
      if (no !== durum.istekNo) return;
      durum.klipler.kayit = { durum: (sonuc && sonuc.durum) || 'calisiyor', mesaj: 'Kayıt başlatıldı…', satirlar: [] };
      kayitDurumCiz();
      yoklamaBaslat(id, no);
    } catch (e) {
      if (no !== durum.istekNo) return;
      kayitDurumCiz(e.message);
      kontrolYenile();
    }
  }

  function yoklamaDurdur() {
    clearTimeout(durum.yoklamaZaman);
    durum.yoklamaZaman = null;
  }
  function yoklamaBaslat(id, no) {
    yoklamaDurdur();
    const tur = async () => {
      if (no !== durum.istekNo) return;
      try {
        const k = await api(demoYol(id, '/klipler'));
        if (no !== durum.istekNo) return;
        const oncekiKlip = JSON.stringify((durum.klipler.highlightlar || []).map((h) => h.klip));
        durum.klipler = k;
        const bitti = !k.kayit || k.kayit.durum !== 'calisiyor';
        const yeniKlip = JSON.stringify((k.highlightlar || []).map((h) => h.klip));
        if (bitti || yeniKlip !== oncekiKlip) highlightCiz();
        kayitDurumCiz();
        if (bitti) {
          demolariYenile();
          kontrolYenile();
          return;
        }
      } catch (e) {
        if (no !== durum.istekNo) return;
        kayitDurumCiz('Kayıt durumu alınamadı: ' + e.message);
      }
      durum.yoklamaZaman = setTimeout(tur, YOKLAMA_MS);
    };
    durum.yoklamaZaman = setTimeout(tur, YOKLAMA_MS);
  }

  /* ---------------- ipucu ---------------- */
  function ipucuKur() {
    const tip = $('ipucu');
    addEventListener('scroll', () => { tip.hidden = true; }, true);
    document.addEventListener('mousemove', (e) => {
      const hedef = e.target.closest && e.target.closest('[data-ipucu]');
      if (!hedef) { tip.hidden = true; return; }
      tip.innerHTML = esc(hedef.dataset.ipucu).replace(/\n/g, '<br>');
      tip.hidden = false;
      const w = tip.offsetWidth, h = tip.offsetHeight;
      tip.style.left = `${Math.min(e.clientX + 14, innerWidth - w - 8)}px`;
      tip.style.top = `${e.clientY + 16 + h > innerHeight ? e.clientY - h - 10 : e.clientY + 16}px`;
    });
  }

  /* ---------------- başlangıç ---------------- */
  function surukleBirakKur() {
    const birak = $('birak');
    const secici = $('dosyaSec');
    secici.onchange = () => { if (secici.files.length) dosyalariAl(secici.files); secici.value = ''; };
    birak.onkeydown = (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); secici.click(); } };
    let derinlik = 0;
    const dosyaVar = (e) => e.dataTransfer && [...e.dataTransfer.types].includes('Files');
    addEventListener('dragenter', (e) => { if (dosyaVar(e)) { derinlik++; birak.classList.add('uzerinde'); } });
    addEventListener('dragleave', (e) => { if (dosyaVar(e) && --derinlik <= 0) { derinlik = 0; birak.classList.remove('uzerinde'); } });
    addEventListener('dragover', (e) => { if (dosyaVar(e)) { e.preventDefault(); e.dataTransfer.dropEffect = 'copy'; } });
    addEventListener('drop', (e) => {
      if (!dosyaVar(e)) return;
      e.preventDefault();
      derinlik = 0;
      birak.classList.remove('uzerinde');
      if (e.dataTransfer.files.length) dosyalariAl(e.dataTransfer.files);
    });
  }

  async function basla() {
    if (ORNEK_MODU) {
      document.querySelector('.logo').insertAdjacentHTML('beforeend', ' <span class="rozet sari">örnek veri</span>');
      document.title = 'cs-klip (örnek)';
    }
    surukleBirakKur();
    ipucuKur();
    $('demolar').onclick = (e) => { const li = e.target.closest('li[data-id]'); if (li) demoSec(li.dataset.id); };
    $('yenile').onclick = () => { demolariYenile(); kontrolYenile(); };
    addEventListener('hashchange', hashtenAc);
    setInterval(kontrolYenile, 30000);

    kontrolYenile();
    await demolariYenile();
    if (location.hash.length > 1) hashtenAc();
    else {
      const ilk = durum.demolar.find((d) => d.analiz_edildi);
      if (ilk) {
        history.replaceState(null, '', '#' + encodeURIComponent(ilk.id));
        demoAc(ilk.id);
      }
    }
  }

  basla();
})();
