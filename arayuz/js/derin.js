/* cs-klip arayüzü — derin analiz: ısı haritası, utility, nişan.
   Klasik betik: index.html'deki sırayla yüklenir, üst düzey adlar öteki dosyalarla ortaktır. */
'use strict';

/* ======== derin analiz: ısı haritası, utility, nişan (stats.json "derin" bloğu, analiz_derin.py) ======== */
const DERIN_SURUM = 1;
const DR = { tur: 'hepsi', taraf: 'hepsi', gorunum: 'isi', hesaplaniyor: new Set(), hata: {} };
const DR_BOMBA = [['flas', 'Flaş', '#e9edf4'], ['smoke', 'Smoke', '#8b97ad'], ['molotof', 'Molotof', 'var(--or)'], ['he', 'HE', 'var(--iyi)'], ['decoy', 'Decoy', '#56607a']];
const yuzdeYaz = (x) => (x == null ? '–' : '%' + sayi(x, 0));
const derinVar = (s) => { const d = s && s.derin; return !!(d && typeof d === 'object' && (d.surum || 0) >= DERIN_SURUM && !d.hata); };
const drBas = (no, ad, ek) => `<div class="bas"><h2><span class="bas-no"><span>${no}</span></span>${ad}</h2><span class="bas-ek">${ek}</span></div>`;

function derinHtml(s) {
  const id = S.secili;
  if (!derinVar(s)) {
    const d = s.derin;
    const sur = DR.hesaplaniyor.has(id);
    const neden = d && d.hata ? `Önceki deneme başarısız oldu: ${esc(d.hata)}`
      : 'Bu maçın istatistikleri derin analizden önceki bir sürümle hesaplanmış (<code>stats.json</code> içinde <code>derin</code> bloğu yok).';
    return `<div id="derin"><section class="panel giris" id="isiHarita" style="--d:300ms">
      ${drBas('07', 'Derin analiz', 'Isı haritası · Utility · Nişan')}
      <div class="dr-eksik">
        <p>${neden} Isı haritası, utility ve nişan metrikleri için demo yeniden hesaplanmalı; skor tablosu ve klipler değişmez.</p>
        ${DR.hata[id] ? `<p class="renk-kotu">${esc(DR.hata[id])}</p>` : ''}
        <button class="btn-ikincil" type="button" data-dr-yenile ${sur ? 'disabled' : ''}>${ikon('i-refresh')}${sur ? 'Hesaplanıyor…' : 'Yeniden hesapla'}</button>
        ${sur ? '<p class="soluk" id="drSure" aria-live="off">10–40 saniye sürebilir.</p>' : ''}
        ${sur ? '<small>Demo yeniden okunuyor; büyük demolarda 10–40 saniye sürebilir.</small>' : ''}
      </div></section></div>`;
  }
  const d = s.derin;
  return `<div id="derin">
    <section class="panel giris" id="isiHarita" style="--d:300ms">
      ${drBas('07', 'Isı haritası', `${esc(haritaAd(s.harita) || '')} · ${EN('kill')} ve ölüm konumların`)}
      <div class="dr-harita">
        <div class="dr-tuval" id="drTuval"><canvas id="drZemin" aria-hidden="true"></canvas><canvas id="drIsi" aria-hidden="true"></canvas>
          <svg id="drNokta" viewBox="0 0 1000 1000" role="img" aria-label="Harita üstünde kill ve ölüm noktaları"></svg></div>
        <div class="dr-yan" id="drYan"></div>
      </div>
    </section>
    <div class="ikili">
      <section class="panel giris" id="utility" style="--d:340ms">
        ${drBas('08', 'Utility', `${d.utility ? sayi(d.utility.round_basi, 2) : '–'} bomba / round`)}
        ${utilityHtml(d.utility || {})}
      </section>
      <section class="panel giris" id="nisan" style="--d:380ms">
        ${drBas('09', 'Nişan', 'isabet · sprey · tepki')}
        ${nisanHtml(d.nisan || {})}
      </section>
    </div>
    <p class="dr-not">${(d.notlar || []).map(esc).join(' ')} Crosshair yerleşimi ve counter-strafe bu sürümde hesaplanmıyor.</p>
  </div>`;
}

