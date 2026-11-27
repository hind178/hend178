// Scene-building toolkit: camera with parallax, cached backdrops, extras sprites, props, grading, particles.
const path = require('path');
const fs = require('fs');
const { f, lerp, clamp, mkRng, kf, ease, easeInOut } = require('../lib/util');
const ROOT = path.join(__dirname, '..', '..');
const BG = (n) => 'file://' + path.join(ROOT, 'assets', 'backgrounds', n + '.jpg');
const EX = (n) => 'file://' + path.join(ROOT, 'assets', 'characters', 'extras', n + '.png');
const ENV = JSON.parse(fs.readFileSync(path.join(ROOT, 'build', 'envelope.json'), 'utf8'));
const FPS = 30;

/** camera: (cx,cy) = frame point brought to centre, z = zoom; depth d for parallax (1 = subject plane) */
function cam(c, inner, d = 1) {
  const [cx, cy, z] = c;
  const zz = 1 + (z - 1) * d;
  const px = 540 + (cx - 540) * d, py = 960 + (cy - 960) * d;
  return `<g transform="translate(540,960) scale(${zz.toFixed(4)}) translate(${f(-px)},${f(-py)})">${inner}</g>`;
}
function bg(name, opt = {}) {
  return `<image href="${BG(name)}" x="${opt.x ?? -135}" y="${opt.y ?? -240}" width="${opt.w ?? 1350}" height="${opt.h ?? 2400}" preserveAspectRatio="none" ${opt.blur ? `filter="url(#blur${opt.blur})"` : ''}/>`;
}
/** extras sprite; (x,y) = feet position, s = character scale (sprite rendered at 0.5) */
function extra(name, x, y, s, opt = {}) {
  const k = s / 0.5;
  const bob = opt.bob ? Math.sin(opt.t * 2.1 + (opt.ph || 0)) * 3 * k : 0;
  const rot = opt.rock ? Math.sin(opt.t * (opt.rockF || 2.4) + (opt.ph || 0)) * opt.rock : 0;
  return `<g transform="rotate(${f(rot)} ${f(x)} ${f(y)})" ${opt.blur ? `filter="url(#blur${opt.blur})"` : ''} opacity="${opt.op ?? 1}"><image href="${EX(name)}" x="${f(x - 300 * k)}" y="${f(y - 980 * k + bob)}" width="${f(600 * k)}" height="${f(1000 * k)}"/></g>`;
}
/** chatting extra that alternates between calm (A) and laughing (B) */
function chatter(v, side, x, y, s, t, ph = 0, opt = {}) {
  const laugh = Math.sin(t * 1.7 + ph) > 0.55;
  return extra(`${v}_${laugh ? 'B' : 'A'}_${side}`, x, y, s, { t, ph, bob: true, ...opt });
}
/** natural blink: returns 0..1 */
function blink(t, seed = 0) {
  const period = 3.1 + (seed % 3) * 0.7;
  const p = ((t + seed * 1.37) % period) / period * period;
  if (p < 0.07) return p / 0.07;
  if (p < 0.16) return 1 - (p - 0.07) / 0.09;
  return 0;
}
/** subtle idle motion (head sway & breathing) */
const idle = (t, seed = 0) => ({ tilt: Math.sin(t * 0.7 + seed) * 1.2, breathe: t + seed, bob: Math.sin(t * 1.6 + seed) * 1.5 });
/** mouth openness from the narration loudness (for quoted dialogue) */
function lip(t, a, b) {
  if (t < a || t > b) return 0;
  const i = Math.min(ENV.length - 1, Math.max(0, Math.round(t * FPS)));
  const v = ENV[i];
  const wob = 0.75 + 0.25 * Math.sin(t * 37);
  return clamp(v * wob * 1.05);
}
function vignette(strength = 0.55) {
  return `<rect width="1080" height="1920" fill="url(#vig)" opacity="${strength}"/>`;
}
function grade(opt = {}) {
  const warm = opt.warm ?? 0.08;
  return `<rect width="1080" height="1920" fill="${opt.tint || '#ffb46a'}" opacity="${warm}" style="mix-blend-mode:soft-light"/>
    ${opt.leak ? `<rect width="1080" height="1920" fill="url(#leak)" opacity="${opt.leak}"/>` : ''}
    ${vignette(opt.vig ?? 0.5)}`;
}
/** floating dust in sunlight */
function dust(t, n = 26, seed = 4, color = '#fff6dc') {
  const r = mkRng(seed);
  let s = '';
  for (let i = 0; i < n; i++) {
    const x0 = r() * 1080, y0 = r() * 1920, sp = 8 + r() * 18, sz = 1.5 + r() * 3.5, ph = r() * 6;
    const x = (x0 + Math.sin(t * 0.4 + ph) * 30 + t * sp * 0.6) % 1100, y = (y0 - t * sp + 1920 * 4) % 1920;
    s += `<circle cx="${f(x)}" cy="${f(y)}" r="${f(sz)}" fill="${color}" opacity="${f(0.25 + 0.35 * Math.abs(Math.sin(t + ph)))}"/>`;
  }
  return `<g filter="url(#blur1)">${s}</g>`;
}
function rays(t, x = 900, y = -100, op = 0.18) {
  let s = '';
  for (let i = 0; i < 5; i++) {
    const a = 108 + i * 9 + Math.sin(t * 0.3 + i) * 1.5;
    s += `<path d="M${x},${y} L${f(x + Math.cos(a * Math.PI / 180) * 2600 - 60)},${f(y + Math.sin(a * Math.PI / 180) * 2600)} L${f(x + Math.cos(a * Math.PI / 180) * 2600 + 60)},${f(y + Math.sin(a * Math.PI / 180) * 2600)} Z" fill="#fff3d0" opacity="${f(op * (0.6 + 0.4 * Math.sin(t * 0.5 + i * 1.3)))}"/>`;
  }
  return `<g filter="url(#blur14)" style="mix-blend-mode:screen">${s}</g>`;
}
const fade = (a, col = '#000') => a > 0.001 ? `<rect width="1080" height="1920" fill="${col}" opacity="${clamp(a).toFixed(3)}"/>` : '';

