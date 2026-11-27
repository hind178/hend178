const { openPage, snapshot } = require('../src/engine');
const hind = require('../src/characters/hind');
(async () => {
  const { browser, page } = await openPage(1);
  const bg = '<rect width="1080" height="1920" fill="#efe6de"/>';
  const a = hind.draw({ x: 300, y: 1800, s: 0.55, smile: 0.5 });
  const b = hind.draw({ x: 780, y: 1800, s: 0.55, turn: 0.6, look: [1, 0], tilt: 4, brow: 0.6, smile: -0.1, mouthO: 0.6, armR: { a: 25, e: 150, hand: 'open' }, armL: { a: -5, e: -70, hand: 'grip' }, tag: 'h2' });
  await snapshot(page, bg + a + b.replace(/hind/g, 'hindB').replace(/url\(#hindB(Limb|LimbV|Face|Neck)\)/g, 'url(#hind$1)'), process.argv[2]);
  await browser.close();
})();
