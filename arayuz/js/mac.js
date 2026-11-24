/* cs-klip arayüzü — demo seçimi ve maç sayfası: özet, skor tablosu, roundlar, silahlar.
   Klasik betik: index.html'deki sırayla yüklenir, üst düzey adlar öteki dosyalarla ortaktır. */
'use strict';

/* ======== demo seçimi (adres çubuğunda #demo-id) ======== */
function demoSec(id) {
  if (location.hash.slice(1) !== encodeURIComponent(id)) location.hash = encodeURIComponent(id);
  else demoAc(id);
}
function hashtenAc() {
  let id = '';
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { /* bozuk adres */ }
  if (!$('#modal').hidden) oynaticiKapat(); // oynatıcıdaki "Maça git" bağlantısı
  if (id === EN_IYI) enIyiAc();
  else if (id === AYARLAR) ayarlarAc();
  else if (id === KARIYER) kariyerAc();
  else if (id) demoAc(id);
  else { // geri tuşuyla boş adrese dönüldü: son maçı (yoksa ilk analiz edilmiş maçı) aç
    const son = S.sonDemo || (S.demolar.find((d) => d.analiz_edildi) || {}).id;
    if (son) { history.replaceState(null, '', '#' + encodeURIComponent(son)); demoAc(son); } else bosCiz();
  }
}

async function demoAc(id) {
  const no = ++S.istekNo;
  S.gorunum = 'mac';
  S.secili = id;
  S.sonDemo = id;
  gezinCiz();
  S.sira = { k: 'rating', az: true };
  menuAc(false);
  ipucuGizle();
  scrollTo({ top: 0, behavior: kaydir() });
  const d = S.demolar.find((x) => x.id === id);
  if (S.demo[id]) {
    listeCiz();
    anaCiz();
    klipleriYukle(id, no);
    return;
  }
  const ilk = !d || !d.analiz_edildi;
  if (ilk && d) S.analizde.add(id);
  listeCiz();
  beklemeCiz(d, ilk);
  const bas = Date.now();
  const sayac = setInterval(() => {
    const el = $('#analizAdim');
    if (!el || no !== S.istekNo) return;
    const sn = Math.floor((Date.now() - bas) / 1000);
    el.textContent = ilk
      ? `${sn} sn${sn > 60 ? ' · hâlâ çalışıyor, büyük demolar daha uzun sürebilir' : ' · ilk analiz 20–40 saniye sürebilir'}`
      : (sn >= 2 ? `${sn} sn` : '');
  }, 500);
  let s;
  try {
    s = await api(demoYol(id));
  } catch (e) {
    S.analizde.delete(id);
    listeCiz();
    if (no !== S.istekNo) return;
    hataCiz('Demo açılamadı', e.message, id);
    return;
  } finally {
    clearInterval(sayac);
  }
  S.analizde.delete(id);
  S.demo[id] = s;
  if (ilk && d) {
    d.analiz_edildi = true;
    d.harita = s.harita || d.harita;
    bildir(`${haritaAd(s.harita) || 'Demo'} analiz edildi.`, 'basari');
    demolariYenile();
  }
  listeCiz();
  if (no !== S.istekNo) return;
  anaCiz();
  klipleriYukle(id, no);
}

