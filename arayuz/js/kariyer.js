/* cs-klip arayüzü — Kariyer (#kariyer): maçlar arası gelişim.
   Klasik betik: index.html'deki sırayla yüklenir, üst düzey adlar öteki dosyalarla ortaktır. */
'use strict';

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
  gorunumAc(KARIYER);
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
  kutu.innerHTML = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(m.duz)}: ${l.length} maç, son 10 ortalaması ${esc(sayi(kayan[kayan.length - 1], m.o))}. Maç maç değerler aşağıdaki tabloda.">${s}</svg>`;
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
