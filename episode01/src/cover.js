// Instagram cover: the three friends near the trip bus, Hind pleasantly surprised.
const { openPage, snapshot } = require('./engine');
const K = require('./scenes/kit');
const B = require('./environments/backgrounds');
const hind = require('./characters/hind'), loreen = require('./characters/loreen'), lizette = require('./characters/lizette');
(async () => {
  const { browser, page } = await openPage(1);
  const c = [540, 1020, 1.08];
  const inner = K.cam(c, K.bg('uni_plain', { blur: 2 }), 0.5) + K.cam(c, B.bus(-430, 900, 1.15, { doorOpen: true }), 0.8)
    + K.cam(c, lizette.draw({ x: 230, y: 1900, s: 0.6, turn: 0.4, look: [1, 0], smile: 0.85, smileEyes: 0.3 })
      + loreen.draw({ x: 850, y: 1910, s: 0.6, turn: -0.4, look: [-1, 0], smile: 0.95, brow: 0.4, armL: { a: 30, e: 120, hand: 'open' } })
      + hind.draw({ x: 545, y: 1960, s: 0.64, turn: 0.05, look: [0, -0.1], brow: 0.6, smile: 0.6, mouthO: 0.15, smileEyes: 0.1, armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } }))
    + K.rays(1.5) + K.grade({ warm: 0.12, leak: 0.45 })
    + `<rect width="1080" height="520" fill="url(#coverTop)"/>
       <defs><linearGradient id="coverTop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c1430" stop-opacity="0.85"/><stop offset="1" stop-color="#1c1430" stop-opacity="0"/></linearGradient></defs>`
    + K.textCard([{ y: 220, size: 104, text: 'سفرة ما چانت بالحسبان', fill: '#fff6e6' }, { y: 330, size: 62, text: 'الحلقة الأولى', fill: '#f2c879' }]);
  await snapshot(page, inner, 'output/Episode_01_Instagram_Cover.png', { wait: 300 });
  await browser.close();
})();
