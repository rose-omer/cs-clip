/* cs-klip arayüzü — olay dinleyicileri ve başlatma (en son yüklenir).
   Klasik betik: index.html'deki sırayla yüklenir, üst düzey adlar öteki dosyalarla ortaktır. */
'use strict';

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
  const eiOy = t.closest('[data-ei-oyuncu]');
  if (eiOy) { S.eiOyuncu = eiOy.dataset.eiOyuncu; S.eiOyuncuElle = true; enIyiCiz(); return; }
  const eiH = t.closest('[data-ei-harita]');
  if (eiH) { S.eiHarita = eiH.dataset.eiHarita; vitrinCiz(); return; }
  const eiA = t.closest('[data-ei-adet]');
  if (eiA) { S.eiAdet = +eiA.dataset.eiAdet; vitrinCiz(); return; }
  const mjA = t.closest('[data-mj-adet]');
  if (mjA) { if (!mjA.disabled) { S.mjAdet = +mjA.dataset.mjAdet; montajCiz(); } return; }
  const mjS = t.closest('[data-mj-sec]');
  if (mjS) {
    if (!mjS.disabled) { const k = mjS.dataset.mjSec; S.mjSec[k] = k === 'dikey' ? mjS.dataset.v === 'true' : mjS.dataset.v; montajCiz(); }
    return;
  }
  const mjAc = t.closest('[data-mj-ac]');
  if (mjAc) { if (!mjAc.disabled) { S.mjSec[mjAc.dataset.mjAc] = !S.mjSec[mjAc.dataset.mjAc]; montajCiz(); } return; }
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
  const oySec = t.closest('[data-oyuncu-sec]');
  if (oySec) { if (!oySec.disabled) oyuncuSec(oySec.dataset.oyuncuSec, true); return; }
  const satir = t.closest('#tablolar tr[data-oyuncu]');
  if (satir) { oyuncuSec(satir.dataset.oyuncu, true); return; }
  const hkO = t.closest('[data-herkes-oynat]');
  if (hkO) { herkesOynat(+hkO.dataset.herkesOynat, hkO); return; }
  if (t.closest('[data-herkes-tekrar]')) { herkesYukle(S.secili); herkesCiz(); return; }
  const n = t.closest('#kayitSecim button[data-n]');
  if (n && !n.disabled) { S.enIyi = +n.dataset.n; $$('#kayitSecim button').forEach((b) => { b.classList.toggle('aktif', b === n); b.setAttribute('aria-checked', String(b === n)); }); kayitCiz(); return; }
  if (t.closest('#kaydet')) { kaydet(); return; }
  if (t.closest('#kayitDurdur')) { kaydiDurdur(); return; }
  if (t.closest('#yuklemeIptal')) { S.kuyruk = []; if (yuklemeXhr) yuklemeXhr.abort(); return; }
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
    if (e.key === 'Home' && e.target.id === 'oyCubuk') { e.preventDefault(); oynatAtla(0); return; }
    if (e.key === 'End' && e.target.id === 'oyCubuk') { e.preventDefault(); oynatAtla(1); return; }
  }
  // role=radio grupları: ok tuşlarıyla seçenekler arasında gezin (WAI-ARIA radiogroup)
  const radyo = e.target.closest && e.target.closest('[role=radiogroup] [role=radio]');
  if (radyo && ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
    const l = [...radyo.closest('[role=radiogroup]').querySelectorAll('[role=radio]:not([disabled])')];
    const i = l.indexOf(radyo);
    if (i < 0 || !l.length) return;
    const yeni = l[(i + (e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 1) + l.length) % l.length];
    e.preventDefault();
    const grup = yeni.closest('[role=radiogroup]').getAttribute('aria-label'), metin = yeni.textContent;
    yeni.click();
    // tıklama grubu yeniden çizmiş olabilir: aynı gruptaki aynı yazılı düğmeye odaklan
    const hedef = yeni.isConnected ? yeni : [...document.querySelectorAll('[role=radiogroup] [role=radio]')]
      .find((b) => b.closest('[role=radiogroup]').getAttribute('aria-label') === grup && b.textContent === metin);
    if (hedef) hedef.focus();
    return;
  }
  if ((e.key === 'Enter' || e.key === ' ') && e.target === $('#birak')) { e.preventDefault(); $('#dosyaSec').click(); return; }
  if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('th[data-sira]')) { e.preventDefault(); siralaDegis(e.target); }
  if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('#tablolar tr[data-oyuncu]')) { e.preventDefault(); oyuncuSec(e.target.dataset.oyuncu, true); }
});
document.addEventListener('change', (e) => {
  if (e.target && e.target.id === 'oyuncuListe') oyuncuSec(e.target.value);
});
// Montaj seçeneklerindeki metin kutuları: yalnız durumu güncelle (yeniden çizmek odağı kaçırır).
document.addEventListener('input', (e) => {
  const el = e.target.closest && e.target.closest('[data-mj-in]');
  if (el) S.mjSec[el.dataset.mjIn] = el.value;
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
  otoYenile();
  setInterval(() => { if (document.visibilityState === 'visible') otoYenile(false); }, 5000);
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
