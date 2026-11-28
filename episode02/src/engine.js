// Rendering engine: headless Chromium rasterises per-frame SVG; frames stream into FFmpeg.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { defs } = require('./lib/defs');
const extraDefs = () => require('./scenes/props2').defs2 + require('./scenes/kit').sceneDefs + require('./environments/backgrounds').busDefs() + '<filter id="bgBlur6" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>';
const ROOT = path.join(__dirname, '..');
const W = 1080, H = 1920;

async function openPage(scale = 1) {
  const html = `<!doctype html><html><head><meta charset="utf-8">
  <link rel="stylesheet" href="${path.join(ROOT, 'assets/fonts/fonts.css')}">
  <style>html,body{margin:0;background:#000;overflow:hidden} #stage{width:${W}px;height:${H}px}</style></head>
  <body><svg width="0" height="0" style="position:absolute"><defs>${defs()}${extraDefs()}</defs></svg><div id="stage"></div>
  <div style="position:absolute;left:-999px;font-family:Amiri;font-weight:700">هند</div><div style="position:absolute;left:-999px;font-family:'Reem Kufi'">هند</div></body></html>`;
  const file = path.join(ROOT, 'build', 'page.html');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, html);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: scale });
  await page.goto('file://' + file);
  await page.evaluate(() => document.fonts.ready);
  return { browser, page };
}
async function setFrame(page, svg) {
  await page.evaluate((s) => { document.getElementById('stage').innerHTML = s; }, svg);
}
const wrap = (inner, w = W, h = H) => `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">${inner}</svg>`;
async function snapshot(page, inner, out, opts = {}) {
  await setFrame(page, wrap(inner, opts.w || W, opts.h || H));
  await page.waitForTimeout(opts.wait || 30);
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: opts.w || W, height: opts.h || H }, omitBackground: !!opts.transparent, type: out.endsWith('.jpg') ? 'jpeg' : 'png', ...(out.endsWith('.jpg') ? { quality: 90 } : {}) });
}
module.exports = { openPage, setFrame, snapshot, wrap, W, H, ROOT };