function drNoktalar(s) {
  const T = taraflar(s), biz = s.benim_takim ?? 0;
  return ((s.derin.harita || {}).noktalar || []).map((p) => ({ ...p, taraf: takimTaraf(T, biz, p.round) }))
    .filter((p) => (DR.tur === 'hepsi' || p.tur === DR.tur) && (DR.taraf === 'hepsi' || p.taraf === DR.taraf));
}

function drSecim(ad, anahtar, secenekler) {
  return `<div class="dr-secim"><span class="kayit-et">${ad}</span><div class="secim" role="radiogroup" aria-label="${ad}">${secenekler.map(([v, y]) =>
    `<button type="button" role="radio" data-dr-${anahtar}="${v}" class="${DR[anahtar] === v ? 'aktif' : ''}" aria-checked="${DR[anahtar] === v}">${y}</button>`).join('')}</div></div>`;
}

function drYanCiz(s, pts) {
  const yan = $('#drYan');
  if (!yan) return;
  const h = s.derin.harita;
  const k = pts.filter((p) => p.tur === 'kill'), o = pts.filter((p) => p.tur === 'olum');
  const hs = k.filter((p) => p.hs).length;
  const say = {};
  k.forEach((p) => { say[p.silah] = (say[p.silah] || 0) + 1; });
  const enCok = Object.entries(say).sort((a, b) => b[1] - a[1]).slice(0, 3);
  const zemin = h.zemin ? 'Zemin: maçtaki tüm oyuncuların konumlarından çizildi (radar görseli kullanılmıyor).' : 'Zemin verisi yok; noktalar konumlarına göre ölçeklendi.';
  yan.innerHTML = `
    ${drSecim('Göster', 'tur', [['hepsi', 'Hepsi'], ['kill', EN('Kill')], ['olum', 'Ölüm']])}
    ${drSecim('Taraf', 'taraf', [['hepsi', 'İkisi'], ['t', 'T'], ['ct', 'CT']])}
    ${drSecim('Görünüm', 'gorunum', [['isi', 'Isı'], ['nokta', 'Nokta']])}
    <div class="dr-ozet">
      <div><b class="renk-iyi">${k.length}</b>${EN('kill')}<small>${hs} ${EN('headshot')}</small></div>
      <div><b class="renk-kotu">${o.length}</b>ölüm<small>${o.filter((p) => p.rx != null).length} rakip konumlu</small></div>
    </div>
    ${enCok.length ? `<div class="dr-silahlar">${enCok.map(([w, n]) => `<span><b>${n}</b>${esc(silahAd(w))}</span>`).join('')}</div>` : ''}
    <div class="lejant dr-lejant"><span><i class="dr-l-k"></i>${EN('Kill')} (senin konumun)</span><span><i class="dr-l-hs"></i>${EN('Headshot')}</span>
      <span><i class="dr-l-o"></i>Ölüm</span><span><i class="dr-l-c"></i>Rakip konumu (üzerine gel)</span></div>
    <p class="dr-kaynak">${zemin}${h.radar ? '' : ' Bu harita için radar tablosu yok.'}</p>`;
}

