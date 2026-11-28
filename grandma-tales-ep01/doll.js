// Handcrafted collectible-doll characters: sculpted head + painted face decal, lathe-turned body and clothes,
// articulated arms (shoulder → elbow → wrist → five-finger hand) and legs (hip → knee → ankle → shoe).
// Built in "doll units" (height 1, feet at y=0, facing +z), then scaled to the character's height.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const V = (x, y) => new THREE.Vector2(x, y);
const TAU = Math.PI * 2;
export const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;

// ---------- textures ----------
function canvasTex(w, h, draw, { repeat = null, srgb = true } = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repeat); }
  return t;
}
function rnd(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

// woven fabric grain on top of a base colour
function weave(g, w, h, base, amt = 0.06, seed = 1) {
  g.fillStyle = base; g.fillRect(0, 0, w, h);
  const r = rnd(seed);
  for (let i = 0; i < w * h / 6; i++) {
    const x = r() * w, y = r() * h, d = (r() - .5) * amt;
    g.fillStyle = d > 0 ? `rgba(255,255,255,${d})` : `rgba(0,0,0,${-d})`;
    g.fillRect(x, y, r() < .5 ? 2 : 1, r() < .5 ? 1 : 2);
  }
}
// soft vertical drape folds
function folds(g, w, h, n, amt, seed) {
  const r = rnd(seed);
  for (let i = 0; i < n; i++) {
    const x = r() * w, ww = 6 + r() * 26;
    const gr = g.createLinearGradient(x - ww, 0, x + ww, 0);
    gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(.5, `rgba(0,0,0,${amt * (.5 + r())})`); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr; g.fillRect(x - ww, 0, ww * 2, h);
  }
}

export const TEX = {};
function buildTextures() {
  if (TEX.ready) return;
  // Hind: royal-blue patchwork skirt (block-print panels)
  TEX.patch = canvasTex(1024, 512, (g, w, h) => {
    const r = rnd(7); g.fillStyle = '#1f3c9a'; g.fillRect(0, 0, w, h);
    const blues = ['#1c3590', '#2a4fb8', '#e9e6dc', '#3f66c8', '#14296e', '#6f8fd6'];
    const cw = 64, ch = 64;
    for (let y = 0; y < h; y += ch) for (let x = 0; x < w; x += cw) {
      const pw = cw * (r() < .3 ? 2 : 1), base = blues[Math.floor(r() * blues.length)];
      g.fillStyle = base; g.fillRect(x, y, pw, ch);
      const ink = base === '#e9e6dc' ? '#1f3c9a' : (r() < .5 ? '#e9e6dc' : '#0f2160');
      g.fillStyle = ink; g.strokeStyle = ink; g.lineWidth = 2;
      const k = Math.floor(r() * 4);
      for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) {
        const cx = x + 8 + i * 16, cy = y + 8 + j * 16;
        if (k === 0) { g.beginPath(); g.moveTo(cx, cy - 5); g.lineTo(cx + 5, cy); g.lineTo(cx, cy + 5); g.lineTo(cx - 5, cy); g.fill(); }
        else if (k === 1) { g.beginPath(); g.arc(cx, cy, 3, 0, TAU); g.fill(); }
        else if (k === 2) { g.strokeRect(cx - 5, cy - 5, 10, 10); }
        else { g.fillRect(cx - 1, cy - 6, 2, 12); g.fillRect(cx - 6, cy - 1, 12, 2); }
      }
      g.strokeStyle = 'rgba(233,230,220,.8)'; g.lineWidth = 2; g.strokeRect(x + 2, y + 2, pw - 4, ch - 4);
    }
    folds(g, w, h, 40, .16, 3);
    const d = g.getImageData(0, 0, w, h); // fabric grain
    for (let i = 0; i < d.data.length; i += 4) { const n = (r() - .5) * 18; d.data[i] += n; d.data[i + 1] += n; d.data[i + 2] += n; }
    g.putImageData(d, 0, 0);
  });
  TEX.cream = canvasTex(256, 256, (g, w, h) => { weave(g, w, h, '#f1ece2', .07, 2); folds(g, w, h, 10, .07, 5); });
  TEX.royal = canvasTex(256, 256, (g, w, h) => { weave(g, w, h, '#2340b4', .10, 4); folds(g, w, h, 14, .22, 9); });
  TEX.pink = canvasTex(256, 256, (g, w, h) => {
    weave(g, w, h, '#eda0ae', .06, 6);
    g.strokeStyle = 'rgba(160,60,80,.22)'; g.lineWidth = 2; for (let y = 10; y < h; y += 14) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
  });
  TEX.black = canvasTex(256, 256, (g, w, h) => { weave(g, w, h, '#1d1b20', .08, 8); folds(g, w, h, 16, .3, 11); });
  TEX.denim = canvasTex(256, 256, (g, w, h) => { weave(g, w, h, '#f4f3ef', .08, 12); folds(g, w, h, 8, .05, 13); });
  TEX.dots = canvasTex(256, 256, (g, w, h) => {
    weave(g, w, h, '#17161b', .08, 14);
    g.fillStyle = '#f2f0ea'; for (let y = 0; y < h; y += 16) for (let x = (y / 16) % 2 ? 8 : 0; x < w; x += 16) { g.beginPath(); g.arc(x + 4, y + 4, 2.4, 0, TAU); g.fill(); }
    folds(g, w, h, 12, .25, 15);
  }, { repeat: [3, 2] });
  TEX.floral = canvasTex(512, 512, (g, w, h) => {
    const r = rnd(21); g.fillStyle = '#f3ecdf'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 160; i++) {
      const x = r() * w, y = r() * h, s = 7 + r() * 10, c = r() < .65 ? '#26307e' : '#5463b4';
      g.fillStyle = c;
      for (let p = 0; p < 5; p++) { const a = p / 5 * TAU + r(); g.beginPath(); g.ellipse(x + Math.cos(a) * s * .6, y + Math.sin(a) * s * .6, s * .55, s * .32, a, 0, TAU); g.fill(); }
      g.fillStyle = '#f3ecdf'; g.beginPath(); g.arc(x, y, s * .22, 0, TAU); g.fill();
    }
    folds(g, w, h, 18, .15, 22);
  });
  TEX.leather = canvasTex(256, 256, (g, w, h) => { weave(g, w, h, '#8a4f28', .12, 30); });
  TEX.plaid = canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = '#d8b48a'; g.fillRect(0, 0, w, h);
    g.fillStyle = 'rgba(25,20,20,.85)'; for (let x = 0; x < w; x += 64) { g.fillRect(x + 20, 0, 9, h); g.fillRect(0, x + 20, w, 9); }
    g.fillStyle = 'rgba(240,235,225,.9)'; for (let x = 0; x < w; x += 64) { g.fillRect(x + 40, 0, 4, h); g.fillRect(0, x + 40, w, 4); }
    g.fillStyle = 'rgba(200,50,50,.8)'; for (let x = 0; x < w; x += 64) { g.fillRect(x + 52, 0, 2, h); g.fillRect(0, x + 52, w, 2); }
  });
  // hair strands with caramel balayage toward the tips
  TEX.hair = canvasTex(512, 512, (g, w, h) => {
    const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#4a2e1c'); gr.addColorStop(.45, '#6b4428'); gr.addColorStop(1, '#a87a4e');
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const r = rnd(40);
    for (let i = 0; i < 900; i++) {
      const x = r() * w; g.strokeStyle = r() < .5 ? `rgba(40,22,12,${.15 + r() * .3})` : `rgba(220,170,115,${.08 + r() * .25})`;
      g.lineWidth = .6 + r() * 1.6; g.beginPath(); g.moveTo(x, 0);
      g.bezierCurveTo(x + (r() - .5) * 30, h * .33, x + (r() - .5) * 30, h * .66, x + (r() - .5) * 20, h); g.stroke();
    }
  });
  TEX.ready = true;
}

