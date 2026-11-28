// Lossless PNG previews: node tools/png.mjs <project> <out.png> --t 4.9 [--q 'mode=hind'] [--size 1080x1920]
// Uses the library's page loader (LIB env var = library root).
import path from 'path';
const LIB = process.env.LIB; if (!LIB) { console.error('set LIB'); process.exit(1); }
const { openDemo, closeServer, takeSize } = await import(path.join(LIB, 'core/render/page.mjs'));
const args = process.argv.slice(2);
const take = k => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : null; };
const { w, h } = takeSize(args), q = take('--q') || '', t = parseFloat(take('--t') || '0');
const [dir, out] = args;
const { browser, page } = await openDemo(path.resolve(dir), { w, h, q });
await page.evaluate(t => window.render(t), t);
await page.screenshot({ path: out, type: 'png' });
console.log(out);
await browser.close(); closeServer();