function drZeminCiz(z, zemin, P) {
  z.fillStyle = '#0a0d13';
  z.fillRect(0, 0, P, P);
  z.strokeStyle = 'rgba(255,255,255,.035)';
  z.lineWidth = 1;
  for (let i = 1; i < 8; i++) { const q = Math.round(i * P / 8) + 0.5; z.beginPath(); z.moveTo(q, 0); z.lineTo(q, P); z.moveTo(0, q); z.lineTo(P, q); z.stroke(); }
  if (!zemin || !zemin.bitler) return;
  const n = zemin.n, ham = atob(zemin.bitler);
  const off = document.createElement('canvas');
  off.width = off.height = n;
  const oc = off.getContext('2d');
  const im = oc.createImageData(n, n);
  for (let i = 0; i < n * n; i++) {
    if (!((ham.charCodeAt(i >> 3) >> (i & 7)) & 1)) continue;
    im.data.set([58, 68, 90, 255], i * 4);
  }
  oc.putImageData(im, 0, 0);
  z.imageSmoothingEnabled = true;
  z.save();
  z.filter = `blur(${Math.max(1, P / n * 0.9)}px)`;
  z.globalAlpha = 0.9;
  z.drawImage(off, 0, 0, P, P);
  z.restore();
  z.globalAlpha = 0.55;
  z.drawImage(off, 0, 0, P, P);
  z.globalAlpha = 1;
}

function derinCiz() {
  const s = S.demo[S.secili];
  const kutu = $('#drTuval');
  if (!kutu || !derinVar(s)) return;
  const h = s.derin.harita || {}, k = h.kutu || { x0: 0, x1: 1, y0: 0, y1: 1 };
  const W = kutu.clientWidth;
  if (!W) return;
  const P = Math.round(W * Math.min(devicePixelRatio || 1, 2));
  const zc = $('#drZemin'), ic = $('#drIsi');
  [zc, ic].forEach((c) => { c.width = P; c.height = P; });
  const z = zc.getContext('2d');
  drZeminCiz(z, h.zemin, P); // kutu radarla aynı alan: radar görseli eklenirse (1024x1024) birebir oturur

  const pts = drNoktalar(s);
  const pr = (x, y) => [(x - k.x0) / (k.x1 - k.x0), (k.y1 - y) / (k.y1 - k.y0)];
  const c = ic.getContext('2d');
  c.clearRect(0, 0, P, P);
  if (DR.gorunum === 'isi') {
    c.globalCompositeOperation = 'lighter';
    const r = P * 0.055;
    pts.forEach((p) => {
      const [u, v] = pr(p.x, p.y);
      const renk = p.tur === 'kill' ? '61,220,138' : '255,77,98';
      const g = c.createRadialGradient(u * P, v * P, 0, u * P, v * P, r);
      g.addColorStop(0, `rgba(${renk},.8)`);
      g.addColorStop(0.4, `rgba(${renk},.38)`);
      g.addColorStop(1, `rgba(${renk},0)`);
      c.fillStyle = g;
      c.fillRect(u * P - r, v * P - r, 2 * r, 2 * r);
    });
  }
  const svg = $('#drNokta');
  svg.classList.toggle('soluk', DR.gorunum === 'isi');
  const f = (x) => Math.round(x * 1000);
  svg.innerHTML = pts.map((p) => {
    const [u, v] = pr(p.x, p.y), X = f(u), Y = f(v);
    const karsi = p.rx != null ? pr(p.rx, p.ry) : null;
    const cizgi = karsi ? `<line class="dr-cizgi" x1="${X}" y1="${Y}" x2="${f(karsi[0])}" y2="${f(karsi[1])}"/><circle class="dr-karsi" cx="${f(karsi[0])}" cy="${f(karsi[1])}" r="6"/>` : '';
    const isaret = p.tur === 'kill' ? `<circle class="dr-k${p.hs ? ' hs' : ''}" cx="${X}" cy="${Y}" r="9"/>`
      : `<path class="dr-o" d="M${X - 7} ${Y - 7}L${X + 7} ${Y + 7}M${X + 7} ${Y - 7}L${X - 7} ${Y + 7}"/>`;
    const tip = `Round ${p.round} · ${p.tur === 'kill' ? 'Kill' : 'Ölüm'} · ${p.taraf.toUpperCase()}\n${silahAd(p.silah)}${p.hs ? ' · headshot' : ''}${karsi ? '' : p.tur === 'olum' ? '\nRakip konumu yok (bomba/dünya)' : ''}`;
    return `<g class="dr-n ${p.tur}" data-tip="${esc(tip)}">${cizgi}${isaret}<circle class="dr-hedef" cx="${X}" cy="${Y}" r="18"/></g>`;
  }).join('');
  drYanCiz(s, pts);
}

