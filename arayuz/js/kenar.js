/* cs-klip arayüzü — bildirim, ipucu, sayaç, kayıt öncesi kontrol, otomatik kuyruk, kenar çubuğu.
   Klasik betik: index.html'deki sırayla yüklenir, üst düzey adlar öteki dosyalarla ortaktır. */
'use strict';

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

/* ======== otomatik kayıt kuyruğu (GET /api/otomatik; otomatik.py izle yazar) ======== */
const ORNEK_OTO = {
  calisiyor: true, durum: 'Bekliyor: FACEIT açık', aktif: null, satirlar: [], bekleyen: 1,
  kuyruk: [
    { id: '1-7d3e0a11-x-1-1', durum: 'bekliyor', mesaj: '', kaynak: 'faceit' },
    { id: '1-59cf10f2-x-1-1', durum: 'bitti', mesaj: '3 yeni klip', kaynak: 'izleyici' },
  ],
};
const OTO_DURUM = { bekliyor: 'Sırada', kaydediliyor: 'Kaydediliyor', bitti: 'Bitti', hata: 'Hata' };
function otoCiz(o) {
  const kutu = $('#oto');
  if (!kutu) return;
  if (!o) { kutu.hidden = true; return; }
  kutu.hidden = false;
  const liste = (o.kuyruk || []).slice(0, 5).map((i) => {
    const kod = (i.id.split('-')[1] || i.id).slice(0, 8);
    return `<li class="oto-${esc(i.durum)}" title="${esc(i.id + (i.mesaj ? '\n' + i.mesaj : ''))}"><span class="oto-kod">${esc(kod)}</span><span class="oto-mesaj">${esc(i.mesaj || (i.kaynak === 'faceit' ? 'FACEIT' : ''))}</span><b>${esc(OTO_DURUM[i.durum] || i.durum)}</b></li>`;
  }).join('');
  kutu.className = 'oto' + (o.calisiyor ? ' acik' : '');
  kutu.innerHTML = `<div class="oto-bas"><span class="nokta"></span>Otomatik kayıt<em>${o.calisiyor ? (o.bekleyen ? o.bekleyen + ' sırada' : 'açık') : 'kapalı'}</em></div>
    <p class="oto-not">${o.calisiyor ? esc(o.durum || '') : 'Yeni demoları kendiliğinden kaydetmek için <code>otomatik.bat</code> çalıştır.'}</p>
    ${liste ? `<ul>${liste}</ul>` : ''}`;
}
// Otomatik kuyruk: işçi çalışıyorsa 5 sn'de bir, kapalıysa 30 sn'de bir sorulur (basla: 5 sn'lik saat).
let otoSonYoklama = 0, otoCalisiyor = true;
async function otoYenile(zorla = true) {
  if (!zorla && !otoCalisiyor && Date.now() - otoSonYoklama < 30000) return;
  otoSonYoklama = Date.now();
  try {
    const v = await api('/api/otomatik');
    otoCalisiyor = !!(v && v.calisiyor);
    otoCiz(v);
  } catch { otoCiz(null); }
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
