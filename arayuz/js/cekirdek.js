/* cs-klip arayüzü — sabitler, durum, yardımcılar, API istemcisi.
   Klasik betik: index.html'deki sırayla yüklenir, üst düzey adlar öteki dosyalarla ortaktır. */
'use strict';

const ORNEK_MODU = new URLSearchParams(location.search).get('ornek') === '1';

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
  // Başka oyuncunun highlight'ları (skor tablosundan seçilir) ve maçtaki herkesin en iyi anı
  oyuncu: {},          // demo id -> seçili oyuncunun steamid'i (yoksa varsayılan oyuncu)
  herkes: {},          // demo id -> {oyuncular} (GET /api/demo/<id>/herkes)
  herkesHata: {},
  eiOyuncu: '',        // vitrin oyuncu filtresi: '' = sen, '*' = herkes, yoksa klip adındaki etiket
  mjAdet: 10,
  // Montaj türü: 'sade' (yeniden kodlamadan birleştir) | 'paylasim' (TikTok/Reels/LinkedIn'e hazır video)
  mjSec: { tur: 'sade', dikey: true, yerlesim: 'bulanik', kart: true, etiket: true, kalite: '1080p', sikistirma: 'dengeli', hedefMb: '', muzik: '' },
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
const AYARLAR = 'ayarlar';

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
// Seçili oyuncu (null = varsayılan oyuncu) ve onun istatistik satırı
const secOyuncu = (id) => S.oyuncu[id] || null;
const oyuncuBul = (s, sid) => (s && sid ? (s.oyuncular || []).find((o) => String(o.steamid) === String(sid)) || null : null);
const gosterilen = (id) => oyuncuBul(S.demo[id], secOyuncu(id)) || (S.demo[id] ? benBul(S.demo[id]) : null);
// Klip adındaki oyuncu etiketi (analyze.player_tag ile aynı kural): yalnız harf ve rakam
const oyuncuEtiket = (ad, sid = '') => [...String(ad || '')].filter((c) => /[\p{L}\p{N}]/u.test(c)).join('').slice(0, 20) || String(sid).slice(-8) || 'oyuncu';
const klipYol = (id, sid = secOyuncu(id)) => demoYol(id, '/klipler') + (sid ? `?oyuncu=${encodeURIComponent(sid)}` : '');
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
// Yarı uzunluğu: rekabetçi MR12 (12 round), wingman MR8 (8 round). Takım başına oyuncu sayısından çıkarılır.
const yariUzunlugu = (s) => {
  const n = {};
  (s && s.oyuncular || []).forEach((o) => { n[o.takim] = (n[o.takim] || 0) + 1; });
  const enCok = Math.max(0, ...Object.values(n));
  return enCok && enCok <= 2 ? 8 : 12;
};
const yariNo = (no, y = 12) => (no <= y ? 0 : no <= 2 * y ? 1 : 2 + Math.floor((no - 2 * y - 1) / 3));
const yariAd = (g) => (g === 0 ? '1. yarı' : g === 1 ? '2. yarı' : `Uzatma ${Math.floor((g - 2) / 2) + 1} · ${((g - 2) % 2) + 1}. yarı`);
function taraflar(s) {
  const y = yariUzunlugu(s);
  const m = { y };  // y: yarı uzunluğu (takimTaraf kullanır)
  const R = s.roundlar || [];
  R.forEach((r) => {
    const g = yariNo(r.no, y);
    const w = kazananTaraf(r);
    if (m[g] || !w) return;
    m[g] = r.kazanan_takim === 0 ? w : karsi(w);
  });
  const son = Math.max(0, ...R.map((r) => yariNo(r.no, y)));
  for (let g = 0; g <= son; g++) if (!m[g]) m[g] = g === 0 ? (m[1] ? karsi(m[1]) : 't') : karsi(m[g - 1]);
  return m;
}
const takimTaraf = (m, takim, no) => { const x = m[yariNo(no, m.y)] || 't'; return takim === 0 ? x : karsi(x); };
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
  // Zaman aşımı: ilk analiz ve montaj dakikalar sürebilir; sunucu takılırsa sayfa sonsuza dek beklemesin.
  const iptal = new AbortController();
  const sure = setTimeout(() => iptal.abort(), API_ZAMAN_ASIMI_MS);
  try {
    yanit = await fetch(yol, {
      method: secenek.method || 'GET',
      headers: secenek.body ? { 'Content-Type': 'application/json' } : undefined,
      body: secenek.body,
      cache: 'no-store',
      signal: iptal.signal,
    });
  } catch {
    clearTimeout(sure);
    if (iptal.signal.aborted) throw new Error(`Sunucu ${API_ZAMAN_ASIMI_MS / 60000} dakikadır yanıt vermiyor; arayüz sunucusunu yeniden başlatmayı dene.`);
    throw new Error('Sunucuya ulaşılamadı. cs-klip sunucusu çalışıyor mu?');
  }
  let metin;
  try {
    metin = await yanit.text();
  } catch {
    throw new Error('Sunucu yanıtı yarıda kesildi.');
  } finally {
    clearTimeout(sure);
  }
  let veri = null;
  try { veri = metin ? JSON.parse(metin) : null; } catch { /* JSON değil */ }
  if (!yanit.ok) {
    const h = new Error((veri && veri.hata) || `Sunucu hatası (HTTP ${yanit.status}).`);
    h.status = yanit.status;
    h.veri = veri; // ör. /api/ayarlar alan hataları: veri.alanlar
    throw h;
  }
  if (veri === null && metin) throw new Error('Sunucudan geçersiz yanıt geldi.');
  return zararsiz(veri);
}
const API_ZAMAN_ASIMI_MS = 5 * 60 * 1000;
// 404: sunucu bu ucu tanımıyor (arayüz güncellendi, sunucu eski sürümle açık kaldı).
const SUNUCU_ESKI = 'Sunucu bu isteği tanımıyor (HTTP 404). Arayüz sunucusu bu özellikten önce başlatılmış olabilir: kapatıp arayuz.bat ile yeniden başlat.';
// Sunucu yanıtı diskteki .stats.json / .highlights.json'dan gelir; bu dosyaları başkası da koyabilir.
// Şablonlarda sayı diye basılan alanlara HTML sızmasın: metinlerde < > " zararsız benzerleriyle değişir.
const ZARARSIZ = { '<': '‹', '>': '›', '"': '″' };
const zararsiz = (v) => (typeof v === 'string' ? v.replace(/[<>"]/g, (c) => ZARARSIZ[c])
  : Array.isArray(v) ? v.map(zararsiz)
    : v && typeof v === 'object' ? Object.fromEntries(Object.entries(v).map(([k, x]) => [zararsiz(k), zararsiz(x)]))
      : v);
const demoYol = (id, ek = '') => `/api/demo/${encodeURIComponent(id)}${ek}`;

let yuklemeXhr = null;
function yukleXhr(dosya, ilerleme) {
  if (ORNEK_MODU) return ornekYukleme(dosya, ilerleme);
  return new Promise((coz, red) => {
    const xhr = new XMLHttpRequest();
    yuklemeXhr = xhr; // "İptal" düğmesi için
    xhr.onloadend = () => { if (yuklemeXhr === xhr) yuklemeXhr = null; };
    xhr.open('POST', '/api/yukle');
    xhr.setRequestHeader('X-Dosya-Adi', encodeURIComponent(dosya.name));
    xhr.setRequestHeader('Content-Type', 'application/octet-stream');
    xhr.upload.onprogress = (e) => { if (e.lengthComputable) ilerleme(e.loaded, e.total); };
    xhr.onload = () => {
      let veri = null;
      try { veri = JSON.parse(xhr.responseText); } catch { /* boş */ }
      if (xhr.status >= 200 && xhr.status < 300) coz(zararsiz(veri || {}));
      else red(new Error((veri && veri.hata) || `Yükleme başarısız (HTTP ${xhr.status}).`));
    };
    xhr.onerror = () => red(new Error('Yükleme sırasında bağlantı koptu.'));
    xhr.onabort = () => red(new Error('Yükleme iptal edildi.'));
    xhr.send(dosya);
  });
}