function utilityHtml(u) {
  const a = u.atilan || {}, top = u.atilan_toplam || 0;
  const bar = DR_BOMBA.filter(([k]) => a[k]).map(([k, ad, renk]) =>
    `<i style="width:${a[k] / top * 100}%;background:${renk}" data-tip="${ad}\n${a[k]} adet"></i>`).join('');
  const hasar = u.bomba_hasar || {};
  const takim = u.kor_takim || 0;
  return `<div class="dr-bomba">
      <div class="dr-bomba-ust"><span class="ri-ad">Atılan bombalar</span><b>${top}</b></div>
      <div class="dr-bar">${bar || '<i class="bos"></i>'}</div>
      <div class="dr-bomba-tur">${DR_BOMBA.map(([k, ad, renk]) => `<span class="${a[k] ? '' : 'yok'}"><i style="background:${renk}"></i>${ad} <b>${a[k] || 0}</b></span>`).join('')}</div>
    </div>
    <div class="ri">
      <div class="ri-oge"><div class="ri-ad">Flaş asisti</div><div class="ri-deger">${u.flas_asist ?? 0}</div><div class="ri-alt">kör ettiğin rakibi takımın vurdu</div></div>
      <div class="ri-oge"><div class="ri-ad">Kör edilen rakip</div><div class="ri-deger">${u.kor_dusman ?? 0}<small> · ${sayi(u.kor_dusman_sn, 1)} sn</small></div>
        <div class="ri-alt">${u.flas_basi_kor_sn != null ? `flaş başına ${sayi(u.flas_basi_kor_sn, 1)} sn, ${sayi(u.flas_basi_dusman, 1)} rakip` : 'flaş atılmadı'}</div></div>
      <div class="ri-oge"><div class="ri-ad">Takım arkadaşı kör</div><div class="ri-deger ${takim ? 'renk-kotu' : ''}">${takim}<small> · ${sayi(u.kor_takim_sn, 1)} sn</small></div><div class="ri-alt">kendi flaşınla</div></div>
      <div class="ri-oge"><div class="ri-ad">Bomba hasarı</div><div class="ri-deger">${u.bomba_hasar_toplam ?? 0}</div><div class="ri-alt">HE ${hasar.he ?? 0} · molotof ${hasar.molotof ?? 0} (rakibe, kalan canla sınırlı)</div></div>
    </div>`;
}

