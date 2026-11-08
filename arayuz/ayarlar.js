/* cs-klip arayüzü — Ayarlar sayfası (#ayarlar): GET/POST /api/ayarlar.
   app.js yönlendirir ve window.csklip yardımcılarını (api, bildir, esc, ikon) verir. */
(() => {
  'use strict';

  // Alan tanımları: ayarlar.json anahtarı, etiket, tür ve açıklama.
  const BOLUMLER = [
    { no: '01', baslik: 'Oyuncu', ek: 'Klipler ve istatistikler bu oyuncuya göre', alanlar: [
      { k: 'oyuncu', etiket: 'Oyuncu adı', tur: 'metin', ipucu: 'Demodaki adın ya da SteamID64. Değişirse maçlar yeniden analiz edilir.' },
    ] },
    { no: '02', baslik: 'Klipler', ek: 'Hangi anlar, ne kadar uzun', alanlar: [
      { k: 'min_skor', etiket: 'En düşük puan', tur: 'sayi', min: 0, max: 100, adim: 0.5, ipucu: 'Bu puanın altındaki anlar kaydedilmez (2K = 3, 3K = 6, ACE = 16).' },
      { k: 'mac_basi_en_fazla', etiket: 'Maç başına en fazla', tur: 'sayi', min: 0, max: 50, adim: 1, ipucu: '0 = eşiği geçen hepsi.' },
      { k: 'once_sn', etiket: 'İlk kill\'den önce (sn)', tur: 'sayi', min: 0, max: 30, adim: 0.5 },
      { k: 'sonra_sn', etiket: 'Son kill\'den sonra (sn)', tur: 'sayi', min: 0, max: 30, adim: 0.5 },
      { k: 'temiz_hud', etiket: 'Temiz HUD', tur: 'acik', ipucu: 'Ekranda yalnız kill akışı görünür.' },
      { k: 'montaj', etiket: 'Montaj', tur: 'acik', ipucu: 'Kayıttan sonra klipleri tek videoda birleştir.' },
    ] },
    { no: '03', baslik: 'Klasörler', ek: 'Demolar ve klipler nerede', alanlar: [
      { k: 'cikti_klasoru', etiket: 'Klip klasörü', tur: 'yol', ipucu: 'Göreli yol cs-klip klasörüne göredir (varsayılan: klipler).' },
      { k: 'demo_klasorleri', etiket: 'Demo klasörleri', tur: 'liste', ipucu: 'Her satıra bir klasör. Boşsa İndirilenler ve demos/ taranır.' },
      { k: 'csgo_klasoru', etiket: 'CS2 klasörü', tur: 'yol', yerTutucu: 'Boş: Steam\'den bulunur', ipucu: '…\\Counter-Strike Global Offensive\\game\\csgo' },
    ] },
    { no: '04', baslik: 'Araç yolları', ek: 'Boş bırakılırsa kendiliğinden bulunur', gelismis: true, alanlar: [
      { k: 'csdm_yolu', etiket: 'CS Demo Manager (csdm.cmd)', tur: 'yol', yerTutucu: 'Boş: %LOCALAPPDATA%\\Programs\\cs-demo-manager\\csdm.cmd' },
      { k: 'ffmpeg_yolu', etiket: 'ffmpeg.exe', tur: 'yol', yerTutucu: 'Boş: PATH ve winget klasörü' },
      { k: 'pg_veri_klasoru', etiket: 'PostgreSQL veri klasörü', tur: 'yol', yerTutucu: 'Boş: %LOCALAPPDATA%\\csdm-pg\\data' },
    ] },
  ];
  const ALANLAR = BOLUMLER.flatMap((b) => b.alanlar);

  // Örnek modu (?ornek=1): sunucu yok, ayarlar sayfada tutulur.
  const ORNEK = {
    ayarlar: { oyuncu: 'DuranEnnmi', min_skor: 3, mac_basi_en_fazla: 0, once_sn: 3, sonra_sn: 2, temiz_hud: true, montaj: true,
      cikti_klasoru: 'klipler', csgo_klasoru: '', csdm_yolu: '', ffmpeg_yolu: '', pg_veri_klasoru: '', demo_klasorleri: [] },
    dosya: 'ayarlar.json (örnek)',
  };
  ORNEK.varsayilan = { ...ORNEK.ayarlar };

  const A = { veri: null, hata: null, alanHata: {}, kaydediliyor: false, kok: null };
  const C = () => window.csklip;

  async function istek(method, govde) {
    if (C().ornek) {
      if (method === 'POST') Object.assign(ORNEK.ayarlar, govde);
      return JSON.parse(JSON.stringify({ ...ORNEK, yeniden_analiz: 0 }));
    }
    return C().api('/api/ayarlar', method === 'POST' ? { method, body: JSON.stringify(govde) } : {});
  }

  function deger(a, k) {
    const v = a[k];
    return Array.isArray(v) ? v.join('\n') : v;
  }

  function alanHtml(f, a, vars) {
    const { esc } = C();
    const id = 'ay_' + f.k;
    const hata = A.alanHata[f.k];
    const v = deger(a, f.k);
    const farkli = JSON.stringify(a[f.k]) !== JSON.stringify(vars[f.k]);
    const ipucu = f.ipucu ? `<small class="ay-ipucu" id="${id}_i">${esc(f.ipucu)}</small>` : '';
    const hataHtml = `<small class="ay-hata" id="${id}_h"${hata ? '' : ' hidden'}>${esc(hata || '')}</small>`;
    const tanim = `aria-describedby="${id}_i ${id}_h"${hata ? ' aria-invalid="true"' : ''}`;
    let giris;
    if (f.tur === 'acik') {
      giris = `<label class="ay-anahtar"><input type="checkbox" id="${id}" name="${f.k}" ${v ? 'checked' : ''} ${tanim}><span class="ay-anahtar-yol"></span><span class="ay-anahtar-yazi">${v ? 'Açık' : 'Kapalı'}</span></label>`;
    } else if (f.tur === 'liste') {
      giris = `<textarea id="${id}" name="${f.k}" rows="3" spellcheck="false" placeholder="C:\\Users\\…\\Downloads" ${tanim}>${esc(v)}</textarea>`;
    } else if (f.tur === 'sayi') {
      giris = `<input type="number" id="${id}" name="${f.k}" value="${esc(v)}" min="${f.min}" max="${f.max}" step="${f.adim}" inputmode="decimal" required ${tanim}>`;
    } else {
      giris = `<input type="text" id="${id}" name="${f.k}" value="${esc(v)}" spellcheck="false" autocomplete="off"${f.yerTutucu ? ` placeholder="${esc(f.yerTutucu)}"` : ''}${f.k === 'oyuncu' || f.k === 'cikti_klasoru' ? ' required' : ''} ${tanim}>`;
    }
    return `<div class="ay-alan${hata ? ' hatali' : ''}${f.tur === 'liste' ? ' genis' : ''}" data-alan="${f.k}">
      <label class="ay-etiket" for="${id}">${esc(f.etiket)}${farkli ? '<em title="Varsayılandan farklı">değişti</em>' : ''}</label>
      ${giris}${ipucu}${hataHtml}</div>`;
  }

  function ciz() {
    const { esc, ikon } = C();
    const kok = A.kok;
    if (!kok) return;
    if (!A.veri) {
      kok.innerHTML = A.hata
        ? `<div class="analiz"><div class="analiz-ic giris"><h2>Ayarlar alınamadı</h2><p>${esc(A.hata)}</p>
            <button class="btn-ikincil" type="button" data-ay-yenile>${ikon('i-refresh')}Tekrar dene</button></div></div>`
        : `<div class="analiz"><div class="analiz-ic giris"><div class="yukleyici"></div><h2>Ayarlar yükleniyor</h2><p>ayarlar.json okunuyor…</p></div></div>`;
      return;
    }
    const a = A.veri.ayarlar, vars = A.veri.varsayilan;
    const bolum = (b, i) => {
      const ic = `<div class="ay-izgara">${b.alanlar.map((f) => alanHtml(f, a, vars)).join('')}</div>`;
      const acik = b.alanlar.some((f) => A.alanHata[f.k] || (a[f.k] !== '' && a[f.k] != null));
      return `<section class="panel giris ay-bolum" style="--d:${60 * (i + 1)}ms">
        <div class="bas"><h2><span class="bas-no"><span>${b.no}</span></span>${esc(b.baslik)}</h2><span class="bas-ek">${esc(b.ek)}</span></div>
        ${b.gelismis ? `<details class="ay-gelismis"${acik ? ' open' : ''}><summary>Gelişmiş: araçları elle göster</summary>${ic}</details>` : ic}
      </section>`;
    };
    kok.innerHTML = `<form class="ay-form" id="ayForm" novalidate>
      <div class="ay-ust giris">
        <div><h1 class="ay-baslik">Ayarlar</h1>
          <p class="ay-aciklama">Değişiklikler <code>${esc(A.veri.dosya)}</code> dosyasına yazılır; bir sonraki analiz ve kayıtta kullanılır.</p></div>
        <button class="btn-ikincil" type="button" data-maca-don>${ikon('i-back')}Maçlara dön</button>
      </div>
      ${BOLUMLER.map(bolum).join('')}
      <div class="ay-dugmeler">
        <button class="btn-kaydet ay-kaydet" type="submit"${A.kaydediliyor ? ' disabled' : ''}>${A.kaydediliyor ? 'Kaydediliyor…' : 'Kaydet'}</button>
        <button class="btn-ikincil" type="button" data-ay-geri>${ikon('i-back')}Değişiklikleri geri al</button>
        <button class="btn-ikincil" type="button" data-ay-varsayilan>${ikon('i-refresh')}Varsayılanları doldur</button>
      </div>
    </form>`;
  }

  // Formdaki değerler; sayılar sunucuda da doğrulanır, burada yalnız tür çevrilir.
  function formOku() {
    const form = A.kok.querySelector('#ayForm');
    const out = {};
    for (const f of ALANLAR) {
      const el = form.elements[f.k];
      if (!el) continue;
      if (f.tur === 'acik') out[f.k] = el.checked;
      else if (f.tur === 'sayi') out[f.k] = el.value.trim() === '' ? '' : Number(el.value.replace(',', '.'));
      else if (f.tur === 'liste') out[f.k] = el.value.split(/\r?\n/).map((s) => s.trim()).filter(Boolean);
      else out[f.k] = el.value;
    }
    return out;
  }

  function formDoldur(a) {
    const form = A.kok.querySelector('#ayForm');
    for (const f of ALANLAR) {
      const el = form.elements[f.k];
      if (!el) continue;
      if (f.tur === 'acik') { el.checked = !!a[f.k]; anahtarYazi(el); } else el.value = deger(a, f.k) ?? '';
    }
  }

  function anahtarYazi(el) {
    const y = el.closest('.ay-anahtar')?.querySelector('.ay-anahtar-yazi');
    if (y) y.textContent = el.checked ? 'Açık' : 'Kapalı';
  }

  // Sunucu reddetmeden önce bariz hataları söyle (boş ad, aralık dışı sayı).
  function yerelDenetim(v) {
    const h = {};
    if (!String(v.oyuncu || '').trim()) h.oyuncu = 'Oyuncu adı boş olamaz.';
    if (!String(v.cikti_klasoru || '').trim()) h.cikti_klasoru = 'Klip klasörü boş olamaz.';
    for (const f of ALANLAR.filter((x) => x.tur === 'sayi')) {
      const n = v[f.k];
      if (n === '' || !Number.isFinite(n)) h[f.k] = 'Sayı olmalı.';
      else if (n < f.min || n > f.max) h[f.k] = `${f.min} ile ${f.max} arasında olmalı.`;
      else if (f.adim === 1 && !Number.isInteger(n)) h[f.k] = 'Tam sayı olmalı.';
    }
    return h;
  }

  function hatalariGoster() {
    for (const f of ALANLAR) {
      const kutu = A.kok.querySelector(`[data-alan="${f.k}"]`);
      if (!kutu) continue;
      const m = A.alanHata[f.k];
      kutu.classList.toggle('hatali', !!m);
      const el = kutu.querySelector('input, textarea');
      if (m) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid');
      const s = kutu.querySelector('.ay-hata');
      s.hidden = !m;
      s.textContent = m || '';
    }
    const ilk = ALANLAR.find((f) => A.alanHata[f.k]);
    if (ilk) {
      const det = A.kok.querySelector(`[data-alan="${ilk.k}"]`)?.closest('details');
      if (det) det.open = true;
      A.kok.querySelector(`[name="${ilk.k}"]`)?.focus();
    }
  }

  async function kaydet() {
    if (A.kaydediliyor) return;
    const { bildir } = C();
    const v = formOku();
    A.alanHata = yerelDenetim(v);
    if (Object.keys(A.alanHata).length) { hatalariGoster(); bildir('Kaydedilmedi: işaretli alanları düzelt.', 'hata'); return; }
    A.kaydediliyor = true;
    const dugme = A.kok.querySelector('.ay-kaydet');
    if (dugme) { dugme.disabled = true; dugme.textContent = 'Kaydediliyor…'; }
    try {
      const sonuc = await istek('POST', v);
      A.veri = sonuc;
      A.alanHata = {};
      A.kaydediliyor = false;
      ciz();
      const n = sonuc.yeniden_analiz || 0;
      bildir(n ? `Ayarlar kaydedildi. ${n} maçın analizi yeni ayarlarla yeniden yapılacak.` : 'Ayarlar kaydedildi.', 'basari');
      C().ayarlarKaydedildi(sonuc);
    } catch (e) {
      A.kaydediliyor = false;
      if (dugme) { dugme.disabled = false; dugme.textContent = 'Kaydet'; }
      A.alanHata = (e && e.veri && e.veri.alanlar) || {};
      hatalariGoster();
      const adlar = Object.keys(A.alanHata).map((k) => (ALANLAR.find((f) => f.k === k) || { etiket: k }).etiket);
      bildir('Kaydedilmedi: ' + (adlar.length ? 'işaretli alanları düzelt (' + adlar.join(', ') + ').'
        : (e && e.message ? e.message : 'bilinmeyen hata')), 'hata');
    }
  }

  async function yukle() {
    A.hata = null;
    try {
      A.veri = await istek('GET');
    } catch (e) {
      A.hata = e && e.status === 404
        ? 'Sunucu bu isteği tanımıyor (HTTP 404). Arayüz sunucusu bu özellikten önce başlatılmış olabilir: kapatıp arayuz.bat ile yeniden başlat.'
        : (e && e.message) || 'Bilinmeyen hata.';
    }
    if (location.hash === '#ayarlar') ciz();
  }

  function ac(kok) {
    A.kok = kok;
    A.alanHata = {};
    A.veri = null;
    ciz();
    yukle();
  }

  // Gezinme vurgusu: üst şerit ve kenar çubuğundaki "Ayarlar" bağlantıları.
  function isaretle() {
    const ac = location.hash === '#ayarlar';
    ['ustAyarlar', 'kenarAyarlar'].forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.classList.toggle('aktif', ac);
      if (ac) el.setAttribute('aria-current', 'page'); else el.removeAttribute('aria-current');
    });
  }
  addEventListener('hashchange', isaretle);
  addEventListener('DOMContentLoaded', isaretle);

  document.addEventListener('submit', (e) => {
    if (e.target.id !== 'ayForm') return;
    e.preventDefault();
    kaydet();
  });
  document.addEventListener('change', (e) => {
    if (e.target.closest && e.target.closest('#ayForm') && e.target.type === 'checkbox') anahtarYazi(e.target);
  });
  document.addEventListener('click', (e) => {
    const t = e.target;
    // zaten #ayarlar'dayken bağlantıya tekrar tıklamak sayfayı yeniden yükler
    if (t.closest('a[href="#ayarlar"]') && location.hash === '#ayarlar') { e.preventDefault(); ac(document.getElementById('ana')); return; }
    if (!A.kok || !A.kok.contains(t)) return;
    if (t.closest('[data-ay-yenile]')) { ac(A.kok); return; }
    if (t.closest('[data-ay-geri]') && A.veri) { A.alanHata = {}; hatalariGoster(); formDoldur(A.veri.ayarlar); C().bildir('Kaydedilmiş ayarlara dönüldü.'); return; }
    if (t.closest('[data-ay-varsayilan]') && A.veri) {
      A.alanHata = {};
      hatalariGoster();
      formDoldur({ ...A.veri.varsayilan, oyuncu: formOku().oyuncu }); // oyuncu adı başkasınınkiyle değişmesin
      C().bildir('Varsayılanlar dolduruldu; kalıcı olması için Kaydet\'e bas.');
    }
  });

  window.csklipAyarlar = { ac };
})();