// ---------- face ----------
// painted onto a canvas that wraps the front of the head (see faceGeo). Coordinates in head-radius units.
const FPHI = 1.9, FTH0 = 0.95, FTH = 1.4, FW = 512, FH = Math.round(512 * FTH * 1.1 / FPHI);
function fx(xr) { return FW / 2 + Math.asin(clamp(xr, -.99, .99)) / FPHI * FW; }
function fy(yr) { return (Math.acos(clamp(yr / 1.1, -.99, .99)) - FTH0) / FTH * FH; }
const SC = FW / FPHI; // pixels per radius unit (approx.)

export function drawFace(g, f, e) {
  // f: face spec, e: expression {smile, open, brow, inner, lid, blink, gx, gy}
  g.clearRect(0, 0, FW, FH);
  const S = SC;
  // blush
  for (const s of [-1, 1]) {
    const x = fx(s * .43), y = fy(-.34), rr = .2 * S;
    const gr = g.createRadialGradient(x, y, 0, x, y, rr); gr.addColorStop(0, f.blush); gr.addColorStop(1, 'rgba(240,140,140,0)');
    g.fillStyle = gr; g.beginPath(); g.ellipse(x, y, rr, rr * .75, 0, 0, TAU); g.fill();
  }
  // eyes
  for (const s of [-1, 1]) {
    const cx = fx(s * f.eyeX), cy = fy(f.eyeY), ew = f.eyeW * S, eh = f.eyeH * S * (1 + .18 * e.brow);
    const tilt = f.tilt * s; // outer corner lift
    const open = clamp(1 - e.blink, 0, 1) * (1 - .25 * e.lid);
    const inner = [cx - s * ew, cy + eh * .1], outer = [cx + s * ew, cy - eh * tilt];
    const topY = cy - eh * (open * 1.0) + eh * .02, botY = cy + eh * .8;
    // sclera
    g.save();
    g.beginPath(); g.moveTo(...inner);
    g.bezierCurveTo(cx - s * ew * .55, topY - eh * .15, cx + s * ew * .55, topY - eh * .2, ...outer);
    g.bezierCurveTo(cx + s * ew * .6, botY + eh * .05, cx - s * ew * .5, botY + eh * .1, ...inner);
    g.closePath();
    if (open > .06) {
      g.fillStyle = '#fbf8f4'; g.fill(); g.clip();
      // iris
      const ir = f.iris * S, ix = cx + e.gx * ew * .32, iy = cy + eh * .12 + e.gy * eh * .25;
      const gi = g.createRadialGradient(ix, iy + ir * .3, ir * .1, ix, iy, ir);
      gi.addColorStop(0, f.irisLight); gi.addColorStop(.6, f.irisColor); gi.addColorStop(1, '#2a160c');
      g.fillStyle = gi; g.beginPath(); g.arc(ix, iy, ir, 0, TAU); g.fill();
      g.fillStyle = '#140a06'; g.beginPath(); g.arc(ix, iy, ir * .45, 0, TAU); g.fill();
      // shadow of the upper lid on the eyeball
      const gs = g.createLinearGradient(0, topY - eh * .2, 0, topY + eh * .55); gs.addColorStop(0, 'rgba(60,30,20,.55)'); gs.addColorStop(1, 'rgba(60,30,20,0)');
      g.fillStyle = gs; g.fillRect(cx - ew * 1.3, topY - eh, ew * 2.6, eh * 1.6);
      // catch-lights
      g.fillStyle = 'rgba(255,255,255,.95)'; g.beginPath(); g.ellipse(ix - ir * .35, iy - ir * .4, ir * .26, ir * .2, 0, 0, TAU); g.fill();
      g.fillStyle = 'rgba(255,255,255,.6)'; g.beginPath(); g.arc(ix + ir * .35, iy + ir * .35, ir * .11, 0, TAU); g.fill();
    }
    g.restore();
    // eyelid skin over the closed part + lash line
    g.lineCap = 'round'; g.lineJoin = 'round';
    g.strokeStyle = f.lash; g.lineWidth = .05 * S;
    g.beginPath(); g.moveTo(...inner);
    if (open > .06) g.bezierCurveTo(cx - s * ew * .55, topY - eh * .15, cx + s * ew * .55, topY - eh * .2, ...outer);
    else g.bezierCurveTo(cx - s * ew * .5, cy + eh * .45, cx + s * ew * .5, cy + eh * .4, ...outer);
    g.stroke();
    // winged liner and lashes
    g.lineWidth = .03 * S; g.beginPath(); g.moveTo(...outer); g.lineTo(outer[0] + s * ew * f.wing, outer[1] - eh * (.35 + f.wing * .5)); g.stroke();
    g.lineWidth = .014 * S;
    for (let i = 0; i < 5; i++) {
      const t = .55 + i * .11, bx = lerp(inner[0], outer[0], t), by = (open > .06 ? lerp(topY - eh * .12, outer[1], (t - .5) * 2) : cy + eh * .42);
      g.beginPath(); g.moveTo(bx, by); g.lineTo(bx + s * ew * .14, by - eh * (open > .06 ? .35 : -.3)); g.stroke();
    }
    // lower lash line + crease
    if (open > .06) {
      g.strokeStyle = 'rgba(90,50,35,.55)'; g.lineWidth = .014 * S;
      g.beginPath(); g.moveTo(inner[0] + s * ew * .3, botY - eh * .02); g.quadraticCurveTo(cx + s * ew * .3, botY + eh * .12, outer[0] - s * ew * .05, outer[1] + eh * .3); g.stroke();
    }
    g.strokeStyle = 'rgba(150,90,70,.45)'; g.lineWidth = .016 * S;
    g.beginPath(); g.moveTo(inner[0] + s * ew * .15, topY - eh * .45); g.quadraticCurveTo(cx, topY - eh * .85, outer[0] - s * ew * .1, outer[1] - eh * .55); g.stroke();
    // brow
    const by = fy(f.eyeY + .27 + .07 * e.brow), lift = .06 * e.inner;
    g.strokeStyle = f.brow; g.lineWidth = .045 * S;
    g.beginPath(); g.moveTo(fx(s * (f.eyeX - .2)), by + (.02 - lift) * S);
    g.quadraticCurveTo(fx(s * (f.eyeX + .02)), by - (.07 + .02 * e.brow) * S, fx(s * (f.eyeX + .23)), by + .02 * S); g.stroke();
  }
  // nose: soft shadow + tip highlight
  const ny = fy(-.3);
  g.strokeStyle = 'rgba(170,100,80,.35)'; g.lineWidth = .02 * S;
  g.beginPath(); g.moveTo(fx(-.05), ny); g.quadraticCurveTo(fx(0), ny + .04 * S, fx(.05), ny); g.stroke();
  // mouth
  const my = fy(-.56), mw = (.12 + .04 * e.smile) * S, mx = FW / 2;
  if (e.open > .05 && e.smile > .45) {
    const oh = (.04 + .08 * e.open) * S, ow = mw * 1.05;
    g.fillStyle = '#7a2f35'; g.beginPath(); g.moveTo(mx - ow, my - .02 * S); g.quadraticCurveTo(mx, my - .04 * S, mx + ow, my - .02 * S); g.quadraticCurveTo(mx + ow * .5, my + oh * 1.6, mx, my + oh * 1.6); g.quadraticCurveTo(mx - ow * .5, my + oh * 1.6, mx - ow, my - .02 * S); g.fill();
    g.fillStyle = 'rgba(255,255,255,.95)'; g.beginPath(); g.moveTo(mx - ow * .8, my - .015 * S); g.quadraticCurveTo(mx, my - .03 * S, mx + ow * .8, my - .015 * S); g.lineTo(mx + ow * .6, my + oh * .35); g.quadraticCurveTo(mx, my + oh * .5, mx - ow * .6, my + oh * .35); g.fill();
    g.fillStyle = '#e07f86'; g.beginPath(); g.ellipse(mx, my + oh * 1.2, ow * .45, oh * .35, 0, 0, TAU); g.fill();
    g.strokeStyle = f.lip; g.lineWidth = .03 * S; g.beginPath(); g.moveTo(mx - ow, my - .02 * S); g.quadraticCurveTo(mx + ow * .5 - ow * .5, my + oh * 1.75, mx + ow, my - .02 * S); g.stroke();
  } else if (e.open > .05) {
    const oh = (.05 + .1 * e.open) * S, ow = mw * (.75 - .25 * e.open);
    g.fillStyle = '#7a2f35'; g.beginPath(); g.ellipse(mx, my + oh * .3, ow, oh, 0, 0, TAU); g.fill();
    g.fillStyle = 'rgba(255,255,255,.85)'; g.beginPath(); g.ellipse(mx, my + oh * .3 - oh * .72, ow * .7, oh * .22, 0, 0, Math.PI); g.fill();
    g.strokeStyle = f.lip; g.lineWidth = .028 * S; g.beginPath(); g.ellipse(mx, my + oh * .3, ow, oh, 0, 0, TAU); g.stroke();
  } else {
    const c = e.smile;
    g.fillStyle = f.lip;
    g.beginPath(); g.moveTo(mx - mw, my - c * .03 * S);
    g.quadraticCurveTo(mx, my + (.04 + .08 * c) * S, mx + mw, my - c * .03 * S);
    g.quadraticCurveTo(mx, my + (.0 + .03 * c) * S, mx - mw, my - c * .03 * S); g.fill();
    g.strokeStyle = 'rgba(120,50,50,.7)'; g.lineWidth = .014 * S;
    g.beginPath(); g.moveTo(mx - mw, my - c * .03 * S); g.quadraticCurveTo(mx, my + (.02 + .05 * c) * S, mx + mw, my - c * .03 * S); g.stroke();
    // upper lip hint
    g.fillStyle = f.lipTop; g.beginPath(); g.moveTo(mx - mw * .8, my - c * .02 * S); g.quadraticCurveTo(mx - mw * .3, my - .045 * S, mx, my - .02 * S);
    g.quadraticCurveTo(mx + mw * .3, my - .045 * S, mx + mw * .8, my - c * .02 * S); g.quadraticCurveTo(mx, my + .01 * S, mx - mw * .8, my - c * .02 * S); g.fill();
    if (c > .3) { g.strokeStyle = 'rgba(170,90,80,.3)'; for (const s of [-1, 1]) { g.beginPath(); g.arc(mx + s * (mw + .02 * S), my - .02 * S, .03 * S, s > 0 ? Math.PI * .6 : -Math.PI * .1, s > 0 ? Math.PI * 1.1 : Math.PI * .4); g.stroke(); } }
  }
  if (f.mole) { g.fillStyle = 'rgba(90,55,40,.7)'; g.beginPath(); g.arc(fx(f.mole[0]), fy(f.mole[1]), .012 * S, 0, TAU); g.fill(); }
}

