/* cs-klip arayüzü — highlight klipleri, oyuncu seçimi, herkesin en iyi anı, kayıt.
   Klasik betik: index.html'deki sırayla yüklenir, üst düzey adlar öteki dosyalarla ortaktır. */
'use strict';

/* ======== klipler ======== */
const klipAnahtar = (id, h, sid = secOyuncu(id)) => id + ':' + (sid || '') + ':' + h.round;
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
  const ben = durum.oyuncu || benBul(s); // kill akışındaki oyuncu (başka oyuncu seçiliyse o)
  const biz = durum.oyuncu && durum.oyuncu.takim != null ? durum.oyuncu.takim : (s.benim_takim ?? 0);
  const T = taraflar(s);
  const yan = takimTaraf(T, biz, h.round);
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
// Puan dökümü: highlights.find_highlights 'puanlar' alanı ([etiket, puan]); eski önbellekte yok.
const puanDokumu = (h) => (h.puanlar && h.puanlar.length)
  ? `<details class="kl-dokum"><summary>Puan dökümü</summary><ul>${h.puanlar.map(([e, p]) =>
    `<li><span>${esc(e)}</span><b>+${sayi(p, 1)}</b></li>`).join('')}</ul></details>`
  : '';
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
  const calisiyor = k.kayit && k.kayit.durum === 'calisiyor' && kayitBuOyuncu(id);
  const hedef = new Set(calisiyor ? hl.slice(0, hedefSayisi(id)).map((h) => h.round) : []);
  const oy = gosterilen(id);
  const baska = !!(oy && !oy.ben && secOyuncu(id));
  $('#klipOzet').innerHTML = `${baska ? `<b>${esc(oy.ad)}</b> · ` : ''}${hl.length} ${EN('highlight')} · ${hl.filter((h) => h.klip).length} klip kayıtlı`;
  if (!hl.length) { iz.innerHTML = `<p class="bos-not">${baska ? esc(oy.ad) + ' için' : 'Bu maçta'} öne çıkan an bulunamadı.</p>`; return; }
  iz.innerHTML = hl.map((h, i) => {
    const b = baslikYap(h);
    const durum = { kayitli: !!h.klip, yeni: S.yeni.has(klipAnahtar(id, h)), kaydediliyor: !h.klip && hedef.has(h.round), oyuncu: baska ? oy : null };
    const etk = etiketHtml(h.labels) + (h.ozellikler || []).map((x) => `<span class="etk ozel">${esc(x)}</span>`).join('');
    return `<article class="klip ${durum.kayitli ? 'kayitli' : 'kayitsiz'}${i === 0 ? ' one' : ''} giris" style="--d:${i * 60}ms">
      ${sahneHtml(s, h, i, durum)}
      <div class="kl-govde">
        <div class="kl-ust"><span class="kl-sira">#${i + 1}</span>
          <h3 class="kl-baslik"><span class="kl-ust-et">${i === 0 ? (baska ? 'En iyi anı · ' : 'Maçın anı · ') : ''}${b.ust}</span>${b.ana}</h3>
          <div class="kl-puan">${sayi(h.score, 1)}<small>puan</small></div></div>
        <div class="kl-puan-bar"><i style="--p:${h.score / enYuksek * 100}%"></i></div>
        <div class="kl-etiketler">${etk}</div>
        ${puanDokumu(h)}
        <div class="kl-alt"><span lang="en">${(h.weapons || []).map((w) => esc(silahAd(w))).join(' · ') || '—'}</span><span>Round ${h.round} · ${h.saniye ?? '?'} sn</span></div>
      </div></article>`;
  }).join('');
}

async function klipleriYukle(id, no) {
  delete S.klipHata[id];
  const sid = secOyuncu(id);
  try {
    const k = await api(klipYol(id, sid));
    if (sid !== secOyuncu(id)) return; // bu arada başka oyuncu seçildi
    S.klipler[id] = k;
    if (k.kayit && k.kayit.durum === 'calisiyor') { S.aktifIs = id; yoklamaBaslat(); listeCiz(); }
  } catch (e) {
    if (sid !== secOyuncu(id)) return;
    S.klipHata[id] = e.message;
  }
  if (no !== S.istekNo || S.secili !== id) return;
  klipleriCiz();
  kayitCiz();
}