function beklemeCiz(d, ilk) {
  $('#ana').innerHTML = `<div class="analiz"><div class="analiz-ic giris">
    <div class="yukleyici"></div>
    <h2>${ilk ? 'Demo analiz ediliyor' : 'İstatistikler yükleniyor'}</h2>
    <p>${d ? `${esc(d.ad)} · ${sayi(d.boyut_mb, 1)} MB` : 'Demo aranıyor…'}</p>
    <div class="il-bar belirsiz"><i></i></div>
    <div class="analiz-adim" id="analizAdim">${ilk ? 'Sunucu demoyu ayrıştırıyor…' : ''}</div></div></div>`;
}
function hataCiz(baslik, mesaj, id) {
  $('#ana').innerHTML = `<div class="analiz"><div class="analiz-ic giris">
    <h2>${esc(baslik)}</h2><p>${esc(mesaj)}</p>
    ${id ? `<button class="btn-ikincil" type="button" data-tekrar="${esc(id)}">${ikon('i-refresh')}Tekrar dene</button>` : ''}</div></div>`;
}
function bosCiz() {
  $('#ana').innerHTML = `<div class="analiz"><div class="analiz-ic giris">
    <h2>Bir demo seç</h2>
    <p>${S.demolar.length ? 'Soldaki listeden bir demo seç. Analiz edilmemiş demolar ilk açılışta analiz edilir.' : 'Henüz demo yok. Bir .dem dosyasını sürükleyip bırak ya da “Demo yükle”ye tıkla.'}</p>
    <button class="btn-ikincil" type="button" id="bosYukle">${ikon('i-upload')}Demo yükle</button></div></div>`;
}

/* ======== ana içerik ======== */
function anaCiz() {
  const id = S.secili;
  const s = S.demo[id];
  const d = S.demolar.find((x) => x.id === id);
  const ben = benBul(s);
  const klip = S.klipler[id];
  $('#ana').innerHTML = `
    ${skorBandi(s, d)}
    <nav class="bolum-nav" id="bolumNav" aria-label="Bölümler">
      <a href="#ozet" class="aktif">Özet</a><a href="#tablo">Skor tablosu</a><a href="#roundlar">Roundlar</a><a href="#silahlar">Silahlar</a>
      <a href="#klipler">Klipler <em id="navKlipSay">${klip ? (klip.highlightlar || []).length : '…'}</em></a>
      <a href="#isiHarita">Derin analiz</a>
      <a href="#herkes">Herkes</a>
    </nav>
    ${ben ? spotHtml(ben, s) : '<section class="panel" id="ozet"><p class="bos-not">Bu demoda oyuncu bulunamadı (oyuncu_steamid eşleşmedi).</p></section>'}
    <section class="panel giris" id="tablo" style="--d:120ms">
      <div class="bas"><h2><span class="bas-no"><span>02</span></span>Skor tablosu</h2><span class="bas-ek">Sıralamak için başlığa, ${EN('highlight')}'ları için oyuncuya tıkla</span></div>
      <div class="tablolar" id="tablolar"></div>
      <div class="tablo-not"><span lang="en">Rating</span>: <span class="renk-iyi">≥ 1,10 iyi</span> · 0,90–1,09 ortalama · <span class="renk-kotu">&lt; 0,90 zayıf</span> &nbsp;·&nbsp; ADR ve KAST eşik renkli.</div>
    </section>
    <section class="panel giris" id="roundlar" style="--d:160ms">
      <div class="bas"><h2><span class="bas-no"><span>03</span></span>Round geçmişi</h2><span class="bas-ek">${s.round_sayisi ?? (s.roundlar || []).length} round · üzerine gel</span></div>
      ${zamanHtml(s)}
    </section>
    <div class="ikili">
      <section class="panel giris" id="silahlar" style="--d:200ms">
        <div class="bas"><h2><span class="bas-no"><span>04</span></span>Silah dağılımı</h2><span class="bas-ek">headshot / diğer</span></div>
        ${silahHtml(s.silahlar || [])}
      </section>
      <section class="panel giris" style="--d:240ms">
        <div class="bas"><h2><span class="bas-no"><span>05</span></span>Round istatistikleri</h2><span class="bas-ek">${esc(ben ? ben.ad : '')}</span></div>
        ${roundIstHtml(s, ben)}
      </section>
    </div>
    <section class="panel giris" id="klipler" style="--d:280ms">
      <div class="bas"><h2><span class="bas-no"><span>06</span></span><span lang="en">Highlight</span>&nbsp;klipleri</h2><span class="bas-ek" id="klipOzet"></span></div>
      <div class="oyuncu-sec" id="oyuncuSec"></div>
      <div class="kayit">
        <div class="kayit-sol">
          <div class="kayit-satir"><span class="kayit-et">Kaydedilecek</span>
            <div class="secim" id="kayitSecim" role="radiogroup" aria-label="Kaç klip kaydedilsin">
              ${[[3, '3'], [5, '5'], [0, 'Hepsi']].map(([n, ad]) => `<button type="button" role="radio" data-n="${n}" class="${S.enIyi === n ? 'aktif' : ''}" aria-checked="${S.enIyi === n}">${n ? 'En iyi ' : ''}${ad}</button>`).join('')}
            </div></div>
          <button class="btn-kaydet" id="kaydet" type="button"><span class="rec"></span><span id="kaydetMetin">Klipleri kaydet</span> <small id="kaydetAlt"></small></button>
          <div class="kayit-bilgi">${ORNEK_MODU ? '<b>Örnek mod:</b> kayıt taklit edilir, CS2 açılmaz. ' : ''}Kayıt CS2'yi açar ve demoyu <span id="kimGozu">senin</span> gözünden oynatır; bitene kadar bilgisayarı kullanma. Başlamadan önce FACEIT ve CS2 kapalı olmalı. Klipler çıktı klasörüne (<code>klipler</code>) MP4 olarak yazılır; var olanlar atlanır.</div>
        </div>
        <div class="kontrol" id="kontrolKutu"></div>
        <div class="ilerleme" id="ilerleme" hidden></div>
      </div>
      <div class="klip-izgara" id="klipIzgara"></div>
    </section>
    ${derinHtml(s)}
    <section class="panel giris" id="herkes" style="--d:320ms">
      <div class="bas"><h2><span class="bas-no"><span>${derinVar(s) ? '10' : '08'}</span></span>Herkesin en iyi anı</h2><span class="bas-ek" id="herkesOzet">Maçtaki her oyuncunun en yüksek puanlı anı</span></div>
      <div id="herkesListe"></div>
    </section>`;
  tablolariCiz();
  derinCiz();
  oyuncuSecCiz();
  kontrolCiz();
  kayitCiz();
  klipleriCiz();
  herkesCiz();
  if (!S.herkes[id] && !S.herkesHata[id]) herkesYukle(id);
  sayaclar($('#ana'));
  navGozlem();
}