// head shape: a sculpted sphere — taller, a tapered jaw, soft doll cheeks
function sculpt(geo, r, { taper = .3, cheek = .05, front = .96 } = {}) {
  const p = geo.attributes.position, v = new THREE.Vector3();
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i).divideScalar(r);
    let { x, y, z } = v;
    if (y < 0) { const k = 1 - taper * Math.pow(-y, 1.7); x *= k; z *= lerp(1, k, .7); }
    if (z > 0) { z *= front; const c = Math.exp(-((y + .3) ** 2) / .05) * Math.exp(-((Math.abs(x) - .45) ** 2) / .08); x += Math.sign(x) * c * cheek; z += c * cheek; }
    y *= 1.1;
    p.setXYZ(i, x * r, y * r, z * r);
  }
  geo.computeVertexNormals();
  return geo;
}
// shell around the head (hijab, hair) with an alpha-mapped face opening
function openingMask(top, bottom, half, extra) {
  return canvasTex(512, 256, (g, w, h) => {
    g.fillStyle = '#fff'; g.fillRect(0, 0, w, h);
    g.fillStyle = '#000';
    // sphere uv: u = phi/2π (front = .25), v = 1 - θ/π ; canvas y = θ/π
    const cx = .25 * w, y0 = top / Math.PI * h, y1 = bottom / Math.PI * h, hw = half / TAU * w;
    g.beginPath(); g.ellipse(cx, (y0 + y1) / 2, hw, (y1 - y0) / 2, 0, 0, TAU); g.fill();
    if (extra) extra(g, w, h);
  }, { srgb: false });
}

