const { openPage, snapshot } = require('../src/engine');
const hind = require('../src/characters/hind'), loreen = require('../src/characters/loreen'), lizette = require('../src/characters/lizette');
(async () => {
  const { browser, page } = await openPage(1);
  const bg = '<rect width="1080" height="1920" fill="#efe6de"/>';
  const s = 0.42, y = 1500;
  const inner = bg + lizette.draw({ x: 190, y, s, smile: 0.6 }) + hind.draw({ x: 540, y, s, smile: 0.4 }) + loreen.draw({ x: 890, y, s, smile: 0.5 });
  await snapshot(page, inner, process.argv[2]);
  const big = bg + `<g transform="translate(540,960) scale(2.7) translate(-540,-850)">${lizette.draw({ x: 190, y, s, smile: 0.6 }) + hind.draw({ x: 540, y, s, smile: 0.4 }) + loreen.draw({ x: 890, y, s, smile: 0.5 })}</g>`;
  await snapshot(page, big, process.argv[3]);
  await browser.close();
})();
