/* cs-klip arayüzü — En iyi anlarım (#en-iyi): vitrin ve montaj.
   Klasik betik: index.html'deki sırayla yüklenir, üst düzey adlar öteki dosyalarla ortaktır. */
'use strict';

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
  // Sade montaj ve paylaşım videolarından en yenisi kartta görünür.
  const adaylar = [v && v.montaj, ...(Array.isArray(v && v.paylasim) ? v.paylasim : [])].filter((m) => m && m.klip);
  const montaj = adaylar.sort((a, b) => String(b.tarih || '').localeCompare(String(a.tarih || '')))[0] || null;
  return { klipler, montaj };
}
// 404: sunucu bu ucu tanımıyor (yeni özellikten önce başlatılmış).
const enIyiHataMetni = (e) => (e && e.status === 404 ? SUNUCU_ESKI : (e && e.message) || 'Bilinmeyen hata.');

// Maç dışı görünümler (en iyi anlar, ayarlar, kariyer) için ortak açılış.
function gorunumAc(ad) {
  S.istekNo++; // süren demo yüklemeleri #ana'yı artık çizmesin
  S.gorunum = ad;
  S.secili = null;
  menuAc(false);
  ipucuGizle();
  if (gozlem) { gozlem.disconnect(); gozlem = null; }
  scrollTo({ top: 0, behavior: kaydir() });
  listeCiz();
  gezinCiz();
}
function enIyiAc() {
  gorunumAc(EN_IYI);
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

// Vitrindeki başka oyuncular (klip adında p-<etiket> olanlar): [{etiket, ad, n}]
function eiOyuncular() {
  const m = new Map();
  (S.ei ? S.ei.klipler : []).forEach((k) => {
    if (!k.oyuncu) return;
    const a = String(k.oyuncu).toLowerCase();
    const x = m.get(a) || { etiket: k.oyuncu, ad: k.oyuncu_ad || k.oyuncu, n: 0 };
    x.n++;
    m.set(a, x);
  });
  return [...m.values()].sort((a, b) => b.n - a.n || a.ad.localeCompare(b.ad, 'tr'));
}
// Süzgeç geçersizse düzeltir: yalnız başkalarının klipleri varsa "Herkes"e geçer.
function eiOyuncuDuzelt() {
  if (!S.ei) return;
  const l = S.ei.klipler;
  if (S.eiOyuncu && S.eiOyuncu !== '*' && !oyuncuSuz(l, S.eiOyuncu).length) S.eiOyuncu = '';
  if (!S.eiOyuncuElle && S.eiOyuncu === '' && !oyuncuSuz(l, '').length && l.length) S.eiOyuncu = '*';
}
const eiListe = () => (S.ei ? oyuncuSuz(S.ei.klipler, S.eiOyuncu) : []);
const eiOyuncuAd = (f) => (f === '*' ? 'herkes' : f ? ((eiOyuncular().find((x) => x.etiket.toLowerCase() === String(f).toLowerCase()) || {}).ad || f) : 'sen');
function vitrinOyuncu(k) {
  if (!k.oyuncu) return null;
  const s = k.demo && S.demo[k.demo];
  const o = s && (s.oyuncular || []).find((x) => oyuncuEtiket(x.ad, x.steamid).toLowerCase() === String(k.oyuncu).toLowerCase());
  return o || { ad: k.oyuncu_ad || k.oyuncu, takim: 0 };
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
  eiOyuncuDuzelt();
  const l = eiListe();
  const kimin = S.eiOyuncu === '*' ? 'Herkesin en iyi <span>anları</span>'
    : S.eiOyuncu ? `${esc(eiOyuncuAd(S.eiOyuncu))} · en iyi <span>anları</span>` : 'En iyi <span>anlarım</span>';
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
        <div class="ei-bas-metin"><h1 class="ei-baslik">${kimin}</h1>
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
  const tum = eiListe();
  const oyuncular = eiOyuncular();
  const say = {};
  tum.forEach((k) => { const h = haritaAnahtar(k.harita); if (h) say[h] = (say[h] || 0) + 1; });
  const sirali = Object.keys(say).sort((a, b) => say[b] - say[a] || a.localeCompare(b));
  const cip = (h, ad, n) => `<button type="button" class="ei-cip${S.eiHarita === h ? ' aktif' : ''}" data-ei-harita="${esc(h)}" aria-pressed="${S.eiHarita === h}"${h ? ` style="${haritaStil(h)}"` : ''}>${h ? '<i></i>' : ''}<span${h ? ' lang="en"' : ''}>${esc(ad)}</span><em>${n}</em></button>`;
  const oyCip = (f, ad, n) => `<button type="button" class="ei-cip ei-oy${S.eiOyuncu === f ? ' aktif' : ''}" data-ei-oyuncu="${esc(f)}" aria-pressed="${S.eiOyuncu === f}"><span>${esc(ad)}</span><em>${n}</em></button>`;
  const oyHtml = oyuncular.length ? `<div class="ei-cipler ei-oyuncular" role="group" aria-label="Oyuncu filtresi"><span class="kayit-et">Oyuncu</span>
    ${oyCip('', 'Sen', oyuncuSuz(S.ei.klipler, '').length)}${oyuncular.map((x) => oyCip(x.etiket, x.ad, x.n)).join('')}${oyCip('*', 'Herkes', S.ei.klipler.length)}</div>` : '';
  $('#eiFiltre').innerHTML = (tum.length || oyHtml) ? `${oyHtml}
    <div class="ei-cipler" role="group" aria-label="Harita filtresi">${cip('', 'Tümü', tum.length)}${sirali.map((h) => cip(h, haritaAd(h), say[h])).join('')}</div>
    <div class="secim" role="radiogroup" aria-label="Kaç klip gösterilsin">${[[10, 'En iyi 10'], [20, 'En iyi 20'], [0, 'Hepsi']].map(([n, ad]) =>
      `<button type="button" role="radio" data-ei-adet="${n}" class="${S.eiAdet === n ? 'aktif' : ''}" aria-checked="${S.eiAdet === n}">${ad}</button>`).join('')}</div>` : '';
  const f = S.eiHarita ? tum.filter((k) => haritaAnahtar(k.harita) === S.eiHarita) : tum;
  const g = S.eiAdet ? f.slice(0, S.eiAdet) : f;
  S.eiGorunen = g;
  $('#eiOzet').innerHTML = tum.length ? `${g.length} / ${f.length} klip${S.eiHarita ? ` · <span lang="en">${esc(haritaAd(S.eiHarita))}</span>` : ''}` : '';
  if (!tum.length) {
    iz.innerHTML = `<div class="ei-bos"><span class="birak-ikon">${ikon('i-film')}</span><div><strong>${S.ei.klipler.length ? 'Bu oyuncunun klibi yok' : 'Henüz klip yok'}</strong>
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
    ${sahneHtml(vitrinDemo(k), h, i, { kayitli: true, oynatAt: `data-ei-oynat="${i}"`, oyuncu: vitrinOyuncu(k) })}
    <div class="kl-govde">
      <div class="kl-ust"><span class="kl-sira${i < 3 ? ' podyum' : ''}">#${i + 1}</span>
        <h3 class="kl-baslik"><span class="kl-ust-et">${i === 0 && !k.oyuncu ? 'En iyi anın · ' : ''}${k.oyuncu ? `<b class="ei-oyuncu">${esc(k.oyuncu_ad || k.oyuncu)}</b> · ` : ''}<span lang="en">${esc(ad)}</span> · ${b.ust}</span>${b.ana}</h3>
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
    baslik: `${k.oyuncu ? esc(k.oyuncu_ad || k.oyuncu) + ' · ' : ''}${b.ana} · <span lang="en">${esc(haritaAd(k.harita) || '')}</span>`,
    sahne: ORNEK_MODU ? sahneHtml(vitrinDemo(k), { ...h, saniye: k.saniye || 15 }, i, { kayitli: false, oyuncu: vitrinOyuncu(k) }) : '',
    ek: k.demo ? ` · <a href="#${encodeURIComponent(k.demo)}">Maça git →</a>` : '',
  }, kaynak);
}

function montajCiz() {
  const kutu = $('#montajKutu');
  if (!kutu || !S.ei) return;
  const n = eiListe().length;
  const kimin = S.eiOyuncu ? ` (${esc(eiOyuncuAd(S.eiOyuncu))})` : '';
  const mj = S.ei.montaj;
  const sur = S.montajSuruyor;
  const adetN = Math.min(S.mjAdet, n);
  const sn = Math.floor((Date.now() - S.montajBas) / 1000);
  kutu.innerHTML = `
    <div class="kayit-sol">
      <div class="kayit-satir"><span class="kayit-et">Klip sayısı</span>
        <div class="secim" role="radiogroup" aria-label="Montajda kaç klip olsun">${[5, 10, 15, 20].map((x) =>
          `<button type="button" role="radio" data-mj-adet="${x}" class="${S.mjAdet === x ? 'aktif' : ''}" aria-checked="${S.mjAdet === x}"${sur ? ' disabled' : ''}>${x}</button>`).join('')}</div></div>
      ${mjSecenekHtml(sur)}
      <button class="btn-kaydet btn-montaj${sur ? ' calisiyor' : ''}" id="montajYap" type="button"${sur || !n ? ' disabled' : ''}${!n ? ' title="Önce klip kaydet."' : ''}>
        ${sur ? '<span class="rec"></span>' : ikon('i-film')}<span>${sur ? 'Montaj hazırlanıyor…' : mj ? 'Yeniden montaj yap' : 'Montaj yap'}</span>
        <small>${sur || !n ? '' : `(en iyi ${adetN})`}</small></button>
      ${sur ? `<div class="mj-bekle"><div class="il-bar belirsiz"><i></i></div><div class="analiz-adim" id="montajSure">${sn} sn · ${S.mjSec.tur === 'paylasim' ? 'video kodlanıyor' : 'klipler birleştiriliyor'}</div></div>` : ''}
      ${S.montajHata && !sur ? `<div class="mj-hata" role="alert">${ikon('i-alert')}<span>${esc(S.montajHata)}</span></div>` : ''}
      <div class="kayit-bilgi">${ORNEK_MODU ? '<b>Örnek mod:</b> montaj taklit edilir, dosya yazılmaz. ' : ''}${S.mjSec.tur === 'paylasim'
        ? `Puanı en yüksek ${adetN || ''} klip${kimin} ${S.mjSec.dikey ? 'dikey 9:16' : 'yatay 16:9'} olarak yeniden kodlanır${S.mjSec.kart ? ', başa harita/skor kartı' : ''}${S.mjSec.etiket ? ', köşeye kill etiketi' : ''} eklenir (<code>klipler/paylasim/en_iyi_${S.mjSec.dikey ? 'dikey' : 'yatay'}.mp4</code>). Klip başına 10-30 saniye sürebilir; klipler değişmez.`
        : `Puanı en yüksek ${adetN || ''} klip${kimin} sırayla tek bir MP4'te birleştirilir (<code>klipler/en_iyi_montaj.mp4</code>); var olan montajın üzerine yazılır. Birkaç saniye ile bir dakika sürebilir.`}${n && S.mjAdet > n ? ` Şu an yalnız ${n} klip var.` : ''}</div>
    </div>
    <div class="mj-kart${mj ? '' : ' bos'}${mj && S.montajYeni ? ' yeni' : ''}">${mj ? montajKartHtml(mj) : `
      <span class="birak-ikon">${ikon('i-film')}</span><strong>Henüz montaj yok</strong>
      <span>${n ? `Klip sayısını seç ve “Montaj yap”a bas. En iyi anların art arda tek videoda birleşir.` : 'Montaj için önce klip kaydetmelisin.'}</span>`}</div>`;
  S.montajYeni = false;
}
function mjSecenekHtml(sur) {
  const o = S.mjSec;
  const dis = sur ? ' disabled' : '';
  const grup = (et, anahtar, secenekler) => `<div class="kayit-satir"><span class="kayit-et">${et}</span>
    <div class="secim" role="radiogroup" aria-label="${esc(et)}">${secenekler.map(([v, ad]) =>
      `<button type="button" role="radio" data-mj-sec="${anahtar}" data-v="${esc(v)}" class="${String(o[anahtar]) === String(v) ? 'aktif' : ''}" aria-checked="${String(o[anahtar]) === String(v)}"${dis}>${ad}</button>`).join('')}</div></div>`;
  const ac = (anahtar, ad) => `<button type="button" data-mj-ac="${anahtar}" class="${o[anahtar] ? 'aktif' : ''}" aria-pressed="${!!o[anahtar]}"${dis}>${ad}</button>`;
  let h = grup('Tür', 'tur', [['sade', 'Sade'], ['paylasim', 'Paylaşım']]);
  if (o.tur !== 'paylasim') return h;
  h += grup('Biçim', 'dikey', [['false', 'Yatay 16:9'], ['true', 'Dikey 9:16']]);
  if (o.dikey) h += grup('Yerleşim', 'yerlesim', [['bulanik', 'Bulanık'], ['kirp', 'Kırp']]);
  h += `<div class="kayit-satir"><span class="kayit-et">Ekler</span><div class="secim">${ac('kart', 'Açılış kartı')}${ac('etiket', 'Kill etiketi')}</div></div>`;
  h += grup('Kalite', 'kalite', [['1080p', '1080p'], ['1440p', '1440p']]);
  h += grup('Boyut', 'sikistirma', [['yuksek', 'Yüksek'], ['dengeli', 'Dengeli'], ['kucuk', 'Küçük']]);
  h += `<label class="kayit-satir mj-alan"><span class="kayit-et">Hedef MB</span><input type="number" min="1" max="4000" step="1" placeholder="boş = Boyut seçimi" data-mj-in="hedefMb" value="${esc(o.hedefMb)}"${dis}></label>`;
  h += `<label class="kayit-satir mj-alan"><span class="kayit-et">Müzik</span><input type="text" placeholder="isteğe bağlı: C:\\Müzik\\parca.mp3" data-mj-in="muzik" value="${esc(o.muzik)}" spellcheck="false"${dis}></label>`;
  return h;
}
const MJ_CRF = { yuksek: 17, dengeli: 20, kucuk: 26 };
function mjGovde(adet) {
  const o = S.mjSec;
  if (o.tur !== 'paylasim') return { adet };
  const g = { adet, paylasim: true, dikey: o.dikey, yerlesim: o.yerlesim, kart: o.kart, etiket: o.etiket, kalite: o.kalite, crf: MJ_CRF[o.sikistirma] || 20 };
  const mb = Number(o.hedefMb);
  if (o.hedefMb !== '' && mb > 0) g.hedef_mb = mb;
  if (o.muzik.trim()) g.muzik = o.muzik.trim();
  return g;
}
function montajKartHtml(mj) {
  const serit = oyuncuSuz(S.ei.klipler, mj.oyuncu || '').slice(0, Math.max(1, Math.min(mj.adet || 1, 20)))
    .map((k) => `<i style="${haritaStil(k.harita)}"></i>`).join('');
  let dosya = '';
  try { dosya = decodeURIComponent(String(mj.klip).split('/').pop()); } catch { dosya = String(mj.klip); }
  return `<button class="mj-poster" type="button" data-mj-oynat aria-label="Montajı oynat">
      <span class="mj-serit">${serit}</span><span class="kl-round">Montaj</span>
      <span class="kl-oynat">${ikon('i-play', '')}</span></button>
    <div class="mj-bilgi">
      <div class="mj-ad">En iyi ${esc(mj.adet ?? '?')} an${mj.oyuncu ? ` · ${esc(eiOyuncuAd(mj.oyuncu))}` : ''}<small>${esc(dosya)}</small></div>
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
  const ilk = oyuncuSuz(S.ei.klipler, mj.oyuncu || '')[0] || S.ei.klipler[0];
  pencereAc({
    klip: mj.klip, src: montajSrc(mj), rozet: `${mj.adet ?? '?'} klip`, baslik: 'En iyi anlar · montaj',
    saniye: ORNEK_MODU ? (mj.saniye || (mj.adet || 1) * 15) : 0,
    sahne: ORNEK_MODU && ilk ? sahneHtml(vitrinDemo(ilk), { ...vitrinHl(ilk), saniye: mj.saniye || 60 }, 0, { kayitli: false }) : '',
  }, kaynak);
}
async function montajYap() {
  if (S.montajSuruyor || !S.ei || !eiListe().length) return;
  const adet = S.mjAdet;
  const oyuncu = S.eiOyuncu;
  S.montajSuruyor = true;
  S.montajHata = null;
  S.montajBas = Date.now();
  montajCiz();
  const sayac = setInterval(() => {
    const el = $('#montajSure');
    if (el) el.textContent = `${Math.floor((Date.now() - S.montajBas) / 1000)} sn · ${S.mjSec.tur === 'paylasim' ? 'video kodlanıyor' : 'klipler birleştiriliyor'}`;
  }, 500);
  try {
    const r = await api('/api/en-iyi/montaj', { method: 'POST', body: JSON.stringify(oyuncu ? { ...mjGovde(adet), oyuncu } : mjGovde(adet)) });
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