// ---------- body parts ----------
function lathe(profile, seg = 40, zs = .75, mat) {
  const g = new THREE.LatheGeometry(profile.map(([r, y]) => V(r, y)), seg);
  g.scale(1, 1, zs);
  return new THREE.Mesh(g, mat);
}
function tube(r0, r1, len, mat, seg = 16) {
  const g = new THREE.CylinderGeometry(r1, r0, len, seg, 4); g.translate(0, -len / 2, 0);
  return new THREE.Mesh(g, mat);
}
function sphere(r, mat, sx = 1, sy = 1, sz = 1) { const m = new THREE.Mesh(new THREE.SphereGeometry(r, 24, 16), mat); m.scale.set(sx, sy, sz); return m; }
function shadowAll(o) { o.traverse(m => { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); }

function makeHand(skin, side) {
  const hand = new THREE.Group();
  const palm = sphere(.017, skin, .55, 1.25, 1); palm.position.y = -.018; hand.add(palm);
  const fingers = [];
  for (let i = 0; i < 4; i++) {
    const f = new THREE.Group(); f.position.set(0, -.036, (i - 1.5) * .0072);
    const len = [.019, .022, .021, .017][i];
    const seg = new THREE.Mesh(new THREE.CapsuleGeometry(.0034, len, 3, 8), skin); seg.position.y = -len / 2; f.add(seg);
    f.rotation.z = side * .25; f.rotation.x = (i - 1.5) * -.05;
    hand.add(f); fingers.push(f);
  }
  const th = new THREE.Group(); th.position.set(side * -.002, -.016, .013);
  const ts = new THREE.Mesh(new THREE.CapsuleGeometry(.0039, .016, 3, 8), skin); ts.position.y = -.009; th.add(ts);
  th.rotation.x = .55; th.rotation.z = side * -.2; hand.add(th);
  return { hand, fingers, thumb: th };
}

// one arm: shoulder → upper arm → elbow → forearm → wrist → hand. Hangs along -y.
function makeArm(side, o) {
  const sh = new THREE.Group(); sh.position.set(side * .093, .745, 0);
  sh.rotation.order = 'ZXY';
  const up = o.sleeveUpper || o.skin;
  const ua = tube(.021, .017, .13, up); sh.add(ua);
  const cap = sphere(o.sleeve ? .024 : .02, up, 1, o.sleeve ? .8 : 1, 1); cap.position.y = -.006; sh.add(cap);
  if (o.sleeve) { const s = lathe(o.sleeve.upper, 20, 1, o.sleeve.mat); sh.add(s); }
  const el = new THREE.Group(); el.position.y = -.13; sh.add(el);
  const fa = tube(.0165, .0125, .125, o.sleeveLower || o.skin); el.add(fa);
  el.add(sphere(.0168, o.sleeveLower || o.skin));
  if (o.sleeve && o.sleeve.lower) { const s = lathe(o.sleeve.lower, 20, 1, o.sleeve.mat); el.add(s); const ep = sphere(o.sleeve.lower[0][0] * 1.05, o.sleeve.mat); el.add(ep); }
  const wr = new THREE.Group(); wr.position.y = -.125; el.add(wr);
  const h = makeHand(o.skin, side); wr.add(h.hand);
  return { sh, el, wr, ...h };
}

function makeLeg(side, o) {
  const hip = new THREE.Group(); hip.position.set(side * .038, .49, 0);
  hip.add(tube(o.thigh || .038, .029, .225, o.legUpper || o.skin));
  const kn = new THREE.Group(); kn.position.y = -.225; hip.add(kn);
  kn.add(sphere(.028, o.legUpper || o.skin));
  kn.add(tube(.027, .018, .215, o.legLower || o.skin));
  if (o.cuff) { const c = tube(.0215, .0205, .02, o.legUpper); c.position.y = -.17; kn.add(c); }
  const an = new THREE.Group(); an.position.y = -.215; kn.add(an);
  an.add(o.shoe());
  return { hip, kn, an };
}

// ---------- shoes ----------
function loafer(col) {
  return () => {
    const g = new THREE.Group(), m = new THREE.MeshPhysicalMaterial({ color: col, roughness: .35, clearcoat: .6, clearcoatRoughness: .3 });
    const b = new THREE.Mesh(new RoundedBoxGeometry(.044, .03, .1, 3, .014), m); b.position.set(0, -.012, .022); g.add(b);
    const sole = new THREE.Mesh(new RoundedBoxGeometry(.046, .008, .104, 2, .003), new THREE.MeshStandardMaterial({ color: '#2a1a12', roughness: .8 })); sole.position.set(0, -.027, .022); g.add(sole);
    const tas = sphere(.006, m, 1, .8, 1.4); tas.position.set(0, .004, .05); g.add(tas);
    return g;
  };
}
function sneaker() {
  return () => {
    const g = new THREE.Group();
    const b = new THREE.Mesh(new RoundedBoxGeometry(.046, .034, .102, 3, .015), new THREE.MeshStandardMaterial({ color: '#151418', roughness: .6 })); b.position.set(0, -.01, .022); g.add(b);
    const sole = new THREE.Mesh(new RoundedBoxGeometry(.049, .014, .107, 2, .005), new THREE.MeshStandardMaterial({ color: '#f5f3ee', roughness: .7 })); sole.position.set(0, -.027, .022); g.add(sole);
    return g;
  };
}
function sandal(skin) {
  return () => {
    const g = new THREE.Group();
    const foot = new THREE.Mesh(new RoundedBoxGeometry(.036, .022, .09, 3, .01), skin); foot.position.set(0, -.012, .02); g.add(foot);
    const sole = new THREE.Mesh(new RoundedBoxGeometry(.044, .014, .1, 2, .005), new THREE.MeshStandardMaterial({ color: '#c79a63', roughness: .7 })); sole.position.set(0, -.029, .022); g.add(sole);
    const strap = new THREE.Mesh(new THREE.TorusGeometry(.021, .004, 6, 16, Math.PI), new THREE.MeshStandardMaterial({ color: '#efe7da', roughness: .6 })); strap.position.set(0, -.02, .035); g.add(strap);
    const fm = new THREE.MeshStandardMaterial({ color: '#fbf8f1', roughness: .5 });
    for (let i = 0; i < 3; i++) { const f = sphere(.007, fm, 1, .5, 1); f.position.set((i - 1) * .012, -.006, .036); g.add(f); }
    return g;
  };
}

// ---------- characters ----------
const SKIN = (c) => new THREE.MeshPhysicalMaterial({ color: c, roughness: .58, sheen: .35, sheenColor: new THREE.Color('#ffd9c8'), sheenRoughness: .6 });
const FAB = (map, col = '#ffffff', rough = .9, sheen = .5) => new THREE.MeshPhysicalMaterial({ map, color: col, roughness: rough, sheen, sheenRoughness: .8, sheenColor: new THREE.Color('#ffffff') });

export function makeDoll(kind, opts = {}) {
  buildTextures();
  const root = new THREE.Group(), body = new THREE.Group(); root.add(body);
  const spec = SPECS[kind] ? SPECS[kind]() : extraSpec(opts);
  const skin = SKIN(spec.skin);
  const R = .09; // head radius (doll proportions: big head)

  // torso (skin) + chest group for breathing
  const chest = new THREE.Group(); chest.position.y = .55; body.add(chest);
  const torso = lathe([[.001, .44], [.064, .45], [.068, .5], [.06, .56], [.067, .62], [.076, .67], [.079, .71], [.074, .74], [.055, .765], [.026, .78], [.001, .785]].map(([r, y]) => [r, y - .55]), 32, .72, skin);
  chest.add(torso);
  if (spec.top) { const t = lathe(spec.top.profile.map(([r, y]) => [r, y - .55]), 40, .74, spec.top.mat); chest.add(t); }
  const neck = tube(.024, .021, .06, skin); neck.position.y = .835 - .55; chest.add(neck);
  if (spec.extraChest) spec.extraChest(chest, skin);

  // head
  const headPivot = new THREE.Group(); headPivot.position.y = .81 - .55; chest.add(headPivot);
  const head = new THREE.Group(); head.position.y = .095; headPivot.add(head);
  const skull = new THREE.Mesh(sculpt(new THREE.SphereGeometry(R, 48, 36), R), skin); head.add(skull);
  // face decal
  const fc = document.createElement('canvas'); fc.width = FW; fc.height = FH;
  const ftex = new THREE.CanvasTexture(fc); ftex.colorSpace = THREE.SRGBColorSpace; ftex.anisotropy = 8;
  const fgeo = sculpt(new THREE.SphereGeometry(R * 1.004, 48, 36, Math.PI / 2 - FPHI / 2, FPHI, FTH0, FTH), R * 1.004);
  const fmat = new THREE.MeshStandardMaterial({ map: ftex, transparent: true, roughness: .5, polygonOffset: true, polygonOffsetFactor: -2, depthWrite: false });
  const faceMesh = new THREE.Mesh(fgeo, fmat); faceMesh.renderOrder = 2; head.add(faceMesh);
  const nose = sphere(.0075, skin, .9, 1, .8); nose.position.set(0, -.03, R * .9); head.add(nose);
  if (spec.headwear) spec.headwear(head, R, skin);

  // arms and legs
  const armOpts = { skin, ...spec.arm };
  const armR = makeArm(-1, armOpts), armL = makeArm(1, armOpts); // R = character's right (-x)
  [armR, armL].forEach(a => { a.sh.position.y -= .55; chest.add(a.sh); });
  const legOpts = { skin, shoe: spec.shoe, ...spec.leg };
  const legR = makeLeg(-1, legOpts), legL = makeLeg(1, legOpts);
  body.add(legR.hip, legL.hip);
  if (spec.hips) body.add(lathe(spec.hips.profile, 40, .78, spec.hips.mat));
  let skirt = null;
  if (spec.skirt) {
    skirt = new THREE.Group(); skirt.position.y = spec.skirt.top; body.add(skirt);
    const prof = spec.skirt.profile.map(([r, y]) => V(r, y - spec.skirt.top));
    const g = new THREE.LatheGeometry(prof, 72, 0, TAU);
    // folds: ripple grows toward the hem
    const p = g.attributes.position, v = new THREE.Vector3();
    for (let i = 0; i < p.count; i++) {
      v.fromBufferAttribute(p, i); const a = Math.atan2(v.z, v.x), d = clamp(-v.y / (spec.skirt.top - .04), 0, 1);
      const k = 1 + d * .09 * Math.sin(a * 11) + d * .04 * Math.sin(a * 5 + 1.3);
      p.setXYZ(i, v.x * k, v.y, v.z * k * .86);
    }
    g.computeVertexNormals();
    spec.skirt.mat.side = THREE.DoubleSide; const sk = new THREE.Mesh(g, spec.skirt.mat); skirt.add(sk);
    if (spec.skirt.belt) { const b = lathe([[.069, -.0], [.07, .018], [.069, .03]], 40, .86, spec.skirt.belt); skirt.add(b);
      const buckle = new THREE.Mesh(new THREE.TorusGeometry(.012, .0025, 6, 4), new THREE.MeshStandardMaterial({ color: '#c9c3b8', metalness: .9, roughness: .3 })); buckle.position.set(0, .015, .061); buckle.rotation.z = Math.PI / 4; skirt.add(buckle); }
  }
  if (spec.accessories) spec.accessories({ root, body, chest, armR, armL, head, skin });

  // face canvas state
  const fspec = spec.face;
  let lastKey = '';
  function setFace(e) {
    const key = [e.smile, e.open, e.brow, e.inner, e.lid, e.blink, e.gx, e.gy].map(x => x.toFixed(2)).join();
    if (key === lastKey) return; lastKey = key;
    drawFace(fc.getContext('2d'), fspec, e); ftex.needsUpdate = true;
  }
  setFace({ smile: .3, open: 0, brow: 0, inner: 0, lid: 0, blink: 0, gx: 0, gy: 0 });

  shadowAll(root);
  faceMesh.castShadow = false;
  const H = spec.height * 1.25; root.scale.setScalar(H);

  // pose: everything a frame needs
  function pose(p) {
    const br = Math.sin(p.breath || 0);
    chest.scale.set(1 + .006 * br, 1 + .01 * br, 1 + .012 * br);
    chest.rotation.set(p.lean || 0, p.twist || 0, p.sway || 0);
    headPivot.rotation.set(p.headX || 0, p.headY || 0, p.headZ || 0);
    body.position.y = p.bob || 0;
    const A = (arm, q, s) => {
      arm.sh.rotation.set(-(q.flex || 0), q.twist || 0, s * (q.abd ?? .12));
      arm.el.rotation.set(-(q.bend ?? .15), 0, 0);
      arm.wr.rotation.set(q.wflex || 0, q.wtw || 0, s * (q.wdev || 0));
      arm.fingers.forEach((f, i) => { f.rotation.x = (i - 1.5) * -.05 - (q.curl ?? .35) * (1 + i * .08); });
      arm.thumb.rotation.x = .55 + (q.curl ?? .35) * .6;
    };
    A(armR, p.armR || {}, -1); A(armL, p.armL || {}, 1);
    const L = (leg, q) => { leg.hip.rotation.set(-(q.flex || 0), 0, q.abd || 0); leg.kn.rotation.set(q.knee || 0, 0, 0); leg.an.rotation.set(-(q.ankle || 0), 0, 0); };
    L(legR, p.legR || {}); L(legL, p.legL || {});
    if (skirt) skirt.rotation.set(p.skirtX || 0, 0, p.skirtZ || 0);
    setFace({ smile: 0, open: 0, brow: 0, inner: 0, lid: 0, blink: 0, gx: 0, gy: 0, ...(p.face || {}) });
  }
  return { root, pose, H, kind, head, headPivot, chest, armR, armL, spec };
}

// ----- character specs -----
const SPECS = {
  hind: () => {
    const cream = FAB(TEX.cream, '#ffffff', .92), royal = FAB(TEX.royal, '#ffffff', .95, .7), patch = FAB(TEX.patch, '#ffffff', .9, .4);
    return {
      height: 1.55, skin: '#f4d3c0',
      face: { eyeX: .37, eyeY: -.1, eyeW: .22, eyeH: .175, tilt: .04, wing: .12, iris: .135, irisColor: '#7a4a26', irisLight: '#c08a52', lash: '#2a1810', brow: '#4b2c1c', lip: '#d77f7c', lipTop: '#c66c6c', blush: 'rgba(240,135,130,.42)', mole: [.25, -.32] },
      top: { profile: [[.07, .49], [.072, .52], [.066, .56], [.071, .62], [.081, .67], [.083, .71], [.078, .74], [.06, .767], [.03, .786], [.024, .79]], mat: cream },
      arm: { sleeveUpper: cream, sleeveLower: cream, sleeve: { mat: cream, upper: [[.026, .0], [.029, -.05], [.028, -.13]], lower: [[.027, .0], [.032, -.05], [.03, -.09], [.02, -.105], [.0185, -.125]] } },
      skirt: { top: .565, mat: patch, profile: [[.0, .565], [.069, .565], [.074, .52], [.098, .4], [.13, .24], [.158, .1], [.168, .05], [.0, .05]] },
      shoe: loafer('#4a2a1a'),
      headwear: (head, R) => {
        // under-cap (white band at the forehead)
        const under = new THREE.Mesh(sculpt(new THREE.SphereGeometry(R * 1.045, 48, 32), R * 1.045, { taper: .22, cheek: 0 }),
          new THREE.MeshStandardMaterial({ color: '#f4f1ea', roughness: .9, alphaMap: openingMask(1.1, 2.76, .975), alphaTest: .5, side: THREE.DoubleSide }));
        head.add(under);
        const hij = new THREE.Mesh(sculpt(new THREE.SphereGeometry(R * 1.085, 56, 40), R * 1.085, { taper: .22, cheek: 0, front: 1 }),
          new THREE.MeshPhysicalMaterial({ map: TEX.royal, bumpMap: TEX.royal, bumpScale: 2.5, roughness: .95, sheen: .8, sheenColor: new THREE.Color('#6d86ff'), sheenRoughness: .6, alphaMap: openingMask(1.04, 2.74, 1.0), alphaTest: .5, side: THREE.DoubleSide }));
        hij.scale.set(1.0, 1.02, 1.04); hij.position.set(0, .006, -.008); head.add(hij);
      },
      extraChest: (chest) => {
        const royal = new THREE.MeshPhysicalMaterial({ map: TEX.royal, bumpMap: TEX.royal, bumpScale: 2.5, roughness: .95, sheen: .8, sheenColor: new THREE.Color('#6d86ff'), side: THREE.DoubleSide });
        // drape around neck and over the shoulders
        const drape = lathe([[.045, .85], [.055, .825], [.072, .795], [.09, .768], [.1, .745], [.102, .72], [.1, .69], [.095, .665], [.093, .655]].map(([r, y]) => [r, y - .55]), 72, .8, royal);
        { const p = drape.geometry.attributes.position, v = new THREE.Vector3();
          for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i); const a = Math.atan2(v.x, v.z), d = clamp((.85 - .55 - v.y) / .2, 0, 1);
            const k = 1 + d * (.035 * Math.sin(a * 7) + .02 * Math.sin(a * 3 + 1)); p.setXYZ(i, v.x * k, v.y - d * d * .006 * (1 + Math.sin(a * 7)), v.z * k); }
          drape.geometry.computeVertexNormals(); }
        chest.add(drape);
        // long scarf end over her left shoulder
        const tail = new THREE.Mesh(new RoundedBoxGeometry(.046, .24, .008, 2, .0035), royal);
        tail.position.set(.056, .6 - .55, .064); tail.rotation.set(-.12, 0, -.08); chest.add(tail); chest.userData.tail = tail;
        // necklace of lapis beads
        const bm = new THREE.MeshPhysicalMaterial({ color: '#2238a8', roughness: .2, clearcoat: 1 });
        for (let i = 0; i < 15; i++) { const a = (i / 14 - .5) * 2.3; const b = sphere(.0055, bm); b.position.set(Math.sin(a) * .06, .695 - .55 - Math.cos(a) * .04 + .04, Math.cos(a) * .06 * .74 + .006); chest.add(b); }
      },
      accessories: ({ chest, armL }) => {
        // cross-body leather bag: strap over the right shoulder, bag at the left hip
        const lm = new THREE.MeshPhysicalMaterial({ map: TEX.leather, roughness: .55, clearcoat: .3 });
        const pts = [[-.085, .76, 0], [-.06, .74, .066], [0, .66, .074], [.06, .58, .07], [.1, .52, .045]].map(([x, y, z]) => new THREE.Vector3(x, y - .55, z));
        chest.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 24, .0045, 6), lm));
        const back = [[-.085, .76, 0], [-.04, .72, -.065], [.04, .62, -.065], [.1, .52, -.03]].map(([x, y, z]) => new THREE.Vector3(x, y - .55, z));
        chest.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(back), 24, .0045, 6), lm));
        const bag = new THREE.Mesh(new RoundedBoxGeometry(.03, .075, .085, 3, .012), lm); bag.position.set(.112, .47 - .55, .02); chest.add(bag);
        const flap = new THREE.Mesh(new RoundedBoxGeometry(.006, .05, .088, 2, .003), lm); flap.position.set(.128, .49 - .55, .02); chest.add(flap);
        const buckle = new THREE.Mesh(new THREE.BoxGeometry(.004, .012, .014), new THREE.MeshStandardMaterial({ color: '#d8b25a', metalness: 1, roughness: .3 })); buckle.position.set(.132, .475 - .55, .02); chest.add(buckle);
        // gold watch
        const w = new THREE.Mesh(new THREE.TorusGeometry(.014, .003, 6, 20), new THREE.MeshStandardMaterial({ color: '#d9b15a', metalness: 1, roughness: .25 }));
        w.rotation.x = Math.PI / 2; w.position.y = -.112; armL.el.add(w);
      },
    };
  },
  loreen: () => {
    const pink = FAB(TEX.pink, '#ffffff', .6, .6), black = FAB(TEX.black, '#9a9aa2', .8, .12);
    return {
      height: 1.62, skin: '#f1ceb5',
      face: { eyeX: .38, eyeY: -.09, eyeW: .235, eyeH: .14, tilt: .2, wing: .32, iris: .115, irisColor: '#6a3e20', irisLight: '#b3793f', lash: '#1b0f0a', brow: '#3a2216', lip: '#d8737a', lipTop: '#c96470', blush: 'rgba(240,140,140,.32)' },
      top: { profile: [[.07, .49], [.07, .53], [.066, .56], [.071, .62], [.08, .67], [.082, .71], [.077, .74], [.06, .767], [.032, .786], [.026, .8]], mat: pink },
      arm: { sleeveUpper: pink, sleeveLower: pink, sleeve: { mat: pink, upper: [[.026, .0], [.03, -.03], [.024, -.08], [.021, -.13]], lower: [[.019, .0], [.022, -.06], [.022, -.1], [.0185, -.112], [.0175, -.125]] } },
      skirt: { top: .58, mat: black, belt: new THREE.MeshStandardMaterial({ color: '#141216', roughness: .4 }), profile: [[.0, .58], [.07, .58], [.072, .54], [.1, .42], [.135, .26], [.165, .12], [.172, .075], [.0, .075]] },
      shoe: sneaker(),
      headwear: (head, R) => {
        const fl = new THREE.MeshPhysicalMaterial({ map: TEX.floral, roughness: .85, sheen: .6, sheenColor: new THREE.Color('#ffffff'), alphaMap: openingMask(1.0, 2.9, 1.05, (g, w, h) => { g.fillRect(0, h * .74, w, h); }), alphaTest: .5, side: THREE.DoubleSide });
        const tur = new THREE.Mesh(sculpt(new THREE.SphereGeometry(R * 1.1, 56, 40), R * 1.1, { taper: .1, cheek: 0, front: 1 }), fl);
        tur.position.set(0, .01, -.004); head.add(tur);
        const flo = new THREE.MeshPhysicalMaterial({ map: TEX.floral, roughness: .85, sheen: .6 });
        const knot = sphere(.05, flo, 1.25, .85, 1); knot.position.set(0, .085, -.035); head.add(knot);
        const twist = new THREE.Mesh(new THREE.TorusGeometry(.097, .017, 10, 40, Math.PI * 1.1), flo); twist.position.set(0, .04, -.004); twist.rotation.set(-.35, 0, Math.PI * -.05); head.add(twist);
        const pearl = new THREE.MeshPhysicalMaterial({ color: '#fbf6ec', roughness: .15, clearcoat: 1 });
        for (const s of [-1, 1]) { const p = sphere(.006, pearl); p.position.set(s * .088, -.035, .0); head.add(p); }
      },
      extraChest: (chest, skin) => {
        const ch = new THREE.Mesh(new THREE.TorusGeometry(.024, .005, 8, 24), new THREE.MeshStandardMaterial({ color: '#111', roughness: .4 })); ch.rotation.x = Math.PI / 2; ch.position.y = .825 - .55; ch.scale.z = .9; chest.add(ch);
        // bow at the collar
        const pk = new THREE.MeshPhysicalMaterial({ map: TEX.pink, roughness: .5, sheen: .7 });
        for (const s of [-1, 1]) { const l = sphere(.02, pk, 1.1, .6, .4); l.position.set(s * .02, .772 - .55, .058); l.rotation.z = s * .4; chest.add(l); }
        const k = sphere(.008, pk); k.position.set(0, .772 - .55, .06); chest.add(k);
        for (const s of [-1, 1]) { const tl = new THREE.Mesh(new RoundedBoxGeometry(.012, .06, .004, 1, .002), pk); tl.position.set(s * .008, .74 - .55, .06); tl.rotation.z = s * .18; chest.add(tl); }
      },
      accessories: ({ armR, armL }) => {
        // plaid handbag in her right hand
        const bag = new THREE.Group();
        const body = new THREE.Mesh(new RoundedBoxGeometry(.11, .07, .045, 3, .012), new THREE.MeshPhysicalMaterial({ map: TEX.plaid, roughness: .6 }));
        body.position.y = -.075; bag.add(body);
        const trim = new THREE.MeshStandardMaterial({ color: '#141216', roughness: .35 });
        const h = new THREE.Mesh(new THREE.TorusGeometry(.028, .004, 6, 16, Math.PI), trim); h.position.y = -.04; bag.add(h);
        const band = new THREE.Mesh(new RoundedBoxGeometry(.112, .014, .047, 2, .004), trim); band.position.y = -.06; bag.add(band);
        bag.position.set(0, -.035, .004); bag.rotation.y = Math.PI / 2; armR.wr.add(bag);
        const w = new THREE.Mesh(new THREE.TorusGeometry(.0135, .0028, 6, 20), new THREE.MeshStandardMaterial({ color: '#1a1a1a', roughness: .4 }));
        w.rotation.x = Math.PI / 2; w.position.y = -.112; armL.el.add(w);
      },
    };
  },
  lizette: () => {
    const dots = FAB(TEX.dots, '#ffffff', .8, .12), denim = FAB(TEX.denim, '#ffffff', .9, .3);
    const hairM = new THREE.MeshPhysicalMaterial({ map: TEX.hair, roughness: .55, sheen: 1, sheenColor: new THREE.Color('#e0b07a'), sheenRoughness: .35, side: THREE.DoubleSide });
    return {
      height: 1.58, skin: '#f2cfb3',
      face: { eyeX: .37, eyeY: -.1, eyeW: .215, eyeH: .16, tilt: .08, wing: .22, iris: .125, irisColor: '#4a2a16', irisLight: '#8a5a32', lash: '#140a06', brow: '#4a2c1a', lip: '#d47c76', lipTop: '#c4686a', blush: 'rgba(240,140,130,.38)' },
      top: { profile: [[.088, .47], [.086, .5], [.074, .56], [.076, .62], [.084, .67], [.088, .7], [.09, .715], [.0, .716]], mat: dots },
      arm: { sleeveUpper: dots, sleeve: { mat: dots, upper: [[.028, -.04], [.036, -.08], [.036, -.12], [.03, -.15]], lower: [[.03, .02], [.026, -.03], [.018, -.045]] } },
      leg: { legUpper: denim, legLower: denim, cuff: true, thigh: .046 },
      hips: { profile: [[.001, .435], [.05, .44], [.07, .47], [.074, .51], [.068, .56], [.0, .56]], mat: denim },
      shoe: sandal(SKIN('#f2cfb3')),
      headwear: (head, R) => {
        const hairShell = new THREE.Mesh(sculpt(new THREE.SphereGeometry(R * 1.06, 56, 40), R * 1.06, { taper: .05, cheek: 0, front: 1 }),
          new THREE.MeshPhysicalMaterial({ map: TEX.hair, roughness: .55, sheen: 1, sheenColor: new THREE.Color('#e0b07a'), alphaMap: openingMask(1.0, 3.3, 1.02), alphaTest: .5, side: THREE.DoubleSide }));
        hairShell.position.set(0, .004, -.006); head.add(hairShell);
        // long hair: a lathe curtain open at the face, waves down to mid-back
        const prof = []; for (let i = 0; i <= 24; i++) { const t = i / 24; const y = .03 - t * .37; const r = (t < .3 ? lerp(.096, .12, t / .3) : lerp(.12, .128, (t - .3) / .7)) + .005 * Math.sin(t * 18); prof.push(V(r, y)); }
        const g = new THREE.LatheGeometry(prof, 48, .78, TAU - 1.56); // opening centred on +z (lathe φ=0 is +z)
        g.scale(1, 1, .82);
        const curtain = new THREE.Mesh(g, hairM); curtain.position.set(0, -.0, -.004); head.add(curtain);
        head.userData.hair = curtain;
        // cap
        const cm = new THREE.MeshStandardMaterial({ color: '#17161a', roughness: .75 });
        const dome = new THREE.Mesh(new THREE.SphereGeometry(R * 1.14, 40, 20, 0, TAU, 0, 1.45), cm); dome.position.set(0, .014, -.008); dome.scale.set(1, .95, 1.02); head.add(dome);
        const brim = new THREE.Mesh(new THREE.CylinderGeometry(.075, .075, .006, 32, 1, false, -Math.PI * .5, Math.PI), cm);
        brim.scale.set(1.15, 1, 1.25); brim.position.set(0, .04, .075); brim.rotation.x = .2; head.add(brim);
        const logo = new THREE.Mesh(new THREE.PlaneGeometry(.035, .012), new THREE.MeshBasicMaterial({ color: '#eeeeea' }));
        logo.position.set(0, .082, .086); logo.rotation.x = -.6; head.add(logo);
        const hoop = new THREE.MeshStandardMaterial({ color: '#dcdcdc', metalness: 1, roughness: .2 });
        for (const s of [-1, 1]) { const h = new THREE.Mesh(new THREE.TorusGeometry(.009, .0015, 6, 16), hoop); h.position.set(s * .092, -.05, -.004); h.rotation.y = Math.PI / 2; head.add(h); }
      },
      extraChest: (chest) => {
        // ruffled elastic neckline of the off-shoulder blouse
        const dm = FAB(TEX.dots, '#ffffff', .8, .5);
        const ruff = new THREE.Mesh(new THREE.TorusGeometry(.094, .011, 8, 48), dm); ruff.rotation.x = Math.PI / 2; ruff.scale.set(1, .74, 1.2); ruff.position.y = .712 - .55; chest.add(ruff);
        const ch = new THREE.Mesh(new THREE.TorusGeometry(.024, .005, 8, 24), new THREE.MeshStandardMaterial({ color: '#111', roughness: .4 })); ch.rotation.x = Math.PI / 2; ch.position.y = .815 - .55; chest.add(ch);
        // backpack
        const bm = new THREE.MeshStandardMaterial({ color: '#1d1c20', roughness: .55 });
        const bp = new THREE.Mesh(new RoundedBoxGeometry(.11, .13, .05, 3, .018), bm); bp.position.set(0, .63 - .55, -.085); chest.add(bp);
        for (const s of [-1, 1]) { const st = new THREE.Mesh(new THREE.TorusGeometry(.055, .006, 6, 16, Math.PI), bm); st.position.set(s * .052, .66 - .55, -.02); st.rotation.y = Math.PI / 2; st.rotation.z = Math.PI / 2 + .3; chest.add(st); }
      },
      accessories: ({ armL }) => {
        const w = new THREE.Mesh(new THREE.TorusGeometry(.0135, .0028, 6, 20), new THREE.MeshStandardMaterial({ color: '#cfcfcf', metalness: 1, roughness: .25 }));
        w.rotation.x = Math.PI / 2; w.position.y = -.112; armL.el.add(w);
      },
    };
  },
};