function skorBandi(s, d) {
  const biz = s.benim_takim ?? 0;
  const T = taraflar(s);
  const R = [...(s.roundlar || [])].sort((a, b) => a.no - b.no);
  const ilkNo = R.length ? R[0].no : 1;
  const bizBas = takimTaraf(T, biz, ilkNo), onBas = karsi(bizBas);
  const TK = takimlarOf(s);
  const bT = TK[biz], oT = TK[1 - biz];
  const sonuc = bT.skor > oT.skor ? ['galibiyet', 'Galibiyet'] : bT.skor < oT.skor ? ['maglubiyet', 'Mağlubiyet'] : ['berabere', 'Berabere'];
  const yarilar = {};
  const yu = yariUzunlugu(s);
  R.forEach((r) => { const g = yariNo(r.no, yu); yarilar[g] = yarilar[g] || [0, 0]; yarilar[g][r.kazanan_takim === biz ? 0 : 1]++; });
  const yariHtml = Object.keys(yarilar).map(Number).sort((a, b) => a - b).map((g) =>
    `<span class="yari">${esc(yariAd(g))} <strong>${yarilar[g][0]}–${yarilar[g][1]}</strong></span>`).join('');
  const ad = haritaAd(s.harita) || 'Bilinmeyen';
  const takim = (t, yan, sinif, etiket) => `<div class="sb-takim ${sinif}" style="--c:${tarafRenk(yan)};--ca:${tarafAlfa(yan)}">
      <span class="sb-yan">${yan.toUpperCase()}</span>
      <div class="sb-isim"><div class="sb-ad" lang="en">${esc(t.ad)}</div><div class="sb-alt">${etiket} · <b>${yan.toUpperCase()}</b> başladı</div></div></div>`;
  return `<section class="sb" id="mac" style="${haritaStil(s.harita)}">
    <div class="sb-zemin"></div><div class="sb-filigran" lang="en">${esc(ad)}</div>
    <div class="sb-ust"><span class="sb-etiket">Maç sonu</span><span>Demo analizi</span><span class="ayir"></span><span>${esc(tarihYaz(d && d.tarih, true))}</span>
      ${benBul(s) ? `<span class="ust-bosluk"></span><button class="btn-ikincil sb-paylas" type="button" data-kart-ac>${ikon('i-share')}Kartı paylaş</button>` : ''}</div>
    <div class="sb-bant">
      ${takim(bT, bizBas, 'sol', 'Senin takımın')}
      <div class="sb-skor sol${bT.skor > oT.skor ? ' kazandi' : ''}" style="--c:${tarafRenk(bizBas)}" data-say="${bT.skor}">${bT.skor}</div>
      <div class="sb-orta"><div class="sb-harita" lang="en">${esc(ad)}</div><div class="sb-not">${s.round_sayisi ?? R.length} round</div></div>
      <div class="sb-skor sag${oT.skor > bT.skor ? ' kazandi' : ''}" style="--c:${tarafRenk(onBas)}" data-say="${oT.skor}">${oT.skor}</div>
      ${takim(oT, onBas, 'sag', 'Rakip')}
    </div>
    <div class="altbant"><span class="ab-sonuc ${sonuc[0]}">${sonuc[1]}</span>
      <span class="ab-metin"><span><b>${esc(bT.ad)}</b> ${bT.skor}–${oT.skor} <b>${esc(oT.ad)}</b></span>${yariHtml}</span>
      <span class="ab-tarih">${d ? esc(((d.ad || '').match(UZANTI) || ['.dem'])[0]) + ' · ' + sayi(d.boyut_mb, 1) + ' MB' : ''}</span></div>
  </section>`;
}