function nisanHtml(n) {
  const t = n.ttd || {};
  const enCok = Math.max(1, ...(t.dagilim || []).map((b) => b.sayi));
  const dag = (t.dagilim || []).map((b) => `<span data-tip="${esc(`${b.ust == null ? b.alt + '+ ms' : b.alt + '–' + b.ust + ' ms'}\n${b.sayi} çatışma`)}"><i style="height:${b.sayi / enCok * 100}%"></i><small>${b.ust == null ? '1s+' : b.alt}</small></span>`).join('');
  const kart = (ad, deger, alt, sinif = '') => `<div class="ri-oge"><div class="ri-ad">${ad}</div><div class="ri-deger ${sinif}">${deger}</div><div class="ri-alt">${alt}</div></div>`;
  const sil = (n.silahlar || []).filter((w) => w.atis || w.vurus || w.kill);
  return `<div class="ri">
      <div class="ri-oge dr-ttd"><div class="ri-ad">Tepki süresi (TTD)</div>
        <div class="ri-deger">${t.medyan_ms != null ? `${t.medyan_ms}<small> ms</small>` : '–'}</div>
        <div class="ri-alt">${t.ornek ? `medyan · ${t.ornek} çatışma · ort. ${t.ortalama_ms} ms` : 'ölçülebilir çatışma yok'}</div>
        ${t.ornek ? `<div class="dr-dag">${dag}</div>` : ''}</div>
      ${kart('İsabet', yuzdeYaz(n.isabet_yuzde), `${n.isabetli_atis ?? 0} / ${n.atis ?? 0} mermi rakibe değdi`)}
      ${kart('Sprey isabeti', yuzdeYaz(n.sprey_isabet_yuzde), n.sprey_atis ? `${n.sprey_atis} mermi · otomatik silahta 4. mermi ve sonrası` : 'sprey yok')}
      ${kart('İlk mermi', yuzdeYaz(n.ilk_mermi_isabet_yuzde), `${n.ilk_mermi_atis ?? 0} ilk mermi (geri tepme yokken)`)}
      ${kart(`Kafa isabeti`, yuzdeYaz(n.kafa_vurus_yuzde), `${n.kafa_vurus ?? 0} / ${n.vurus ?? 0} vuruş kafaya`)}
    </div>
    ${sil.length ? `<div class="tablo-sar dr-tablo"><table>
      <thead><tr><th scope="col">Silah</th><th scope="col">Atış</th><th scope="col">İsabet</th><th scope="col" class="gz-a">Vuruş</th><th scope="col">Kafa</th><th scope="col">${EN('Kill')}</th><th scope="col">HS ${EN('kill')}</th></tr></thead>
      <tbody>${sil.map((w) => `<tr><td><span lang="en">${esc(silahAd(w.silah))}</span></td><td class="soluk">${w.atis}</td><td>${yuzdeYaz(w.isabet_yuzde)}</td>
        <td class="soluk gz-a">${w.vurus}</td><td class="${(w.kafa_yuzde ?? 0) >= 30 ? 'renk-iyi' : ''}">${yuzdeYaz(w.kafa_yuzde)}</td><td class="k">${w.kill}</td><td>${yuzdeYaz(w.hs_kill_yuzde)}</td></tr>`).join('')}</tbody>
    </table></div>` : ''}`;
}

async function derinYenile(id) {
  if (!id || DR.hesaplaniyor.has(id)) return;
  DR.hesaplaniyor.add(id);
  delete DR.hata[id];
  derinYerine(id);
  const dur = sureSayaci('#drSure', (sn) => `${sn} sn · 10–40 saniye sürebilir.`);
  try {
    const s = await api(demoYol(id, '/yeniden-hesapla'), { method: 'POST', body: '{}' });
    S.demo[id] = s;
    if (derinVar(s)) bildir('Derin analiz hazır.', 'basari');
    else DR.hata[id] = (s.derin && s.derin.hata) || 'Derin analiz hesaplanamadı.';
  } catch (e) {
    DR.hata[id] = e.message;
    bildir(e.message, 'hata');
  } finally {
    dur();
    DR.hesaplaniyor.delete(id);
    derinYerine(id);
  }
}

function derinYerine(id) {
  const el = $('#derin'), s = S.demo[id];
  if (!el || !s || S.secili !== id || S.gorunum !== 'mac') return;
  el.outerHTML = derinHtml(s);
  derinCiz();
}

document.addEventListener('click', (e) => {
  const t = e.target;
  if (t.closest('[data-dr-yenile]')) { derinYenile(S.secili); return; }
  const b = t.closest('#drYan .secim button');
  if (!b) return;
  for (const k of ['tur', 'taraf', 'gorunum']) if (b.dataset['dr' + k[0].toUpperCase() + k.slice(1)]) DR[k] = b.dataset['dr' + k[0].toUpperCase() + k.slice(1)];
  derinCiz();
});
let drBoyut = 0;
addEventListener('resize', () => { clearTimeout(drBoyut); drBoyut = setTimeout(derinCiz, 120); });