/* ======== oyuncu seçimi: skor tablosu -> o oyuncunun highlight'ları (GET /klipler?oyuncu=<steamid>) ======== */
// Süren kayıt gösterilen oyuncunun mu? (sunucu iş durumunu demo başına tutar)
const kayitBuOyuncu = (id) => {
  const k = S.klipler[id];
  return !!(k && k.kayit) && String(k.kayit.oyuncu || '') === String(secOyuncu(id) || '');
};
function oyuncuSec(sid, kaydirarak = false) {
  const id = S.secili;
  const s = S.demo[id];
  if (!id || !s) return;
  const o = oyuncuBul(s, sid);
  const yeni = !o || o.ben ? null : String(o.steamid);
  if (yeni !== secOyuncu(id)) {
    if (yeni) S.oyuncu[id] = yeni; else delete S.oyuncu[id];
    delete S.klipler[id];
    delete S.klipHata[id];
    tablolariCiz();
    oyuncuSecCiz();
    kayitCiz();
    klipleriCiz();
    herkesCiz();
    klipleriYukle(id, S.istekNo);
  }
  if (kaydirarak) { const kk = $('#klipler'); if (kk) kk.scrollIntoView({ behavior: kaydir() }); }
}
function oyuncuSecCiz() {
  const kutu = $('#oyuncuSec');
  const s = S.demo[S.secili];
  if (!kutu || !s) return;
  const oy = gosterilen(S.secili);
  const ben = benBul(s);
  const baska = !!(oy && !oy.ben && secOyuncu(S.secili));
  const TK = takimlarOf(s);
  const biz = s.benim_takim ?? 0;
  const grup = (t) => `<optgroup label="${esc(TK[t].ad)} · ${t === biz ? 'Senin takımın' : 'Rakip'}">${(s.oyuncular || []).filter((o) => o.takim === t)
    .map((o) => `<option value="${esc(o.steamid)}"${oy && String(oy.steamid) === String(o.steamid) ? ' selected' : ''}>${esc(o.ad)}${o.ben ? ' (sen)' : ''}</option>`).join('')}</optgroup>`;
  kutu.className = 'oyuncu-sec' + (baska ? ' baska' : '');
  kutu.innerHTML = `<span class="kayit-et">Oyuncu</span>
    <label class="sr" for="oyuncuListe">Kimin ${EN('highlight')}'ları gösterilsin</label>
    <select id="oyuncuListe" class="oyuncu-liste">${grup(biz)}${grup(1 - biz)}</select>
    ${baska ? `<span class="oyuncu-not">${esc(oy.ad)} oyuncusunun anları · klip adlarına <code>p-${esc(oyuncuEtiket(oy.ad, oy.steamid))}</code> eklenir</span>
      <button class="btn-ikincil" type="button" data-oyuncu-sec="${esc(ben ? ben.steamid : '')}">${ikon('i-back')}Kendi anlarım</button>`
      : `<span class="oyuncu-not">Başka bir oyuncunun anları için skor tablosunda adına tıkla.</span>`}`;
}