function spotHtml(o, s) {
  const lobi = s.oyuncular || [];
  const sira = (k) => 1 + lobi.filter((x) => (x[k] ?? -1) > (o[k] ?? -1)).length;
  const ort = (k) => lobi.reduce((a, x) => a + (x[k] || 0), 0) / (lobi.length || 1);
  const aralik = (k) => { const v = lobi.map((x) => x[k] || 0); return [Math.min(...v), Math.max(...v)]; };
  const yuzde = (k, v) => { const [a, b] = aralik(k); return b > a ? sinirla((v - a) / (b - a) * 100, 3, 100) : 50; };
  const mvp = lobi.length && lobi.every((x) => x.rating <= o.rating);
  const rs = ratingSinif(o.rating);
  const rP = sinirla((o.rating - 0.4) / (1.8 - 0.4) * 100, 2, 100);
  const fark = o.kill - o.death;
  const tile = (ad, degerHtml, k, iyi, kotu, o2 = 1) => {
    const v = o[k];
    return `<div class="tile ${esik(v, iyi, kotu)}">
      <div class="tile-ad">${ad}</div>
      <div class="tile-deger">${degerHtml}</div>
      <div class="tile-olcek"><i style="--p:${yuzde(k, v)}%"></i><b style="--p:${yuzde(k, ort(k))}%" title="Lobi ortalaması"></b></div>
      <div class="tile-alt"><span>Lobide <b>${sira(k)}.</b> / ${lobi.length}</span><span>ort. ${sayi(ort(k), o2)}</span></div></div>`;
  };
  const ak = o.acilis_kill ?? 0, ad = o.acilis_death ?? 0, at = Math.max(ak + ad, 1);
  const ck = o.cok_kill || {};
  return `<section class="panel giris" id="ozet" style="--d:60ms">
    <div class="bas"><h2><span class="bas-no"><span>01</span></span>Oyuncu özeti</h2><span class="bas-ek">Lobi: ${lobi.length} oyuncu</span></div>
    <div class="spot">
      <div class="hero ${rs}">
        <div class="hero-ust"><span class="cip or">Sen</span>${mvp ? '<span class="cip yildiz">Maçın yıldızı</span>' : ''}<span class="cip">Lobide ${sira('rating')}. / ${lobi.length}</span></div>
        <div class="hero-ad">${esc(o.ad)}</div>
        <div class="hero-sid">${esc(o.steamid)}</div>
        <div class="hero-rating"><span class="hero-sayi" data-say="${o.rating}" data-o="2">${sayi(o.rating, 2)}</span>
          <span class="hero-rl"><span lang="en">Rating</span><small>HLTV 1.0 tarzı</small></span></div>
        <div class="olcek"><i style="--p:${rP}%"></i>
          <span class="cizgi" style="left:${(0.9 - 0.4) / 1.4 * 100}%"></span><span class="cizgi" style="left:${(1.1 - 0.4) / 1.4 * 100}%"></span></div>
        <div class="olcek-yazi"><span>0,40</span><span>0,90</span><span>1,10</span><span>1,80</span></div>
        <div class="hero-alt">
          <div>K / D / A<b>${o.kill}<small>/</small>${o.death}<small>/</small>${o.assist}</b></div>
          <div>Fark<b class="${fark > 0 ? 'renk-iyi' : fark < 0 ? 'renk-kotu' : ''}">${fark > 0 ? '+' : ''}${fark}</b></div>
          <div>Lobi ort.<b>${sayi(ort('rating'), 2)}</b></div>
        </div>
      </div>
      <div class="tiles">
        ${tile('ADR', `<span data-say="${o.adr}" data-o="1">${sayi(o.adr, 1)}</span>`, 'adr', 85, 65)}
        ${tile('KAST', `<span data-say="${o.kast}" data-o="1">${sayi(o.kast, 1)}</span><small>%</small>`, 'kast', 75, 65)}
        ${tile('K/D', `<span data-say="${o.kd}" data-o="2">${sayi(o.kd, 2)}</span>`, 'kd', 1.1, 0.9, 2)}
        ${tile('Headshot', `<span data-say="${o.hs_yuzde}" data-o="1">${sayi(o.hs_yuzde, 1)}</span><small>%</small>`, 'hs_yuzde', 50, 30)}
        <div class="tile ${ak > ad ? 'iyi' : ak < ad ? 'kotu' : 'orta'}">
          <div class="tile-ad">Açılış düelloları</div>
          <div class="tile-deger">${ak}<span class="ayr">–</span>${ad}</div>
          <div class="duello"><i class="k" style="width:${ak / at * 100}%"></i><i class="d" style="width:${ad / at * 100}%"></i>${ak + ad ? '' : '<i class="n"></i>'}</div>
          <div class="tile-alt"><span>kazanılan – kaybedilen</span><span>%${sayi(ak / at * 100)}</span></div>
        </div>
        <div class="tile orta">
          <div class="tile-ad">Çoklu ${EN('kill')}</div>
          <div class="coklu">${[['2', '2K'], ['3', '3K'], ['4', '4K'], ['5', 'ACE']].map(([k, a]) => `<span class="${ck[k] ? 'var' : ''}"><b>${ck[k] || 0}</b>${a}</span>`).join('')}</div>
          <div class="tile-alt"><span>round sayısı</span><span>toplam ${Object.values(ck).reduce((a, b) => a + (b || 0), 0)}</span></div>
        </div>
      </div>
    </div>
  </section>`;
}