// background students: same build, simpler palettes (seen small and blurred)
const EXTRA_TOPS = ['#e8d9c0', '#9fc3e6', '#f2b8a2', '#c9d9a5', '#f5efe3', '#b8a6d9', '#f4d27a', '#e59a9a'];
const EXTRA_BOTTOMS = ['#2b2f45', '#4a3a2c', '#1d2a50', '#6b5b4b', '#2e2e2e', '#7a8796'];
const EXTRA_SCARF = ['#c94f6d', '#3b7a6a', '#e0b453', '#6d5ba8', '#d98c5f', '#f2e6d0'];
const sharedFace = {};
function extraSpec(o) {
  const r = rnd(o.seed || 1), pick = a => a[Math.floor(r() * a.length)];
  const top = FAB(TEX.cream, pick(EXTRA_TOPS), .9), bot = FAB(TEX.cream, pick(EXTRA_BOTTOMS), .9);
  const female = r() < .62, scarf = female && r() < .6;
  const hairC = pick(['#2a1a12', '#3b2416', '#1a1310', '#5a3a22']);
  return {
    height: female ? 1.55 + r() * .1 : 1.68 + r() * .12, skin: pick(['#f0cfb6', '#e8c0a0', '#dcb090', '#f3d6c2']),
    face: { eyeX: .37, eyeY: -.1, eyeW: .19, eyeH: .14, tilt: .08, wing: female ? .15 : 0, iris: .09, irisColor: '#5a3a20', irisLight: '#9a6a3a', lash: '#24140c', brow: '#3a2416', lip: female ? '#d47c76' : '#c08a7a', lipTop: '#b87070', blush: 'rgba(240,140,130,.25)' },
    top: { profile: [[.07, .47], [.07, .53], [.066, .56], [.071, .62], [.079, .67], [.081, .71], [.077, .74], [.06, .767], [.03, .786], [.025, .79]], mat: top },
    arm: { sleeveUpper: top, sleeveLower: r() < .5 ? top : undefined },
    leg: female && !scarf ? { legUpper: bot, legLower: bot } : { legUpper: bot, legLower: bot },
    skirt: scarf ? { top: .565, mat: bot, profile: [[.0, .565], [.069, .565], [.074, .52], [.098, .4], [.13, .24], [.152, .1], [.16, .05], [.0, .05]] } : null,
    hips: scarf ? null : { profile: [[.001, .42], [.06, .425], [.072, .47], [.072, .52], [.066, .56], [.0, .56]], mat: bot },
    shoe: r() < .5 ? sneaker() : loafer('#3a2a20'),
    headwear: (head, R) => {
      if (scarf) {
        const m = new THREE.MeshStandardMaterial({ color: pick(EXTRA_SCARF), roughness: .95, alphaMap: openingMask(1.04, 2.74, 1.0), alphaTest: .5, side: THREE.DoubleSide });
        head.add(new THREE.Mesh(sculpt(new THREE.SphereGeometry(R * 1.13, 32, 24), R * 1.13, { taper: .05, cheek: 0, front: 1 }), m));
      } else {
        const m = new THREE.MeshStandardMaterial({ color: hairC, roughness: .6, alphaMap: openingMask(1.0, female ? 3.3 : 2.4, female ? 1.02 : 1.25), alphaTest: .5, side: THREE.DoubleSide });
        const h = new THREE.Mesh(sculpt(new THREE.SphereGeometry(R * 1.06, 32, 24), R * 1.06, { taper: .05, cheek: 0, front: 1 }), m); h.position.z = -.005; head.add(h);
        if (female) { const tail = sphere(.06, m, .9, 1.6, .6); tail.position.set(0, -.08, -.06); head.add(tail); }
      }
    },
    extraChest: scarf ? (chest) => { const m = new THREE.MeshStandardMaterial({ color: '#888', roughness: .95 }); } : null,
  };
}