/* ---------- props ---------- */
function suitcase(x, y, s, tiltDeg = -8) {
  // handle top at (x,y); hangs/rolls behind the hand
  return `<g transform="translate(${f(x)},${f(y)}) scale(${s}) rotate(${tiltDeg})">
    <path d="M-10,0 L-10,150 M10,0 L10,150" stroke="#3b3f48" stroke-width="8"/><rect x="-26" y="-12" width="52" height="16" rx="6" fill="#2a2d33"/>
    <rect x="-95" y="150" width="190" height="300" rx="26" fill="#2c4a86" stroke="#1a2c52" stroke-width="5"/>
    ${[-50, 0, 50].map((dx) => `<path d="M${dx},160 L${dx},440" stroke="#22396b" stroke-width="6"/>`).join('')}
    <rect x="-95" y="150" width="60" height="300" rx="26" fill="#fff" opacity="0.12"/>
    <circle cx="-62" cy="462" r="16" fill="#1d2127"/><circle cx="62" cy="462" r="16" fill="#1d2127"/></g>`;
}
function books(x, y, s, rot = 0) {
  return `<g transform="translate(${f(x)},${f(y)}) scale(${s}) rotate(${rot})">
    <rect x="-70" y="-26" width="140" height="22" fill="#8c3b2f" stroke="#4a1d16" stroke-width="2"/><rect x="-64" y="-48" width="132" height="22" fill="#2f4f7a" stroke="#18283f" stroke-width="2"/>
    <rect x="-74" y="-4" width="146" height="20" fill="#e9d9b6" stroke="#9a8a6a" stroke-width="2"/></g>`;
}
function desk(x, y, w, s = 1) {
  return `<g transform="translate(${x},${y}) scale(${s})">
    <rect x="${-w / 2}" y="0" width="${w}" height="34" rx="4" fill="#a8774a" stroke="#5e3f24" stroke-width="3"/>
    <rect x="${-w / 2 + 10}" y="34" width="${w - 20}" height="420" fill="#8a5f3a" stroke="#5e3f24" stroke-width="3"/>
    <rect x="${-w / 2 + 10}" y="34" width="${w - 20}" height="40" fill="#000" opacity="0.18"/>
    <path d="M${-w / 2},6 L${w / 2},6" stroke="#d2a77a" stroke-width="3"/></g>`;
}
function laptopNotebooks(x, y, s, t) {
  return `<g transform="translate(${x},${y}) scale(${s})">
    <path d="M-40,0 L-60,-170 L200,-170 L220,0 Z" fill="#c9ced6" stroke="#7d848e" stroke-width="3"/><path d="M-40,-10 L-56,-160 L196,-160 L212,-10 Z" fill="#20314a"/>
    ${Array.from({ length: 6 }, (_, i) => `<rect x="-20" y="${-140 + i * 18}" width="${f(120 + ((i * 37) % 80))}" height="6" fill="${i % 2 ? '#7fd1a8' : '#8fb4ff'}" opacity="0.8"/>`).join('')}
    <rect x="${f(-20 + ((t * 40) % 140))}" y="-32" width="10" height="6" fill="#fff" opacity="${Math.sin(t * 8) > 0 ? 0.9 : 0}"/>
    <path d="M-60,0 L240,0 L250,14 L-70,14 Z" fill="#aeb4bd"/>
    <rect x="-330" y="-30" width="220" height="30" fill="#fbf8ef" stroke="#a99d84" stroke-width="2" transform="rotate(-4)"/>
    <rect x="-320" y="-58" width="200" height="28" fill="#2c4fb4" stroke="#1a2c62" stroke-width="2" transform="rotate(-2)"/>
    <rect x="-300" y="-84" width="170" height="26" fill="#b9524f" stroke="#6e2a28" stroke-width="2"/>
    <rect x="270" y="-20" width="160" height="20" fill="#fdfbf4" stroke="#b5a88a" stroke-width="2" transform="rotate(6)"/>
    <path d="M290,-14 L400,-4 M290,-8 L380,2" stroke="#8a9ab8" stroke-width="2" transform="rotate(6)"/>
    <rect x="420" y="-70" width="40" height="70" rx="6" fill="#f4efe6" stroke="#a99d84" stroke-width="2"/><path d="M460,-55 C480,-55 480,-25 460,-25" stroke="#a99d84" stroke-width="5" fill="none"/>
  </g>`;
}
/** blue coach seat seen from behind (occludes seated characters' lower body) */
function seatBack(x, y, s, op = 1) {
  return `<g transform="translate(${f(x)},${f(y)}) scale(${s})" opacity="${op}">
    <path d="M-190,-60 C-190,-120 190,-120 190,-60 L200,700 L-200,700 Z" fill="url(#seatFG)" stroke="#16264a" stroke-width="5"/>
    <rect x="-150" y="-118" width="300" height="80" rx="22" fill="#ece7dd" stroke="#b9b2a5" stroke-width="3"/>
    <path d="M-160,40 L160,40" stroke="#1b2f5a" stroke-width="4"/><rect x="-60" y="120" width="120" height="70" rx="10" fill="#1b2f5a" opacity="0.6"/>
  </g>`;
}
function textCard(lines) {
  return lines.map((l) => `<text x="540" y="${l.y}" text-anchor="middle" direction="rtl" font-family="${l.font || 'Amiri'}" font-weight="700" font-size="${l.size}" fill="${l.fill || '#fff'}" opacity="${l.op ?? 1}" ${l.ls ? `letter-spacing="${l.ls}"` : ''}>${l.text}</text>`).join('');
}
const sceneDefs = `
  <radialGradient id="vig" cx="0.5" cy="0.5" r="0.75"><stop offset="0.55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#1a0d05" stop-opacity="0.9"/></radialGradient>
  <linearGradient id="leak" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffcf8a" stop-opacity="0.8"/><stop offset="0.45" stop-color="#ffcf8a" stop-opacity="0"/></linearGradient>
  <linearGradient id="seatFG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1f3466"/><stop offset="0.4" stop-color="#3a5ea8"/><stop offset="1" stop-color="#22396b"/></linearGradient>
  <radialGradient id="dreamMask" cx="0.5" cy="0.5" r="0.5"><stop offset="0.6" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <mask id="dream"><rect width="1080" height="1920" fill="#000"/><ellipse cx="540" cy="560" rx="380" ry="330" fill="url(#dreamMask)"/></mask>`;

module.exports = { cam, bg, extra, chatter, blink, idle, lip, grade, dust, rays, fade, suitcase, books, desk, laptopNotebooks, seatBack, textCard, sceneDefs, BG, FPS, kf, lerp, clamp, ease, easeInOut };