const SUTUNLAR = [
  ['ad', 'Oyuncu', ''], ['kill', 'K', ''], ['death', 'D', ''], ['assist', 'A', 'gz-a'], ['fark', '+/−', 'gz-b'],
  ['adr', 'ADR', ''], ['hs_yuzde', 'HS%', 'gz-a'], ['kast', 'KAST', ''], ['rating', EN('Rating'), ''],
];
function tablolariCiz() {
  const kutu = $('#tablolar');
  const s = S.demo[S.secili];
  if (!kutu || !s) return;
  const biz = s.benim_takim ?? 0;
  const T = taraflar(s);
  const R = [...(s.roundlar || [])].sort((a, b) => a.no - b.no);
  const ilkNo = R.length ? R[0].no : 1;
  const { k, az } = S.sira;
  const deger = (o, a) => (a === 'fark' ? o.kill - o.death : o[a]);
  const sirala = (x, y) => {
    const c = k === 'ad' ? String(x.ad).localeCompare(String(y.ad), 'tr') : (deger(x, k) ?? -1) - (deger(y, k) ?? -1);
    return az ? -c : c;
  };
  const TK = takimlarOf(s);
  const birden = TK.some((t) => t.kazandi);
  kutu.innerHTML = [biz, 1 - biz].map((t) => {
    const takim = TK[t];
    const yan = takimTaraf(T, t, ilkNo);
    const oy = (s.oyuncular || []).filter((o) => o.takim === t).sort(sirala);
    return `<div style="--c:${tarafRenk(yan)};--ca:${tarafAlfa(yan)}">
      <div class="takim-bas"><span class="takim-skor">${takim.skor}</span><span class="takim-ad" lang="en">${esc(takim.ad)}</span>
        <span class="cip ${takim.kazandi ? 'g' : birden ? 'm' : ''}">${t === biz ? 'Senin takımın' : 'Rakip'} · ${takim.kazandi ? 'G' : birden ? 'M' : 'B'}</span></div>
      <div class="tablo-sar"><table>
        <thead><tr>${SUTUNLAR.map(([a, ad, g]) => `<th data-sira="${a}" class="${g} ${a === k ? 'sirali' + (az ? '' : ' artan') : ''}" scope="col" tabindex="0" aria-sort="${a === k ? (az ? 'descending' : 'ascending') : 'none'}">${ad}</th>`).join('')}</tr></thead>
        <tbody>${oy.map((o) => {
          const f = o.kill - o.death;
          const secili = String((gosterilen(S.secili) || {}).steamid) === String(o.steamid);
          return `<tr class="${o.ben ? 'ben' : ''} secilebilir${secili ? ' secili' : ''}" data-oyuncu="${esc(o.steamid)}" tabindex="0"
              title="${esc(o.ad)} · ${esc(o.steamid)}\nHighlight'larını göstermek için tıkla">
            <td><span class="oy"><span>${esc(o.ad)}</span>${o.ben ? '<span class="cip or">Sen</span>' : ''}${secili && !o.ben ? '<span class="cip secildi">Seçili</span>' : ''}</span></td>
            <td class="k">${o.kill}</td><td class="soluk">${o.death}</td><td class="soluk gz-a">${o.assist}</td>
            <td class="gz-b ${f > 0 ? 'fark-a' : f < 0 ? 'fark-e' : 'soluk'}">${f > 0 ? '+' : ''}${f}</td>
            <td class="${{ iyi: 'renk-iyi', kotu: 'renk-kotu', orta: '' }[esik(o.adr, 85, 65)]}">${sayi(o.adr, 1)}</td>
            <td class="gz-a">${sayi(o.hs_yuzde, 0)}%</td>
            <td class="${{ iyi: 'renk-iyi', kotu: 'renk-kotu', orta: '' }[esik(o.kast, 75, 65)]}">${sayi(o.kast, 1)}%</td>
            <td><span class="rozet ${ratingSinif(o.rating)}">${sayi(o.rating, 2)}</span></td></tr>`;
        }).join('')}</tbody></table></div></div>`;
  }).join('');
}

