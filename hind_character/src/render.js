// Render Hind_Front.svg -> Hind_Front.png with headless Chromium (Playwright).
// Usage: node render.js <in.svg> <out.png> [scale] [clipX clipY clipW clipH]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [inp, out, scaleArg, ...clip] = process.argv.slice(2);
  const svg = fs.readFileSync(inp, 'utf8');
  const m = svg.match(/viewBox="0 0 (\d+) (\d+)"/);
  const W = +m[1], H = +m[2];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: +(scaleArg || 2) });
  await page.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`);
  const opts = { path: out };
  if (clip.length === 4) { const [x, y, w, h] = clip.map(Number); opts.clip = { x, y, width: w, height: h }; }
  else opts.clip = { x: 0, y: 0, width: W, height: H };
  await page.screenshot(opts);
  await browser.close();
  console.log('wrote', out);
})();
