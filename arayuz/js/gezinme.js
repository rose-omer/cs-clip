/* cs-klip arayüzü — Ayarlar görünümü ve bölüm gezinme vurgusu.
   Klasik betik: index.html'deki sırayla yüklenir, üst düzey adlar öteki dosyalarla ortaktır. */
'use strict';

/* ======== Ayarlar (#ayarlar): sayfayı arayuz/ayarlar.js çizer ======== */
function ayarlarAc() {
  gorunumAc(AYARLAR);
  if (window.csklipAyarlar) window.csklipAyarlar.ac($('#ana'));
  else hataCiz('Ayarlar açılamadı', 'ayarlar.js yüklenemedi; sayfayı yenile.', null);
}
// ayarlar.js'in kullandığı yardımcılar; kayıttan sonra demo listesi ve kontrol yenilenir.
window.csklip = {
  api, bildir, esc, ikon, ornek: ORNEK_MODU, SUNUCU_ESKI,
  ayarlarKaydedildi(sonuc) {
    if (sonuc && sonuc.yeniden_analiz) { S.demo = {}; S.klipler = {}; S.ei = null; }
    // Oyuncu ya da süreler değiştiyse "Herkes", seçili oyuncu ve kariyer eski kişiyi gösterir; ucuz, hep temizle.
    S.herkes = {}; S.herkesHata = {}; S.oyuncu = {}; S.kr = null; S.krHata = null;
    demolariYenile();
    kontrolYenile();
  },
};

/* ======== bölüm gezinme vurgusu ======== */
let gozlem = null;
function navGozlem() {
  if (gozlem) gozlem.disconnect();
  const linkler = $$('#bolumNav a');
  gozlem = new IntersectionObserver((girdiler) => {
    girdiler.forEach((g) => {
      if (!g.isIntersecting) return;
      linkler.forEach((a) => a.classList.toggle('aktif', a.getAttribute('href') === '#' + g.target.id));
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  ['ozet', 'tablo', 'roundlar', 'silahlar', 'klipler', 'isiHarita', 'herkes'].forEach((x) => { const el = document.getElementById(x); if (el) gozlem.observe(el); });
}