function zamanHtml(s) {
  const biz = s.benim_takim ?? 0;
  const T = taraflar(s);
  const R = [...(s.roundlar || [])].sort((a, b) => a.no - b.no);
  if (!R.length) return '<p class="bos-not">Round bilgisi yok.</p>';
  const gruplar = {};
  const yu = yariUzunlugu(s);
  R.forEach((r) => { (gruplar[yariNo(r.no, yu)] = gruplar[yariNo(r.no, yu)] || []).push(r); });
  const html = Object.keys(gruplar).map(Number).sort((a, b) => a - b).map((g) => {
    const rs = gruplar[g];
    const bizT = takimTaraf(T, biz, rs[0].no), onT = karsi(bizT);
    const bizSkor = rs.filter((r) => r.kazanan_takim === biz).length;
    let h = `<div class="tl-grup"><div class="tl-bas"><span>${esc(yariAd(g))}</span>
      <span class="tl-bas-skor"><b class="${bizT}">${bizSkor}</b> – <b class="${onT}">${rs.length - bizSkor}</b></span>
      <span class="tl-bas-r">R${rs[0].no}–${rs[rs.length - 1].no}</span></div>
      <div class="tl-izgara" style="--n:${rs.length}">
        <span class="tl-et ${bizT}"><b>Biz</b><small>${bizT.toUpperCase()}</small></span>
        <span class="tl-et ${onT}"><b>Rakip</b><small>${onT.toUpperCase()}</small></span>
        <span class="tl-et2" lang="en">Kill</span><span class="tl-et2">Ölüm</span><span class="tl-et2">#</span>`;
    rs.forEach((r) => {
      const kaz = r.kazanan_takim === biz;
      const w = kazananTaraf(r) || (kaz ? bizT : onT);
      const svg = ikon(IKON[r.neden] || 'i-elim');
      const tip = esc(`Round ${r.no} · ${kaz ? 'Kazandınız' : 'Kaybettiniz'}\n${nedenAd(r.neden)} (${w.toUpperCase()})\n${r.benim_kill ? r.benim_kill + ' kill' : 'Kill yok'} · ${r.ben_oldum ? 'Öldün' : 'Hayatta kaldın'}`);
      const at = `data-r="${r.no}" data-tip="${tip}"`;
      h += `<span class="tl-k${kaz ? ' dolu ' + w : ''}" ${at}>${kaz ? svg : ''}</span>`;
      h += `<span class="tl-k${!kaz ? ' dolu ' + w : ''}" ${at}>${!kaz ? svg : ''}</span>`;
      h += `<span class="tl-kill k${Math.min(r.benim_kill || 0, 5)}" ${at}>${r.benim_kill || ''}</span>`;
      h += `<span class="tl-olum ${r.ben_oldum ? 'oldu' : 'yasadi'}" ${at}>${r.ben_oldum ? ikon('i-x', '') : ''}</span>`;
      h += `<span class="tl-no" data-r="${r.no}">${r.no}</span>`;
    });
    return h + '</div></div>';
  }).join('');
  return `<div class="tl-gruplar">${html}</div>
    <div class="lejant">
      <span><i style="background:var(--ct)"></i>CT kazandı</span><span><i style="background:var(--t)"></i>T kazandı</span>
      <span>${ikon('i-elim', '')}Eleme</span><span>${ikon('i-bomb', '')}Bomba patladı</span><span>${ikon('i-defuse', '')}İmha</span><span>${ikon('i-time', '')}Süre doldu</span>
      <span><b>3</b> senin ${EN('kill')} sayın</span><span><svg style="fill:var(--kotu)"><use href="#i-x"/></svg>öldün</span>
    </div>`;
}

