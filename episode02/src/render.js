// Episode renderer.
//   node src/render.js stills <t1> <t2> ...          -> build/stills/*.jpg (+ contact sheet)
//   node src/render.js video [scale] [from] [to] [workers]  -> output/Episode_01_University_Trip.mp4
const fs = require('fs'), path = require('path');
const { spawn, execFileSync } = require('child_process');
const { openPage, setFrame, wrap, ROOT } = require('./engine');
const TL = require('./timeline');
const FPS = 30;
const [, , mode, ...args] = process.argv;

async function stills(times) {
  const dir = path.join(ROOT, 'build', 'stills'); fs.mkdirSync(dir, { recursive: true });
  const { browser, page } = await openPage(0.5);
  for (const t of times) {
    const t0 = Date.now();
    await setFrame(page, wrap(TL.frame(+t)));
    await page.waitForTimeout(40);
    await page.screenshot({ path: path.join(dir, `t${(+t).toFixed(2).padStart(6, '0')}.jpg`), type: 'jpeg', quality: 85 });
    process.stdout.write(`${t}(${Date.now() - t0}ms) `);
  }
  await browser.close(); console.log();
}

async function segment(idx, f0, f1, scale, outFile) {
  const { browser, page } = await openPage(scale);
  const W = Math.round(1080 * scale), H = Math.round(1920 * scale);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-vf', `scale=${W}:${H}`, '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(FPS), outFile], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let fr = f0; fr < f1; fr++) {
    await setFrame(page, wrap(TL.frame(fr / FPS)));
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    if ((fr - f0) % 150 === 0) console.log(`[w${idx}] ${fr - f0}/${f1 - f0} ${((Date.now() - t0) / Math.max(1, fr - f0)).toFixed(0)}ms/f`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  await browser.close();
}

async function video(scale = 1, from = 0, to = TL.DUR, workers = 4) {
  const total = Math.round(to * FPS), first = Math.round(from * FPS);
  const segDir = path.join(ROOT, 'build', 'segments'); fs.mkdirSync(segDir, { recursive: true });
  const n = workers, per = Math.ceil((total - first) / n);
  const files = [];
  await Promise.all(Array.from({ length: n }, (_, i) => {
    const a = first + i * per, b = Math.min(total, a + per);
    const file = path.join(segDir, `seg${i}.mp4`); files.push(file);
    return a < b ? segment(i, a, b, scale, file) : Promise.resolve();
  }));
  fs.writeFileSync(path.join(segDir, 'list.txt'), files.filter(fs.existsSync).map((f) => `file '${f}'`).join('\n'));
  const silent = path.join(ROOT, 'build', 'video_silent.mp4');
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(segDir, 'list.txt'), '-c', 'copy', silent]);
  console.log('video assembled', silent);
}

(async () => {
  if (mode === 'stills') await stills(args);
  else if (mode === 'video') await video(+(args[0] || 1), +(args[1] || 0), +(args[2] || TL.DUR), +(args[3] || 4));
})();

// Per-shot rendering with resume: each completed shot is saved to build/shots/NN.mp4 and skipped on rerun.
async function shotsMode(scale = 1, workers = 4) {
  const dir = path.join(ROOT, 'build', 'shots'); fs.mkdirSync(dir, { recursive: true });
  const jobs = TL.shots.map((s, i) => ({ i, f0: Math.round(s.a * FPS), f1: i === TL.shots.length - 1 ? Math.ceil(TL.DUR * FPS) : Math.round(s.b * FPS) }));
  const file = (j) => path.join(dir, `${String(j.i).padStart(2, '0')}.mp4`);
  const queue = jobs.filter((j) => !fs.existsSync(file(j)));
  console.log(`${jobs.length - queue.length} shots cached, ${queue.length} to render`);
  await Promise.all(Array.from({ length: workers }, async (_, w) => {
    while (queue.length) {
      const j = queue.shift();
      const tmp = file(j) + '.part.mp4';
      await segment(w, j.f0, j.f1, scale, tmp);
      fs.renameSync(tmp, file(j));
      console.log(`shot ${j.i} done`);
    }
  }));
  fs.writeFileSync(path.join(dir, 'list.txt'), jobs.map((j) => `file '${file(j)}'`).join('\n'));
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(dir, 'list.txt'), '-c', 'copy', path.join(ROOT, 'build', 'video_silent.mp4')]);
  console.log('assembled');
}
if (mode === 'shots') shotsMode(+(args[0] || 1), +(args[1] || 4));
