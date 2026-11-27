// Background students: recoloured variants of the three rigs, rendered once as transparent sprites (A = chatting, B = laughing).
const { chromium } = require('playwright');
const path = require('path');
const { defs } = require('./lib/defs');
const hind = require('./characters/hind'), loreen = require('./characters/loreen'), lizette = require('./characters/lizette');
const OUT = path.join(__dirname, '..', 'assets', 'characters', 'extras');
const flatPatterns = (s, col) => s.replace(/url\(#p(NavyFloral|CreamIkat|RoyalLattice|LightCross|MedallionDots|Medallion|CreamDots|Band|Speckle)\)/g, col);
const V = {
  e1: (p) => flatPatterns(hind.draw(p), '#6f7f8f').replace(/url\(#hijabGrad\)|url\(#hijabTailGrad\)/g, '#8a3a4a').replace(/url\(#bagGrad\)|url\(#flapGrad\)|url\(#strapGrad\)/g, '#2b2b2e'),
  e2: (p) => flatPatterns(hind.draw(p), '#3d4b5f').replace(/url\(#hijabGrad\)|url\(#hijabTailGrad\)/g, '#c9ad84').replace(/url\(#blouseGrad\)|url\(#sleeveGrad\)/g, '#e7eef2'),
  e3: (p) => loreen.draw(p, { noBag: true }).replace(/url\(#pTurban\)/g, '#6b8fae').replace(/url\(#pinkGrad\)|url\(#pinkSleeve\)/g, '#bcd6c6').replace(/#f2a7b3/g, '#bcd6c6').replace(/url\(#blackSkirt\)/g, '#5a4636'),
  e4: (p) => lizette.draw(p, { noPack: true }).replace(/url\(#hairGrad\)|url\(#hairSide\)/g, '#2a1a12').replace(/url\(#pPolka\)/g, '#b9524f').replace(/url\(#denimGrad\)/g, '#4c6a9a').replace(/url\(#capCrown\)/g, '#7b2e2c'),
  e5: (p) => loreen.draw(p, { noBag: true }).replace(/url\(#pTurban\)/g, '#d9a3a8').replace(/url\(#pinkGrad\)|url\(#pinkSleeve\)/g, '#f2e4c8').replace(/#f2a7b3/g, '#f2e4c8').replace(/url\(#blackSkirt\)/g, '#2f3e5a'),
  e6: (p) => flatPatterns(hind.draw(p), '#7b5a43').replace(/url\(#hijabGrad\)|url\(#hijabTailGrad\)/g, '#2b2b30').replace(/url\(#bagGrad\)|url\(#flapGrad\)|url\(#strapGrad\)/g, '#6b4a32'),
};
const poses = {
  A: (turn) => ({ x: 300, y: 980, s: 0.5, turn, smile: 0.45, look: [turn * 1.5, 0], armR: { a: 6, e: -8 }, armL: { a: 6, e: -8 } }),
  B: (turn) => ({ x: 300, y: 980, s: 0.5, turn, tilt: -turn * 6, smile: 0.9, open: 0.6, smileEyes: 0.8, armR: { a: -5, e: -60, hand: 'relaxed' }, armL: { a: 6, e: -8 } }),
};
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 600, height: 1000 } });
  await page.setContent(`<html><body style="margin:0;background:transparent"><svg width="0" height="0" style="position:absolute"><defs>${defs()}</defs></svg><div id="st"></div></body></html>`);
  for (const [k, fn] of Object.entries(V)) for (const [pk, pf] of Object.entries(poses)) for (const turn of [-0.5, 0.5]) {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 1000" width="600" height="1000">${fn(pf(turn))}</svg>`;
    await page.evaluate((s) => { document.getElementById('st').innerHTML = s; }, svg);
    await page.screenshot({ path: path.join(OUT, `${k}_${pk}_${turn < 0 ? 'L' : 'R'}.png`), omitBackground: true });
  }
  await browser.close(); console.log('extras done');
})();