function silahHtml(liste) {
  if (!liste.length) return `<p class="bos-not">Bu maçta ${EN('kill')} yok.</p>`;
  const l = [...liste].sort((a, b) => b.kill - a.kill);
  const enCok = Math.max(...l.map((x) => x.kill), 1);
  const top = l.reduce((a, x) => a + x.kill, 0), hsTop = l.reduce((a, x) => a + Math.min(x.hs || 0, x.kill), 0);
  return `<div class="silah-ozet"><b>${top}</b> ${EN('kill')} · ${hsTop} ${EN('headshot')} (%${sayi(hsTop / Math.max(top, 1) * 100)})</div>
    ${l.map((x, i) => {
      const hs = Math.min(x.hs || 0, x.kill);
      return `<div class="sl" data-tip="${esc(`${silahAd(x.silah)}\n${x.kill} kill · ${hs} headshot`)}">
        <div class="sl-ust"><span class="sl-ad" lang="en">${esc(silahAd(x.silah))}</span><span class="sl-tur">${esc(silahTur(x.silah))}</span>
          <span class="sl-sayi"><b>${x.kill}</b> ${EN('kill')}${hs ? ` · ${hs} HS` : ''}</span></div>
        <div class="sl-bar" style="--d:${i * 70}ms"><i class="hs" style="width:${hs / enCok * 100}%;animation-delay:${i * 70}ms"></i><i class="gv" style="width:${(x.kill - hs) / enCok * 100}%;animation-delay:${i * 70 + 120}ms"></i></div></div>`;
    }).join('')}
    <div class="lejant"><span><i style="background:var(--or)"></i>${EN('Headshot')}</span><span><i style="background:#56607a"></i>Diğer</span></div>`;
}