/* ======== herkesin en iyi anı: GET /api/demo/<id>/herkes ======== */
async function herkesYukle(id) {
  if (S.herkesYukleniyor === id) return;
  S.herkesYukleniyor = id;
  delete S.herkesHata[id];
  const dur = sureSayaci('#herkesListe .yukleniyor-not',
    (sn) => `Tüm oyuncuların ${EN('highlight')}'ları çıkarılıyor… ${sn} sn (ilk seferde birkaç saniye)`, true);
  try {
    S.herkes[id] = await api(demoYol(id, '/herkes'));
  } catch (e) {
    S.herkesHata[id] = e.status === 404 ? SUNUCU_ESKI : e.message;
  } finally {
    dur();
    if (S.herkesYukleniyor === id) S.herkesYukleniyor = null;
  }
  if (S.secili === id && S.gorunum === 'mac') herkesCiz();
}
function herkesCiz() {
  const kutu = $('#herkesListe');
  const id = S.secili, s = S.demo[id];
  if (!kutu || !s) return;
  const veri = S.herkes[id];
  if (!veri) {
    kutu.innerHTML = S.herkesHata[id]
      ? `<div class="kontrol sorun"><div class="kontrol-bas">${ikon('i-alert')}Oyuncuların anları alınamadı</div><ul><li>${esc(S.herkesHata[id])}</li></ul>
          <button class="btn-ikincil" type="button" data-herkes-tekrar>${ikon('i-refresh')}Tekrar dene</button></div>`
      : `<p class="bos-not yukleniyor-not">Tüm oyuncuların ${EN('highlight')}'ları çıkarılıyor… (ilk seferde birkaç saniye)</p>`;
    return;
  }
  const l = veri.oyuncular || [];
  const T = taraflar(s);
  const enYuksek = Math.max(...l.map((x) => (x.en_iyi ? x.en_iyi.score : 0)), 1);
  const secili = String((gosterilen(id) || {}).steamid);
  $('#herkesOzet').textContent = `${l.filter((x) => x.en_iyi).length} / ${l.length} oyuncunun öne çıkan anı var`;
  kutu.innerHTML = `<ol class="herkes">${l.map((x, i) => {
    const o = oyuncuBul(s, x.steamid) || { ad: x.ad, takim: null };
    const h = x.en_iyi;
    const yan = o.takim != null ? takimTaraf(T, o.takim, h ? h.round : 1) : null;
    const b = h ? baslikYap(h) : null;
    return `<li class="hk${x.varsayilan ? ' ben' : ''}${String(x.steamid) === secili ? ' secili' : ''}${h ? '' : ' yok'}"${yan ? ` style="--c:${tarafRenk(yan)}"` : ''}>
      <span class="hk-sira">${h ? i + 1 : '–'}</span>
      <span class="hk-oy"><b>${esc(x.ad)}</b>${x.varsayilan ? '<span class="cip or">Sen</span>' : ''}<small>${o.takim == null ? '' : x.varsayilan ? '' : o.takim === (s.benim_takim ?? 0) ? 'Takım arkadaşı' : 'Rakip'}</small></span>
      ${h ? `<span class="hk-an"><span class="hk-baslik">${b.ana}<small>${b.ust}</small></span><span class="kl-etiketler">${etiketHtml(h.labels)}</span></span>
        <span class="hk-puan">${sayi(h.score, 1)}<small>puan</small><i style="--p:${sinirla(h.score / enYuksek * 100, 3, 100)}%"></i></span>`
        : `<span class="hk-an bos-not">Öne çıkan an yok</span><span class="hk-puan"></span>`}
      <span class="hk-dugme">
        ${h && h.klip ? `<button class="ikon-dugme" type="button" data-herkes-oynat="${i}" aria-label="${esc(x.ad)}: en iyi anı oynat" title="Klibi oynat">${ikon('i-play')}</button>` : ''}
        <button class="btn-ikincil" type="button" data-oyuncu-sec="${esc(x.steamid)}"${x.highlight_sayisi ? '' : ' disabled'}>${x.highlight_sayisi || 0} an →</button>
      </span></li>`;
  }).join('')}</ol>`;
}
function herkesOynat(i, kaynak) {
  const s = S.demo[S.secili];
  const x = ((S.herkes[S.secili] || {}).oyuncular || [])[i];
  if (!s || !x || !x.en_iyi || !x.en_iyi.klip) return;
  const h = x.en_iyi;
  const o = oyuncuBul(s, x.steamid);
  const b = baslikYap(h);
  pencereAc({
    klip: h.klip, rozet: `R${h.round}`, saniye: h.saniye,
    baslik: `${esc(x.ad)} · ${b.ana} · <span lang="en">${esc(haritaAd(s.harita) || '')}</span>`,
    sahne: ORNEK_MODU ? sahneHtml(s, h, i, { kayitli: false, oyuncu: o && !o.ben ? o : null }) : '',
  }, kaynak);
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
    else if (/^Kayıt: .*round karşılaştırıldı/.test(x)) { adim = Math.max(adim, 2); mesaj = 'Canlı kayıttan kesiliyor (CS2 açılmaz)'; }
    else if (/^atlandı \(kayıtta yok\)/.test(x)) { mesaj = 'Kayıtta olmayan an atlandı: ' + x.replace(/^atlandı \(kayıtta yok\):\s*/, ''); }
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
  const oy = gosterilen(id);
  const baska = !!(oy && !oy.ben && secOyuncu(id));
  const canli = !!(k && k.canli && !baska); // maçın canlı kaydı: klipler CS2 açılmadan ondan kesilir
  btn.disabled = !k || calisiyor || S.kayitBasliyor;
  btn.title = S.aktifIs && S.aktifIs !== id ? 'Başka bir demonun kaydı sürüyor.' : baska ? `${oy.ad} oyuncusunun anları onun gözünden kaydedilir.`
    : canli ? 'Klipler bu maçın canlı kaydından kesilir; CS2 açılmaz.' : '';
  const cb = $('#canliBilgi');
  if (cb) {
    cb.hidden = !canli;
    cb.innerHTML = canli ? `<b>Canlı kayıt bulundu:</b> ${esc(k.canli.video)} · ${k.canli.roundlar + 1} round eşleşti. Klipler bu kayıttan kesilir: <b>CS2 açılmaz</b>, FACEIT açık kalabilir.` : '';
  }
  const ac = $('#kayitAciklama');
  if (ac) ac.hidden = canli;
  btn.classList.toggle('baska', baska);
  const goz = $('#kimGozu');
  if (goz) goz.textContent = baska ? `${oy.ad} oyuncusunun` : 'senin';
  $('#kaydetMetin').textContent = !k ? (S.klipHata[id] ? 'Klipler alınamadı' : 'Yükleniyor…')
    : S.kayitBasliyor ? 'Başlatılıyor…' : calisiyor ? (k.kayit && k.kayit.kaynak === 'canli' ? 'Kesiliyor…' : 'Kayıt sürüyor…')
      : baska ? 'Bu oyuncunun kliplerini kaydet' : canli ? 'Kayıttan kes' : 'Klipleri kaydet';
  $('#kaydetAlt').textContent = !k || calisiyor || S.kayitBasliyor ? '' : `(${S.enIyi ? 'en iyi ' + n : 'hepsi · ' + n})`;
  $$('#kayitSecim button').forEach((x) => { x.disabled = calisiyor; });
  const il = $('#ilerleme');
  if (!b) { il.hidden = true; il.innerHTML = ''; return; }
  const isOy = k && k.kayit && k.kayit.oyuncu ? oyuncuBul(S.demo[id], k.kayit.oyuncu) : null;
  if (isOy && !isOy.ben) b.mesaj = `${isOy.ad} · ${b.mesaj}`;
  const eski = $('#gunluk', il);
  const altta = !eski || eski.scrollHeight - eski.scrollTop - eski.clientHeight < 30;
  il.hidden = false;
  il.className = 'ilerleme ' + b.durum;
  const adimSinif = (i) => (b.durum === 'bitti' || i < b.adim ? 'tamam' : i === b.adim ? (b.durum === 'hata' ? 'hata' : 'simdi') : '');
  il.innerHTML = `<div class="il-ust"><span class="il-durum">${b.durum === 'bitti' ? 'Tamamlandı' : b.durum === 'hata' ? 'Hata' : 'Rec'}</span>
      <span class="il-mesaj" title="${esc(b.mesaj)}">${esc(b.mesaj)}</span><span class="il-yuzde" title="Günlük satırlarından tahmini ilerleme">${b.durum === 'hata' ? '' : Math.round(b.yuzde) + '%'}</span>
      ${calisiyor ? `<button class="btn-ikincil il-durdur" type="button" id="kayitDurdur"${S.durduruluyor ? ' disabled' : ''}>${S.durduruluyor ? 'Durduruluyor…' : 'Durdur'}</button>` : ''}</div>
    <div class="il-bar"><i style="width:${b.durum === 'hata' ? 100 : b.yuzde}%"></i></div>
    <div class="adimlar">${ADIMLAR.map((a, i) => { const c = adimSinif(i); return `<div class="adim ${c}"><i>${c === 'tamam' ? '✓' : c === 'hata' ? '!' : i + 1}</i><span>${a}</span></div>`; }).join('')}</div>
    ${S.yoklamaHata && calisiyor ? `<div class="kayit-bilgi" style="color:var(--kotu);margin-top:10px">Kayıt durumu alınamadı: ${esc(S.yoklamaHata)} — yeniden deneniyor.</div>` : ''}
    <details class="gunluk"${S.gunlukAcik || b.durum === 'hata' ? ' open' : ''}><summary>Kayıt günlüğü (${b.satirlar.length} satır${b.satirlar.length >= 40 ? ', son 40' : ''})</summary><pre id="gunluk">${b.satirlar.map((x) => `<span class="${satirSinif(x)}">${esc(x)}</span>`).join('\n') || '<span class="z">Henüz çıktı yok…</span>'}</pre></details>`;
  const pre = $('#gunluk', il);
  if (pre && altta) pre.scrollTop = pre.scrollHeight;
  $('.gunluk', il).addEventListener('toggle', (e) => { S.gunlukAcik = e.target.open; });
}

