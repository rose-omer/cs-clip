/* cs-klip arayüzü — Maç kartı (paylaşım PNG'si, canvas).
   Klasik betik: index.html'deki sırayla yüklenir, üst düzey adlar öteki dosyalarla ortaktır. */
'use strict';

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
