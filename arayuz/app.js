/* cs-klip arayüzü — "Esports Yayın" görünümü. Derleme adımı yok; dış kaynak yalnız Google Fonts. */
(() => {
  'use strict';

  const ORNEK_MODU = new URLSearchParams(location.search).get('ornek') === '1';
  // ornek.json'un gömülü kopyası (index.html çift tıklanınca fetch çalışmazsa kullanılır).
  // Güncellemek için ornek.json ile aynı içerik buraya tek satır olarak yazılır.
  const ORNEK_GOMULU = /*ORNEK_BASLA*/{"kontrol":{"hazir":false,"sorunlar":["FACEIT açık — kayıttan önce FACEIT istemcisini kapatın."]},"demolar":[{"id":"1-59cf10f2-8a41-4c3e-b0d7-2f61e9a8c512-1-1","ad":"1-59cf10f2-8a41-4c3e-b0d7-2f61e9a8c512-1-1.dem.zst","harita":"de_anubis","tarih":"2026-11-08T15:18:00","boyut_mb":151.2,"analiz_edildi":true,"klip_sayisi":3},{"id":"1-0b7e33a9-51d2-4f08-9c6e-a4d18e7f0233-1-1","ad":"1-0b7e33a9-51d2-4f08-9c6e-a4d18e7f0233-1-1.dem.gz","harita":"de_mirage","tarih":"2026-11-06T21:42:00","boyut_mb":238.7,"analiz_edildi":true,"klip_sayisi":2},{"id":"1-c41a9e07-7b3f-45d1-8e22-91f0b5d6ac48-1-1","ad":"1-c41a9e07-7b3f-45d1-8e22-91f0b5d6ac48-1-1.dem","harita":null,"tarih":"2026-11-03T19:05:00","boyut_mb":312.4,"analiz_edildi":false,"klip_sayisi":0}],"demo":{"1-59cf10f2-8a41-4c3e-b0d7-2f61e9a8c512-1-1":{"harita":"de_anubis","round_sayisi":22,"takimlar":[{"ad":"Takım A","skor":13,"kazandi":true},{"ad":"Takım B","skor":9,"kazandi":false}],"benim_takim":0,"oyuncu_steamid":"76561198963443734","oyuncular":[{"steamid":"76561198963443734","ad":"DuranEnnmi","takim":0,"kill":14,"death":12,"assist":5,"adr":66.3,"hs_yuzde":42.9,"kd":1.17,"kast":67.8,"rating":1.05,"acilis_kill":3,"acilis_death":3,"cok_kill":{"2":2,"3":2,"4":0,"5":0},"ben":true},{"steamid":"76561198104523311","ad":"kaanzz","takim":0,"kill":26,"death":19,"assist":8,"adr":117.2,"hs_yuzde":54.3,"kd":1.37,"kast":79.3,"rating":1.61,"acilis_kill":0,"acilis_death":4,"cok_kill":{"2":4,"3":1,"4":0,"5":0},"ben":false},{"steamid":"76561198877001245","ad":"Mert_06","takim":0,"kill":23,"death":15,"assist":5,"adr":108.7,"hs_yuzde":42.2,"kd":1.53,"kast":86.4,"rating":1.6,"acilis_kill":3,"acilis_death":0,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198230984410","ad":"swagg3r","takim":0,"kill":15,"death":20,"assist":5,"adr":64.4,"hs_yuzde":56.8,"kd":0.75,"kast":59.7,"rating":0.83,"acilis_kill":1,"acilis_death":0,"cok_kill":{"2":1,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561199012347766","ad":"ozii","takim":0,"kill":11,"death":10,"assist":3,"adr":59.2,"hs_yuzde":50.6,"kd":1.1,"kast":77.7,"rating":1.02,"acilis_kill":4,"acilis_death":4,"cok_kill":{"2":1,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198341200987","ad":"n1ghtfall","takim":1,"kill":20,"death":18,"assist":3,"adr":104.7,"hs_yuzde":33.3,"kd":1.11,"kast":72.4,"rating":1.29,"acilis_kill":2,"acilis_death":3,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198455109823","ad":"Bora.","takim":1,"kill":20,"death":21,"assist":2,"adr":91.8,"hs_yuzde":38.9,"kd":0.95,"kast":63.1,"rating":1.1,"acilis_kill":4,"acilis_death":2,"cok_kill":{"2":2,"3":1,"4":0,"5":0},"ben":false},{"steamid":"76561198199887432","ad":"zeuS_tr","takim":1,"kill":9,"death":18,"assist":3,"adr":54.6,"hs_yuzde":58.2,"kd":0.5,"kast":57.4,"rating":0.59,"acilis_kill":4,"acilis_death":1,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198600123554","ad":"Krampus","takim":1,"kill":10,"death":14,"assist":8,"adr":58.7,"hs_yuzde":53.1,"kd":0.71,"kast":63.4,"rating":0.8,"acilis_kill":1,"acilis_death":4,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198777321009","ad":"leviathan","takim":1,"kill":17,"death":18,"assist":3,"adr":89.2,"hs_yuzde":54.4,"kd":0.94,"kast":70.6,"rating":1.11,"acilis_kill":1,"acilis_death":1,"cok_kill":{"2":1,"3":0,"4":0,"5":0},"ben":false}],"roundlar":[{"no":1,"kazanan_takim":1,"benim_kill":3,"ben_oldum":false,"neden":"ct_win"},{"no":2,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"bomb_exploded"},{"no":3,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":4,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"bomb_exploded"},{"no":5,"kazanan_takim":0,"benim_kill":1,"ben_oldum":false,"neden":"t_win"},{"no":6,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"bomb_defused"},{"no":7,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":8,"kazanan_takim":1,"benim_kill":1,"ben_oldum":true,"neden":"ct_win"},{"no":9,"kazanan_takim":1,"benim_kill":1,"ben_oldum":true,"neden":"bomb_defused"},{"no":10,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":11,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":12,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"ct_win"},{"no":13,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"bomb_defused"},{"no":14,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"bomb_defused"},{"no":15,"kazanan_takim":0,"benim_kill":2,"ben_oldum":false,"neden":"bomb_defused"},{"no":16,"kazanan_takim":1,"benim_kill":0,"ben_oldum":false,"neden":"t_win"},{"no":17,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"target_saved"},{"no":18,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":19,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"ct_win"},{"no":20,"kazanan_takim":1,"benim_kill":3,"ben_oldum":false,"neden":"bomb_exploded"},{"no":21,"kazanan_takim":1,"benim_kill":2,"ben_oldum":true,"neden":"t_win"},{"no":22,"kazanan_takim":0,"benim_kill":1,"ben_oldum":true,"neden":"ct_win"}],"silahlar":[{"silah":"m4a1_silencer","kill":6,"hs":3},{"silah":"glock","kill":3,"hs":1},{"silah":"ak47","kill":3,"hs":1},{"silah":"awp","kill":1,"hs":1},{"silah":"mp9","kill":1,"hs":0}]},"1-0b7e33a9-51d2-4f08-9c6e-a4d18e7f0233-1-1":{"harita":"de_mirage","round_sayisi":23,"takimlar":[{"ad":"Takım A","skor":10,"kazandi":false},{"ad":"Takım B","skor":13,"kazandi":true}],"benim_takim":0,"oyuncu_steamid":"76561198963443734","oyuncular":[{"steamid":"76561198963443734","ad":"DuranEnnmi","takim":0,"kill":19,"death":16,"assist":7,"adr":81.7,"hs_yuzde":47.4,"kd":1.19,"kast":79.1,"rating":1.27,"acilis_kill":4,"acilis_death":4,"cok_kill":{"2":4,"3":1,"4":1,"5":0},"ben":true},{"steamid":"76561198104523311","ad":"kaanzz","takim":0,"kill":19,"death":17,"assist":3,"adr":79.2,"hs_yuzde":52.7,"kd":1.12,"kast":77.1,"rating":1.21,"acilis_kill":3,"acilis_death":1,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198877001245","ad":"Mert_06","takim":0,"kill":21,"death":18,"assist":8,"adr":105.3,"hs_yuzde":35.2,"kd":1.17,"kast":69.6,"rating":1.31,"acilis_kill":2,"acilis_death":4,"cok_kill":{"2":1,"3":1,"4":0,"5":0},"ben":false},{"steamid":"76561198230984410","ad":"swagg3r","takim":0,"kill":14,"death":22,"assist":5,"adr":72.6,"hs_yuzde":53.2,"kd":0.64,"kast":50.8,"rating":0.7,"acilis_kill":4,"acilis_death":1,"cok_kill":{"2":1,"3":1,"4":0,"5":0},"ben":false},{"steamid":"76561199012347766","ad":"ozii","takim":0,"kill":11,"death":19,"assist":6,"adr":45.3,"hs_yuzde":57.7,"kd":0.58,"kast":56.2,"rating":0.62,"acilis_kill":4,"acilis_death":0,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198341200987","ad":"n1ghtfall","takim":1,"kill":26,"death":20,"assist":5,"adr":111.1,"hs_yuzde":35.9,"kd":1.3,"kast":78.1,"rating":1.52,"acilis_kill":5,"acilis_death":4,"cok_kill":{"2":4,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198455109823","ad":"Bora.","takim":1,"kill":22,"death":20,"assist":5,"adr":107.7,"hs_yuzde":44.8,"kd":1.1,"kast":76.1,"rating":1.35,"acilis_kill":0,"acilis_death":4,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198199887432","ad":"zeuS_tr","takim":1,"kill":13,"death":11,"assist":7,"adr":59.9,"hs_yuzde":45.2,"kd":1.18,"kast":75.9,"rating":1.07,"acilis_kill":5,"acilis_death":4,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198600123554","ad":"Krampus","takim":1,"kill":14,"death":14,"assist":8,"adr":73.8,"hs_yuzde":51.6,"kd":1.0,"kast":72.2,"rating":1.06,"acilis_kill":0,"acilis_death":0,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198777321009","ad":"leviathan","takim":1,"kill":17,"death":19,"assist":3,"adr":82.4,"hs_yuzde":40.8,"kd":0.89,"kast":72.0,"rating":1.06,"acilis_kill":5,"acilis_death":0,"cok_kill":{"2":1,"3":0,"4":0,"5":0},"ben":false}],"roundlar":[{"no":1,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"bomb_exploded"},{"no":2,"kazanan_takim":1,"benim_kill":3,"ben_oldum":true,"neden":"target_saved"},{"no":3,"kazanan_takim":1,"benim_kill":0,"ben_oldum":false,"neden":"bomb_defused"},{"no":4,"kazanan_takim":1,"benim_kill":1,"ben_oldum":true,"neden":"target_saved"},{"no":5,"kazanan_takim":0,"benim_kill":2,"ben_oldum":false,"neden":"bomb_exploded"},{"no":6,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"target_saved"},{"no":7,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"bomb_defused"},{"no":8,"kazanan_takim":1,"benim_kill":2,"ben_oldum":true,"neden":"bomb_defused"},{"no":9,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":10,"kazanan_takim":1,"benim_kill":1,"ben_oldum":true,"neden":"ct_win"},{"no":11,"kazanan_takim":1,"benim_kill":0,"ben_oldum":false,"neden":"ct_win"},{"no":12,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"ct_win"},{"no":13,"kazanan_takim":0,"benim_kill":1,"ben_oldum":false,"neden":"bomb_defused"},{"no":14,"kazanan_takim":0,"benim_kill":1,"ben_oldum":true,"neden":"target_saved"},{"no":15,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"bomb_defused"},{"no":16,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"bomb_exploded"},{"no":17,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"target_saved"},{"no":18,"kazanan_takim":1,"benim_kill":2,"ben_oldum":true,"neden":"t_win"},{"no":19,"kazanan_takim":0,"benim_kill":4,"ben_oldum":true,"neden":"ct_win"},{"no":20,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"ct_win"},{"no":21,"kazanan_takim":1,"benim_kill":2,"ben_oldum":false,"neden":"bomb_exploded"},{"no":22,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"target_saved"},{"no":23,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"t_win"}],"silahlar":[{"silah":"m4a1_silencer","kill":7,"hs":3},{"silah":"awp","kill":4,"hs":2},{"silah":"ak47","kill":4,"hs":2},{"silah":"deagle","kill":3,"hs":1},{"silah":"usp_silencer","kill":1,"hs":1}]},"1-c41a9e07-7b3f-45d1-8e22-91f0b5d6ac48-1-1":{"harita":"de_inferno","round_sayisi":20,"takimlar":[{"ad":"Takım A","skor":13,"kazandi":true},{"ad":"Takım B","skor":7,"kazandi":false}],"benim_takim":0,"oyuncu_steamid":"76561198963443734","oyuncular":[{"steamid":"76561198963443734","ad":"DuranEnnmi","takim":0,"kill":17,"death":11,"assist":2,"adr":84.9,"hs_yuzde":47.1,"kd":1.55,"kast":82.1,"rating":1.38,"acilis_kill":0,"acilis_death":4,"cok_kill":{"2":4,"3":0,"4":1,"5":0},"ben":true},{"steamid":"76561198104523311","ad":"kaanzz","takim":0,"kill":16,"death":9,"assist":7,"adr":89.1,"hs_yuzde":61.2,"kd":1.78,"kast":80.0,"rating":1.42,"acilis_kill":0,"acilis_death":1,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198877001245","ad":"Mert_06","takim":0,"kill":21,"death":20,"assist":6,"adr":115.9,"hs_yuzde":38.0,"kd":1.05,"kast":77.2,"rating":1.4,"acilis_kill":0,"acilis_death":4,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198230984410","ad":"swagg3r","takim":0,"kill":7,"death":13,"assist":8,"adr":40.6,"hs_yuzde":32.6,"kd":0.54,"kast":55.9,"rating":0.6,"acilis_kill":1,"acilis_death":1,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561199012347766","ad":"ozii","takim":0,"kill":19,"death":12,"assist":3,"adr":111.1,"hs_yuzde":53.8,"kd":1.58,"kast":89.9,"rating":1.59,"acilis_kill":5,"acilis_death":2,"cok_kill":{"2":1,"3":1,"4":0,"5":0},"ben":false},{"steamid":"76561198341200987","ad":"n1ghtfall","takim":1,"kill":14,"death":19,"assist":7,"adr":76.2,"hs_yuzde":59.7,"kd":0.74,"kast":61.1,"rating":0.88,"acilis_kill":2,"acilis_death":4,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198455109823","ad":"Bora.","takim":1,"kill":15,"death":11,"assist":2,"adr":87.2,"hs_yuzde":60.4,"kd":1.36,"kast":80.6,"rating":1.29,"acilis_kill":4,"acilis_death":3,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198199887432","ad":"zeuS_tr","takim":1,"kill":11,"death":13,"assist":4,"adr":51.0,"hs_yuzde":40.9,"kd":0.85,"kast":68.1,"rating":0.87,"acilis_kill":0,"acilis_death":1,"cok_kill":{"2":1,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198600123554","ad":"Krampus","takim":1,"kill":13,"death":19,"assist":3,"adr":67.6,"hs_yuzde":43.6,"kd":0.68,"kast":62.6,"rating":0.81,"acilis_kill":2,"acilis_death":0,"cok_kill":{"2":0,"3":0,"4":0,"5":0},"ben":false},{"steamid":"76561198777321009","ad":"leviathan","takim":1,"kill":13,"death":18,"assist":6,"adr":72.1,"hs_yuzde":54.4,"kd":0.72,"kast":65.9,"rating":0.89,"acilis_kill":0,"acilis_death":4,"cok_kill":{"2":2,"3":0,"4":0,"5":0},"ben":false}],"roundlar":[{"no":1,"kazanan_takim":1,"benim_kill":1,"ben_oldum":false,"neden":"ct_win"},{"no":2,"kazanan_takim":0,"benim_kill":2,"ben_oldum":false,"neden":"t_win"},{"no":3,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"bomb_exploded"},{"no":4,"kazanan_takim":1,"benim_kill":0,"ben_oldum":false,"neden":"bomb_defused"},{"no":5,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"bomb_exploded"},{"no":6,"kazanan_takim":1,"benim_kill":1,"ben_oldum":false,"neden":"ct_win"},{"no":7,"kazanan_takim":0,"benim_kill":2,"ben_oldum":false,"neden":"bomb_exploded"},{"no":8,"kazanan_takim":1,"benim_kill":0,"ben_oldum":true,"neden":"ct_win"},{"no":9,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"t_win"},{"no":10,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":11,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"t_win"},{"no":12,"kazanan_takim":1,"benim_kill":4,"ben_oldum":true,"neden":"ct_win"},{"no":13,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"bomb_defused"},{"no":14,"kazanan_takim":0,"benim_kill":2,"ben_oldum":false,"neden":"bomb_defused"},{"no":15,"kazanan_takim":0,"benim_kill":0,"ben_oldum":true,"neden":"bomb_defused"},{"no":16,"kazanan_takim":1,"benim_kill":1,"ben_oldum":true,"neden":"t_win"},{"no":17,"kazanan_takim":1,"benim_kill":1,"ben_oldum":true,"neden":"t_win"},{"no":18,"kazanan_takim":0,"benim_kill":0,"ben_oldum":false,"neden":"bomb_defused"},{"no":19,"kazanan_takim":0,"benim_kill":2,"ben_oldum":true,"neden":"bomb_defused"},{"no":20,"kazanan_takim":0,"benim_kill":1,"ben_oldum":true,"neden":"target_saved"}],"silahlar":[{"silah":"ak47","kill":7,"hs":3},{"silah":"m4a1_silencer","kill":4,"hs":2},{"silah":"deagle","kill":3,"hs":1},{"silah":"famas","kill":2,"hs":1},{"silah":"glock","kill":1,"hs":1}]}},"klipler":{"1-59cf10f2-8a41-4c3e-b0d7-2f61e9a8c512-1-1":{"highlightlar":[{"round":15,"score":8.0,"labels":["1v2 clutch","2K","2 HS"],"weapons":["m4a1_silencer"],"saniye":12,"klip":"/klip/anubis_59cf10f2_R15_1v2-clutch.mp4"},{"round":20,"score":7.5,"labels":["3K","3 HS"],"weapons":["famas","m4a1_silencer"],"saniye":16,"klip":"/klip/anubis_59cf10f2_R20_3k.mp4"},{"round":1,"score":6,"labels":["3K"],"weapons":["ak47","galilar"],"saniye":22,"klip":"/klip/anubis_59cf10f2_R1_3k.mp4"},{"round":21,"score":3.5,"labels":["2K","1 HS"],"weapons":["famas","mp9"],"saniye":14,"klip":null},{"round":5,"score":1.5,"labels":["1 HS"],"weapons":["awp"],"saniye":14,"klip":null}],"kayit":{"durum":"bos","mesaj":"","satirlar":[]}},"1-0b7e33a9-51d2-4f08-9c6e-a4d18e7f0233-1-1":{"highlightlar":[{"round":19,"score":13.0,"labels":["4K","3 HS","hızlı"],"weapons":["deagle","famas","m4a1_silencer"],"saniye":15,"klip":"/klip/mirage_0b7e33a9_R19_4K_3-HS_hızlı.mp4"},{"round":2,"score":7.5,"labels":["3K","3 HS"],"weapons":["ak47","deagle","galilar"],"saniye":18,"klip":"/klip/mirage_0b7e33a9_R02_3K_3-HS.mp4"},{"round":8,"score":4.0,"labels":["2K","2 HS"],"weapons":["ak47","deagle"],"saniye":10,"klip":null},{"round":18,"score":3.5,"labels":["2K","1 HS"],"weapons":["deagle","m4a1_silencer"],"saniye":18,"klip":null},{"round":5,"score":3,"labels":["2K"],"weapons":["ak47"],"saniye":18,"klip":null}],"kayit":{"durum":"bos","mesaj":"","satirlar":[]}},"1-c41a9e07-7b3f-45d1-8e22-91f0b5d6ac48-1-1":{"highlightlar":[{"round":7,"score":11.0,"labels":["1v3 clutch","2K","2 HS"],"weapons":["tec9"],"saniye":21,"klip":null},{"round":12,"score":10.5,"labels":["4K","1 HS"],"weapons":["ak47","galilar"],"saniye":19,"klip":null},{"round":2,"score":8.5,"labels":["1v2 clutch","2K","smoke arkası"],"weapons":["ak47"],"saniye":19,"klip":null},{"round":14,"score":5.5,"labels":["2K","2 HS","smoke arkası"],"weapons":["deagle","m4a1_silencer"],"saniye":10,"klip":null},{"round":19,"score":3.5,"labels":["2K","1 HS"],"weapons":["m4a1_silencer","mp9"],"saniye":11,"klip":null}],"kayit":{"durum":"bos","mesaj":"","satirlar":[]}}},"en_iyi_ek":[{"ad":"ancient_e3c103b2_R11_1v3-clutch_4K_1-HS.mp4","klip":"/klip/ancient_e3c103b2_R11_1v3-clutch_4K_1-HS.mp4","harita":"ancient","kod":"e3c103b2","round":11,"etiketler":["1v3 clutch","4K","1 HS"],"silahlar":["m4a1_silencer","hegrenade"],"skor":17.5,"tahmini":false,"demo":null,"tarih":"2026-10-28T20:14:00","boyut_mb":30.9,"saniye":19},{"ad":"ancient_e3c103b2_R04_3K_2-HS.mp4","klip":"/klip/ancient_e3c103b2_R04_3K_2-HS.mp4","harita":"ancient","kod":"e3c103b2","round":4,"etiketler":["3K","2 HS"],"silahlar":["ak47"],"skor":7.5,"tahmini":false,"demo":null,"tarih":"2026-10-28T20:14:00","boyut_mb":24.2,"saniye":14},{"ad":"ancient_e3c103b2_R20_2K_1-HS.mp4","klip":"/klip/ancient_e3c103b2_R20_2K_1-HS.mp4","harita":"ancient","kod":"e3c103b2","round":20,"etiketler":["2K","1 HS"],"silahlar":["famas"],"skor":4.0,"tahmini":false,"demo":null,"tarih":"2026-10-28T20:14:00","boyut_mb":18.6,"saniye":11},{"ad":"nuke_7f21aa90_R09_ACE.mp4","klip":"/klip/nuke_7f21aa90_R09_ACE.mp4","harita":"nuke","kod":"7f21aa90","round":9,"etiketler":["ACE"],"silahlar":[],"skor":15.0,"tahmini":true,"demo":null,"tarih":"2026-10-19T22:31:00","boyut_mb":36.4,"saniye":22},{"ad":"nuke_7f21aa90_R22_1v2-clutch.mp4","klip":"/klip/nuke_7f21aa90_R22_1v2-clutch.mp4","harita":"nuke","kod":"7f21aa90","round":22,"etiketler":["1v2 clutch"],"silahlar":[],"skor":6.5,"tahmini":true,"demo":null,"tarih":"2026-10-19T22:31:00","boyut_mb":21.7,"saniye":16},{"ad":"dust2_a5c90e17_R03_3K_3-HS_hızlı.mp4","klip":"/klip/dust2_a5c90e17_R03_3K_3-HS_hızlı.mp4","harita":"dust2","kod":"a5c90e17","round":3,"etiketler":["3K","3 HS","hızlı"],"silahlar":["deagle"],"skor":9.0,"tahmini":false,"demo":null,"tarih":"2026-10-24T18:02:00","boyut_mb":19.8,"saniye":12},{"ad":"dust2_a5c90e17_R14_2K_smoke-arkası.mp4","klip":"/klip/dust2_a5c90e17_R14_2K_smoke-arkası.mp4","harita":"dust2","kod":"a5c90e17","round":14,"etiketler":["2K","smoke arkası"],"silahlar":["awp"],"skor":4.5,"tahmini":false,"demo":null,"tarih":"2026-10-24T18:02:00","boyut_mb":17.1,"saniye":10}],"en_iyi_montaj":null,"kariyer_ek":[{"id":"1-5d9dc9f8-9531-40ed-ae8e-36f681e74ef5-1-1","tarih":"2026-10-02T20:14:00","demo_var":false,"harita":"de_mirage","round_sayisi":22,"skor":[9,13],"sonuc":"M","ad":"DuranEnnmi","cok_kill":{"2":2,"3":0,"4":0,"5":0},"rating":0.82,"adr":62.2,"kast":56.3,"kd":1.0,"hs_yuzde":45.8,"kill":13,"death":13,"assist":2,"acilis_kill":1,"acilis_death":4},{"id":"1-f28c105d-3926-4a17-aa09-f29d953f48f1-1-1","tarih":"2026-10-04T21:30:00","demo_var":false,"harita":"de_inferno","round_sayisi":24,"skor":[13,11],"sonuc":"G","ad":"DuranEnnmi","cok_kill":{"2":2,"3":0,"4":0,"5":0},"rating":0.97,"adr":71.5,"kast":61.9,"kd":1.21,"hs_yuzde":46.4,"kill":17,"death":14,"assist":2,"acilis_kill":5,"acilis_death":5},{"id":"1-24ede6a4-8a6a-41e2-a922-8f6d4ef8aa38-1-1","tarih":"2026-10-07T19:52:00","demo_var":false,"harita":"de_ancient","round_sayisi":20,"skor":[7,13],"sonuc":"M","ad":"DuranEnnmi","cok_kill":{"2":1,"3":0,"4":0,"5":0},"rating":0.71,"adr":47.3,"kast":60.0,"kd":0.71,"hs_yuzde":40.4,"kill":10,"death":14,"assist":8,"acilis_kill":2,"acilis_death":1},{"id":"1-0f4205b4-9e77-434b-a7f1-881eae2eb154-1-1","tarih":"2026-10-09T22:05:00","demo_var":false,"harita":"de_nuke","round_sayisi":21,"skor":[13,8],"sonuc":"G","ad":"DuranEnnmi","cok_kill":{"2":2,"3":0,"4":0,"5":0},"rating":1.12,"adr":79.9,"kast":72.4,"kd":1.42,"hs_yuzde":35.4,"kill":17,"death":12,"assist":5,"acilis_kill":3,"acilis_death":4},{"id":"1-3e7d1bfb-14f4-4930-a4cd-7ebf86734721-1-1","tarih":"2026-10-11T18:40:00","demo_var":false,"harita":"de_dust2","round_sayisi":24,"skor":[11,13],"sonuc":"M","ad":"DuranEnnmi","cok_kill":{"2":2,"3":0,"4":0,"5":0},"rating":0.93,"adr":65.7,"kast":67.7,"kd":1.21,"hs_yuzde":49.4,"kill":17,"death":14,"assist":4,"acilis_kill":4,"acilis_death":3},{"id":"1-eeeacbe2-7d2c-46bf-a0a0-ab10f646e1f4-1-1","tarih":"2026-10-14T20:48:00","demo_var":false,"harita":"de_mirage","round_sayisi":23,"skor":[13,10],"sonuc":"G","ad":"DuranEnnmi","cok_kill":{"2":2,"3":0,"4":0,"5":0},"rating":1.04,"adr":75.9,"kast":65.6,"kd":1.5,"hs_yuzde":41.5,"kill":18,"death":12,"assist":2,"acilis_kill":5,"acilis_death":5},{"id":"1-cc011cdd-74c9-4119-ad70-f1d617f5e837-1-1","tarih":"2026-10-16T21:12:00","demo_var":false,"harita":"de_anubis","round_sayisi":23,"skor":[10,13],"sonuc":"M","ad":"DuranEnnmi","cok_kill":{"2":2,"3":0,"4":0,"5":0},"rating":0.88,"adr":62.7,"kast":61.3,"kd":1.07,"hs_yuzde":44.9,"kill":16,"death":15,"assist":4,"acilis_kill":4,"acilis_death":1},{"id":"1-48db40af-b774-462c-ae31-58d5ab2cd31e-1-1","tarih":"2026-10-18T19:25:00","demo_var":false,"harita":"de_inferno","round_sayisi":19,"skor":[13,6],"sonuc":"G","ad":"DuranEnnmi","cok_kill":{"2":1,"3":1,"4":0,"5":0},"rating":1.31,"adr":96.5,"kast":84.1,"kd":1.89,"hs_yuzde":52.1,"kill":17,"death":9,"assist":2,"acilis_kill":4,"acilis_death":3},{"id":"1-3f63af83-65dc-4641-aeab-7f1bdf1582b0-1-1","tarih":"2026-10-21T22:31:00","demo_var":false,"harita":"de_train","round_sayisi":24,"skor":[13,11],"sonuc":"G","ad":"DuranEnnmi","cok_kill":{"2":2,"3":0,"4":0,"5":0},"rating":0.99,"adr":67.0,"kast":69.7,"kd":1.23,"hs_yuzde":36.8,"kill":16,"death":13,"assist":2,"acilis_kill":2,"acilis_death":4},{"id":"1-b4d66a3a-6a50-4fc8-a5bd-e25aaec6f024-1-1","tarih":"2026-10-23T20:02:00","demo_var":false,"harita":"de_mirage","round_sayisi":30,"skor":[14,16],"sonuc":"M","ad":"DuranEnnmi","cok_kill":{"2":3,"3":0,"4":0,"5":0},"rating":1.08,"adr":74.2,"kast":69.7,"kd":1.44,"hs_yuzde":46.1,"kill":23,"death":16,"assist":5,"acilis_kill":2,"acilis_death":2},{"id":"1-2eae05cf-4343-4482-a010-6b40254b0c4e-1-1","tarih":"2026-10-25T18:15:00","demo_var":false,"harita":"de_ancient","round_sayisi":22,"skor":[13,9],"sonuc":"G","ad":"DuranEnnmi","cok_kill":{"2":1,"3":1,"4":0,"5":0},"rating":1.17,"adr":86.8,"kast":69.0,"kd":1.64,"hs_yuzde":52.3,"kill":18,"death":11,"assist":6,"acilis_kill":3,"acilis_death":5},{"id":"1-ad1b72db-bd62-40dd-a74e-def8e647cb8f-1-1","tarih":"2026-10-27T21:44:00","demo_var":false,"harita":"de_dust2","round_sayisi":17,"skor":[13,4],"sonuc":"G","ad":"DuranEnnmi","cok_kill":{"2":1,"3":1,"4":1,"5":0},"rating":1.46,"adr":107.5,"kast":85.0,"kd":2.25,"hs_yuzde":47.6,"kill":18,"death":8,"assist":8,"acilis_kill":5,"acilis_death":4},{"id":"1-fc132d0d-3571-470c-a298-570d1c2442f9-1-1","tarih":"2026-10-29T20:20:00","demo_var":false,"harita":"de_nuke","round_sayisi":21,"skor":[8,13],"sonuc":"M","ad":"DuranEnnmi","cok_kill":{"2":2,"3":0,"4":0,"5":0},"rating":0.79,"adr":58.1,"kast":58.4,"kd":0.92,"hs_yuzde":38.2,"kill":12,"death":13,"assist":6,"acilis_kill":1,"acilis_death":1},{"id":"1-dfd43f37-353c-49d3-a605-a2682607679d-1-1","tarih":"2026-10-31T19:08:00","demo_var":false,"harita":"de_anubis","round_sayisi":24,"skor":[13,11],"sonuc":"G","ad":"DuranEnnmi","cok_kill":{"2":2,"3":0,"4":0,"5":0},"rating":1.09,"adr":74.5,"kast":69.5,"kd":1.5,"hs_yuzde":34.6,"kill":18,"death":12,"assist":4,"acilis_kill":3,"acilis_death":5},{"id":"1-7bdc968b-4fd5-415f-a24e-bfea1a28f7b3-1-1","tarih":"2026-11-01T21:37:00","demo_var":false,"harita":"de_inferno","round_sayisi":20,"skor":[13,7],"sonuc":"G","ad":"DuranEnnmi","cok_kill":{"2":1,"3":1,"4":0,"5":0},"rating":1.22,"adr":92.6,"kast":80.7,"kd":1.89,"hs_yuzde":44.3,"kill":17,"death":9,"assist":4,"acilis_kill":3,"acilis_death":4}]}/*ORNEK_BITIR*/;

  /* ======== sabitler ======== */
  const UZANTI = /\.dem(\.(zst|gz|bz2))?$/i;
  const YOKLAMA_MS = 2000;
  const KONTROL_MS = 30000;
  const OZET_EN_FAZLA = 12; // kenar çubuğundaki skor/form özeti için arka planda alınan demo sayısı
  const NEDEN = {
    t_win: "T'ler rakibi eledi", ct_win: "CT'ler rakibi eledi",
    bomb_exploded: 'Bomba patladı', bomb_defused: 'Bomba imha edildi',
    target_saved: 'Süre doldu, hedef korundu', time_ran_out: 'Süre doldu',
    t_surrender: "T'ler teslim oldu", ct_surrender: "CT'ler teslim oldu",
    terrorists_surrender: "T'ler teslim oldu", cts_surrender: "CT'ler teslim oldu", draw: 'Berabere',
  };
  const IKON = { t_win: 'i-elim', ct_win: 'i-elim', bomb_exploded: 'i-bomb', bomb_defused: 'i-defuse', target_saved: 'i-time', time_ran_out: 'i-time' };
  const CT_NEDEN = new Set(['ct_win', 'bomb_defused', 'target_saved', 'time_ran_out', 't_surrender', 'terrorists_surrender']);
  const T_NEDEN = new Set(['t_win', 'bomb_exploded', 'ct_surrender', 'cts_surrender']);
  const SILAH = {
    ak47: 'AK-47', m4a1: 'M4A4', m4a1_silencer: 'M4A1-S', awp: 'AWP', deagle: 'Desert Eagle',
    usp_silencer: 'USP-S', glock: 'Glock-18', hkp2000: 'P2000', p250: 'P250', tec9: 'Tec-9',
    fiveseven: 'Five-SeveN', cz75a: 'CZ75-Auto', elite: 'Dual Berettas', revolver: 'R8',
    galilar: 'Galil AR', famas: 'FAMAS', sg556: 'SG 553', aug: 'AUG', ssg08: 'SSG 08',
    scar20: 'SCAR-20', g3sg1: 'G3SG1', mac10: 'MAC-10', mp9: 'MP9', mp7: 'MP7', mp5sd: 'MP5-SD',
    ump45: 'UMP-45', p90: 'P90', bizon: 'PP-Bizon', nova: 'Nova', xm1014: 'XM1014',
    mag7: 'MAG-7', sawedoff: 'Sawed-Off', m249: 'M249', negev: 'Negev', taser: 'Zeus x27',
    knife: 'Bıçak', hegrenade: 'El bombası', inferno: 'Molotof', molotov: 'Molotof', incgrenade: 'Yangın bombası', world: 'Dünya',
  };
  const TUR = {};
  [['Tüfek', 'ak47 m4a1 m4a1_silencer galilar famas sg556 aug'], ['Keskin nişancı', 'awp ssg08 scar20 g3sg1'],
   ['Tabanca', 'glock usp_silencer hkp2000 p250 tec9 fiveseven cz75a elite deagle revolver'],
   ['SMG', 'mac10 mp9 mp7 mp5sd ump45 p90 bizon'], ['Ağır', 'nova xm1014 mag7 sawedoff m249 negev'],
   ['Ekipman', 'knife taser hegrenade inferno molotov incgrenade']].forEach(([t, l]) => l.split(' ').forEach((s) => { TUR[s] = t; }));
  const HARITA_RENK = {
    anubis: ['#cfa865', '#255f63', '#f1dcae'], mirage: ['#dca46a', '#6b3f22', '#f6d9ac'],
    inferno: ['#c25f3d', '#47271e', '#efbf94'], dust2: ['#d9b676', '#6b5230', '#f5e2b8'],
    nuke: ['#8ea8b6', '#2b3a45', '#d2e0e8'], ancient: ['#6d9a5a', '#253d27', '#c3dca4'],
    overpass: ['#7e9b7b', '#2f4036', '#cddcc6'], vertigo: ['#91a8c6', '#2a3750', '#d8e3f0'],
    train: ['#8a8b76', '#32342a', '#cfcfba'],
  };
  // Türkçe büyük harf düzeltmesi: <html lang="tr"> altında text-transform:uppercase "i"yi "İ" yapar;
  // İngilizce sözcükler lang="en" ile sarılır ("HIGHLIGHT", "KILL" doğru çıkar).
  const EN = (w) => `<span lang="en">${w}</span>`;
  const KILL_ADI = { '2K': `Çift ${EN('kill')}`, '3K': `Üçlü ${EN('kill')}`, '4K': `Dörtlü ${EN('kill')}`, '5K': 'ACE', ACE: 'ACE' };
  const ADIMLAR = ['Hazırlık', 'CS2 başlatma', 'Kayıt', 'Tamamlama'];

  /* ======== durum ======== */
  const S = {
    demolar: [],
    kontrol: null,
    demo: {},            // demo id -> istatistik (GET /api/demo/<id>)
    klipler: {},         // demo id -> {highlightlar, kayit} (GET /api/demo/<id>/klipler)
    klipHata: {},        // demo id -> hata mesajı
    secili: null,
    sira: { k: 'rating', az: true },
    enIyi: 3,
    istekNo: 0,
    aktifIs: null,       // kaydı süren demo (sunucu aynı anda tek kayıt yapar)
    kayitHedef: {},      // demo id -> kaç klip istendi
    ilerleme: {},        // demo id -> {adim, yuzde} (geri gitmesin diye)
    yoklamaZaman: null,
    yoklamaHata: null,
    kayitBasliyor: false,
    gunlukAcik: false,
    yeni: new Set(),     // bu oturumda kaydedilen klip anahtarları
    kuyruk: [], yukleniyor: false,
    analizde: new Set(),
    ozetSuruyor: false,
    kontrolSuruyor: null,
    // "En iyi anlarım" (#en-iyi): tüm maçlardaki klipler (GET /api/en-iyi)
    gorunum: 'mac',      // 'mac' | 'en-iyi'
    sonDemo: null,       // "Maçlara dön" bu demoyu açar
    ei: null,            // {klipler, montaj}
    eiHata: null,
    eiYukleniyor: false,
    eiHarita: '',        // harita filtresi ('' = tümü)
    eiAdet: 10,          // vitrinde kaç klip (0 = hepsi)
    eiGorunen: [],       // vitrinde çizilen klipler (oynatıcı sırası)
    mjAdet: 10,
    montajSuruyor: false,
    montajBas: 0,
    montajHata: null,
    montajYeni: false,
    // Kariyer (#kariyer): GET /api/kariyer + maç kartı
    kr: null,            // {maclar, bekleyen, okunamayan}
    krHata: null,
    krYukleniyor: false,
    krMetrik: 'rating',  // grafikte gösterilen ölçü
    kartBoyut: 'linkedin',
  };
  const EN_IYI = 'en-iyi';

  /* ======== yardımcılar ======== */
  const $ = (s, k = document) => k.querySelector(s);
  const $$ = (s, k = document) => [...k.querySelectorAll(s)];
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const sayi = (x, o = 0) => (x == null || isNaN(x)) ? '–' : Number(x).toLocaleString('tr-TR', { minimumFractionDigits: o, maximumFractionDigits: o });
  const ikon = (id, sinif = 'i') => `<svg class="${sinif}"><use href="#${id}"/></svg>`;
  const bekle = (ms) => new Promise((r) => setTimeout(r, ms));
  const kopya = (x) => JSON.parse(JSON.stringify(x));
  const karsi = (x) => (x === 'ct' ? 't' : 'ct');
  const sinirla = (x, a, b) => Math.max(a, Math.min(b, x));
  const haritaAnahtar = (h) => String(h || '').replace(/^(de|cs|ar)_/, '').toLowerCase();
  function haritaAd(h) {
    if (!h) return null;
    const a = haritaAnahtar(h).replace(/_/g, ' ');
    return a.charAt(0).toUpperCase() + a.slice(1); // harita adları İngilizce ('inferno' → 'Inferno')
  }
  function haritaStil(h) {
    const r = HARITA_RENK[haritaAnahtar(h)] || ['#56607a', '#1b2030', '#a3aec8'];
    return `--h1:${r[0]};--h2:${r[1]};--h3:${r[2]}`;
  }
  function tarihYaz(t, yil) {
    const d = new Date(t);
    if (!t || isNaN(d)) return String(t || '');
    const o = { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' };
    if (yil || d.getFullYear() !== new Date().getFullYear()) o.year = 'numeric';
    return d.toLocaleString('tr-TR', o);
  }
  const silahAd = (s) => SILAH[s] || String(s || '?').replace(/^weapon_/, '');
  const silahTur = (s) => TUR[s] || 'Diğer';
  const nedenAd = (n) => NEDEN[n] || String(n || 'bilinmiyor').replace(/_/g, ' ');
  const ratingSinif = (r) => (r >= 1.1 ? 'r-iyi' : r < 0.9 ? 'r-kotu' : 'r-orta');
  const esik = (d, iyi, kotu) => (d == null ? 'orta' : d >= iyi ? 'iyi' : d < kotu ? 'kotu' : 'orta');
  const benBul = (s) => (s.oyuncular || []).find((o) => o.ben)
    || (s.oyuncular || []).find((o) => String(o.steamid) === String(s.oyuncu_steamid)) || null;
  const sure = (sn) => { sn = Math.max(0, sn || 0); return `${Math.floor(sn / 60)}:${String(Math.floor(sn % 60)).padStart(2, '0')}`; };
  const AZ_HAREKET = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const kaydir = () => (AZ_HAREKET ? 'auto' : 'smooth');
  const takimlarOf = (s) => {
    const t = s.takimlar || [];
    return [t[0] || { ad: 'Takım A', skor: 0, kazandi: false }, t[1] || { ad: 'Takım B', skor: 0, kazandi: false }];
  };
  const kisaSorun = (s) => String(s || '').split(/\. | — /)[0];

  /* taraf çıkarımı: round bitiş nedeninden (ct_win, bomb_defused…) kazanan taraf belli olur */
  const kazananTaraf = (r) => (CT_NEDEN.has(r.neden) ? 'ct' : T_NEDEN.has(r.neden) ? 't' : null);
  const yariNo = (no) => (no <= 12 ? 0 : no <= 24 ? 1 : 2 + Math.floor((no - 25) / 3));
  const yariAd = (g) => (g === 0 ? '1. yarı' : g === 1 ? '2. yarı' : `Uzatma ${Math.floor((g - 2) / 2) + 1} · ${((g - 2) % 2) + 1}. yarı`);
  function taraflar(s) {
    const m = {};
    const R = s.roundlar || [];
    R.forEach((r) => {
      const g = yariNo(r.no);
      const w = kazananTaraf(r);
      if (m[g] || !w) return;
      m[g] = r.kazanan_takim === 0 ? w : karsi(w);
    });
    const son = Math.max(0, ...R.map((r) => yariNo(r.no)));
    for (let g = 0; g <= son; g++) if (!m[g]) m[g] = g === 0 ? (m[1] ? karsi(m[1]) : 't') : karsi(m[g - 1]);
    return m;
  }
  const takimTaraf = (m, takim, no) => { const x = m[yariNo(no)] || 't'; return takim === 0 ? x : karsi(x); };
  const tarafRenk = (t) => (t === 'ct' ? 'var(--ct)' : 'var(--t)');
  const tarafAlfa = (t) => (t === 'ct' ? 'var(--ct-a)' : 'var(--t-a)');

  function demoOzet(id) {
    const d = S.demolar.find((x) => x.id === id);
    const s = S.demo[id];
    if (!d || !s) return null;
    const biz = s.benim_takim ?? 0;
    const T = takimlarOf(s);
    const a = T[biz].skor, b = T[1 - biz].skor;
    return { biz: a, onlar: b, sonuc: a > b ? 'G' : a < b ? 'M' : 'B', ben: benBul(s) };
  }

  /* ======== API ======== */
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

  /* ======== örnek mod (ağ yok; ?ornek=1) ======== */
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

  // Kayıt işini taklit eder; satırlar klip.py'nin gerçek çıktısıyla aynı biçimde (ilerleme bundan okunur).
  function ornekIsIlerlet(id) {
    const v = ornekVeri;
    const is = v.isler[id];
    const k = v.klipler[id];
    if (!is || k.kayit.durum !== 'calisiyor') return;
    const s = v.demo[id];
    const d = v.demolar.find((x) => x.id === id);
    const ad = d ? d.ad : id;
    const sirali = [...k.highlightlar].sort((a, b) => b.score - a.score);
    const hedef = is.enIyi > 0 ? sirali.slice(0, is.enIyi) : sirali;
    const n = hedef.length;
    const onek = `${String(s.harita || 'demo').replace(/^de_/, '')}_${(id.split('-')[1] || id).slice(0, 8)}`;
    const dosya = (h) => `${onek}_R${String(h.round).padStart(2, '0')}_${(h.labels || []).join('_').replace(/\s+/g, '-')}.mp4`;
    const ekle = (...x) => { k.kayit.satirlar = [...k.kayit.satirlar, ...x].slice(-40); };
    const a = ++is.adim;
    if (a === 1) ekle(`=== ${ad} ===`, `${s.harita} — ${sirali.length} highlight (skor >= 3.0)`);
    else if (a === 2) ekle(`[1/1] ${ad}: ${n} klip`);
    else if (a < 3 + n * 2) ekle(`  [csdm] Recording sequence ${Math.ceil((a - 2) / 2)}/${n}…`);
    else if (a < 3 + n * 3) {
      const h = hedef[a - 3 - n * 2];
      ekle(`  -> ${dosya(h)} (1 parça)`);
      if (!h.klip) h.klip = `/klip/${dosya(h)}`;
      if (d) d.klip_sayisi = k.highlightlar.filter((x) => x.klip).length;
    } else {
      ekle(`${n} yeni klip: C:\\cs-clip\\klipler`);
      k.kayit.durum = 'bitti';
      k.kayit.mesaj = 'Kayıt bitti';
      delete v.isler[id];
    }
  }

  async function ornekApi(yol, { method = 'GET', body } = {}) {
    const v = await ornekYukle();
    await bekle(120);
    const hata = (status, mesaj) => Object.assign(new Error(mesaj), { status });
    if (yol === '/api/kontrol') return kopya(v.kontrol);
    if (yol === '/api/demolar') return kopya(v.demolar);
    if (yol === '/api/en-iyi') return ornekEnIyi(v);
    if (yol === '/api/kariyer') return ornekKariyer(v);
    if (yol === '/api/en-iyi/montaj') {
      if (method !== 'POST') throw hata(405, 'Geçersiz istek.');
      if (v.montajSuruyor) throw hata(409, 'Montaj zaten hazırlanıyor.');
      const l = ornekEnIyi(v).klipler;
      if (!l.length) throw hata(409, 'Montaj için klip yok.');
      const adet = Math.min(Math.max(Number(JSON.parse(body || '{}').adet) || 10, 1), l.length);
      v.montajSuruyor = true;
      try { await bekle(2600); } finally { v.montajSuruyor = false; }
      const secilen = l.slice(0, adet);
      v.en_iyi_montaj = {
        klip: '/klip/en_iyi_montaj.mp4', adet,
        boyut_mb: Math.round(secilen.reduce((a, k) => a + (k.boyut_mb || 0), 0) * 9.2) / 10,
        tarih: new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 19), // yerel saat
        saniye: secilen.reduce((a, k) => a + (k.saniye || 15), 0),
      };
      return kopya(v.en_iyi_montaj);
    }
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
    if (Object.keys(v.isler).length) throw hata(409, 'Başka bir kayıt sürüyor.');
    const enIyi = Number(JSON.parse(body || '{}').en_iyi) || 0;
    k.kayit = { durum: 'calisiyor', mesaj: 'Kayıt başladı', satirlar: [] };
    v.isler[id] = { adim: 0, enIyi };
    return { durum: 'calisiyor' };
  }

  // GET /api/en-iyi taklidi: örnek demolarda kayıtlı klipler + ornek.json'daki eski maç klipleri
  // (en_iyi_ek: listede olmayan maçlar, biri dosya adından tahmini puanlı).
  function ornekEnIyi(v) {
    const l = [];
    v.demolar.forEach((d) => {
      const k = v.klipler[d.id], s = v.demo[d.id];
      if (!k) return;
      (k.highlightlar || []).forEach((h) => {
        if (!h.klip) return;
        l.push({
          ad: decodeURIComponent(h.klip.split('/').pop()), klip: h.klip,
          harita: haritaAnahtar((s && s.harita) || d.harita), kod: (d.id.split('-')[1] || d.id).slice(0, 8),
          round: h.round, etiketler: h.labels || [], silahlar: h.weapons || [], skor: h.score, tahmini: false,
          demo: d.id, tarih: d.tarih, boyut_mb: Math.round((h.saniye || 15) * 19) / 10, saniye: h.saniye,
        });
      });
    });
    (v.en_iyi_ek || []).forEach((x) => l.push(kopya(x)));
    l.sort((a, b) => b.skor - a.skor);
    return { klipler: l, montaj: v.en_iyi_montaj ? kopya(v.en_iyi_montaj) : null };
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

  /* ======== bildirim + ipucu ======== */
  function bildir(metin, tur = '') {
    const el = document.createElement('div');
    el.className = 'bildirim ' + tur;
    el.setAttribute('role', tur === 'hata' ? 'alert' : 'status');
    el.innerHTML = ikon(tur === 'hata' ? 'i-alert' : tur === 'basari' ? 'i-check' : 'i-film') + `<span>${esc(metin)}</span>`;
    $('#bildirimler').append(el);
    setTimeout(() => { el.classList.add('cikis'); setTimeout(() => el.remove(), 320); }, tur === 'hata' ? 6500 : 3800);
  }
  const ipucu = $('#ipucu');
  let ipucuEl = null;
  function ipucuGoster(el) {
    ipucuEl = el;
    const [ilk, ...geri] = el.dataset.tip.split('\n');
    ipucu.innerHTML = `<b>${esc(ilk)}</b>${geri.length ? '\n' + esc(geri.join('\n')) : ''}`;
    const r = el.getBoundingClientRect();
    const w = ipucu.offsetWidth, h = ipucu.offsetHeight;
    const x = sinirla(r.left + r.width / 2 - w / 2, 8, innerWidth - w - 8);
    let y = r.top - h - 10;
    if (y < 70) y = r.bottom + 10;
    ipucu.style.transform = `translate(${Math.round(x)}px,${Math.round(y)}px)`;
    ipucu.classList.add('acik');
  }
  function ipucuGizle() { ipucuEl = null; ipucu.classList.remove('acik'); }
  document.addEventListener('pointerover', (e) => {
    const el = e.target.closest('[data-tip]');
    if (el !== ipucuEl) { if (el) ipucuGoster(el); else ipucuGizle(); }
    const iz = e.target.closest('.tl-izgara');
    $$('.tl-izgara .hl').forEach((x) => x.classList.remove('hl'));
    const r = e.target.closest('[data-r]');
    if (iz && r) $$(`[data-r="${r.dataset.r}"]`, iz).forEach((x) => x.classList.add('hl'));
  });
  addEventListener('scroll', ipucuGizle, { passive: true });

  /* ======== sayaç animasyonu ======== */
  function sayaclar(kok) {
    $$('[data-say]', kok).forEach((el) => {
      const hedef = parseFloat(el.dataset.say);
      const o = +(el.dataset.o || 0);
      if (AZ_HAREKET || isNaN(hedef)) { el.textContent = sayi(hedef, o); return; }
      const t0 = performance.now(), dur = 750;
      const adim = (t) => {
        const p = Math.min(1, (t - t0) / dur);
        el.textContent = sayi(hedef * (1 - Math.pow(1 - p, 3)), o);
        if (p < 1) requestAnimationFrame(adim);
      };
      requestAnimationFrame(adim);
    });
  }

  /* ======== kayıt öncesi kontrol (GET /api/kontrol) ======== */
  function kontrolCiz() {
    const k = S.kontrol;
    const hap = $('#durumHap');
    const metin = $('#durumMetin');
    if (!k) {
      hap.classList.remove('hazir');
      metin.textContent = 'Kontrol…';
      hap.title = 'Kayıt öncesi kontrol yapılıyor';
    } else {
      const sorunlar = k.sorunlar || [];
      hap.classList.toggle('hazir', !!k.hazir);
      metin.innerHTML = k.hazir ? 'Kayda hazır'
        : 'Hazır değil' + (sorunlar.length ? '<span class="uzun"> · ' + esc(kisaSorun(sorunlar[0])) + (sorunlar.length > 1 ? ` +${sorunlar.length - 1}` : '') + '</span>' : '');
      hap.title = k.hazir ? 'CS2 ve FACEIT kapalı; kayıt başlatılabilir.' : sorunlar.join('\n');
    }
    const kutu = $('#kontrolKutu');
    if (!kutu) return;
    const dugme = (yukleniyor) => `<button class="btn-ikincil${yukleniyor ? ' donuyor' : ''}" id="kontrolYenile" type="button"${yukleniyor ? ' disabled' : ''}>${ikon('i-refresh')}${yukleniyor ? 'Kontrol ediliyor…' : 'Yeniden kontrol et'}</button>`;
    if (!k) {
      kutu.className = 'kontrol';
      kutu.innerHTML = `<div class="kontrol-bas">${ikon('i-time')}Kayıt öncesi kontrol</div><p class="bos-not yukleniyor-not">Kontrol ediliyor…</p>`;
      return;
    }
    const yukleniyor = !!S.kontrolSuruyor;
    kutu.className = 'kontrol ' + (k.hazir ? 'hazir' : 'sorun');
    kutu.innerHTML = k.hazir
      ? `<div class="kontrol-bas">${ikon('i-check')}Kayda hazır</div>
         <ul><li>CS2 ve FACEIT kapalı.</li><li>CS Demo Manager, FFmpeg ve PostgreSQL hazır; diskte yer var.</li></ul>
         ${dugme(yukleniyor)}`
      : `<div class="kontrol-bas">${ikon('i-alert')}${k.ulasilamadi ? 'Sunucuya ulaşılamadı' : 'Kayıt öncesi kontrol'}</div>
         <ul>${(k.sorunlar || []).map((s) => `<li>${esc(s)}</li>`).join('')}</ul>
         ${dugme(yukleniyor)}`;
  }
  function kontrolYenile(elle = false) {
    if (S.kontrolSuruyor) return S.kontrolSuruyor;
    S.kontrolSuruyor = (async () => {
      await null; // S.kontrolSuruyor atansın, düğme "Kontrol ediliyor…" çizilsin
      if (elle) kontrolCiz();
      try {
        S.kontrol = await api('/api/kontrol');
      } catch (e) {
        S.kontrol = { hazir: false, sorunlar: [e.message], ulasilamadi: true };
      }
      S.kontrolSuruyor = null;
      kontrolCiz();
      if (elle) {
        const k = S.kontrol;
        if (k.hazir) bildir('Kontrol tamam: kayda hazırsın.', 'basari');
        else bildir('Hâlâ hazır değil: ' + ((k.sorunlar || []).map(kisaSorun).join(', ') || 'bilinmeyen sorun'), 'hata');
      }
      return S.kontrol;
    })();
    return S.kontrolSuruyor;
  }

  /* ======== kenar çubuğu ======== */
  function formCiz() {
    const oz = S.demolar.map((d) => demoOzet(d.id)).filter(Boolean);
    const kutular = S.demolar.slice(0, 5).map((d) => {
      const o = demoOzet(d.id);
      return o ? `<span class="${o.sonuc}" data-tip="${esc(haritaAd(d.harita) || 'Demo')} · ${o.biz}–${o.onlar}\n${esc(tarihYaz(d.tarih))}">${o.sonuc}</span>`
        : `<span class="bos" data-tip="${d.analiz_edildi ? 'Özet yükleniyor' : 'Analiz edilmedi'}"></span>`;
    }).join('');
    const ort = (f) => {
      const l = oz.filter((o) => o.ben);
      return l.length ? l.reduce((a, o) => a + (o.ben[f] || 0), 0) / l.length : null;
    };
    const r = ort('rating');
    $('#form').innerHTML = `<div class="form-bas"><span>Son maçlar</span><span>${oz.filter((o) => o.sonuc === 'G').length}G · ${oz.filter((o) => o.sonuc === 'M').length}M</span></div>
      <div class="form-kutular">${kutular || '<span class="bos"></span>'}</div>
      <div class="form-say"><div>Ort. ${EN('rating')}<b class="${r != null ? ratingSinif(r) : ''}"${r != null ? ' style="color:var(--rc)"' : ''}>${sayi(r, 2)}</b></div><div>Ort. ADR<b>${sayi(ort('adr'), 1)}</b></div></div>`;
  }
  function listeCiz() {
    $('#demoSay').textContent = S.demolar.length;
    $('#menuSay').textContent = S.demolar.length;
    $('#demolar').innerHTML = S.demolar.map((d) => {
      const o = demoOzet(d.id);
      const ad = haritaAd(d.harita);
      const kod = ad ? ad.slice(0, 3).toUpperCase() : '?';
      const isVar = S.aktifIs === d.id;
      const sag = o
        ? `<span class="do-skor ${o.sonuc}"><b>${o.biz}</b><i>:</i>${o.onlar}</span><span class="do-sonuc ${o.sonuc}">${o.sonuc === 'G' ? 'Galibiyet' : o.sonuc === 'M' ? 'Mağlubiyet' : 'Berabere'}</span>`
        : S.analizde.has(d.id) ? '<span class="do-sonuc A">Analizde…</span>'
          : d.analiz_edildi ? '<span class="do-sonuc B">Analiz edildi</span>' : '<span class="do-sonuc A">Analiz edilmedi</span>';
      return `<li><button class="demo-oge${d.id === S.secili ? ' secili' : ''}" data-demo="${esc(d.id)}" title="${esc(d.ad)}" type="button">
        <span class="do-harita${ad ? '' : ' bilinmez'}" style="${haritaStil(d.harita)}" lang="en">${esc(kod)}</span>
        <span class="do-orta"><span class="do-ad"${ad ? ' lang="en"' : ''}>${esc(ad || 'Bilinmeyen harita')}</span>
          <span class="do-tarih">${esc(tarihYaz(d.tarih))}${d.klip_sayisi ? ` · <span class="klip-say">${ikon('i-film')}${d.klip_sayisi}</span>` : ''}${isVar ? ' · <span style="color:var(--kotu)">● kayıt</span>' : ''}</span></span>
        <span class="do-sag">${sag}</span>
      </button></li>`;
    }).join('') || '<li class="bos-not">Henüz demo yok. Bir .dem dosyası yükle.</li>';
    formCiz();
  }
  function menuAc(ac) {
    $('#kenar').classList.toggle('acik', ac);
    $('#perde').classList.toggle('acik', ac);
    $('#menuDugme').setAttribute('aria-expanded', String(ac));
  }

  async function demolariYenile() {
    try {
      S.demolar = (await api('/api/demolar')) || [];
      listeCiz();
      ozetleriYukle();
      return true;
    } catch (e) {
      $('#demolar').innerHTML = `<li class="bos-not" style="color:var(--kotu)">${esc(e.message)}</li>`;
      return false;
    }
  }

  // Liste ve "Son maçlar" kutusu için analiz edilmiş demoların özetini arka planda al.
  // Yalnız açılmış .dem dosyaları: arşivdeki (.zst/.gz/.bz2) bir demo sunucuda açılmayı gerektirir.
  async function ozetleriYukle() {
    if (S.ozetSuruyor) return;
    S.ozetSuruyor = true;
    try {
      const adaylar = S.demolar.filter((d) => d.analiz_edildi && !S.demo[d.id] && d.id !== S.secili && /\.dem$/i.test(d.ad || '')).slice(0, OZET_EN_FAZLA);
      for (const d of adaylar) {
        if (S.demo[d.id]) continue;
        try {
          S.demo[d.id] = await api(demoYol(d.id));
          listeCiz();
        } catch { /* özet olmadan da liste çalışır */ }
      }
    } finally {
      S.ozetSuruyor = false;
    }
  }

  /* ======== demo seçimi (adres çubuğunda #demo-id) ======== */
  function demoSec(id) {
    if (location.hash.slice(1) !== encodeURIComponent(id)) location.hash = encodeURIComponent(id);
    else demoAc(id);
  }
  function hashtenAc() {
    let id = '';
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { /* bozuk adres */ }
    if (!$('#modal').hidden) oynaticiKapat(); // oynatıcıdaki "Maça git" bağlantısı
    if (id === EN_IYI) enIyiAc();
    else if (id === KARIYER) kariyerAc();
    else if (id) demoAc(id);
  }

  async function demoAc(id) {
    const no = ++S.istekNo;
    S.gorunum = 'mac';
    S.secili = id;
    S.sonDemo = id;
    gezinCiz();
    S.sira = { k: 'rating', az: true };
    menuAc(false);
    ipucuGizle();
    scrollTo({ top: 0, behavior: kaydir() });
    const d = S.demolar.find((x) => x.id === id);
    if (S.demo[id]) {
      listeCiz();
      anaCiz();
      klipleriYukle(id, no);
      return;
    }
    const ilk = !d || !d.analiz_edildi;
    if (ilk && d) S.analizde.add(id);
    listeCiz();
    beklemeCiz(d, ilk);
    const bas = Date.now();
    const sayac = setInterval(() => {
      const el = $('#analizAdim');
      if (!el || no !== S.istekNo) return;
      const sn = Math.floor((Date.now() - bas) / 1000);
      el.textContent = ilk
        ? `${sn} sn${sn > 60 ? ' · hâlâ çalışıyor, büyük demolar daha uzun sürebilir' : ' · ilk analiz 20–40 saniye sürebilir'}`
        : (sn >= 2 ? `${sn} sn` : '');
    }, 500);
    let s;
    try {
      s = await api(demoYol(id));
    } catch (e) {
      S.analizde.delete(id);
      listeCiz();
      if (no !== S.istekNo) return;
      hataCiz('Demo açılamadı', e.message, id);
      return;
    } finally {
      clearInterval(sayac);
    }
    S.analizde.delete(id);
    S.demo[id] = s;
    if (ilk && d) {
      d.analiz_edildi = true;
      d.harita = s.harita || d.harita;
      bildir(`${haritaAd(s.harita) || 'Demo'} analiz edildi.`, 'basari');
      demolariYenile();
    }
    listeCiz();
    if (no !== S.istekNo) return;
    anaCiz();
    klipleriYukle(id, no);
  }

  function beklemeCiz(d, ilk) {
    $('#ana').innerHTML = `<div class="analiz"><div class="analiz-ic giris">
      <div class="yukleyici"></div>
      <h2>${ilk ? 'Demo analiz ediliyor' : 'İstatistikler yükleniyor'}</h2>
      <p>${d ? `${esc(d.ad)} · ${sayi(d.boyut_mb, 1)} MB` : 'Demo aranıyor…'}</p>
      <div class="il-bar belirsiz"><i></i></div>
      <div class="analiz-adim" id="analizAdim">${ilk ? 'Sunucu demoyu ayrıştırıyor…' : ''}</div></div></div>`;
  }
  function hataCiz(baslik, mesaj, id) {
    $('#ana').innerHTML = `<div class="analiz"><div class="analiz-ic giris">
      <h2>${esc(baslik)}</h2><p>${esc(mesaj)}</p>
      ${id ? `<button class="btn-ikincil" type="button" data-tekrar="${esc(id)}">${ikon('i-refresh')}Tekrar dene</button>` : ''}</div></div>`;
  }
  function bosCiz() {
    $('#ana').innerHTML = `<div class="analiz"><div class="analiz-ic giris">
      <h2>Bir demo seç</h2>
      <p>${S.demolar.length ? 'Soldaki listeden bir demo seç. Analiz edilmemiş demolar ilk açılışta analiz edilir.' : 'Henüz demo yok. Bir .dem dosyasını sürükleyip bırak ya da “Demo yükle”ye tıkla.'}</p>
      <button class="btn-ikincil" type="button" id="bosYukle">${ikon('i-upload')}Demo yükle</button></div></div>`;
  }

  /* ======== ana içerik ======== */
  function anaCiz() {
    const id = S.secili;
    const s = S.demo[id];
    const d = S.demolar.find((x) => x.id === id);
    const ben = benBul(s);
    const klip = S.klipler[id];
    $('#ana').innerHTML = `
      ${skorBandi(s, d)}
      <nav class="bolum-nav" id="bolumNav" aria-label="Bölümler">
        <a href="#ozet" class="aktif">Özet</a><a href="#tablo">Skor tablosu</a><a href="#roundlar">Roundlar</a><a href="#silahlar">Silahlar</a>
        <a href="#klipler">Klipler <em id="navKlipSay">${klip ? (klip.highlightlar || []).length : '…'}</em></a>
      </nav>
      ${ben ? spotHtml(ben, s) : '<section class="panel" id="ozet"><p class="bos-not">Bu demoda oyuncu bulunamadı (oyuncu_steamid eşleşmedi).</p></section>'}
      <section class="panel giris" id="tablo" style="--d:120ms">
        <div class="bas"><h2><span class="bas-no"><span>02</span></span>Skor tablosu</h2><span class="bas-ek">Sıralamak için başlığa tıkla</span></div>
        <div class="tablolar" id="tablolar"></div>
        <div class="tablo-not"><span lang="en">Rating</span>: <span class="renk-iyi">≥ 1,10 iyi</span> · 0,90–1,09 ortalama · <span class="renk-kotu">&lt; 0,90 zayıf</span> &nbsp;·&nbsp; ADR ve KAST eşik renkli.</div>
      </section>
      <section class="panel giris" id="roundlar" style="--d:160ms">
        <div class="bas"><h2><span class="bas-no"><span>03</span></span>Round geçmişi</h2><span class="bas-ek">${s.round_sayisi ?? (s.roundlar || []).length} round · üzerine gel</span></div>
        ${zamanHtml(s)}
      </section>
      <div class="ikili">
        <section class="panel giris" id="silahlar" style="--d:200ms">
          <div class="bas"><h2><span class="bas-no"><span>04</span></span>Silah dağılımı</h2><span class="bas-ek">headshot / diğer</span></div>
          ${silahHtml(s.silahlar || [])}
        </section>
        <section class="panel giris" style="--d:240ms">
          <div class="bas"><h2><span class="bas-no"><span>05</span></span>Round istatistikleri</h2><span class="bas-ek">${esc(ben ? ben.ad : '')}</span></div>
          ${roundIstHtml(s, ben)}
        </section>
      </div>
      <section class="panel giris" id="klipler" style="--d:280ms">
        <div class="bas"><h2><span class="bas-no"><span>06</span></span><span lang="en">Highlight</span>&nbsp;klipleri</h2><span class="bas-ek" id="klipOzet"></span></div>
        <div class="kayit">
          <div class="kayit-sol">
            <div class="kayit-satir"><span class="kayit-et">Kaydedilecek</span>
              <div class="secim" role="radiogroup" aria-label="Kaç klip kaydedilsin">
                ${[[3, '3'], [5, '5'], [0, 'Hepsi']].map(([n, ad]) => `<button type="button" role="radio" data-n="${n}" class="${S.enIyi === n ? 'aktif' : ''}" aria-checked="${S.enIyi === n}">${n ? 'En iyi ' : ''}${ad}</button>`).join('')}
              </div></div>
            <button class="btn-kaydet" id="kaydet" type="button"><span class="rec"></span><span id="kaydetMetin">Klipleri kaydet</span> <small id="kaydetAlt"></small></button>
            <div class="kayit-bilgi">${ORNEK_MODU ? '<b>Örnek mod:</b> kayıt taklit edilir, CS2 açılmaz. ' : ''}Kayıt CS2'yi açar ve demoyu senin gözünden oynatır; bitene kadar bilgisayarı kullanma. Başlamadan önce FACEIT ve CS2 kapalı olmalı. Klipler çıktı klasörüne (<code>klipler</code>) MP4 olarak yazılır; var olanlar atlanır.</div>
          </div>
          <div class="kontrol" id="kontrolKutu"></div>
          <div class="ilerleme" id="ilerleme" hidden></div>
        </div>
        <div class="klip-izgara" id="klipIzgara"></div>
      </section>`;
    tablolariCiz();
    kontrolCiz();
    kayitCiz();
    klipleriCiz();
    sayaclar($('#ana'));
    navGozlem();
  }

  function skorBandi(s, d) {
    const biz = s.benim_takim ?? 0;
    const T = taraflar(s);
    const R = [...(s.roundlar || [])].sort((a, b) => a.no - b.no);
    const ilkNo = R.length ? R[0].no : 1;
    const bizBas = takimTaraf(T, biz, ilkNo), onBas = karsi(bizBas);
    const TK = takimlarOf(s);
    const bT = TK[biz], oT = TK[1 - biz];
    const sonuc = bT.skor > oT.skor ? ['galibiyet', 'Galibiyet'] : bT.skor < oT.skor ? ['maglubiyet', 'Mağlubiyet'] : ['berabere', 'Berabere'];
    const yarilar = {};
    R.forEach((r) => { const g = yariNo(r.no); yarilar[g] = yarilar[g] || [0, 0]; yarilar[g][r.kazanan_takim === biz ? 0 : 1]++; });
    const yariHtml = Object.keys(yarilar).map(Number).sort((a, b) => a - b).map((g) =>
      `<span class="yari">${esc(yariAd(g))} <strong>${yarilar[g][0]}–${yarilar[g][1]}</strong></span>`).join('');
    const ad = haritaAd(s.harita) || 'Bilinmeyen';
    const takim = (t, yan, sinif, etiket) => `<div class="sb-takim ${sinif}" style="--c:${tarafRenk(yan)};--ca:${tarafAlfa(yan)}">
        <span class="sb-yan">${yan.toUpperCase()}</span>
        <div class="sb-isim"><div class="sb-ad" lang="en">${esc(t.ad)}</div><div class="sb-alt">${etiket} · <b>${yan.toUpperCase()}</b> başladı</div></div></div>`;
    return `<section class="sb" id="mac" style="${haritaStil(s.harita)}">
      <div class="sb-zemin"></div><div class="sb-filigran" lang="en">${esc(ad)}</div>
      <div class="sb-ust"><span class="sb-etiket">Maç sonu</span><span>Demo analizi</span><span class="ayir"></span><span>${esc(tarihYaz(d && d.tarih, true))}</span>
        ${benBul(s) ? `<span class="ust-bosluk"></span><button class="btn-ikincil sb-paylas" type="button" data-kart-ac>${ikon('i-share')}Kartı paylaş</button>` : ''}</div>
      <div class="sb-bant">
        ${takim(bT, bizBas, 'sol', 'Senin takımın')}
        <div class="sb-skor sol${bT.skor > oT.skor ? ' kazandi' : ''}" style="--c:${tarafRenk(bizBas)}" data-say="${bT.skor}">${bT.skor}</div>
        <div class="sb-orta"><div class="sb-harita" lang="en">${esc(ad)}</div><div class="sb-not">${s.round_sayisi ?? R.length} round</div></div>
        <div class="sb-skor sag${oT.skor > bT.skor ? ' kazandi' : ''}" style="--c:${tarafRenk(onBas)}" data-say="${oT.skor}">${oT.skor}</div>
        ${takim(oT, onBas, 'sag', 'Rakip')}
      </div>
      <div class="altbant"><span class="ab-sonuc ${sonuc[0]}">${sonuc[1]}</span>
        <span class="ab-metin"><span><b>${esc(bT.ad)}</b> ${bT.skor}–${oT.skor} <b>${esc(oT.ad)}</b></span>${yariHtml}</span>
        <span class="ab-tarih">${d ? esc(((d.ad || '').match(UZANTI) || ['.dem'])[0]) + ' · ' + sayi(d.boyut_mb, 1) + ' MB' : ''}</span></div>
    </section>`;
  }

  function spotHtml(o, s) {
    const lobi = s.oyuncular || [];
    const sira = (k) => 1 + lobi.filter((x) => (x[k] ?? -1) > (o[k] ?? -1)).length;
    const ort = (k) => lobi.reduce((a, x) => a + (x[k] || 0), 0) / (lobi.length || 1);
    const aralik = (k) => { const v = lobi.map((x) => x[k] || 0); return [Math.min(...v), Math.max(...v)]; };
    const yuzde = (k, v) => { const [a, b] = aralik(k); return b > a ? sinirla((v - a) / (b - a) * 100, 3, 100) : 50; };
    const mvp = lobi.length && lobi.every((x) => x.rating <= o.rating);
    const rs = ratingSinif(o.rating);
    const rP = sinirla((o.rating - 0.4) / (1.8 - 0.4) * 100, 2, 100);
    const fark = o.kill - o.death;
    const tile = (ad, degerHtml, k, iyi, kotu, o2 = 1) => {
      const v = o[k];
      return `<div class="tile ${esik(v, iyi, kotu)}">
        <div class="tile-ad">${ad}</div>
        <div class="tile-deger">${degerHtml}</div>
        <div class="tile-olcek"><i style="--p:${yuzde(k, v)}%"></i><b style="--p:${yuzde(k, ort(k))}%" title="Lobi ortalaması"></b></div>
        <div class="tile-alt"><span>Lobide <b>${sira(k)}.</b> / ${lobi.length}</span><span>ort. ${sayi(ort(k), o2)}</span></div></div>`;
    };
    const ak = o.acilis_kill ?? 0, ad = o.acilis_death ?? 0, at = Math.max(ak + ad, 1);
    const ck = o.cok_kill || {};
    return `<section class="panel giris" id="ozet" style="--d:60ms">
      <div class="bas"><h2><span class="bas-no"><span>01</span></span>Oyuncu özeti</h2><span class="bas-ek">Lobi: ${lobi.length} oyuncu</span></div>
      <div class="spot">
        <div class="hero ${rs}">
          <div class="hero-ust"><span class="cip or">Sen</span>${mvp ? '<span class="cip yildiz">Maçın yıldızı</span>' : ''}<span class="cip">Lobide ${sira('rating')}. / ${lobi.length}</span></div>
          <div class="hero-ad">${esc(o.ad)}</div>
          <div class="hero-sid">${esc(o.steamid)}</div>
          <div class="hero-rating"><span class="hero-sayi" data-say="${o.rating}" data-o="2">${sayi(o.rating, 2)}</span>
            <span class="hero-rl"><span lang="en">Rating</span><small>HLTV 1.0 tarzı</small></span></div>
          <div class="olcek"><i style="--p:${rP}%"></i>
            <span class="cizgi" style="left:${(0.9 - 0.4) / 1.4 * 100}%"></span><span class="cizgi" style="left:${(1.1 - 0.4) / 1.4 * 100}%"></span></div>
          <div class="olcek-yazi"><span>0,40</span><span>0,90</span><span>1,10</span><span>1,80</span></div>
          <div class="hero-alt">
            <div>K / D / A<b>${o.kill}<small>/</small>${o.death}<small>/</small>${o.assist}</b></div>
            <div>Fark<b class="${fark > 0 ? 'renk-iyi' : fark < 0 ? 'renk-kotu' : ''}">${fark > 0 ? '+' : ''}${fark}</b></div>
            <div>Lobi ort.<b>${sayi(ort('rating'), 2)}</b></div>
          </div>
        </div>
        <div class="tiles">
          ${tile('ADR', `<span data-say="${o.adr}" data-o="1">${sayi(o.adr, 1)}</span>`, 'adr', 85, 65)}
          ${tile('KAST', `<span data-say="${o.kast}" data-o="1">${sayi(o.kast, 1)}</span><small>%</small>`, 'kast', 75, 65)}
          ${tile('K/D', `<span data-say="${o.kd}" data-o="2">${sayi(o.kd, 2)}</span>`, 'kd', 1.1, 0.9, 2)}
          ${tile('Headshot', `<span data-say="${o.hs_yuzde}" data-o="1">${sayi(o.hs_yuzde, 1)}</span><small>%</small>`, 'hs_yuzde', 50, 30)}
          <div class="tile ${ak > ad ? 'iyi' : ak < ad ? 'kotu' : 'orta'}">
            <div class="tile-ad">Açılış düelloları</div>
            <div class="tile-deger">${ak}<span class="ayr">–</span>${ad}</div>
            <div class="duello"><i class="k" style="width:${ak / at * 100}%"></i><i class="d" style="width:${ad / at * 100}%"></i>${ak + ad ? '' : '<i class="n"></i>'}</div>
            <div class="tile-alt"><span>kazanılan – kaybedilen</span><span>%${sayi(ak / at * 100)}</span></div>
          </div>
          <div class="tile orta">
            <div class="tile-ad">Çoklu ${EN('kill')}</div>
            <div class="coklu">${[['2', '2K'], ['3', '3K'], ['4', '4K'], ['5', 'ACE']].map(([k, a]) => `<span class="${ck[k] ? 'var' : ''}"><b>${ck[k] || 0}</b>${a}</span>`).join('')}</div>
            <div class="tile-alt"><span>round sayısı</span><span>toplam ${Object.values(ck).reduce((a, b) => a + (b || 0), 0)}</span></div>
          </div>
        </div>
      </div>
    </section>`;
  }

  const SUTUNLAR = [
    ['ad', 'Oyuncu', ''], ['kill', 'K', ''], ['death', 'D', ''], ['assist', 'A', 'gz-a'], ['fark', '+/−', 'gz-b'],
    ['adr', 'ADR', ''], ['hs_yuzde', 'HS%', 'gz-a'], ['kast', 'KAST', ''], ['rating', EN('Rating'), ''],
  ];
  function tablolariCiz() {
    const kutu = $('#tablolar');
    const s = S.demo[S.secili];
    if (!kutu || !s) return;
    const biz = s.benim_takim ?? 0;
    const T = taraflar(s);
    const R = [...(s.roundlar || [])].sort((a, b) => a.no - b.no);
    const ilkNo = R.length ? R[0].no : 1;
    const { k, az } = S.sira;
    const deger = (o, a) => (a === 'fark' ? o.kill - o.death : o[a]);
    const sirala = (x, y) => {
      const c = k === 'ad' ? String(x.ad).localeCompare(String(y.ad), 'tr') : (deger(x, k) ?? -1) - (deger(y, k) ?? -1);
      return az ? -c : c;
    };
    const TK = takimlarOf(s);
    const birden = TK.some((t) => t.kazandi);
    kutu.innerHTML = [biz, 1 - biz].map((t) => {
      const takim = TK[t];
      const yan = takimTaraf(T, t, ilkNo);
      const oy = (s.oyuncular || []).filter((o) => o.takim === t).sort(sirala);
      return `<div style="--c:${tarafRenk(yan)};--ca:${tarafAlfa(yan)}">
        <div class="takim-bas"><span class="takim-skor">${takim.skor}</span><span class="takim-ad" lang="en">${esc(takim.ad)}</span>
          <span class="cip ${takim.kazandi ? 'g' : birden ? 'm' : ''}">${t === biz ? 'Senin takımın' : 'Rakip'} · ${takim.kazandi ? 'G' : birden ? 'M' : 'B'}</span></div>
        <div class="tablo-sar"><table>
          <thead><tr>${SUTUNLAR.map(([a, ad, g]) => `<th data-sira="${a}" class="${g} ${a === k ? 'sirali' + (az ? '' : ' artan') : ''}" scope="col" tabindex="0" aria-sort="${a === k ? (az ? 'descending' : 'ascending') : 'none'}">${ad}</th>`).join('')}</tr></thead>
          <tbody>${oy.map((o) => {
            const f = o.kill - o.death;
            return `<tr class="${o.ben ? 'ben' : ''}">
              <td><span class="oy" title="${esc(o.steamid)}"><span>${esc(o.ad)}</span>${o.ben ? '<span class="cip or">Sen</span>' : ''}</span></td>
              <td class="k">${o.kill}</td><td class="soluk">${o.death}</td><td class="soluk gz-a">${o.assist}</td>
              <td class="gz-b ${f > 0 ? 'fark-a' : f < 0 ? 'fark-e' : 'soluk'}">${f > 0 ? '+' : ''}${f}</td>
              <td class="${{ iyi: 'renk-iyi', kotu: 'renk-kotu', orta: '' }[esik(o.adr, 85, 65)]}">${sayi(o.adr, 1)}</td>
              <td class="gz-a">${sayi(o.hs_yuzde, 0)}%</td>
              <td class="${{ iyi: 'renk-iyi', kotu: 'renk-kotu', orta: '' }[esik(o.kast, 75, 65)]}">${sayi(o.kast, 1)}%</td>
              <td><span class="rozet ${ratingSinif(o.rating)}">${sayi(o.rating, 2)}</span></td></tr>`;
          }).join('')}</tbody></table></div></div>`;
    }).join('');
  }

  function zamanHtml(s) {
    const biz = s.benim_takim ?? 0;
    const T = taraflar(s);
    const R = [...(s.roundlar || [])].sort((a, b) => a.no - b.no);
    if (!R.length) return '<p class="bos-not">Round bilgisi yok.</p>';
    const gruplar = {};
    R.forEach((r) => { (gruplar[yariNo(r.no)] = gruplar[yariNo(r.no)] || []).push(r); });
    const html = Object.keys(gruplar).map(Number).sort((a, b) => a - b).map((g) => {
      const rs = gruplar[g];
      const bizT = takimTaraf(T, biz, rs[0].no), onT = karsi(bizT);
      const bizSkor = rs.filter((r) => r.kazanan_takim === biz).length;
      let h = `<div class="tl-grup"><div class="tl-bas"><span>${esc(yariAd(g))}</span>
        <span class="tl-bas-skor"><b class="${bizT}">${bizSkor}</b> – <b class="${onT}">${rs.length - bizSkor}</b></span>
        <span class="tl-bas-r">R${rs[0].no}–${rs[rs.length - 1].no}</span></div>
        <div class="tl-izgara" style="--n:${rs.length}">
          <span class="tl-et ${bizT}"><b>Biz</b><small>${bizT.toUpperCase()}</small></span>
          <span class="tl-et ${onT}"><b>Rakip</b><small>${onT.toUpperCase()}</small></span>
          <span class="tl-et2" lang="en">Kill</span><span class="tl-et2">Ölüm</span><span class="tl-et2">#</span>`;
      rs.forEach((r) => {
        const kaz = r.kazanan_takim === biz;
        const w = kazananTaraf(r) || (kaz ? bizT : onT);
        const svg = ikon(IKON[r.neden] || 'i-elim');
        const tip = esc(`Round ${r.no} · ${kaz ? 'Kazandınız' : 'Kaybettiniz'}\n${nedenAd(r.neden)} (${w.toUpperCase()})\n${r.benim_kill ? r.benim_kill + ' kill' : 'Kill yok'} · ${r.ben_oldum ? 'Öldün' : 'Hayatta kaldın'}`);
        const at = `data-r="${r.no}" data-tip="${tip}"`;
        h += `<span class="tl-k${kaz ? ' dolu ' + w : ''}" ${at}>${kaz ? svg : ''}</span>`;
        h += `<span class="tl-k${!kaz ? ' dolu ' + w : ''}" ${at}>${!kaz ? svg : ''}</span>`;
        h += `<span class="tl-kill k${Math.min(r.benim_kill || 0, 5)}" ${at}>${r.benim_kill || ''}</span>`;
        h += `<span class="tl-olum ${r.ben_oldum ? 'oldu' : 'yasadi'}" ${at}>${r.ben_oldum ? ikon('i-x', '') : ''}</span>`;
        h += `<span class="tl-no" data-r="${r.no}">${r.no}</span>`;
      });
      return h + '</div></div>';
    }).join('');
    return `<div class="tl-gruplar">${html}</div>
      <div class="lejant">
        <span><i style="background:var(--ct)"></i>CT kazandı</span><span><i style="background:var(--t)"></i>T kazandı</span>
        <span>${ikon('i-elim', '')}Eleme</span><span>${ikon('i-bomb', '')}Bomba patladı</span><span>${ikon('i-defuse', '')}İmha</span><span>${ikon('i-time', '')}Süre doldu</span>
        <span><b>3</b> senin ${EN('kill')} sayın</span><span><svg style="fill:var(--kotu)"><use href="#i-x"/></svg>öldün</span>
      </div>`;
  }

  function silahHtml(liste) {
    if (!liste.length) return `<p class="bos-not">Bu maçta ${EN('kill')} yok.</p>`;
    const l = [...liste].sort((a, b) => b.kill - a.kill);
    const enCok = Math.max(...l.map((x) => x.kill), 1);
    const top = l.reduce((a, x) => a + x.kill, 0), hsTop = l.reduce((a, x) => a + Math.min(x.hs || 0, x.kill), 0);
    return `<div class="silah-ozet"><b>${top}</b> ${EN('kill')} · ${hsTop} ${EN('headshot')} (%${sayi(hsTop / Math.max(top, 1) * 100)})</div>
      ${l.map((x, i) => {
        const hs = Math.min(x.hs || 0, x.kill);
        return `<div class="sl" data-tip="${esc(`${silahAd(x.silah)}\n${x.kill} kill · ${hs} headshot`)}">
          <div class="sl-ust"><span class="sl-ad" lang="en">${esc(silahAd(x.silah))}</span><span class="sl-tur">${esc(silahTur(x.silah))}</span>
            <span class="sl-sayi"><b>${x.kill}</b> ${EN('kill')}${hs ? ` · ${hs} HS` : ''}</span></div>
          <div class="sl-bar" style="--d:${i * 70}ms"><i class="hs" style="width:${hs / enCok * 100}%;animation-delay:${i * 70}ms"></i><i class="gv" style="width:${(x.kill - hs) / enCok * 100}%;animation-delay:${i * 70 + 120}ms"></i></div></div>`;
      }).join('')}
      <div class="lejant"><span><i style="background:var(--or)"></i>${EN('Headshot')}</span><span><i style="background:#56607a"></i>Diğer</span></div>`;
  }

  function roundIstHtml(s, ben) {
    const biz = s.benim_takim ?? 0;
    const R = [...(s.roundlar || [])].sort((a, b) => a.no - b.no);
    const n = s.round_sayisi || R.length || 1;
    const yasadi = R.filter((r) => !r.ben_oldum).length;
    const killRound = R.filter((r) => r.benim_kill > 0).length;
    const enIyi = R.reduce((a, r) => (r.benim_kill > (a ? a.benim_kill : 0) ? r : a), null);
    let seri = 0, enUzun = 0;
    R.forEach((r) => { seri = r.kazanan_takim === biz ? seri + 1 : 0; enUzun = Math.max(enUzun, seri); });
    const pistol = R.filter((r) => r.no === 1 || r.no === 13);
    return `<div class="ri">
      <div class="ri-oge"><div class="ri-ad">Round başına ${EN('kill')}</div><div class="ri-deger">${sayi(ben ? ben.kill / n : 0, 2)}</div><div class="ri-alt">ölüm/round ${sayi(ben ? ben.death / n : 0, 2)}</div></div>
      <div class="ri-oge"><div class="ri-ad">Hayatta kaldın</div><div class="ri-deger">${yasadi}<small> / ${R.length}</small></div><div class="ri-alt">roundların %${sayi(yasadi / Math.max(R.length, 1) * 100)}'i</div></div>
      <div class="ri-oge"><div class="ri-ad">${EN('Kill')} aldığın round</div><div class="ri-deger">${killRound}<small> / ${R.length}</small></div><div class="ri-alt">${enIyi ? `en iyisi R${enIyi.no}: ${enIyi.benim_kill} kill` : 'kill yok'}</div></div>
      <div class="ri-oge"><div class="ri-ad">En uzun seri</div><div class="ri-deger">${enUzun}<small> round</small></div><div class="ri-alt">takımının art arda galibiyeti</div></div>
      <div class="ri-oge" style="grid-column:1/-1"><div class="ri-ad">Tabanca roundları</div>
        <div class="pistol">${pistol.map((r) => { const g = r.kazanan_takim === biz; return `<span class="${g ? 'G' : 'M'}">R${r.no} · ${r.benim_kill} kill<b>${g ? 'Kazanıldı' : 'Kaybedildi'}</b></span>`; }).join('') || '<span>—</span>'}</div></div>
    </div>`;
  }

  /* ======== klipler ======== */
  const klipAnahtar = (id, h) => id + ':' + h.round;
  function baslikYap(h) {
    const l = h.labels || [];
    const clutch = l.find((x) => /clutch/i.test(x));
    const kill = l.find((x) => /^(\dK|ACE)$/i.test(x));
    const r = `Round ${h.round}`;
    if (clutch) return { ust: kill ? `${KILL_ADI[kill.toUpperCase()] || esc(kill)} · ${r}` : r, ana: esc(clutch.replace(/clutch/i, 'Clutch')) };
    if (kill) return { ust: r, ana: KILL_ADI[kill.toUpperCase()] || esc(kill) };
    return { ust: `Öne çıkan an · ${r}`, ana: l[0] ? esc(l[0]) : EN('Highlight') };
  }
  function killSayisi(h) {
    const l = h.labels || [];
    const k = l.find((x) => /^\dK$/i.test(x));
    if (k) return parseInt(k, 10);
    if (l.some((x) => /^ACE$/i.test(x))) return 5;
    return 1;
  }
  // Klip kartının küçük resmi: CSS ile çizilmiş sahne + kill akışı (gerçek kare değil).
  function sahneHtml(s, h, i, durum) {
    const biz = s.benim_takim ?? 0;
    const T = taraflar(s);
    const yan = takimTaraf(T, biz, h.round);
    const ben = benBul(s);
    const rakip = (s.oyuncular || []).filter((o) => o.takim !== biz);
    const n = Math.min(killSayisi(h), 5);
    const hsN = parseInt(((h.labels || []).find((x) => /HS$/i.test(x)) || '0'), 10) || 0;
    const silahlar = h.weapons && h.weapons.length ? h.weapons : null; // bilinmiyorsa uydurma
    const feed = Array.from({ length: n }, (_, j) => {
      const v = rakip.length ? rakip[(h.round + j * 2) % rakip.length].ad : 'rakip';
      return `<div class="kf ben" style="--kc:${tarafRenk(yan)};--vc:${tarafRenk(karsi(yan))};--d:${120 + j * 110}ms">
        <span class="a">${esc(ben ? ben.ad : 'Sen')}</span>${silahlar ? `<em lang="en">${esc(silahAd(silahlar[j % silahlar.length]))}</em>` : ''}${j < hsN ? '<svg class="hs"><use href="#i-hs"/></svg>' : ''}<span class="v">${esc(v)}</span></div>`;
    }).join('');
    return `<div class="kl-resim" style="${haritaStil(s.harita)}">
      <div class="kl-sahne" data-v="${(h.round + i) % 3}"></div><div class="kl-uzak"></div><div class="kl-zemin"></div><div class="kl-silah"></div>
      <div class="kl-nisan"></div>
      <div class="kl-feed">${feed}</div>
      <span class="kl-round">R${h.round}</span>
      ${h.saniye != null ? `<span class="kl-sure">${ikon('i-play', '')}${sure(h.saniye)}</span>` : ''}
      ${durum.kayitli ? `<button class="kl-oynat" type="button" ${durum.oynatAt || `data-oynat="${i}"`} aria-label="Round ${h.round} klibini oynat">${ikon('i-play', '')}</button>` : ''}
      ${!durum.kayitli && !durum.kaydediliyor ? '<span class="kl-damga">Kaydedilmedi</span>' : ''}
      ${durum.yeni ? '<span class="kl-yeni">Yeni</span>' : ''}
      ${durum.kaydediliyor ? '<div class="kl-rec"><span>Kaydediliyor</span></div>' : ''}
    </div>`;
  }
  const etiketHtml = (l) => (l || []).map((x) => `<span class="etk ${/clutch/i.test(x) ? 'clutch' : /^(\dK|ACE)$/i.test(x) ? 'kill' : /HS$/i.test(x) ? 'hs' : ''}">${esc(x)}</span>`).join('');
  function siraliHl(id = S.secili) {
    const k = S.klipler[id];
    return k ? [...(k.highlightlar || [])].sort((a, b) => b.score - a.score) : [];
  }
  function hedefSayisi(id) {
    const n = S.kayitHedef[id] ?? S.enIyi;
    const hl = siraliHl(id);
    return n ? Math.min(n, hl.length) : hl.length;
  }
  function klipleriCiz() {
    const iz = $('#klipIzgara');
    if (!iz) return;
    const id = S.secili, s = S.demo[id];
    const k = S.klipler[id];
    const say = $('#navKlipSay');
    if (!k) {
      $('#klipOzet').textContent = '';
      if (say) say.textContent = S.klipHata[id] ? '!' : '…';
      iz.innerHTML = S.klipHata[id]
        ? `<div class="kontrol sorun" style="grid-column:1/-1"><div class="kontrol-bas">${ikon('i-alert')}${EN('Highlight')}'lar alınamadı</div><ul><li>${esc(S.klipHata[id])}</li></ul>
           <button class="btn-ikincil" type="button" data-klip-tekrar>${ikon('i-refresh')}Tekrar dene</button></div>`
        : `<p class="bos-not yukleniyor-not">${EN('Highlight')}'lar yükleniyor…</p>`;
      return;
    }
    const hl = siraliHl();
    if (say) say.textContent = hl.length;
    const enYuksek = Math.max(...hl.map((h) => h.score), 1);
    const calisiyor = k.kayit && k.kayit.durum === 'calisiyor';
    const hedef = new Set(calisiyor ? hl.slice(0, hedefSayisi(id)).map((h) => h.round) : []);
    $('#klipOzet').innerHTML = `${hl.length} ${EN('highlight')} · ${hl.filter((h) => h.klip).length} klip kayıtlı`;
    if (!hl.length) { iz.innerHTML = '<p class="bos-not">Bu maçta öne çıkan an bulunamadı.</p>'; return; }
    iz.innerHTML = hl.map((h, i) => {
      const b = baslikYap(h);
      const durum = { kayitli: !!h.klip, yeni: S.yeni.has(klipAnahtar(id, h)), kaydediliyor: !h.klip && hedef.has(h.round) };
      const etk = etiketHtml(h.labels);
      return `<article class="klip ${durum.kayitli ? 'kayitli' : 'kayitsiz'}${i === 0 ? ' one' : ''} giris" style="--d:${i * 60}ms">
        ${sahneHtml(s, h, i, durum)}
        <div class="kl-govde">
          <div class="kl-ust"><span class="kl-sira">#${i + 1}</span>
            <h3 class="kl-baslik"><span class="kl-ust-et">${i === 0 ? 'Maçın anı · ' : ''}${b.ust}</span>${b.ana}</h3>
            <div class="kl-puan">${sayi(h.score, 1)}<small>puan</small></div></div>
          <div class="kl-puan-bar"><i style="--p:${h.score / enYuksek * 100}%"></i></div>
          <div class="kl-etiketler">${etk}</div>
          <div class="kl-alt"><span lang="en">${(h.weapons || []).map((w) => esc(silahAd(w))).join(' · ') || '—'}</span><span>Round ${h.round} · ${h.saniye ?? '?'} sn</span></div>
        </div></article>`;
    }).join('');
  }

  async function klipleriYukle(id, no) {
    delete S.klipHata[id];
    try {
      const k = await api(demoYol(id, '/klipler'));
      S.klipler[id] = k;
      if (k.kayit && k.kayit.durum === 'calisiyor') { S.aktifIs = id; yoklamaBaslat(); listeCiz(); }
    } catch (e) {
      S.klipHata[id] = e.message;
    }
    if (no !== S.istekNo || S.secili !== id) return;
    klipleriCiz();
    kayitCiz();
  }

  /* ======== kayıt: POST /api/demo/<id>/kaydet + iş durumu yoklaması ======== */
  // Sunucunun iş durumu yalnız {durum, mesaj, satirlar} (son 40 satır). Adım ve yüzde,
  // klip.py'nin çıktı satırlarından tahmin edilir ve geriye gitmez.
  function kayitBilgi(id) {
    const k = S.klipler[id];
    const kayit = k && k.kayit;
    if (!kayit || !kayit.durum || kayit.durum === 'bos') return null;
    const satirlar = kayit.satirlar || [];
    let adim = 0, csdm = 0, yazilan = 0, mesaj = '';
    for (const ham of satirlar) {
      const x = ham.trim();
      if (/^===/.test(x)) { mesaj = 'Demo hazırlanıyor, highlight\'lar seçiliyor'; }
      else if (/^\[\d+\/\d+\]/.test(x)) { adim = Math.max(adim, 1); mesaj = 'CS2 açılıyor, demo yükleniyor'; }
      else if (/^CSDM'e ekleniyor/i.test(x)) { adim = Math.max(adim, 1); mesaj = "Demo CS Demo Manager'a ekleniyor"; }
      else if (/^\[csdm\]/.test(x)) { csdm++; adim = Math.max(adim, 2); mesaj = 'Kayıt sürüyor · ' + x.replace(/^\[csdm\]\s*/, ''); }
      else if (/^->\s/.test(x)) { yazilan++; adim = 3; mesaj = 'Klip yazıldı: ' + x.replace(/^->\s*/, ''); }
      else if (/^zaten var:/.test(x)) { yazilan++; adim = Math.max(adim, 2); }
      else if (/yeni klip:/.test(x)) { adim = 3; }
    }
    const n = Math.max(hedefSayisi(id), 1);
    let yuzde = adim === 0 ? 3 + Math.min(satirlar.length, 5)
      : adim === 1 ? 12
        : adim === 2 ? 18 + 62 * (1 - Math.exp(-csdm / 18))
          : 84 + 14 * Math.min(yazilan / n, 1);
    const onceki = S.ilerleme[id];
    if (kayit.durum === 'calisiyor' && onceki) { adim = Math.max(adim, onceki.adim); yuzde = Math.max(yuzde, onceki.yuzde); }
    if (kayit.durum === 'calisiyor') S.ilerleme[id] = { adim, yuzde };
    if (kayit.durum === 'bitti') { adim = ADIMLAR.length; yuzde = 100; mesaj = `${kayit.mesaj || 'Kayıt bitti'} · ${yazilan} klip yazıldı`; }
    if (kayit.durum === 'hata') mesaj = kayit.mesaj || 'Kayıt başarısız';
    if (!mesaj) mesaj = kayit.mesaj || 'Kayıt başladı';
    return { durum: kayit.durum, mesaj, yuzde, adim, satirlar, yazilan };
  }
  const satirSinif = (x) => (/->|yeni klip:|zaten var/.test(x) ? 'y'
    : /^\s*!|başlayamaz|başarısız|Traceback|Error|hata/i.test(x) ? 'h'
      : /\[csdm\]/.test(x) ? 'z' : '');

  function kayitCiz() {
    const btn = $('#kaydet');
    if (!btn) return;
    const id = S.secili;
    const k = S.klipler[id];
    const b = kayitBilgi(id);
    const calisiyor = !!(b && b.durum === 'calisiyor');
    const hl = siraliHl();
    const n = S.enIyi ? Math.min(S.enIyi, hl.length) : hl.length;
    btn.disabled = !k || calisiyor || S.kayitBasliyor;
    btn.title = S.aktifIs && S.aktifIs !== id ? 'Başka bir demonun kaydı sürüyor.' : '';
    $('#kaydetMetin').textContent = !k ? (S.klipHata[id] ? 'Klipler alınamadı' : 'Yükleniyor…')
      : S.kayitBasliyor ? 'Başlatılıyor…' : calisiyor ? 'Kayıt sürüyor…' : 'Klipleri kaydet';
    $('#kaydetAlt').textContent = !k || calisiyor || S.kayitBasliyor ? '' : `(${S.enIyi ? 'en iyi ' + n : 'hepsi · ' + n})`;
    $$('.secim button').forEach((x) => { x.disabled = calisiyor; });
    const il = $('#ilerleme');
    if (!b) { il.hidden = true; il.innerHTML = ''; return; }
    const eski = $('#gunluk', il);
    const altta = !eski || eski.scrollHeight - eski.scrollTop - eski.clientHeight < 30;
    il.hidden = false;
    il.className = 'ilerleme ' + b.durum;
    const adimSinif = (i) => (b.durum === 'bitti' || i < b.adim ? 'tamam' : i === b.adim ? (b.durum === 'hata' ? 'hata' : 'simdi') : '');
    il.innerHTML = `<div class="il-ust"><span class="il-durum">${b.durum === 'bitti' ? 'Tamamlandı' : b.durum === 'hata' ? 'Hata' : 'Rec'}</span>
        <span class="il-mesaj" title="${esc(b.mesaj)}">${esc(b.mesaj)}</span><span class="il-yuzde" title="Günlük satırlarından tahmini ilerleme">${b.durum === 'hata' ? '' : Math.round(b.yuzde) + '%'}</span></div>
      <div class="il-bar"><i style="width:${b.durum === 'hata' ? 100 : b.yuzde}%"></i></div>
      <div class="adimlar">${ADIMLAR.map((a, i) => { const c = adimSinif(i); return `<div class="adim ${c}"><i>${c === 'tamam' ? '✓' : c === 'hata' ? '!' : i + 1}</i><span>${a}</span></div>`; }).join('')}</div>
      ${S.yoklamaHata && calisiyor ? `<div class="kayit-bilgi" style="color:var(--kotu);margin-top:10px">Kayıt durumu alınamadı: ${esc(S.yoklamaHata)} — yeniden deneniyor.</div>` : ''}
      <details class="gunluk"${S.gunlukAcik || b.durum === 'hata' ? ' open' : ''}><summary>Kayıt günlüğü (${b.satirlar.length} satır${b.satirlar.length >= 40 ? ', son 40' : ''})</summary><pre id="gunluk">${b.satirlar.map((x) => `<span class="${satirSinif(x)}">${esc(x)}</span>`).join('\n') || '<span class="z">Henüz çıktı yok…</span>'}</pre></details>`;
    const pre = $('#gunluk', il);
    if (pre && altta) pre.scrollTop = pre.scrollHeight;
    $('.gunluk', il).addEventListener('toggle', (e) => { S.gunlukAcik = e.target.open; });
  }

  async function kaydet() {
    const id = S.secili;
    const k = S.klipler[id];
    if (!k || S.kayitBasliyor) return;
    if (S.aktifIs && S.aktifIs !== id) { bildir('Başka bir kayıt sürüyor; bitmesini bekle.', 'hata'); return; }
    const hl = siraliHl();
    if (!hl.length) { bildir('Kaydedilecek highlight yok.', 'hata'); return; }
    const enIyi = S.enIyi;
    S.kayitBasliyor = true;
    kayitCiz();
    try {
      const sonuc = await api(demoYol(id, '/kaydet'), { method: 'POST', body: JSON.stringify({ en_iyi: enIyi }) });
      S.kayitHedef[id] = enIyi;
      delete S.ilerleme[id];
      k.kayit = { durum: (sonuc && sonuc.durum) || 'calisiyor', mesaj: 'Kayıt başladı', satirlar: [] };
      S.aktifIs = id;
      S.yoklamaHata = null;
      bildir(ORNEK_MODU ? 'Örnek mod: kayıt taklit ediliyor.' : 'Kayıt başladı. CS2 açılacak; bitene kadar bilgisayarı kullanma.');
      yoklamaBaslat();
      listeCiz();
    } catch (e) {
      bildir(e.message, 'hata');
      if (/başlayamaz/i.test(e.message)) {
        const kb = $('#kontrolKutu');
        if (kb) { kb.classList.remove('salla'); void kb.offsetWidth; kb.classList.add('salla'); }
      }
      kontrolYenile();
    } finally {
      S.kayitBasliyor = false;
      if (S.secili === id) { kayitCiz(); klipleriCiz(); }
    }
  }

  function yoklamaDurdur() {
    clearTimeout(S.yoklamaZaman);
    S.yoklamaZaman = null;
  }
  // Kaydı süren demoyu (seçili olmasa da) bitene kadar yoklar.
  function yoklamaBaslat() {
    yoklamaDurdur();
    let hataSay = 0;
    const tur = async () => {
      const id = S.aktifIs;
      if (!id) return;
      try {
        const yeni = await api(demoYol(id, '/klipler'));
        const eski = S.klipler[id];
        const once = new Map(((eski && eski.highlightlar) || []).map((h) => [h.round, h.klip]));
        (yeni.highlightlar || []).forEach((h) => { if (h.klip && !once.get(h.round) && eski) S.yeni.add(klipAnahtar(id, h)); });
        S.klipler[id] = yeni;
        S.yoklamaHata = null;
        hataSay = 0;
        const bitti = !yeni.kayit || yeni.kayit.durum !== 'calisiyor';
        if (S.secili === id) { kayitCiz(); klipleriCiz(); }
        if (bitti) {
          S.aktifIs = null;
          delete S.ilerleme[id];
          const s = S.demo[id];
          const ad = haritaAd(s && s.harita) || 'Demo';
          if (yeni.kayit && yeni.kayit.durum === 'hata') bildir(`${ad}: kayıt başarısız — ${yeni.kayit.mesaj || 'bilinmeyen hata'}`, 'hata');
          else {
            const b = kayitBilgi(id);
            bildir(`${ad}: kayıt bitti${b ? `, ${b.yazilan} klip yazıldı` : ''}.`, 'basari');
          }
          await demolariYenile();
          kontrolYenile();
          return;
        }
      } catch (e) {
        S.yoklamaHata = e.message;
        if (++hataSay === 1) bildir('Kayıt durumu alınamadı: ' + e.message, 'hata');
        if (S.secili === id) kayitCiz();
      }
      S.yoklamaZaman = setTimeout(tur, YOKLAMA_MS);
    };
    S.yoklamaZaman = setTimeout(tur, YOKLAMA_MS);
  }

  /* ======== oynatıcı penceresi ======== */
  let oynat = null;      // {video} gerçek klip ya da {t, top, raf} örnek mod taklidi
  let oynatKaynak = null; // pencere kapanınca odağın döneceği düğme
  function oynaticiAc(i, kaynak) {
    const hl = siraliHl();
    const h = hl[i];
    if (!h || !h.klip) return;
    const s = S.demo[S.secili];
    const b = baslikYap(h);
    pencereAc({
      klip: h.klip, rozet: `R${h.round}`, saniye: h.saniye,
      baslik: `${b.ana} · <span lang="en">${esc(haritaAd(s.harita) || '')}</span>`,
      sahne: ORNEK_MODU ? sahneHtml(s, h, i, { kayitli: false }) : '',
    }, kaynak);
  }
  // o: {klip, src?, rozet, baslik (HTML), saniye, sahne (örnek mod HTML), ek (alt satıra HTML)}
  function pencereAc(o, kaynak) {
    oynaticiKapat();
    oynatKaynak = kaynak || null;
    const m = $('#modal');
    const src = o.src || o.klip;
    let dosya = '';
    try { dosya = decodeURIComponent(String(o.klip).split('/').pop() || ''); } catch { dosya = String(o.klip); }
    m.innerHTML = `<div class="oynatici">
      <div class="oy-bas"><span class="cip or">${esc(o.rozet)}</span><h3 id="oyBaslik">${o.baslik}</h3>
        <button class="ikon-dugme" type="button" data-kapat aria-label="Kapat">${ikon('i-x')}</button></div>
      <div class="oy-ekran">${ORNEK_MODU ? o.sahne : `<video id="oyVideo" src="${esc(src)}" preload="auto" playsinline></video>`}</div>
      <div class="oy-kontrol"><button class="ikon-dugme" type="button" id="oyDugme" aria-label="Oynat / duraklat">${ikon('i-pause')}</button>
        <div class="oy-cubuk" id="oyCubuk" role="slider" aria-label="Klipte konum" tabindex="0"><i id="oyIlerle" style="width:0"></i></div><span class="oy-zaman" id="oyZaman">0:00 / ${sure(o.saniye || 0)}</span>
        ${ORNEK_MODU ? '' : `<button class="ikon-dugme ikincil" type="button" id="oyTam" aria-label="Tam ekran" title="Tam ekran">${ikon('i-full')}</button>`}</div>
      <div class="oy-not">${ORNEK_MODU ? `Örnek mod: ${esc(o.klip)} (dosya yok, oynatma taklit edilir)`
        : `<a href="${esc(src)}" target="_blank" rel="noopener">${esc(dosya)}</a> · Boşluk: oynat/duraklat · ←/→: 5 sn`}${o.ek || ''}</div></div>`;
    $('.kl-damga', m)?.remove();
    m.hidden = false;
    if (ORNEK_MODU) taklitOynat(o.saniye); else videoOynat();
    $('#oyDugme').focus();
  }
  function videoOynat() {
    const v = $('#oyVideo');
    oynat = { video: v };
    const guncelle = () => {
      const top = isFinite(v.duration) && v.duration > 0 ? v.duration : 0;
      $('#oyIlerle').style.width = (top ? v.currentTime / top * 100 : 0) + '%';
      $('#oyZaman').textContent = `${sure(v.currentTime)} / ${sure(top)}`;
    };
    const dugme = () => { $('#oyDugme').innerHTML = ikon(v.paused ? 'i-play' : 'i-pause'); };
    v.addEventListener('timeupdate', guncelle);
    v.addEventListener('loadedmetadata', guncelle);
    v.addEventListener('durationchange', guncelle);
    v.addEventListener('play', dugme);
    v.addEventListener('pause', dugme);
    v.addEventListener('ended', dugme);
    v.addEventListener('click', () => oynatDegistir());
    v.addEventListener('error', () => {
      if (!oynat || oynat.video !== v || $('.oy-hata')) return;
      v.insertAdjacentHTML('afterend', '<div class="oy-hata">Klip dosyası açılamadı</div>');
      dugme();
    });
    const p = v.play();
    if (p && p.catch) p.catch(() => dugme());
  }
  function taklitOynat(saniye) {
    const top = Math.max(saniye || 1, 1);
    oynat = { t: 0, calis: true, son: performance.now(), top, raf: 0 };
    const kare = (zaman) => {
      if (!oynat || oynat.video) return;
      if (oynat.calis) oynat.t = Math.min(oynat.top, oynat.t + (zaman - oynat.son) / 1000);
      oynat.son = zaman;
      $('#oyIlerle').style.width = (oynat.t / oynat.top * 100) + '%';
      $('#oyZaman').textContent = `${sure(oynat.t)} / ${sure(oynat.top)}`;
      if (oynat.t >= oynat.top && oynat.calis) { oynat.calis = false; $('#oyDugme').innerHTML = ikon('i-play'); }
      oynat.raf = requestAnimationFrame(kare);
    };
    oynat.raf = requestAnimationFrame(kare);
  }
  function oynatDegistir() {
    if (!oynat) return;
    if (oynat.video) {
      const v = oynat.video;
      if (v.paused) { if (v.ended) v.currentTime = 0; const p = v.play(); if (p && p.catch) p.catch(() => {}); } else v.pause();
      return;
    }
    if (oynat.t >= oynat.top) oynat.t = 0;
    oynat.calis = !oynat.calis;
    $('#oyDugme').innerHTML = ikon(oynat.calis ? 'i-pause' : 'i-play');
  }
  function oynatAtla(oran, fark) {
    if (!oynat) return;
    if (oynat.video) {
      const v = oynat.video;
      const top = isFinite(v.duration) ? v.duration : 0;
      if (!top) return;
      v.currentTime = sinirla(oran != null ? oran * top : v.currentTime + fark, 0, top);
      return;
    }
    oynat.t = sinirla(oran != null ? oran * oynat.top : oynat.t + fark, 0, oynat.top);
  }
  function oynaticiKapat() {
    if (oynat && oynat.raf) cancelAnimationFrame(oynat.raf);
    if (oynat && oynat.video) {
      const v = oynat.video;
      v.pause();
      v.removeAttribute('src'); // indirmeyi durdur
      v.load();
    }
    const acikti = !$('#modal').hidden;
    oynat = null;
    $('#modal').hidden = true;
    $('#modal').innerHTML = '';
    if (acikti && oynatKaynak && document.contains(oynatKaynak)) oynatKaynak.focus();
    oynatKaynak = null;
  }

  /* ======== En iyi anlarım (#en-iyi): GET /api/en-iyi + POST /api/en-iyi/montaj ======== */
  function gezinCiz() {
    const ac = S.gorunum === 'en-iyi';
    ['#ustEnIyi', '#kenarEnIyi'].forEach((s) => {
      const el = $(s);
      if (!el) return;
      el.classList.toggle('aktif', ac);
      if (ac) el.setAttribute('aria-current', 'page'); else el.removeAttribute('aria-current');
    });
    const alt = $('#kenarEiAlt');
    if (alt) alt.textContent = S.ei ? `${S.ei.klipler.length} klip · puana göre sıralı` : 'Tüm maçlardaki klipler, sıralı';
    kariyerGezin();
  }
  function enIyiDuzenle(v) {
    const klipler = (Array.isArray(v && v.klipler) ? v.klipler : [])
      .filter((k) => k && k.klip)
      .sort((a, b) => (b.skor || 0) - (a.skor || 0));
    const montaj = v && v.montaj && v.montaj.klip ? v.montaj : null;
    return { klipler, montaj };
  }
  // 404: sunucu bu ucu tanımıyor (yeni özellikten önce başlatılmış).
  const enIyiHataMetni = (e) => (e && e.status === 404
    ? 'Sunucu bu isteği tanımıyor (HTTP 404). Arayüz sunucusu bu özellikten önce başlatılmış olabilir: kapatıp arayuz.bat ile yeniden başlat.'
    : (e && e.message) || 'Bilinmeyen hata.');

  function enIyiAc() {
    S.istekNo++; // süren demo yüklemeleri #ana'yı artık çizmesin
    S.gorunum = 'en-iyi';
    S.secili = null;
    menuAc(false);
    ipucuGizle();
    if (gozlem) { gozlem.disconnect(); gozlem = null; }
    scrollTo({ top: 0, behavior: kaydir() });
    listeCiz();
    gezinCiz();
    enIyiCiz();
    enIyiYukle();
  }
  async function enIyiYukle(elle = false) {
    if (S.eiYukleniyor) return;
    S.eiYukleniyor = true;
    if (!S.ei) { S.eiHata = null; enIyiCiz(); }
    const yen = $('[data-ei-yenile].ikon-dugme');
    if (yen) yen.classList.add('donuyor');
    let degisti = true;
    try {
      const yeni = enIyiDuzenle(await api('/api/en-iyi'));
      degisti = !S.ei || JSON.stringify(yeni) !== JSON.stringify(S.ei);
      S.ei = yeni;
      S.eiHata = null;
      if (elle) bildir('En iyi anlar yenilendi.');
    } catch (e) {
      if (S.ei) { degisti = false; bildir('En iyi anlar alınamadı: ' + enIyiHataMetni(e), 'hata'); }
      else S.eiHata = e;
    } finally {
      S.eiYukleniyor = false;
      $$('[data-ei-yenile].ikon-dugme').forEach((x) => x.classList.remove('donuyor'));
    }
    gezinCiz();
    if (S.gorunum === 'en-iyi' && degisti) enIyiCiz();
  }
  function macaDon() {
    const id = (S.sonDemo && S.demolar.some((d) => d.id === S.sonDemo) && S.sonDemo)
      || (S.demolar.find((d) => d.analiz_edildi) || S.demolar[0] || {}).id;
    if (id) { demoSec(id); return; }
    history.pushState(null, '', location.pathname + location.search);
    S.istekNo++;
    S.gorunum = 'mac';
    gezinCiz();
    bosCiz();
  }

  function enIyiCiz() {
    const ana = $('#ana');
    if (!S.ei) {
      ana.innerHTML = S.eiHata
        ? `<div class="analiz"><div class="analiz-ic giris">
            <h2>En iyi anlar alınamadı</h2><p>${esc(enIyiHataMetni(S.eiHata))}</p>
            <div class="ei-dugmeler orta"><button class="btn-ikincil" type="button" data-ei-yenile>${ikon('i-refresh')}Tekrar dene</button>
              <button class="btn-ikincil" type="button" data-maca-don>${ikon('i-back')}Maçlara dön</button></div></div></div>`
        : `<div class="analiz"><div class="analiz-ic giris"><div class="yukleyici"></div><h2>En iyi anlar yükleniyor</h2>
            <p>Tüm maçlardaki klipler toplanıyor…</p></div></div>`;
      return;
    }
    const l = S.ei.klipler;
    const haritalar = new Set(l.map((k) => haritaAnahtar(k.harita)).filter(Boolean));
    const maclar = new Set(l.map((k) => k.demo || k.kod || k.ad));
    if (S.eiHarita && !haritalar.has(S.eiHarita)) S.eiHarita = '';
    const en = l[0];
    const son = l.reduce((a, k) => (k.tarih && (!a || k.tarih > a) ? k.tarih : a), null);
    ana.innerHTML = `
      <section class="ei-bant" style="${haritaStil(en && en.harita)}">
        <div class="ei-zemin"></div><div class="sb-filigran" lang="en">Highlights</div>
        <div class="sb-ust"><span class="sb-etiket">Kariyer vitrini</span><span>Tüm maçlar</span>${son ? `<span class="ayir"></span><span>Son klip ${esc(tarihYaz(son))}</span>` : ''}</div>
        <div class="ei-bant-ic">
          <div class="ei-bas-metin"><h1 class="ei-baslik">En iyi <span>anlarım</span></h1>
            <p class="ei-aciklama">Kaydettiğin bütün klipler tek listede, puanı en yüksekten başlayarak. Bir karta tıkla, klip oynasın.</p></div>
          <div class="ei-sayilar">
            <div><b data-say="${l.length}">${l.length}</b>klip</div><div><b data-say="${maclar.size}">${maclar.size}</b>maç</div>
            <div><b data-say="${haritalar.size}">${haritalar.size}</b>harita</div>
            <div><b>${en ? (en.tahmini ? '~' : '') + sayi(en.skor, 1) : '–'}</b>en yüksek puan</div></div>
        </div>
        <div class="ei-arac">
          <button class="btn-ikincil" type="button" data-maca-don>${ikon('i-back')}Maçlara dön</button>
          <button class="btn-ikincil" type="button" data-ei-git="eiMontaj">${ikon('i-film')}Montaj${S.ei.montaj ? ' <em class="ei-var">hazır</em>' : ''}</button>
          <span class="ust-bosluk"></span>
          <button class="ikon-dugme" type="button" data-ei-yenile title="Listeyi yenile" aria-label="Listeyi yenile">${ikon('i-refresh')}</button>
        </div>
      </section>
      <section class="panel giris" id="eiVitrin" style="--d:60ms">
        <div class="bas"><h2><span class="bas-no"><span>01</span></span>Sıralama</h2><span class="bas-ek" id="eiOzet"></span></div>
        <div class="ei-filtre" id="eiFiltre"></div>
        <div class="klip-izgara" id="eiIzgara"></div>
      </section>
      <section class="panel giris" id="eiMontaj" style="--d:120ms">
        <div class="bas"><h2><span class="bas-no"><span>02</span></span>Montaj</h2><span class="bas-ek">En iyi klipler art arda, tek videoda</span></div>
        <div class="kayit" id="montajKutu"></div>
      </section>`;
    vitrinCiz();
    montajCiz();
    sayaclar($('.ei-sayilar'));
  }

  // Klibin demosu yüklüyse sahne gerçek oyuncu adlarını kullanır; yoksa yalnız harita renkleri.
  function vitrinDemo(k) {
    const s = k.demo && S.demo[k.demo];
    if (s) return s;
    const ben = Object.values(S.demo).map(benBul).find(Boolean);
    return { harita: k.harita, benim_takim: 0, roundlar: [], oyuncular: ben ? [{ ...ben, takim: 0 }] : [] };
  }
  const vitrinHl = (k) => ({ round: k.round, labels: k.etiketler || [], weapons: k.silahlar || [], saniye: k.saniye });

  function vitrinCiz() {
    const iz = $('#eiIzgara');
    if (!iz || !S.ei) return;
    const tum = S.ei.klipler;
    const say = {};
    tum.forEach((k) => { const h = haritaAnahtar(k.harita); if (h) say[h] = (say[h] || 0) + 1; });
    const sirali = Object.keys(say).sort((a, b) => say[b] - say[a] || a.localeCompare(b));
    const cip = (h, ad, n) => `<button type="button" class="ei-cip${S.eiHarita === h ? ' aktif' : ''}" data-ei-harita="${esc(h)}" aria-pressed="${S.eiHarita === h}"${h ? ` style="${haritaStil(h)}"` : ''}>${h ? '<i></i>' : ''}<span${h ? ' lang="en"' : ''}>${esc(ad)}</span><em>${n}</em></button>`;
    $('#eiFiltre').innerHTML = tum.length ? `
      <div class="ei-cipler" role="group" aria-label="Harita filtresi">${cip('', 'Tümü', tum.length)}${sirali.map((h) => cip(h, haritaAd(h), say[h])).join('')}</div>
      <div class="secim" role="radiogroup" aria-label="Kaç klip gösterilsin">${[[10, 'En iyi 10'], [20, 'En iyi 20'], [0, 'Hepsi']].map(([n, ad]) =>
        `<button type="button" role="radio" data-ei-adet="${n}" class="${S.eiAdet === n ? 'aktif' : ''}" aria-checked="${S.eiAdet === n}">${ad}</button>`).join('')}</div>` : '';
    const f = S.eiHarita ? tum.filter((k) => haritaAnahtar(k.harita) === S.eiHarita) : tum;
    const g = S.eiAdet ? f.slice(0, S.eiAdet) : f;
    S.eiGorunen = g;
    $('#eiOzet').innerHTML = tum.length ? `${g.length} / ${f.length} klip${S.eiHarita ? ` · <span lang="en">${esc(haritaAd(S.eiHarita))}</span>` : ''}` : '';
    if (!tum.length) {
      iz.innerHTML = `<div class="ei-bos"><span class="birak-ikon">${ikon('i-film')}</span><div><strong>Henüz klip yok</strong>
        <p>Bir maçı aç ve “Klipleri kaydet” ile klip üret. Kaydedilen bütün klipler burada puana göre sıralanır.</p>
        <button class="btn-ikincil" type="button" data-maca-don>${ikon('i-back')}Maçlara dön</button></div></div>`;
      return;
    }
    const enYuksek = Math.max(...tum.map((k) => k.skor || 0), 1);
    iz.innerHTML = g.map((k, i) => vitrinKart(k, i, enYuksek)).join('');
  }

  function vitrinKart(k, i, enYuksek) {
    const h = vitrinHl(k);
    const b = baslikYap(h);
    const ad = haritaAd(k.harita) || 'Bilinmeyen harita';
    const tahmin = k.tahmini ? ' data-tip="Tahmini puan\nDosya adından tahmin edildi (highlight verisi yok)."' : '';
    const silah = (k.silahlar || []).map((w) => esc(silahAd(w))).join(' · ');
    return `<article class="klip kayitli ei-klip${i === 0 ? ' one' : ''} giris" style="--d:${Math.min(i, 12) * 45}ms" data-ei="${i}">
      ${sahneHtml(vitrinDemo(k), h, i, { kayitli: true, oynatAt: `data-ei-oynat="${i}"` })}
      <div class="kl-govde">
        <div class="kl-ust"><span class="kl-sira${i < 3 ? ' podyum' : ''}">#${i + 1}</span>
          <h3 class="kl-baslik"><span class="kl-ust-et">${i === 0 ? 'En iyi anın · ' : ''}<span lang="en">${esc(ad)}</span> · ${b.ust}</span>${b.ana}</h3>
          <div class="kl-puan${k.tahmini ? ' tahmini' : ''}"${tahmin}>${k.tahmini ? '~' : ''}${sayi(k.skor, 1)}<small>${k.tahmini ? 'tahmini' : 'puan'}</small></div></div>
        <div class="kl-puan-bar"><i style="--p:${sinirla((k.skor || 0) / enYuksek * 100, 2, 100)}%"></i></div>
        <div class="kl-etiketler">${etiketHtml(h.labels) || '<span class="etk hs">Etiket yok</span>'}</div>
        <div class="kl-alt"><span lang="en">${silah || '—'}</span><span>${esc(tarihYaz(k.tarih))}</span></div>
        <div class="ei-alt"><span class="ei-kod" title="${esc(k.ad || '')}">${esc(k.kod || '')}${k.boyut_mb != null ? ` · ${sayi(k.boyut_mb, 1)} MB` : ''}</span>
          ${k.demo ? `<a class="ei-git" href="#${encodeURIComponent(k.demo)}">Maça git →</a>`
            : '<span class="ei-git yok" data-tip="Maç listede yok\nDemo silinmiş ya da klip eşleşmedi.">Maç yok</span>'}</div>
      </div></article>`;
  }

  function vitrinOynat(i, kaynak) {
    const k = S.eiGorunen[i];
    if (!k) return;
    const h = vitrinHl(k);
    const b = baslikYap(h);
    pencereAc({
      klip: k.klip, rozet: `#${i + 1} · R${k.round}`, saniye: ORNEK_MODU ? (k.saniye || 15) : k.saniye,
      baslik: `${b.ana} · <span lang="en">${esc(haritaAd(k.harita) || '')}</span>`,
      sahne: ORNEK_MODU ? sahneHtml(vitrinDemo(k), { ...h, saniye: k.saniye || 15 }, i, { kayitli: false }) : '',
      ek: k.demo ? ` · <a href="#${encodeURIComponent(k.demo)}">Maça git →</a>` : '',
    }, kaynak);
  }

  function montajCiz() {
    const kutu = $('#montajKutu');
    if (!kutu || !S.ei) return;
    const n = S.ei.klipler.length;
    const mj = S.ei.montaj;
    const sur = S.montajSuruyor;
    const adetN = Math.min(S.mjAdet, n);
    const sn = Math.floor((Date.now() - S.montajBas) / 1000);
    kutu.innerHTML = `
      <div class="kayit-sol">
        <div class="kayit-satir"><span class="kayit-et">Klip sayısı</span>
          <div class="secim" role="radiogroup" aria-label="Montajda kaç klip olsun">${[5, 10, 15, 20].map((x) =>
            `<button type="button" role="radio" data-mj-adet="${x}" class="${S.mjAdet === x ? 'aktif' : ''}" aria-checked="${S.mjAdet === x}"${sur ? ' disabled' : ''}>${x}</button>`).join('')}</div></div>
        <button class="btn-kaydet btn-montaj${sur ? ' calisiyor' : ''}" id="montajYap" type="button"${sur || !n ? ' disabled' : ''}${!n ? ' title="Önce klip kaydet."' : ''}>
          ${sur ? '<span class="rec"></span>' : ikon('i-film')}<span>${sur ? 'Montaj hazırlanıyor…' : mj ? 'Yeniden montaj yap' : 'Montaj yap'}</span>
          <small>${sur || !n ? '' : `(en iyi ${adetN})`}</small></button>
        ${sur ? `<div class="mj-bekle"><div class="il-bar belirsiz"><i></i></div><div class="analiz-adim" id="montajSure">${sn} sn · klipler birleştiriliyor</div></div>` : ''}
        ${S.montajHata && !sur ? `<div class="mj-hata" role="alert">${ikon('i-alert')}<span>${esc(S.montajHata)}</span></div>` : ''}
        <div class="kayit-bilgi">${ORNEK_MODU ? '<b>Örnek mod:</b> montaj taklit edilir, dosya yazılmaz. ' : ''}Puanı en yüksek ${adetN || ''} klip sırayla tek bir MP4'te birleştirilir (<code>klipler/en_iyi_montaj.mp4</code>); var olan montajın üzerine yazılır. Birkaç saniye ile bir dakika sürebilir.${n && S.mjAdet > n ? ` Şu an yalnız ${n} klip var.` : ''}</div>
      </div>
      <div class="mj-kart${mj ? '' : ' bos'}${mj && S.montajYeni ? ' yeni' : ''}">${mj ? montajKartHtml(mj) : `
        <span class="birak-ikon">${ikon('i-film')}</span><strong>Henüz montaj yok</strong>
        <span>${n ? `Klip sayısını seç ve “Montaj yap”a bas. En iyi anların art arda tek videoda birleşir.` : 'Montaj için önce klip kaydetmelisin.'}</span>`}</div>`;
    S.montajYeni = false;
  }
  function montajKartHtml(mj) {
    const serit = S.ei.klipler.slice(0, Math.max(1, Math.min(mj.adet || 1, 20)))
      .map((k) => `<i style="${haritaStil(k.harita)}"></i>`).join('');
    let dosya = '';
    try { dosya = decodeURIComponent(String(mj.klip).split('/').pop()); } catch { dosya = String(mj.klip); }
    return `<button class="mj-poster" type="button" data-mj-oynat aria-label="Montajı oynat">
        <span class="mj-serit">${serit}</span><span class="kl-round">Montaj</span>
        <span class="kl-oynat">${ikon('i-play', '')}</span></button>
      <div class="mj-bilgi">
        <div class="mj-ad">En iyi ${esc(mj.adet ?? '?')} an<small>${esc(dosya)}</small></div>
        <div class="mj-say"><div>Klip<b>${esc(mj.adet ?? '–')}</b></div><div>Boyut<b>${sayi(mj.boyut_mb, 1)} <small>MB</small></b></div><div>Tarih<b>${esc(tarihYaz(mj.tarih))}</b></div></div>
        <div class="ei-dugmeler"><button class="btn-ikincil" type="button" data-mj-oynat>${ikon('i-play')}Oynat</button>
          ${ORNEK_MODU ? '' : `<a class="btn-ikincil" href="${esc(montajSrc(mj))}" target="_blank" rel="noopener">${ikon('i-full')}Yeni sekmede aç</a>`}</div>
      </div>`;
  }
  // Montaj dosya adı hep aynı; yeniden üretilince tarayıcı eski kopyayı göstermesin.
  const montajSrc = (mj) => mj.klip + (mj.tarih ? (mj.klip.includes('?') ? '&' : '?') + 'v=' + encodeURIComponent(mj.tarih) : '');
  function montajOynat(kaynak) {
    const mj = S.ei && S.ei.montaj;
    if (!mj) return;
    const ilk = S.ei.klipler[0];
    pencereAc({
      klip: mj.klip, src: montajSrc(mj), rozet: `${mj.adet ?? '?'} klip`, baslik: 'En iyi anlar · montaj',
      saniye: ORNEK_MODU ? (mj.saniye || (mj.adet || 1) * 15) : 0,
      sahne: ORNEK_MODU && ilk ? sahneHtml(vitrinDemo(ilk), { ...vitrinHl(ilk), saniye: mj.saniye || 60 }, 0, { kayitli: false }) : '',
    }, kaynak);
  }
  async function montajYap() {
    if (S.montajSuruyor || !S.ei || !S.ei.klipler.length) return;
    const adet = S.mjAdet;
    S.montajSuruyor = true;
    S.montajHata = null;
    S.montajBas = Date.now();
    montajCiz();
    const sayac = setInterval(() => {
      const el = $('#montajSure');
      if (el) el.textContent = `${Math.floor((Date.now() - S.montajBas) / 1000)} sn · klipler birleştiriliyor`;
    }, 500);
    try {
      const r = await api('/api/en-iyi/montaj', { method: 'POST', body: JSON.stringify({ adet }) });
      if (!r || !r.klip) throw new Error('Sunucudan geçersiz yanıt geldi.');
      if (S.ei) S.ei.montaj = r;
      S.montajYeni = true;
      bildir(`Montaj hazır: ${r.adet ?? adet} klip · ${sayi(r.boyut_mb, 1)} MB`, 'basari');
    } catch (e) {
      S.montajHata = e.status === 404 ? enIyiHataMetni(e) : e.message;
      bildir('Montaj yapılamadı: ' + S.montajHata, 'hata');
    } finally {
      clearInterval(sayac);
      S.montajSuruyor = false;
      if (S.gorunum === 'en-iyi') {
        montajCiz();
        const git = $('[data-ei-git="eiMontaj"]');
        if (git && S.ei && S.ei.montaj && !$('.ei-var', git)) git.insertAdjacentHTML('beforeend', ' <em class="ei-var">hazır</em>');
      }
    }
  }

  /* ======== yükleme: POST /api/yukle ======== */
  function dosyalariAl(liste) {
    const hepsi = [...liste];
    const uygun = hepsi.filter((f) => UZANTI.test(f.name));
    if (hepsi.length - uygun.length) bildir(`${hepsi.length - uygun.length} dosya atlandı: yalnız .dem, .dem.zst, .dem.gz, .dem.bz2`, 'hata');
    S.kuyruk.push(...uygun);
    kuyruguIsle();
  }
  function yuklemeDurum(ad, oran, alt, hata = false) {
    const kutu = $('#yukleme');
    kutu.hidden = false;
    kutu.classList.toggle('hata', hata);
    $('#yuklemeAd').textContent = ad;
    $('#yuklemeAd').title = ad;
    $('#yuklemeYuzde').textContent = hata ? 'Hata' : Math.floor(oran * 100) + '%';
    $('#yuklemeCubuk').style.width = (hata ? 100 : oran * 100) + '%';
    $('#yuklemeAlt').textContent = alt;
  }
  async function kuyruguIsle() {
    if (S.yukleniyor) return;
    S.yukleniyor = true;
    let sonId = null, hataVar = false;
    while (S.kuyruk.length) {
      const f = S.kuyruk.shift();
      const bas = Date.now();
      const mb = f.size / 1048576;
      const sirada = () => (S.kuyruk.length ? ` · sırada ${S.kuyruk.length} dosya` : '');
      yuklemeDurum(f.name, 0, `0 / ${sayi(mb, 1)} MB${sirada()}`);
      try {
        const sonuc = await yukleXhr(f, (yuklenen, toplam) => {
          const sn = (Date.now() - bas) / 1000;
          const hiz = sn > 0.3 ? ` · ${sayi(yuklenen / 1048576 / sn, 0)} MB/sn` : '';
          yuklemeDurum(f.name, yuklenen / toplam, `${sayi(yuklenen / 1048576, 1)} / ${sayi(toplam / 1048576, 1)} MB${hiz}${sirada()}`);
        });
        yuklemeDurum(f.name, 1, `${sayi(mb, 1)} MB yüklendi${sirada()}`);
        bildir(`${f.name} yüklendi.`, 'basari');
        sonId = (sonuc && sonuc.id) || sonId;
      } catch (e) {
        hataVar = true;
        yuklemeDurum(f.name, 0, e.message, true);
        bildir(`${f.name}: ${e.message}`, 'hata');
      }
    }
    S.yukleniyor = false;
    await demolariYenile();
    if (!hataVar) setTimeout(() => { if (!S.yukleniyor) $('#yukleme').hidden = true; }, 1500);
    if (sonId) demoSec(sonId); // yeni demo açılır; analiz edilmemişse sunucu analiz eder
  }

  /* ======== bölüm gezinme vurgusu ======== */
  let gozlem = null;
  function navGozlem() {
    if (gozlem) gozlem.disconnect();
    const linkler = $$('#bolumNav a');
    gozlem = new IntersectionObserver((girdiler) => {
      girdiler.forEach((g) => {
        if (!g.isIntersecting) return;
        linkler.forEach((a) => a.classList.toggle('aktif', a.getAttribute('href') === '#' + g.target.id));
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    ['ozet', 'tablo', 'roundlar', 'silahlar', 'klipler'].forEach((x) => { const el = document.getElementById(x); if (el) gozlem.observe(el); });
  }

  /* ======== Kariyer (#kariyer): GET /api/kariyer — analiz edilmiş tüm maçlar ======== */
  const KARIYER = 'kariyer';
  const KR_METRIK = [
    { k: 'rating', ad: EN('Rating'), duz: 'Rating', o: 2, ref: 1, iyi: 1.1, kotu: 0.9 },
    { k: 'adr', ad: 'ADR', duz: 'ADR', o: 1, iyi: 85, kotu: 65 },
    { k: 'kast', ad: 'KAST', duz: 'KAST', o: 1, birim: '%', iyi: 75, kotu: 65 },
    { k: 'kd', ad: 'K/D', duz: 'K/D', o: 2, ref: 1, iyi: 1.1, kotu: 0.9 },
    { k: 'hs_yuzde', ad: 'HS%', duz: 'HS%', o: 1, birim: '%', iyi: 50, kotu: 30 },
  ];
  const SONUC_AD = { G: 'Galibiyet', M: 'Mağlubiyet', B: 'Berabere' };
  const SONUC_SINIF = { G: 'galibiyet', M: 'maglubiyet', B: 'berabere' };
  const krOrt = (l, k) => {
    const v = l.map((m) => m[k]).filter((x) => typeof x === 'number');
    return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null;
  };
  const kisaTarih = (t) => { const d = new Date(t); return isNaN(d) ? '' : d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' }); };

  function kariyerGezin() {
    const ac = S.gorunum === KARIYER;
    ['#ustKariyer', '#kenarKariyer'].forEach((s) => {
      const el = $(s);
      if (!el) return;
      el.classList.toggle('aktif', ac);
      if (ac) el.setAttribute('aria-current', 'page'); else el.removeAttribute('aria-current');
    });
    const alt = $('#kenarKrAlt');
    if (alt && S.kr) alt.textContent = S.kr.maclar.length ? `${S.kr.maclar.length} maç · gelişim ve haritalar` : 'Henüz analiz edilmiş maç yok';
  }

  // Maç satırlarından özet: genel/son 10 ortalamaları, form, seriler, harita tablosu, en iyi/kötü maç.
  function kariyerOzet(maclar) {
    const l = maclar;
    const say = (r) => l.filter((m) => m.sonuc === r).length;
    const son10 = l.slice(-10), onceki = l.slice(-20, -10);
    let seri = null;
    for (let i = l.length - 1; i >= 0; i--) {
      if (!seri) seri = { tur: l[i].sonuc, n: 1 };
      else if (l[i].sonuc === seri.tur) seri.n++;
      else break;
    }
    let enUzun = 0, su = 0;
    l.forEach((m) => { su = m.sonuc === 'G' ? su + 1 : 0; enUzun = Math.max(enUzun, su); });
    const puanli = l.filter((m) => typeof m.rating === 'number');
    const enIyi = puanli.reduce((a, m) => (!a || m.rating > a.rating ? m : a), null);
    const enKotu = puanli.length > 1 ? puanli.reduce((a, m) => (!a || m.rating < a.rating ? m : a), null) : null;
    const hm = {};
    l.forEach((m) => {
      const h = haritaAnahtar(m.harita) || '?';
      (hm[h] = hm[h] || []).push(m);
    });
    const haritalar = Object.entries(hm).map(([h, ml]) => {
      const g = ml.filter((m) => m.sonuc === 'G').length, mg = ml.filter((m) => m.sonuc === 'M').length;
      return { h, n: ml.length, g, m: mg, b: ml.length - g - mg, oran: g / ml.length, rating: krOrt(ml, 'rating'), adr: krOrt(ml, 'adr') };
    }).sort((a, b) => b.n - a.n || b.oran - a.oran || a.h.localeCompare(b.h));
    return {
      n: l.length, g: say('G'), m: say('M'), b: say('B'), oran: l.length ? say('G') / l.length : 0,
      son10, onceki, form: son10.map((m) => m.sonuc), seri, enUzun, enIyi, enKotu, haritalar,
    };
  }

  function kariyerAc() {
    S.istekNo++; // süren demo yüklemeleri #ana'yı artık çizmesin
    S.gorunum = KARIYER;
    S.secili = null;
    menuAc(false);
    ipucuGizle();
    if (gozlem) { gozlem.disconnect(); gozlem = null; }
    scrollTo({ top: 0, behavior: kaydir() });
    listeCiz();
    gezinCiz();
    kariyerCiz();
    kariyerYukle();
  }
  async function kariyerYukle(elle = false) {
    if (S.krYukleniyor) return;
    S.krYukleniyor = true;
    if (!S.kr) { S.krHata = null; kariyerCiz(); }
    $$('[data-kr-yenile].ikon-dugme').forEach((x) => x.classList.add('donuyor'));
    let degisti = true;
    try {
      const v = await api('/api/kariyer');
      const yeni = { maclar: Array.isArray(v && v.maclar) ? v.maclar : [], bekleyen: (v && v.analiz_bekleyen) || 0, okunamayan: (v && v.okunamayan) || 0 };
      degisti = !S.kr || JSON.stringify(yeni) !== JSON.stringify(S.kr);
      S.kr = yeni;
      S.krHata = null;
      if (elle) bildir('Kariyer yenilendi.');
    } catch (e) {
      if (S.kr) { degisti = false; bildir('Kariyer alınamadı: ' + enIyiHataMetni(e), 'hata'); } else S.krHata = e;
    } finally {
      S.krYukleniyor = false;
      $$('[data-kr-yenile].ikon-dugme').forEach((x) => x.classList.remove('donuyor'));
    }
    kariyerGezin();
    if (S.gorunum === KARIYER && degisti) kariyerCiz();
  }

  function kariyerCiz() {
    const ana = $('#ana');
    if (!S.kr) {
      ana.innerHTML = S.krHata
        ? `<div class="analiz"><div class="analiz-ic giris"><h2>Kariyer alınamadı</h2><p>${esc(enIyiHataMetni(S.krHata))}</p>
            <div class="ei-dugmeler orta"><button class="btn-ikincil" type="button" data-kr-yenile>${ikon('i-refresh')}Tekrar dene</button>
              <button class="btn-ikincil" type="button" data-maca-don>${ikon('i-back')}Maçlara dön</button></div></div></div>`
        : `<div class="analiz"><div class="analiz-ic giris"><div class="yukleyici"></div><h2>Kariyer yükleniyor</h2>
            <p>Analiz edilmiş maçlar okunuyor…</p></div></div>`;
      return;
    }
    const l = S.kr.maclar;
    const oz = kariyerOzet(l);
    const ad = (l[l.length - 1] || {}).ad || '';
    const r10 = krOrt(oz.son10, 'rating');
    const bekleyen = S.kr.bekleyen ? `<p class="kr-not">${ikon('i-alert')}<span>${S.kr.bekleyen} demo henüz analiz edilmedi; açtığında kariyere eklenir.</span></p>` : '';
    const form = oz.form.map((r, i) => `<span class="kr-form-k ${SONUC_SINIF[r]}" title="${esc(SONUC_AD[r])}"${i === oz.form.length - 1 ? ' aria-current="true"' : ''}>${r}</span>`).join('');
    const seriYaz = oz.seri ? `${oz.seri.n} ${oz.seri.tur === 'G' ? 'galibiyet' : oz.seri.tur === 'M' ? 'mağlubiyet' : 'beraberlik'}` : '–';
    ana.innerHTML = `
      <section class="ei-bant kr-bant" style="${haritaStil((oz.haritalar[0] || {}).h)}">
        <div class="ei-zemin"></div><div class="sb-filigran" lang="en">Career</div>
        <div class="sb-ust"><span class="sb-etiket">Kariyer</span><span>Tüm analiz edilmiş maçlar</span>${l.length ? `<span class="ayir"></span><span>${esc(kisaTarih(l[0].tarih))} – ${esc(kisaTarih(l[l.length - 1].tarih))}</span>` : ''}</div>
        <div class="ei-bant-ic">
          <div class="ei-bas-metin"><h1 class="ei-baslik">Kariyer<span>im</span></h1>
            <p class="ei-aciklama">${ad ? `<b lang="en">${esc(ad)}</b> · ` : ''}Maç maç gelişim, haritalar ve form. Yalnız analiz edilmiş demolar sayılır.</p></div>
          <div class="ei-sayilar">
            <div><b data-say="${oz.n}">${oz.n}</b>maç</div>
            <div><b>${oz.g}<small>–</small>${oz.m}${oz.b ? `<small>–</small>${oz.b}` : ''}</b>G – M</div>
            <div><b>%${sayi(oz.oran * 100)}</b>galibiyet</div>
            <div><b class="${r10 == null ? '' : 'renk-' + esik(r10, 1.1, 0.9)}">${sayi(r10, 2)}</b>son 10 <span lang="en">rating</span></div></div>
        </div>
        <div class="ei-arac">
          <button class="btn-ikincil" type="button" data-maca-don>${ikon('i-back')}Maçlara dön</button>
          ${l.length ? `<div class="kr-form" aria-label="Son ${oz.form.length} maç, en yeni sağda"><span class="kr-form-et">Form</span>${form}<span class="kr-form-et">Seri: <b>${esc(seriYaz)}</b></span></div>` : ''}
          <span class="ust-bosluk"></span>
          <button class="ikon-dugme" type="button" data-kr-yenile title="Yenile" aria-label="Kariyeri yenile">${ikon('i-refresh')}</button>
        </div>
      </section>
      ${bekleyen}
      ${l.length ? kariyerPaneller(oz) : `<section class="panel giris"><div class="ei-bos"><span class="birak-ikon">${ikon('i-chart')}</span><div><strong>Henüz analiz edilmiş maç yok</strong>
        <p>Soldan bir demo aç; analiz edilince maç burada kariyerine eklenir.</p>
        <button class="btn-ikincil" type="button" data-maca-don>${ikon('i-back')}Maçlara dön</button></div></div></section>`}`;
    sayaclar($('.ei-sayilar'));
    if (l.length) grafikCiz();
  }

  function kariyerPaneller(oz) {
    const l = S.kr.maclar;
    const metrikler = KR_METRIK.map((m) => {
      const g = krOrt(l, m.k), s = krOrt(oz.son10, m.k);
      const f = g != null && s != null && l.length > oz.son10.length ? s - g : null;
      const yon = f == null || Math.abs(f) < (m.o === 2 ? 0.005 : 0.05) ? '' : f > 0 ? 'artis' : 'dusus';
      return `<button type="button" class="kr-metrik${S.krMetrik === m.k ? ' aktif' : ''}" data-kr-metrik="${m.k}" aria-pressed="${S.krMetrik === m.k}">
        <span class="kr-m-ad">${m.ad}</span>
        <span class="kr-m-deger renk-${esik(s, m.iyi, m.kotu)}">${sayi(s, m.o)}${m.birim ? `<small>${m.birim}</small>` : ''}</span>
        <span class="kr-m-alt">son ${oz.son10.length} · genel ${sayi(g, m.o)}${yon ? ` <em class="${yon}">${yon === 'artis' ? '▲' : '▼'} ${sayi(Math.abs(f), m.o)}</em>` : ''}</span></button>`;
    }).join('');
    const kart = (m, baslik, sinif) => {
      if (!m) return '';
      const ic = `<span class="kr-mac-et ${sinif}">${baslik}</span>
        <span class="kr-mac-harita" lang="en">${esc(haritaAd(m.harita) || 'Bilinmeyen')}</span>
        <span class="kr-mac-skor"><b class="${SONUC_SINIF[m.sonuc]}">${m.skor[0]}–${m.skor[1]}</b> ${esc(SONUC_AD[m.sonuc])} · ${esc(kisaTarih(m.tarih))}</span>
        <span class="kr-mac-say"><span><b class="renk-${esik(m.rating, 1.1, 0.9)}">${sayi(m.rating, 2)}</b><span lang="en">rating</span></span><span><b>${m.kill ?? '–'}/${m.death ?? '–'}/${m.assist ?? '–'}</b>K/D/A</span><span><b>${sayi(m.adr, 1)}</b>ADR</span></span>
        <span class="kr-mac-git">${m.demo_var ? 'Maça git →' : 'Demo artık klasörde değil'}</span>`;
      return m.demo_var
        ? `<button type="button" class="kr-mac" data-demo="${esc(m.id)}" style="${haritaStil(m.harita)}">${ic}</button>`
        : `<div class="kr-mac yok" style="${haritaStil(m.harita)}">${ic}</div>`;
    };
    const haritalar = oz.haritalar.map((h) => `<li class="kr-h" style="${haritaStil(h.h)}">
        <span class="kr-h-ad"><i></i><span lang="en">${esc(h.h === '?' ? 'Bilinmeyen' : haritaAd(h.h))}</span></span>
        <span class="kr-h-n">${h.n} maç<small>${h.g}G · ${h.m}M${h.b ? ` · ${h.b}B` : ''}</small></span>
        <span class="kr-h-oran"><span class="kr-cubuk" role="img" aria-label="Galibiyet oranı yüzde ${Math.round(h.oran * 100)}"><i style="width:${Math.max(h.oran * 100, 1.5)}%"></i><b style="left:50%"></b></span><em>%${sayi(h.oran * 100)}</em></span>
        <span class="kr-h-r"><span class="rozet ${ratingSinif(h.rating)}">${sayi(h.rating, 2)}</span><small>${sayi(h.adr, 1)} ADR</small></span></li>`).join('');
    const satirlar = [...l].reverse().map((m) => {
      const ic = `<td>${esc(kisaTarih(m.tarih))}</td><td class="sol" lang="en">${esc(haritaAd(m.harita) || '–')}</td>
        <td><span class="kr-sonuc ${SONUC_SINIF[m.sonuc]}" title="${esc(SONUC_AD[m.sonuc])}">${m.sonuc}</span> ${m.skor[0]}–${m.skor[1]}</td>
        <td class="gz-a">${m.kill ?? '–'}/${m.death ?? '–'}/${m.assist ?? '–'}</td><td>${sayi(m.adr, 1)}</td><td class="kr-gz">${sayi(m.kast, 1)}</td>
        <td class="kr-gz">${sayi(m.hs_yuzde, 1)}</td><td><span class="rozet ${ratingSinif(m.rating)}">${sayi(m.rating, 2)}</span></td>`;
      return `<tr${m.demo_var ? ` class="kr-satir" data-demo="${esc(m.id)}" tabindex="0" title="Maçı aç"` : ' title="Demo artık klasörde değil"'}>${ic}</tr>`;
    }).join('');
    return `
      <section class="panel giris" id="krGelisim" style="--d:60ms">
        <div class="bas"><h2><span class="bas-no"><span>01</span></span>Gelişim</h2><span class="bas-ek">Maç maç · son 10 ortalaması</span></div>
        <div class="kr-metrikler" role="group" aria-label="Grafikte gösterilecek ölçü">${metrikler}</div>
        <div class="kr-lejant"><span><i class="kr-l-nokta"></i>Maç <small>(dolu: galibiyet, boş: mağlubiyet)</small></span><span><i class="kr-l-cizgi"></i>Son 10 ortalaması</span></div>
        <div class="kr-grafik" id="krGrafik"></div>
      </section>
      <div class="ikili">
        <section class="panel giris" id="krHaritalar" style="--d:120ms">
          <div class="bas"><h2><span class="bas-no"><span>02</span></span>Haritalar</h2><span class="bas-ek">Galibiyet oranı · ort. <span lang="en">rating</span></span></div>
          <ul class="kr-haritalar">${haritalar}</ul>
        </section>
        <section class="panel giris" id="krOne" style="--d:160ms">
          <div class="bas"><h2><span class="bas-no"><span>03</span></span>Öne çıkanlar</h2><span class="bas-ek">En uzun galibiyet serisi: <b>${oz.enUzun}</b></span></div>
          <div class="kr-maclar">${kart(oz.enIyi, 'En iyi maç', 'iyi')}${oz.enKotu && oz.enKotu !== oz.enIyi ? kart(oz.enKotu, 'En kötü maç', 'kotu') : ''}</div>
        </section>
      </div>
      <section class="panel giris" id="krGecmis" style="--d:200ms">
        <div class="bas"><h2><span class="bas-no"><span>04</span></span>Maç geçmişi</h2><span class="bas-ek">${l.length} maç · en yeni üstte</span></div>
        <div class="kr-tablo"><table>
          <thead><tr><th>Tarih</th><th class="sol">Harita</th><th>Skor</th><th class="gz-a">K/D/A</th><th>ADR</th><th class="kr-gz">KAST</th><th class="kr-gz">HS%</th><th>${EN('Rating')}</th></tr></thead>
          <tbody>${satirlar}</tbody></table></div>
      </section>`;
  }

  // Seçili ölçünün çizgi grafiği: her maç bir nokta, turuncu çizgi son 10 maçın kayan ortalaması.
  function grafikCiz() {
    const kutu = $('#krGrafik');
    if (!kutu || !S.kr) return;
    const l = S.kr.maclar;
    const m = KR_METRIK.find((x) => x.k === S.krMetrik) || KR_METRIK[0];
    const W = Math.max(kutu.clientWidth, 260), H = W < 520 ? 210 : 260;
    const P = { l: 40, r: 12, t: 14, b: 28 };
    const deg = l.map((x) => (typeof x[m.k] === 'number' ? x[m.k] : null));
    const kayan = deg.map((_, i) => krOrt(l.slice(Math.max(0, i - 9), i + 1), m.k));
    const hepsi = [...deg, ...kayan].filter((x) => x != null).concat(m.ref != null ? [m.ref] : []);
    let lo = Math.min(...hepsi), hi = Math.max(...hepsi);
    if (!(hi > lo)) { lo -= 1; hi += 1; }
    const adim = [0.1, 0.2, 0.25, 0.5, 1, 2, 5, 10, 20, 25, 50].find((a) => (hi - lo) / a <= 5) || 100;
    lo = Math.floor(lo / adim) * adim; hi = Math.ceil(hi / adim) * adim;
    if (hi === lo) hi = lo + adim;
    const iw = W - P.l - P.r, ih = H - P.t - P.b;
    const X = (i) => P.l + (l.length === 1 ? iw / 2 : (i / (l.length - 1)) * iw);
    const Y = (v) => P.t + (1 - (v - lo) / (hi - lo)) * ih;
    const ond = adim < 1 ? (adim < 0.25 ? 1 : 2) : 0;
    let s = '';
    for (let v = lo; v <= hi + adim / 2; v += adim) {
      s += `<line class="kr-izgara" x1="${P.l}" x2="${W - P.r}" y1="${Y(v)}" y2="${Y(v)}"/><text class="kr-eksen" x="${P.l - 8}" y="${Y(v) + 4}" text-anchor="end">${sayi(v, m.o === 2 ? 2 : ond)}</text>`;
    }
    if (m.ref != null) s += `<line class="kr-ref" x1="${P.l}" x2="${W - P.r}" y1="${Y(m.ref)}" y2="${Y(m.ref)}"/>`;
    const yol = (dizi) => dizi.map((v, i) => (v == null ? null : `${X(i).toFixed(1)},${Y(v).toFixed(1)}`)).filter(Boolean).join(' ');
    s += `<polyline class="kr-mac-cizgi" points="${yol(deg)}"/>`;
    s += `<polyline class="kr-ort-cizgi" points="${yol(kayan)}"/>`;
    const etiket = new Set([0, l.length - 1]);
    if (l.length > 6) etiket.add(Math.round((l.length - 1) / 2));
    etiket.forEach((i) => {
      const a = i === 0 && l.length > 1 ? 'start' : i === l.length - 1 && l.length > 1 ? 'end' : 'middle';
      s += `<text class="kr-eksen" x="${X(i)}" y="${H - 8}" text-anchor="${a}">${esc(kisaTarih(l[i].tarih))}</text>`;
    });
    const genis = l.length > 1 ? iw / (l.length - 1) : iw;
    l.forEach((x, i) => {
      if (deg[i] != null) s += `<circle class="kr-nokta ${SONUC_SINIF[x.sonuc]}" cx="${X(i)}" cy="${Y(deg[i])}" r="${l.length > 40 ? 3.5 : 4.5}"/>`;
    });
    // isabet alanları: nokta küçük olsa da sütunun tamamı üzerine gelince ipucu verir
    l.forEach((x, i) => {
      const tip = `${kisaTarih(x.tarih)} · ${haritaAd(x.harita) || '?'} ${x.skor[0]}–${x.skor[1]} (${SONUC_AD[x.sonuc]})\n${m.duz} ${sayi(deg[i], m.o)}${m.birim || ''} · son 10 ort. ${sayi(kayan[i], m.o)}${m.birim || ''}${x.demo_var ? '\nTıkla: maçı aç' : ''}`;
      s += `<rect class="kr-isabet" x="${X(i) - genis / 2}" y="${P.t}" width="${genis}" height="${ih}" data-tip="${esc(tip)}"${x.demo_var ? ` data-demo="${esc(x.id)}"` : ''}/>`;
    });
    kutu.innerHTML = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(m.duz)}: ${l.length} maç, son 10 ortalaması ${esc(sayi(kayan[kayan.length - 1], m.o))}">${s}</svg>`;
  }
  let grafikZaman = 0;
  addEventListener('resize', () => {
    clearTimeout(grafikZaman);
    grafikZaman = setTimeout(() => { if (S.gorunum === KARIYER) grafikCiz(); }, 120);
  });

  // örnek mod: GET /api/kariyer taklidi (örnek demolar + ornek.json'daki eski maçlar: kariyer_ek)
  function ornekKariyer(v) {
    const l = [];
    v.demolar.forEach((d) => {
      const s = v.demo[d.id];
      const p = s && d.analiz_edildi ? benBul(s) : null;
      if (!p) return;
      const biz = p.takim ?? s.benim_takim ?? 0;
      const T = takimlarOf(s);
      const a = T[biz].skor, b = T[1 - biz].skor;
      const r = { id: d.id, tarih: d.tarih, demo_var: true, harita: s.harita, round_sayisi: s.round_sayisi ?? a + b, skor: [a, b], sonuc: a > b ? 'G' : a < b ? 'M' : 'B', ad: p.ad, cok_kill: { ...(p.cok_kill || {}) } };
      ['rating', 'adr', 'kast', 'kd', 'hs_yuzde', 'kill', 'death', 'assist', 'acilis_kill', 'acilis_death'].forEach((k) => { r[k] = p[k] ?? null; });
      l.push(r);
    });
    (v.kariyer_ek || []).forEach((x) => l.push(kopya(x)));
    l.sort((a, b) => (a.tarih < b.tarih ? -1 : a.tarih > b.tarih ? 1 : 0));
    return { maclar: l, analiz_bekleyen: v.demolar.filter((d) => !d.analiz_edildi).length, okunamayan: 0 };
  }

  /* ======== Maç kartı (paylaşım PNG'si): tarayıcıda canvas, sunucu bağımlılığı yok ======== */
  const KART_BOYUT = { linkedin: [1200, 630, 'LinkedIn', '1200×630'], instagram: [1080, 1350, 'Instagram', '1080×1350'] };
  const TR = (x) => String(x ?? '').toLocaleUpperCase('tr-TR');
  const ENB = (x) => String(x ?? '').toUpperCase();

  function kartVeri(id) {
    const s = S.demo[id];
    const ben = s && benBul(s);
    if (!ben) return null;
    const d = S.demolar.find((x) => x.id === id);
    const biz = s.benim_takim ?? ben.takim ?? 0;
    const T = takimlarOf(s);
    const lobi = s.oyuncular || [];
    const a = T[biz].skor, b = T[1 - biz].skor;
    return {
      id, harita: s.harita, haritaAd: haritaAd(s.harita) || 'Harita', tarih: d && d.tarih,
      biz: a, onlar: b, bizAd: T[biz].ad, onAd: T[1 - biz].ad, sonuc: a > b ? 'G' : a < b ? 'M' : 'B',
      ben, sira: 1 + lobi.filter((x) => (x.rating ?? -1) > (ben.rating ?? -1)).length, lobi: lobi.length,
      mvp: lobi.length > 1 && lobi.every((x) => (x.rating ?? 0) <= ben.rating),
      round: s.round_sayisi ?? (s.roundlar || []).length,
    };
  }

  function kartAc(kaynak) {
    const v = kartVeri(S.secili);
    if (!v) { bildir('Bu maçta oyuncu bulunamadı; kart üretilemiyor.', 'hata'); return; }
    oynaticiKapat();
    oynatKaynak = kaynak || null;
    S.kartBoyut = S.kartBoyut || 'linkedin';
    const m = $('#modal');
    const paylasVar = !!(navigator.canShare && window.File);
    m.innerHTML = `<div class="oynatici kart-pencere">
      <div class="oy-bas"><span class="cip or">PNG</span><h3 id="oyBaslik">Maç kartı · <span lang="en">${esc(v.haritaAd)}</span></h3>
        <button class="ikon-dugme" type="button" data-kapat aria-label="Kapat">${ikon('i-x')}</button></div>
      <div class="kart-arac"><div class="secim" role="radiogroup" aria-label="Kart boyutu">${Object.entries(KART_BOYUT).map(([k, [, , ad, olcu]]) =>
        `<button type="button" role="radio" data-kart-boyut="${k}" class="${S.kartBoyut === k ? 'aktif' : ''}" aria-checked="${S.kartBoyut === k}">${ad} <small>${olcu}</small></button>`).join('')}</div></div>
      <div class="kart-onizleme" id="kartOnizleme"><canvas id="kartTuval" aria-label="Maç kartı önizlemesi"></canvas></div>
      <div class="kart-dugmeler">
        <button class="btn-kaydet kart-indir" type="button" data-kart-indir>${ikon('i-download')}PNG indir</button>
        <button class="btn-ikincil" type="button" data-kart-kopyala>${ikon('i-copy')}Görseli kopyala</button>
        ${paylasVar ? `<button class="btn-ikincil" type="button" data-kart-paylas hidden>${ikon('i-share')}Paylaş</button>` : ''}
      </div>
      <div class="oy-not" id="kartNot">Kart bu bilgisayarda üretilir; hiçbir yere gönderilmez.</div></div>`;
    m.hidden = false;
    kartCiz().then(() => $('[data-kart-indir]', m)?.focus());
  }

  let kartSoz = null; // son çizimin PNG'si (kopyala/paylaş için hazır bekler)
  async function kartCiz() {
    const tuval = $('#kartTuval');
    const v = kartVeri(S.secili);
    if (!tuval || !v) return;
    const [W, H] = KART_BOYUT[S.kartBoyut] || KART_BOYUT.linkedin;
    try {
      await Promise.all(['800 100px "Barlow Condensed"', '700 40px "Barlow Condensed"', '600 30px "Barlow Condensed"', '500 24px Barlow']
        .map((f) => document.fonts.load(f)));
    } catch { /* yazı tipi yoksa yedek yazı tipiyle çizilir */ }
    tuval.width = W; tuval.height = H;
    tuval.style.aspectRatio = `${W} / ${H}`;
    kartResim(tuval.getContext('2d'), W, H, v);
    kartSoz = new Promise((coz) => tuval.toBlob(coz, 'image/png'));
    const pd = $('[data-kart-paylas]');
    if (pd) {
      const b = await kartSoz;
      pd.hidden = !(b && navigator.canShare({ files: [new File([b], kartDosyaAdi(v), { type: 'image/png' })] }));
    }
  }
  const kartDosyaAdi = (v) => `cs-klip_${haritaAnahtar(v.harita) || 'mac'}_${(v.id.split('-')[1] || v.id).slice(0, 8)}_${S.kartBoyut}.png`;

  // Esports Yayın dili: harita renkli zemin + çapraz çizgiler, kesik köşeler, turuncu vurgu, skor bandı.
  function kartResim(c, W, H, v) {
    const R = HARITA_RENK[haritaAnahtar(v.harita)] || ['#56607a', '#1b2030', '#a3aec8'];
    const RENK = { or: '#ff6b1a', or2: '#ff8d45', text: '#eef1f6', muted: '#939cb0', dim: '#5f6779', line: '#252c3a', panel: '#12161f', iyi: '#3ddc8a', kotu: '#ff4d62', orta: '#cdd4e0', ct: '#5aa6ff' };
    const dikey = H > W;
    const u = W / 1200; // ölçek birimi
    const F = (agirlik, px, aile = 'disp') => `${agirlik} ${Math.round(px * u)}px ${aile === 'disp' ? '"Barlow Condensed","Arial Narrow",sans-serif' : 'Barlow,system-ui,sans-serif'}`;
    const yaz = (t, x, y, font, renk, hiza = 'left', ara = 0) => {
      c.font = font; c.fillStyle = renk; c.textAlign = hiza; c.textBaseline = 'alphabetic';
      if ('letterSpacing' in c) c.letterSpacing = `${(ara * u).toFixed(1)}px`;
      c.fillText(t, x, y);
      if ('letterSpacing' in c) c.letterSpacing = '0px';
    };
    const genislik = (t, font, ara = 0) => { c.font = font; if ('letterSpacing' in c) c.letterSpacing = `${(ara * u).toFixed(1)}px`; const w = c.measureText(t).width; if ('letterSpacing' in c) c.letterSpacing = '0px'; return w; };
    const sigdir = (t, agirlik, px, enFazla, ara = 0) => { // uzun ad sığana kadar yazı küçülür
      let f = F(agirlik, px);
      while (px > 12 && genislik(t, f, ara) > enFazla) { px -= 2; f = F(agirlik, px); }
      return f;
    };
    const kesik = (x, y, w, h, k, renk) => { // sağ üst köşesi kesik dikdörtgen
      c.beginPath(); c.moveTo(x, y); c.lineTo(x + w - k, y); c.lineTo(x + w, y + k); c.lineTo(x + w, y + h); c.lineTo(x, y + h); c.closePath();
      c.fillStyle = renk; c.fill();
    };
    const egik = (x, y, w, h, renk) => { // sağ kenarı eğik etiket
      c.beginPath(); c.moveTo(x, y); c.lineTo(x + w, y); c.lineTo(x + w - h * 0.35, y + h); c.lineTo(x, y + h); c.closePath(); c.fillStyle = renk; c.fill();
    };
    // zemin
    c.fillStyle = '#08090d'; c.fillRect(0, 0, W, H);
    const g = c.createLinearGradient(0, 0, W * 0.6, H);
    g.addColorStop(0, R[0]); g.addColorStop(1, R[1]);
    c.save();
    c.beginPath(); c.moveTo(0, 0); c.lineTo(W - 46 * u, 0); c.lineTo(W, 46 * u); c.lineTo(W, H); c.lineTo(0, H); c.closePath(); c.clip();
    c.fillStyle = g; c.globalAlpha = 0.85; c.fillRect(0, 0, W, H); c.globalAlpha = 1;
    const k = c.createLinearGradient(0, 0, W, dikey ? H * 0.3 : 0);
    k.addColorStop(0, 'rgba(8,9,13,.9)'); k.addColorStop(0.55, 'rgba(8,9,13,.5)'); k.addColorStop(1, 'rgba(8,9,13,.86)');
    c.fillStyle = k; c.fillRect(0, 0, W, H);
    const alt = c.createLinearGradient(0, H * 0.45, 0, H);
    alt.addColorStop(0, 'rgba(8,9,13,0)'); alt.addColorStop(1, 'rgba(8,9,13,.85)');
    c.fillStyle = alt; c.fillRect(0, 0, W, H);
    c.strokeStyle = 'rgba(255,255,255,.035)'; c.lineWidth = 2 * u;
    for (let x = -H; x < W + H; x += 16 * u) { c.beginPath(); c.moveTo(x, H); c.lineTo(x + H * 0.47, 0); c.stroke(); }
    // filigran: harita adı, içi boş
    c.font = F(800, dikey ? 300 : 330); c.textAlign = 'right'; c.textBaseline = 'alphabetic';
    c.strokeStyle = 'rgba(255,255,255,.08)'; c.lineWidth = 2 * u;
    c.strokeText(ENB(v.haritaAd), W + 12 * u, dikey ? 330 * u : 290 * u);
    c.restore();
    // kenar çizgisi + üst turuncu vurgu
    c.fillStyle = RENK.or; c.fillRect(0, 0, 220 * u, 6 * u);
    const M = 56 * u; // kenar boşluğu
    // üst şerit: etiket + tarih + marka
    const etiket = 'MAÇ SONU';
    const ew = genislik(etiket, F(700, 22), 3.5) + 30 * u;
    egik(M, 44 * u, ew + 10 * u, 38 * u, RENK.or);
    yaz(etiket, M + 14 * u, 71 * u, F(700, 22), '#160900', 'left', 3.5);
    const ust = [v.round ? `${v.round} ROUND` : '', v.tarih ? TR(tarihYaz(v.tarih, true)) : ''].filter(Boolean).join('  ·  ');
    yaz(ust, M + ew + 28 * u, 71 * u, F(700, 21), RENK.muted, 'left', 3);
    // marka (sağ üst)
    const csW = genislik('cs', F(800, 40)) + 26 * u;
    const klW = genislik('-klip', F(800, 40));
    const mx = W - M - klW - csW;
    c.beginPath(); c.moveTo(mx, 40 * u); c.lineTo(mx + csW, 40 * u); c.lineTo(mx + csW - 12 * u, 86 * u); c.lineTo(mx, 86 * u); c.closePath(); c.fillStyle = RENK.or; c.fill();
    yaz('cs', mx + 10 * u, 76 * u, F(800, 40), '#140800');
    yaz('-klip', mx + csW + 4 * u, 76 * u, F(800, 40), RENK.text);

    const sonucRenk = v.sonuc === 'G' ? RENK.iyi : v.sonuc === 'M' ? RENK.kotu : RENK.orta;
    const sonucYazi = { G: 'GALİBİYET', M: 'MAĞLUBİYET', B: 'BERABERE' }[v.sonuc];
    const o = v.ben;
    const rRenk = o.rating >= 1.1 ? RENK.iyi : o.rating < 0.9 ? RENK.kotu : RENK.orta;

    // --- skor bloğu ---
    const skorBlok = (x, y, hiza) => { // y: harita adının taban çizgisi
      const sw = genislik(sonucYazi, F(800, 26), 4) + 44 * u;
      const sx = hiza === 'center' ? x - sw / 2 : x;
      egik(sx, y - 196 * u, sw, 42 * u, sonucRenk);
      yaz(sonucYazi, sx + 16 * u, y - 166 * u, F(800, 26), v.sonuc === 'B' ? '#111' : v.sonuc === 'G' ? '#04170d' : '#1d0307', 'left', 4);
      yaz(ENB(v.haritaAd), x, y - 40 * u, sigdir(ENB(v.haritaAd), 800, 96, 560 * u, 3), RENK.text, hiza, 3);
      // skor: biz – onlar
      const sF = F(800, 170);
      const a = String(v.biz), b = String(v.onlar), tire = '–';
      const aw = genislik(a, sF), bw = genislik(b, sF), tw = genislik(tire, F(700, 110)) + 36 * u;
      const top = aw + tw + bw;
      const bx = hiza === 'center' ? x - top / 2 : x;
      const sy = y + 130 * u;
      yaz(a, bx, sy, sF, v.biz >= v.onlar ? '#ffffff' : RENK.muted);
      yaz(tire, bx + aw + tw / 2, sy - 30 * u, F(700, 110), RENK.dim, 'center');
      yaz(b, bx + aw + tw, sy, sF, v.onlar > v.biz ? '#ffffff' : RENK.muted);
      c.fillStyle = sonucRenk; c.fillRect(v.biz >= v.onlar ? bx : bx + aw + tw, sy + 14 * u, v.biz >= v.onlar ? aw : bw, 5 * u);
      const tk = `${ENB(v.bizAd)}  VS  ${ENB(v.onAd)}`;
      yaz(tk, hiza === 'center' ? x : bx, sy + 58 * u, sigdir(tk, 600, 22, 560 * u, 3), RENK.muted, hiza === 'center' ? 'center' : 'left', 3);
      return sw;
    };

    // --- oyuncu bloğu ---
    const kutucuk = (x, y, w, h, ad, deger, renk = RENK.text, birim = '', px = 54) => {
      kesik(x, y, w, h, 14 * u, 'rgba(14,17,24,.88)');
      c.fillStyle = 'rgba(255,255,255,.06)'; c.fillRect(x, y, w - 14 * u, 1.5 * u);
      yaz(ad, x + 18 * u, y + 34 * u, F(700, 19), RENK.muted, 'left', 3);
      const dF = sigdir(deger, 800, px, w - 36 * u - (birim ? 30 * u : 0));
      yaz(deger, x + 18 * u, y + h - 20 * u, dF, renk);
      if (birim) yaz(birim, x + 22 * u + genislik(deger, dF), y + h - 20 * u, F(700, 30), RENK.muted);
    };
    const kd = `${o.kill ?? 0}/${o.death ?? 0}/${o.assist ?? 0}`;
    const ck = o.cok_kill || {};
    const kutular = [
      ['ADR', sayi(o.adr, 1), (o.adr ?? 0) >= 85 ? RENK.iyi : (o.adr ?? 0) < 65 ? RENK.kotu : RENK.text],
      ['KAST', sayi(o.kast, 1), (o.kast ?? 0) >= 75 ? RENK.iyi : (o.kast ?? 0) < 65 ? RENK.kotu : RENK.text, '%'],
      ['K / D / A', kd, RENK.text],
      ['HS', sayi(o.hs_yuzde, 1), RENK.text, '%'],
      ['K/D', sayi(o.kd, 2), (o.kd ?? 0) >= 1.1 ? RENK.iyi : (o.kd ?? 0) < 0.9 ? RENK.kotu : RENK.text],
      ['AÇILIŞ', `${o.acilis_kill ?? 0}–${o.acilis_death ?? 0}`, RENK.text],
    ];
    const cokluSatir = (x, y, w, h) => {
      const l = [['2', '2K'], ['3', '3K'], ['4', '4K'], ['5', 'ACE']];
      const gap = 10 * u, bw = (w - gap * 3) / 4;
      l.forEach(([key, ad], i) => {
        const n = ck[key] || 0, bx = x + i * (bw + gap);
        c.fillStyle = n ? 'rgba(255,107,26,.16)' : 'rgba(14,17,24,.82)'; c.fillRect(bx, y, bw, h);
        c.strokeStyle = n ? 'rgba(255,107,26,.6)' : RENK.line; c.lineWidth = 1.5 * u; c.strokeRect(bx + 0.75 * u, y + 0.75 * u, bw - 1.5 * u, h - 1.5 * u);
        yaz(String(n), bx + bw / 2, y + h * 0.58, F(800, 40), n ? RENK.text : RENK.dim, 'center');
        yaz(ad, bx + bw / 2, y + h * 0.86, F(700, 17), n ? RENK.or2 : RENK.dim, 'center', 2);
      });
    };
    const rozetler = (x, y, hiza) => {
      const l = [[`LOBİDE ${v.sira}. / ${v.lobi}`, 'rgba(32,38,52,.95)', RENK.muted]];
      if (v.mvp) l.unshift(['MAÇIN YILDIZI', '#ffb020', '#1d1100']);
      let w = l.reduce((a, [t]) => a + genislik(t, F(700, 19), 2.5) + 28 * u + 8 * u, -8 * u);
      let cx = hiza === 'center' ? x - w / 2 : x;
      l.forEach(([t, bg, fg]) => {
        const tw = genislik(t, F(700, 19), 2.5) + 28 * u;
        c.fillStyle = bg; c.fillRect(cx, y, tw, 34 * u);
        yaz(t, cx + 14 * u, y + 24 * u, F(700, 19), fg, 'left', 2.5);
        cx += tw + 8 * u;
      });
    };

    if (!dikey) {
      // yatay (1200×630): solda skor, sağda oyuncu paneli
      const sw = skorBlok(M, 300 * u, 'left');
      rozetler(M + sw + 12 * u, 108 * u, 'left');
      const px = 630 * u, pw = W - M - px, py = 118 * u;
      kesik(px, py, pw, 440 * u, 26 * u, 'rgba(8,9,13,.72)');
      c.fillStyle = rRenk; c.fillRect(px, py, 5 * u, 440 * u);
      yaz(o.ad || '', px + 30 * u, py + 62 * u, sigdir(o.ad || '', 800, 50, pw - 60 * u), RENK.text);
      yaz(sayi(o.rating, 2), px + 30 * u, py + 170 * u, F(800, 118), rRenk);
      const rw = genislik(sayi(o.rating, 2), F(800, 118));
      yaz('RATING', px + 46 * u + rw, py + 128 * u, F(700, 24), RENK.muted, 'left', 4);
      yaz('HLTV 1.0 TARZI', px + 46 * u + rw, py + 160 * u, F(600, 17), RENK.dim, 'left', 2.5);
      const gx = px + 30 * u, gy = py + 196 * u, gw = (pw - 60 * u - 2 * 10 * u) / 3, gh = 104 * u;
      kutular.forEach(([ad, d, r, b], i) => kutucuk(gx + (i % 3) * (gw + 10 * u), gy + Math.floor(i / 3) * (gh + 10 * u), gw, gh, ad, d, r, b));
      // alt bant: çoklu kill + rozetler
      cokluSatir(M, H - 124 * u, 520 * u, 72 * u);
    } else {
      // dikey (1080×1350): üstte skor, ortada oyuncu, altta kutular
      skorBlok(W / 2, 420 * u, 'center');
      const py = 650 * u;
      kesik(M, py, W - 2 * M, 250 * u, 26 * u, 'rgba(8,9,13,.72)');
      c.fillStyle = rRenk; c.fillRect(M, py, 6 * u, 250 * u);
      yaz(o.ad || '', M + 36 * u, py + 74 * u, sigdir(o.ad || '', 800, 58, 560 * u), RENK.text);
      rozetler(M + 36 * u, py + 100 * u, 'left');
      const rs = sayi(o.rating, 2);
      yaz(rs, W - M - 36 * u, py + 206 * u, F(800, 150), rRenk, 'right');
      const rw = genislik(rs, F(800, 150));
      yaz('RATING', W - M - 52 * u - rw, py + 190 * u, F(700, 26), RENK.muted, 'right', 4);
      const gy = py + 280 * u, gap = 12 * u, gw = (W - 2 * M - 2 * gap) / 3, gh = 160 * u;
      kutular.forEach(([ad, d, r, b], i) => kutucuk(M + (i % 3) * (gw + gap), gy + Math.floor(i / 3) * (gh + gap), gw, gh, ad, d, r, b, 76));
      cokluSatir(M, gy + 2 * (gh + gap) + 20 * u, W - 2 * M, 120 * u);
    }
    // alt satır
    c.fillStyle = 'rgba(14,17,24,.9)'; c.fillRect(0, H - 38 * u, W, 38 * u);
    c.fillStyle = RENK.or; c.fillRect(0, H - 38 * u, 6 * u, 38 * u);
    yaz('CS2 DEMO ANALİZİ', M, H - 13 * u, F(700, 18), RENK.muted, 'left', 3.5);
    yaz('CS-KLIP', W - M, H - 13 * u, F(800, 18), RENK.dim, 'right', 3.5);
  }

  async function kartIndir() {
    const v = kartVeri(S.secili);
    const b = kartSoz && await kartSoz;
    if (!v || !b) { bildir('Kart henüz hazır değil.', 'hata'); return; }
    const a = document.createElement('a');
    a.href = URL.createObjectURL(b);
    a.download = kartDosyaAdi(v);
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    bildir(`${a.download} indirildi.`, 'basari');
  }
  async function kartKopyala() {
    if (!navigator.clipboard || !navigator.clipboard.write || !window.ClipboardItem) {
      bildir('Tarayıcın görsel kopyalamayı desteklemiyor; “PNG indir”i kullan.', 'hata');
      return;
    }
    try {
      await navigator.clipboard.write([new ClipboardItem({ 'image/png': kartSoz.then((b) => b || Promise.reject(new Error('boş'))) })]);
      bildir('Kart panoya kopyalandı; LinkedIn ya da Instagram gönderisine yapıştırabilirsin.', 'basari');
    } catch (e) {
      bildir('Görsel kopyalanamadı (' + (e && e.message ? e.message : 'izin verilmedi') + '); “PNG indir”i kullan.', 'hata');
    }
  }
  async function kartPaylas() {
    const v = kartVeri(S.secili);
    const b = kartSoz && await kartSoz;
    if (!v || !b) return;
    try {
      await navigator.share({ files: [new File([b], kartDosyaAdi(v), { type: 'image/png' })], title: `${v.haritaAd} ${v.biz}–${v.onlar}` });
    } catch (e) {
      if (e && e.name !== 'AbortError') bildir('Paylaşılamadı: ' + e.message, 'hata');
    }
  }

  document.addEventListener('click', (e) => {
    const t = e.target;
    if (t.closest('a[href="#kariyer"]')) {
      e.preventDefault();
      if (location.hash.slice(1) === KARIYER) kariyerAc(); else location.hash = KARIYER;
      return;
    }
    if (t.closest('[data-kr-yenile]')) { kariyerYukle(true); return; }
    const km = t.closest('[data-kr-metrik]');
    if (km) {
      S.krMetrik = km.dataset.krMetrik;
      $$('[data-kr-metrik]').forEach((b) => { b.classList.toggle('aktif', b === km); b.setAttribute('aria-pressed', String(b === km)); });
      grafikCiz();
      return;
    }
    const ka = t.closest('[data-kart-ac]');
    if (ka) { kartAc(ka); return; }
    const kb = t.closest('[data-kart-boyut]');
    if (kb) {
      S.kartBoyut = kb.dataset.kartBoyut;
      $$('[data-kart-boyut]').forEach((b) => { b.classList.toggle('aktif', b === kb); b.setAttribute('aria-checked', String(b === kb)); });
      kartCiz();
      return;
    }
    if (t.closest('[data-kart-indir]')) { kartIndir(); return; }
    if (t.closest('[data-kart-kopyala]')) { kartKopyala(); return; }
    if (t.closest('[data-kart-paylas]')) kartPaylas();
  });
  document.addEventListener('keydown', (e) => {
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('tr.kr-satir[data-demo]')) {
      e.preventDefault();
      demoSec(e.target.dataset.demo);
    }
  });

  /* ======== olaylar ======== */
  function siralaDegis(th) {
    const k = th.dataset.sira;
    S.sira = S.sira.k === k ? { k, az: !S.sira.az } : { k, az: k !== 'ad' };
    tablolariCiz();
    const yeni = $(`#tablolar th[data-sira="${k}"]`);
    if (yeni && document.activeElement === document.body) yeni.focus();
  }
  document.addEventListener('click', (e) => {
    const t = e.target;
    const demo = t.closest('[data-demo]');
    if (demo) { demoSec(demo.dataset.demo); return; }
    // "En iyi anlarım": hash zaten #en-iyi ise (çekmeceden tekrar tıklama) görünümü yine aç
    if (t.closest('a[href="#en-iyi"]')) {
      e.preventDefault();
      if (location.hash.slice(1) === EN_IYI) enIyiAc(); else location.hash = EN_IYI;
      return;
    }
    if (t.closest('[data-maca-don]')) { macaDon(); return; }
    if (t.closest('[data-ei-yenile]')) { enIyiYukle(true); return; }
    const eiGit = t.closest('[data-ei-git]');
    if (eiGit) { const h = document.getElementById(eiGit.dataset.eiGit); if (h) h.scrollIntoView({ behavior: kaydir() }); return; }
    const eiH = t.closest('[data-ei-harita]');
    if (eiH) { S.eiHarita = eiH.dataset.eiHarita; vitrinCiz(); return; }
    const eiA = t.closest('[data-ei-adet]');
    if (eiA) { S.eiAdet = +eiA.dataset.eiAdet; vitrinCiz(); return; }
    const mjA = t.closest('[data-mj-adet]');
    if (mjA) { if (!mjA.disabled) { S.mjAdet = +mjA.dataset.mjAdet; montajCiz(); } return; }
    if (t.closest('#montajYap')) { montajYap(); return; }
    const mjO = t.closest('[data-mj-oynat]');
    if (mjO) { montajOynat(mjO); return; }
    const eiO = t.closest('[data-ei-oynat]');
    if (eiO) { vitrinOynat(+eiO.dataset.eiOynat, eiO); return; }
    const eiK = t.closest('.ei-klip');
    if (eiK && !t.closest('a, button, .ei-git')) { vitrinOynat(+eiK.dataset.ei, $('[data-ei-oynat]', eiK)); return; }
    // bölüm bağlantıları adres çubuğundaki #demo-id'yi bozmasın
    const nav = t.closest('#bolumNav a');
    if (nav) {
      e.preventDefault();
      const hedef = document.getElementById(nav.getAttribute('href').slice(1));
      if (hedef) hedef.scrollIntoView({ behavior: kaydir() });
      return;
    }
    if (t.closest('.marka')) { e.preventDefault(); scrollTo({ top: 0, behavior: kaydir() }); return; }
    const th = t.closest('th[data-sira]');
    if (th) { siralaDegis(th); return; }
    const n = t.closest('.secim button[data-n]');
    if (n && !n.disabled) { S.enIyi = +n.dataset.n; $$('.secim button').forEach((b) => { b.classList.toggle('aktif', b === n); b.setAttribute('aria-checked', String(b === n)); }); kayitCiz(); return; }
    if (t.closest('#kaydet')) { kaydet(); return; }
    if (t.closest('#kontrolYenile')) { kontrolYenile(true); return; }
    if (t.closest('#durumHap')) {
      const kk = $('#klipler');
      if (kk) kk.scrollIntoView({ behavior: kaydir() });
      else bildir(S.kontrol ? (S.kontrol.hazir ? 'Kayda hazır.' : (S.kontrol.sorunlar || []).join(' ')) : 'Kontrol ediliyor…', S.kontrol && !S.kontrol.hazir ? 'hata' : '');
      return;
    }
    const tekrar = t.closest('[data-tekrar]');
    if (tekrar) { demoAc(tekrar.dataset.tekrar); return; }
    if (t.closest('[data-klip-tekrar]')) { klipleriYukle(S.secili, S.istekNo); klipleriCiz(); return; }
    const oy = t.closest('[data-oynat]');
    if (oy) { oynaticiAc(+oy.dataset.oynat, oy); return; }
    const resim = t.closest('.klip.kayitli .kl-resim');
    if (resim) { const b = $('[data-oynat]', resim); if (b) oynaticiAc(+b.dataset.oynat, b); return; }
    if (t.closest('[data-kapat]') || t === $('#modal')) { oynaticiKapat(); return; }
    if (t.closest('#oyDugme')) { oynatDegistir(); return; }
    if (t.closest('#oyTam')) {
      const v = $('#oyVideo');
      if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
      else if (v && v.requestFullscreen) v.requestFullscreen().catch(() => {});
      return;
    }
    const cubuk = t.closest('#oyCubuk');
    if (cubuk) { const r = cubuk.getBoundingClientRect(); oynatAtla(sinirla((e.clientX - r.left) / r.width, 0, 1)); return; }
    if (t.closest('#menuDugme')) { menuAc(!$('#kenar').classList.contains('acik')); return; }
    if (t.closest('#perde')) { menuAc(false); return; }
    if (t.closest('#ustYukle') || t.closest('#bosYukle')) { $('#dosyaSec').click(); return; }
    const yen = t.closest('#yenile');
    if (yen) {
      yen.classList.remove('donuyor'); void yen.offsetWidth; yen.classList.add('donuyor');
      demolariYenile().then((ok) => { if (ok) bildir('Demo listesi yenilendi.'); });
      kontrolYenile();
    }
  });
  document.addEventListener('keydown', (e) => {
    const modalAcik = !$('#modal').hidden;
    if (e.key === 'Escape') { if (modalAcik) oynaticiKapat(); else menuAc(false); return; }
    if (modalAcik) {
      const dugmede = e.target.closest && e.target.closest('button, a');
      if (e.key === ' ' && !dugmede) { e.preventDefault(); oynatDegistir(); return; }
      if (e.key === 'ArrowLeft') { e.preventDefault(); oynatAtla(null, -5); return; }
      if (e.key === 'ArrowRight') { e.preventDefault(); oynatAtla(null, 5); return; }
    }
    if ((e.key === 'Enter' || e.key === ' ') && e.target === $('#birak')) { e.preventDefault(); $('#dosyaSec').click(); return; }
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('th[data-sira]')) { e.preventDefault(); siralaDegis(e.target); }
  });
  $('#dosyaSec').addEventListener('change', (e) => { if (e.target.files.length) dosyalariAl(e.target.files); e.target.value = ''; });

  // sürükle-bırak: hem kenar alanı hem tüm pencere
  const birak = $('#birak'), perde = $('#birakPerde');
  let surukle = 0;
  const dosyaMi = (e) => [...(e.dataTransfer?.types || [])].includes('Files');
  addEventListener('dragenter', (e) => { if (!dosyaMi(e)) return; e.preventDefault(); surukle++; perde.classList.add('acik'); });
  addEventListener('dragover', (e) => { if (!dosyaMi(e)) return; e.preventDefault(); e.dataTransfer.dropEffect = 'copy'; birak.classList.toggle('ustunde', birak.contains(e.target)); });
  addEventListener('dragleave', (e) => { if (!dosyaMi(e)) return; surukle = Math.max(0, surukle - 1); if (!surukle) { perde.classList.remove('acik'); birak.classList.remove('ustunde'); } });
  addEventListener('drop', (e) => {
    if (!dosyaMi(e)) return;
    e.preventDefault();
    surukle = 0; perde.classList.remove('acik'); birak.classList.remove('ustunde');
    if (e.dataTransfer.files.length) dosyalariAl(e.dataTransfer.files);
  });
  addEventListener('hashchange', hashtenAc);

  /* ======== başlat ======== */
  async function basla() {
    if (ORNEK_MODU) {
      $('.marka').insertAdjacentHTML('afterend', '<span class="ornek-rozet" title="Veriler arayuz/ornek.json dosyasından; sunucuya istek gitmez.">Örnek veri</span>');
      document.title = 'cs-klip (örnek) — Maç analizi';
    }
    kontrolCiz();
    listeCiz();
    kontrolYenile();
    setInterval(() => { if (document.visibilityState === 'visible') kontrolYenile(); }, KONTROL_MS);
    const ok = await demolariYenile();
    if (location.hash.length > 1) { hashtenAc(); return; }
    const ilk = S.demolar.find((d) => d.analiz_edildi);
    if (ilk) {
      history.replaceState(null, '', '#' + encodeURIComponent(ilk.id));
      demoAc(ilk.id);
    } else if (ok) bosCiz();
    else hataCiz('Demolar alınamadı', 'Sunucuya ulaşılamadı. cs-klip sunucusu çalışıyor mu?', null);
  }

  basla();
})();
