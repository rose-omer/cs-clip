/* cs-klip arayüzü — demo yükleme (POST /api/yukle).
   Klasik betik: index.html'deki sırayla yüklenir, üst düzey adlar öteki dosyalarla ortaktır. */
'use strict';

/* ======== yükleme: POST /api/yukle ======== */
function dosyalariAl(liste) {
  const hepsi = [...liste];
  const uygun = hepsi.filter((f) => UZANTI.test(f.name));
  if (hepsi.length - uygun.length) bildir(`${hepsi.length - uygun.length} dosya atlandı: yalnız .dem, .dem.zst, .dem.gz, .dem.bz2`, 'hata');
  S.kuyruk.push(...uygun);
  kuyruguIsle();
}
function yuklemeDurum(ad, oran, alt, hata = false) {
  const kutu = $('#yukleme');
  kutu.hidden = false;
  kutu.classList.toggle('hata', hata);
  $('#yuklemeAd').textContent = ad;
  $('#yuklemeAd').title = ad;
  $('#yuklemeYuzde').textContent = hata ? 'Hata' : Math.floor(oran * 100) + '%';
  $('#yuklemeCubuk').style.width = (hata ? 100 : oran * 100) + '%';
  $('#yuklemeAlt').textContent = alt;
}
async function kuyruguIsle() {
  if (S.yukleniyor) return;
  S.yukleniyor = true;
  $('#yuklemeIptal').hidden = ORNEK_MODU; // örnek modda yükleme taklit edilir, iptal yok
  let sonId = null, hataVar = false;
  while (S.kuyruk.length) {
    const f = S.kuyruk.shift();
    const bas = Date.now();
    const mb = f.size / 1048576;
    const sirada = () => (S.kuyruk.length ? ` · sırada ${S.kuyruk.length} dosya` : '');
    yuklemeDurum(f.name, 0, `0 / ${sayi(mb, 1)} MB${sirada()}`);
    try {
      const sonuc = await yukleXhr(f, (yuklenen, toplam) => {
        const sn = (Date.now() - bas) / 1000;
        const hiz = sn > 0.3 ? ` · ${sayi(yuklenen / 1048576 / sn, 0)} MB/sn` : '';
        yuklemeDurum(f.name, yuklenen / toplam, `${sayi(yuklenen / 1048576, 1)} / ${sayi(toplam / 1048576, 1)} MB${hiz}${sirada()}`);
      });
      yuklemeDurum(f.name, 1, `${sayi(mb, 1)} MB yüklendi${sirada()}`);
      bildir(`${f.name} yüklendi.`, 'basari');
      sonId = (sonuc && sonuc.id) || sonId;
    } catch (e) {
      hataVar = true;
      yuklemeDurum(f.name, 0, e.message, true);
      bildir(`${f.name}: ${e.message}`, 'hata');
    }
  }
  S.yukleniyor = false;
  $('#yuklemeIptal').hidden = true;
  await demolariYenile();
  if (!hataVar) setTimeout(() => { if (!S.yukleniyor) $('#yukleme').hidden = true; }, 1500);
  if (sonId) demoSec(sonId); // yeni demo açılır; analiz edilmemişse sunucu analiz eder
}