// Takılan kaydı durdurur: sunucu klip.py'yi ve açtığı CS2'yi kapatır; bitmiş klipler kalır.
async function kaydiDurdur() {
  const id = S.secili;
  if (S.durduruluyor || !confirm('Kayıt durdurulsun mu? CS2 kapatılır; bitmiş klipler kalır.')) return;
  S.durduruluyor = true;
  kayitCiz();
  try {
    await api(demoYol(id, '/durdur'), { method: 'POST' });
    bildir('Kayıt durduruluyor.');
  } catch (e) {
    bildir(e.message, 'hata');
  } finally {
    S.durduruluyor = false;
    if (S.secili === id) kayitCiz();
  }
}

async function kaydet() {
  const id = S.secili;
  const k = S.klipler[id];
  if (!k || S.kayitBasliyor) return;
  if (S.aktifIs && S.aktifIs !== id) { bildir('Başka bir kayıt sürüyor; bitmesini bekle.', 'hata'); return; }
  const hl = siraliHl();
  if (!hl.length) { bildir('Kaydedilecek highlight yok.', 'hata'); return; }
  const enIyi = S.enIyi;
  const sid = secOyuncu(id);
  S.kayitBasliyor = true;
  kayitCiz();
  try {
    const govde = sid ? { en_iyi: enIyi, oyuncu: sid } : { en_iyi: enIyi }; // varsayılan oyuncu: eski gövde
    const sonuc = await api(demoYol(id, '/kaydet'), { method: 'POST', body: JSON.stringify(govde) });
    S.kayitHedef[id] = enIyi;
    delete S.ilerleme[id];
    const kesim = !!(sonuc && sonuc.kaynak === 'canli');
    k.kayit = { durum: (sonuc && sonuc.durum) || 'calisiyor', mesaj: kesim ? 'Canlı kayıttan kesiliyor' : 'Kayıt başladı', satirlar: [], oyuncu: sid,
      kaynak: (sonuc && sonuc.kaynak) || 'cs2' };
    S.aktifIs = id;
    S.yoklamaHata = null;
    bildir(ORNEK_MODU ? 'Örnek mod: kayıt taklit ediliyor.'
      : kesim ? 'Klipler canlı kayıttan kesiliyor; CS2 açılmayacak.' : 'Kayıt başladı. CS2 açılacak; bitene kadar bilgisayarı kullanma.');
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
      const sid = secOyuncu(id);
      const yeni = await api(klipYol(id, sid));
      const eski = S.klipler[id];
      if (sid === secOyuncu(id)) { // yanıt gelene kadar oyuncu değiştiyse listeyi karıştırma
        const once = new Map(((eski && eski.highlightlar) || []).map((h) => [h.round, h.klip]));
        (yeni.highlightlar || []).forEach((h) => { if (h.klip && !once.get(h.round) && eski) S.yeni.add(klipAnahtar(id, h, sid)); });
        S.klipler[id] = yeni;
      } else if (eski) eski.kayit = yeni.kayit;
      S.yoklamaHata = null;
      hataSay = 0;
      const bitti = !yeni.kayit || yeni.kayit.durum !== 'calisiyor';
      if (S.secili === id) { kayitCiz(); klipleriCiz(); }
      if (bitti) {
        S.aktifIs = null;
        delete S.ilerleme[id];
        const s = S.demo[id];
        const ad = haritaAd(s && s.harita) || 'Demo';
        delete S.herkes[id]; // klip bağlantıları değişti
        if (S.secili === id && S.gorunum === 'mac') herkesYukle(id);
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