function roundIstHtml(s, ben) {
  const biz = s.benim_takim ?? 0;
  const R = [...(s.roundlar || [])].sort((a, b) => a.no - b.no);
  const n = s.round_sayisi || R.length || 1;
  const yasadi = R.filter((r) => !r.ben_oldum).length;
  const killRound = R.filter((r) => r.benim_kill > 0).length;
  const enIyi = R.reduce((a, r) => (r.benim_kill > (a ? a.benim_kill : 0) ? r : a), null);
  let seri = 0, enUzun = 0;
  R.forEach((r) => { seri = r.kazanan_takim === biz ? seri + 1 : 0; enUzun = Math.max(enUzun, seri); });
  const pistol = R.filter((r) => r.no === 1 || r.no === yariUzunlugu(s) + 1);
  return `<div class="ri">
    <div class="ri-oge"><div class="ri-ad">Round başına ${EN('kill')}</div><div class="ri-deger">${sayi(ben ? ben.kill / n : 0, 2)}</div><div class="ri-alt">ölüm/round ${sayi(ben ? ben.death / n : 0, 2)}</div></div>
    <div class="ri-oge"><div class="ri-ad">Hayatta kaldın</div><div class="ri-deger">${yasadi}<small> / ${R.length}</small></div><div class="ri-alt">roundların %${sayi(yasadi / Math.max(R.length, 1) * 100)}'i</div></div>
    <div class="ri-oge"><div class="ri-ad">${EN('Kill')} aldığın round</div><div class="ri-deger">${killRound}<small> / ${R.length}</small></div><div class="ri-alt">${enIyi ? `en iyisi R${enIyi.no}: ${enIyi.benim_kill} kill` : 'kill yok'}</div></div>
    <div class="ri-oge"><div class="ri-ad">En uzun seri</div><div class="ri-deger">${enUzun}<small> round</small></div><div class="ri-alt">takımının art arda galibiyeti</div></div>
    <div class="ri-oge" style="grid-column:1/-1"><div class="ri-ad">Tabanca roundları</div>
      <div class="pistol">${pistol.map((r) => { const g = r.kazanan_takim === biz; return `<span class="${g ? 'G' : 'M'}">R${r.no} · ${r.benim_kill} kill<b>${g ? 'Kazanıldı' : 'Kaybedildi'}</b></span>`; }).join('') || '<span>—</span>'}</div></div>
  </div>`;
}
