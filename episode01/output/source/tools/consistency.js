// Character_Consistency_Preview: rigged characters (full body + faces) for side-by-side comparison with the sheets.
const { openPage, snapshot } = require('../src/engine');
const hind = require('../src/characters/hind'), loreen = require('../src/characters/loreen'), lizette = require('../src/characters/lizette');
(async () => {
  const { browser, page } = await openPage(1);
  const bg = '<rect width="1080" height="1920" fill="#f3ebe4"/>';
  await snapshot(page, bg + lizette.draw({ x: 190, y: 1880, s: 0.6, smile: 0.6, turn: 0.2 }) + hind.draw({ x: 540, y: 1880, s: 0.6, smile: 0.45 }) + loreen.draw({ x: 890, y: 1880, s: 0.6, smile: 0.55, turn: -0.2 }), 'build/cons_full.png');
  const row = (k, d, i, extra) => `<clipPath id="r${i}"><rect x="${i * 360}" y="0" width="360" height="1920"/></clipPath><g clip-path="url(#r${i})"><g transform="translate(${i * 360 + 180},560) scale(0.95) translate(-500,-330)">${d.draw({ x: 500, y: 1850, s: 1, smile: 0.55, ...extra })}</g></g>`;
  await snapshot(page, bg + row('lizette', lizette, 0, { turn: 0.15 }) + row('hind', hind, 1, {}) + row('loreen', loreen, 2, { turn: -0.15 }), 'build/cons_faces.png');
  await browser.close();
})();
