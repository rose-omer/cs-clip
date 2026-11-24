/* cs-klip arayüzü — klip oynatıcı penceresi.
   Klasik betik: index.html'deki sırayla yüklenir, üst düzey adlar öteki dosyalarla ortaktır. */
'use strict';

/* ======== oynatıcı penceresi ======== */
let oynat = null;      // {video} gerçek klip ya da {t, top, raf} örnek mod taklidi
let oynatKaynak = null; // pencere kapanınca odağın döneceği düğme
function oynaticiAc(i, kaynak) {
  const hl = siraliHl();
  const h = hl[i];
  if (!h || !h.klip) return;
  const s = S.demo[S.secili];
  const b = baslikYap(h);
  const oy = gosterilen(S.secili);
  const baska = oy && !oy.ben && secOyuncu(S.secili) ? oy : null;
  pencereAc({
    klip: h.klip, rozet: `R${h.round}`, saniye: h.saniye,
    baslik: `${baska ? esc(baska.ad) + ' · ' : ''}${b.ana} · <span lang="en">${esc(haritaAd(s.harita) || '')}</span>`,
    sahne: ORNEK_MODU ? sahneHtml(s, h, i, { kayitli: false, oyuncu: baska }) : '',
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
      <div class="oy-cubuk" id="oyCubuk" role="slider" aria-label="Klipte konum" tabindex="0" aria-valuemin="0" aria-valuemax="${Math.round(o.saniye || 0)}" aria-valuenow="0" aria-valuetext="0:00"><i id="oyIlerle" style="width:0"></i></div><span class="oy-zaman" id="oyZaman">0:00 / ${sure(o.saniye || 0)}</span>
      ${ORNEK_MODU ? '' : `<button class="ikon-dugme ikincil" type="button" id="oyTam" aria-label="Tam ekran" title="Tam ekran">${ikon('i-full')}</button>`}</div>
    <div class="oy-not">${ORNEK_MODU ? `Örnek mod: ${esc(o.klip)} (dosya yok, oynatma taklit edilir)`
      : `<a href="${esc(src)}" target="_blank" rel="noopener">${esc(dosya)}</a> · Boşluk: oynat/duraklat · ←/→: 5 sn`}${o.ek || ''}</div></div>`;
  $('.kl-damga', m)?.remove();
  m.hidden = false;
  arkaPlan(true);
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
    cubukAria(v.currentTime, top);
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
// Uzun işte geçen süreyi seçilen öğeye yazar; dönen fonksiyon sayacı durdurur. html: metin HTML içerir.
function sureSayaci(secici, metin, html = false) {
  const bas = Date.now();
  const t = setInterval(() => {
    const el = $(secici);
    if (!el) return;
    const sn = Math.floor((Date.now() - bas) / 1000);
    if (html) el.innerHTML = metin(sn); else el.textContent = metin(sn);
  }, 1000);
  return () => clearInterval(t);
}
// Ekran okuyucu için kaydırma çubuğunun değeri (role=slider); her karede değil, saniye değişince yazılır.
function cubukAria(t, top) {
  const c = $('#oyCubuk');
  if (!c) return;
  const sn = Math.floor(t);
  if (c.getAttribute('aria-valuenow') === String(sn) && c.getAttribute('aria-valuemax') === String(Math.round(top))) return;
  c.setAttribute('aria-valuemax', String(Math.round(top)));
  c.setAttribute('aria-valuenow', String(sn));
  c.setAttribute('aria-valuetext', `${sure(t)} / ${sure(top)}`);
}
// Pencere açıkken arka plan odak ve ekran okuyucu dışında kalır (odak tuzağı).
function arkaPlan(kapali) {
  [...document.body.children].forEach((el) => {
    if (el.id === 'modal' || el.tagName === 'SCRIPT') return;
    if (kapali) el.setAttribute('inert', ''); else el.removeAttribute('inert');
  });
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
    cubukAria(oynat.t, oynat.top);
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
  arkaPlan(false);
  if (acikti && oynatKaynak && document.contains(oynatKaynak)) oynatKaynak.focus();
  oynatKaynak = null;
}
