// The miniature campus: paved plaza, limestone faculty buildings, entrance gate, trees and flower beds,
// a passenger bus and luggage. Fictional place (no real landmark, brand or logo).
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const TAU = Math.PI * 2;
function rnd(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function ctex(w, h, draw, rep, srgb = true) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep); }
  return t;
}
function noiseFill(g, w, h, amt, seed, n = 1) { const r = rnd(seed), d = g.getImageData(0, 0, w, h); for (let i = 0; i < d.data.length; i += 4) { const k = (r() - .5) * amt; d.data[i] += k; d.data[i + 1] += k; d.data[i + 2] += k * .9; } g.putImageData(d, 0, 0); }
const shadow = (o, c = true, rcv = true) => { o.traverse(m => { if (m.isMesh) { m.castShadow = c; m.receiveShadow = rcv; } }); return o; };

// limestone facade: courses of blocks, arched windows with dark reveals and sky-reflective glass, grime toward the ground
function facadeTex(bays, floors, seed, tint = '#e6d6b8') {
  const W = 128 * bays, H = 160 * floors + 40;
  return ctex(W, H, (g) => {
    const r = rnd(seed);
    g.fillStyle = tint; g.fillRect(0, 0, W, H);
    for (let y = 0; y < H; y += 20) { const off = (y / 20) % 2 ? 0 : 22; for (let x = -off; x < W; x += 44) {
      const k = (r() - .5) * 26; g.fillStyle = `rgba(${k > 0 ? 255 : 60},${k > 0 ? 245 : 45},${k > 0 ? 225 : 30},${Math.abs(k) / 120})`; g.fillRect(x + 1, y + 1, 42, 18); } }
    g.strokeStyle = 'rgba(120,95,65,.35)'; g.lineWidth = 1.5;
    for (let y = 0; y < H; y += 20) { g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); }
    // cornice + plinth
    g.fillStyle = 'rgba(255,250,235,.7)'; g.fillRect(0, 0, W, 14); g.fillStyle = 'rgba(90,70,50,.35)'; g.fillRect(0, 14, W, 5);
    g.fillStyle = 'rgba(150,125,95,.6)'; g.fillRect(0, H - 34, W, 34);
    for (let f = 0; f < floors; f++) for (let b = 0; b < bays; b++) {
      const x = b * 128 + 34, y = 40 + f * 160 + 22, w = 60, h = 96;
      // surround
      g.fillStyle = 'rgba(250,244,228,.9)'; g.beginPath(); g.moveTo(x - 9, y + h + 8); g.lineTo(x - 9, y + 26); g.arc(x + w / 2, y + 26, w / 2 + 9, Math.PI, 0); g.lineTo(x + w + 9, y + h + 8); g.fill();
      // reveal (dark) then glass
      g.fillStyle = '#4a3b2e'; g.beginPath(); g.moveTo(x, y + h); g.lineTo(x, y + 26); g.arc(x + w / 2, y + 26, w / 2, Math.PI, 0); g.lineTo(x + w, y + h); g.fill();
      const gl = g.createLinearGradient(0, y, 0, y + h); gl.addColorStop(0, '#9ec6e0'); gl.addColorStop(.5, '#3f6f93'); gl.addColorStop(1, '#2a4560');
      g.fillStyle = gl; g.beginPath(); g.moveTo(x + 5, y + h - 4); g.lineTo(x + 5, y + 28); g.arc(x + w / 2, y + 28, w / 2 - 5, Math.PI, 0); g.lineTo(x + w - 5, y + h - 4); g.fill();
      g.strokeStyle = '#efe6d2'; g.lineWidth = 3; g.beginPath(); g.moveTo(x + w / 2, y + 4); g.lineTo(x + w / 2, y + h - 4); g.moveTo(x + 5, y + 50); g.lineTo(x + w - 5, y + 50); g.stroke();
      g.fillStyle = 'rgba(255,255,255,.25)'; g.beginPath(); g.moveTo(x + 10, y + h - 8); g.lineTo(x + 22, y + 30); g.lineTo(x + 28, y + 30); g.lineTo(x + 16, y + h - 8); g.fill();
      if (r() < .3) { g.fillStyle = 'rgba(255,240,200,.5)'; g.fillRect(x + 8, y + 56, w - 16, 30); }
      g.fillStyle = 'rgba(255,250,240,.95)'; g.fillRect(x - 12, y + h + 6, w + 24, 7); // sill
      g.fillStyle = 'rgba(70,50,30,.25)'; g.fillRect(x - 10, y + h + 13, w + 20, 18); // stain under sill
    }
    const gr = g.createLinearGradient(0, H * .55, 0, H); gr.addColorStop(0, 'rgba(60,45,30,0)'); gr.addColorStop(1, 'rgba(60,45,30,.35)'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
    noiseFill(g, W, H, 14, seed + 1);
  });
}
function building(w, d, floors, seed, tint) {
  const grp = new THREE.Group(), fh = 3.4, h = floors * fh + .8;
  const ft = facadeTex(Math.max(2, Math.round(w / 3.2)), floors, seed, tint), st = facadeTex(Math.max(2, Math.round(d / 3.2)), floors, seed + 5, tint);
  const roof = new THREE.MeshStandardMaterial({ color: '#cbbfa8', roughness: .95 });
  const mf = new THREE.MeshStandardMaterial({ map: ft, roughness: .9 }), ms = new THREE.MeshStandardMaterial({ map: st, roughness: .9 });
  const box = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), [ms, ms, roof, roof, mf, mf]); box.position.y = h / 2; grp.add(box);
  const cor = new THREE.Mesh(new THREE.BoxGeometry(w + .5, .35, d + .5), new THREE.MeshStandardMaterial({ color: '#efe5d0', roughness: .8 })); cor.position.y = h + .1; grp.add(cor);
  const par = new THREE.Mesh(new THREE.BoxGeometry(w + .3, .6, d + .3), new THREE.MeshStandardMaterial({ color: '#e2d4b8', roughness: .9 })); par.position.y = h + .5; grp.add(par);
  // roof clutter: water tanks, a little stair house, solar heaters — typical of the region
  const r = rnd(seed * 7);
  const tankM = new THREE.MeshStandardMaterial({ color: '#f2f2ee', roughness: .5 }), darkM = new THREE.MeshStandardMaterial({ color: '#3d4a5a', roughness: .4, metalness: .3 });
  for (let i = 0; i < 3; i++) { const t = new THREE.Mesh(new THREE.CylinderGeometry(.45, .45, 1, 16), tankM); t.position.set((r() - .5) * (w - 2), h + 1.3, (r() - .5) * (d - 2)); grp.add(t); }
  const sp = new THREE.Mesh(new THREE.BoxGeometry(1.6, .08, 1.1), darkM); sp.position.set((r() - .5) * (w - 3), h + 1.1, (r() - .5) * (d - 3)); sp.rotation.x = -.5; grp.add(sp);
  const hut = new THREE.Mesh(new THREE.BoxGeometry(2.4, 2, 2.4), new THREE.MeshStandardMaterial({ color: '#e6d8bd', roughness: .9 })); hut.position.set(w * .3, h + 1.6, -d * .2); grp.add(hut);
  return shadow(grp);
}

function tree(seed, s = 1) {
  const r = rnd(seed), g = new THREE.Group();
  const trunkM = new THREE.MeshStandardMaterial({ color: '#6b4a32', roughness: .95 });
  const tr = new THREE.Mesh(new THREE.CylinderGeometry(.09 * s, .14 * s, 2.2 * s, 8), trunkM); tr.position.y = 1.1 * s; g.add(tr);
  const greens = ['#3f8f2e', '#4fa336', '#358027', '#5cae3a'];
  for (let i = 0; i < 7; i++) {
    const geo = new THREE.SphereGeometry((.75 + r() * .5) * s, 28, 20), p = geo.attributes.position, ph = r() * 9;
    for (let k = 0; k < p.count; k++) { const x = p.getX(k), y = p.getY(k), z = p.getZ(k); const f = 1 + .09 * Math.sin(x * 7 + ph) * Math.sin(y * 6 + ph) * Math.sin(z * 7) + .05 * Math.sin(x * 17 + y * 13); p.setXYZ(k, x * f, y * f * .9, z * f); }
    geo.computeVertexNormals();
    const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: greens[i % 4], map: leafTex(), bumpMap: leafTex(), bumpScale: 3, roughness: .8 }));
    const a = r() * TAU, rr = (i ? .6 : 0) * s; m.position.set(Math.cos(a) * rr, (2.6 + r() * .9) * s, Math.sin(a) * rr); g.add(m);
  }
  return shadow(g);
}
let _leaf; function leafTex() {
  if (_leaf) return _leaf;
  _leaf = ctex(256, 256, (g, w, h) => { const r = rnd(99); g.fillStyle = '#c8d8b0'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 2600; i++) { const x = r() * w, y = r() * h, k = r(); g.fillStyle = k < .35 ? 'rgba(40,70,20,.55)' : k < .7 ? 'rgba(255,255,220,.45)' : 'rgba(120,160,70,.6)'; g.beginPath(); g.ellipse(x, y, 3 + r() * 3, 1.6 + r() * 1.5, r() * 6.3, 0, 6.3); g.fill(); } }, [3, 3]);
  return _leaf;
}
function cypress(seed, s = 1) {
  const g = new THREE.Group();
  const prof = []; for (let i = 0; i <= 16; i++) { const t = i / 16; prof.push(new THREE.Vector2(.55 * s * Math.sin(Math.PI * Math.pow(t, .8)) * (1 - .35 * t) + .02, t * 4.4 * s)); }
  const m = new THREE.Mesh(new THREE.LatheGeometry(prof, 20), new THREE.MeshStandardMaterial({ color: '#3f8a34', map: leafTex(), bumpMap: leafTex(), bumpScale: 3, roughness: .85 }));
  m.position.y = .3 * s; g.add(m);
  const t = new THREE.Mesh(new THREE.CylinderGeometry(.08, .1, .5, 6), new THREE.MeshStandardMaterial({ color: '#5a3e2a' })); t.position.y = .25; g.add(t);
  return shadow(g);
}

function flowerBed(w, d, seed) {
  const g = new THREE.Group(), r = rnd(seed);
  const curb = new THREE.Mesh(new THREE.BoxGeometry(w + .2, .25, d + .2), new THREE.MeshStandardMaterial({ color: '#efe6d4', roughness: .8 })); curb.position.y = .12; g.add(curb);
  const soil = new THREE.Mesh(new THREE.BoxGeometry(w, .27, d), new THREE.MeshStandardMaterial({ color: '#4fa13a', roughness: .95 })); soil.position.y = .14; g.add(soil);
  const cols = ['#ff5a7a', '#ffd23f', '#ff8c42', '#ffffff', '#c86bff', '#ff3d3d'];
  const n = Math.floor(w * d * 26), geo = new THREE.SphereGeometry(.07, 8, 6);
  for (const c of cols) {
    const im = new THREE.InstancedMesh(geo, new THREE.MeshStandardMaterial({ color: c, roughness: .6 }), Math.ceil(n / cols.length));
    const M = new THREE.Matrix4();
    for (let i = 0; i < im.count; i++) { M.makeTranslation((r() - .5) * w * .95, .3 + r() * .1, (r() - .5) * d * .95); im.setMatrixAt(i, M); }
    im.castShadow = true; g.add(im);
  }
  const bushGeo = new THREE.IcosahedronGeometry(.22, 1), bm = new THREE.MeshStandardMaterial({ color: '#3d8a2c', roughness: .9 });
  const bi = new THREE.InstancedMesh(bushGeo, bm, Math.floor(w * d * 3)); const M = new THREE.Matrix4();
  for (let i = 0; i < bi.count; i++) { M.makeTranslation((r() - .5) * w * .9, .3, (r() - .5) * d * .9); bi.setMatrixAt(i, M); }
  bi.castShadow = true; g.add(bi);
  return shadow(g, false, true);
}

// passenger coach: cream body, teal band, dark glass, chrome trim, soft wheels
export function makeBus() {
  const g = new THREE.Group(), L = 11, H = 3.1, W = 2.5;
  const tex = ctex(1024, 256, (c, w, h) => {
    c.fillStyle = '#f6f1e6'; c.fillRect(0, 0, w, h);
    c.fillStyle = '#1f8a8a'; c.fillRect(0, h * .72, w, h * .1); c.fillStyle = '#e8a23a'; c.fillRect(0, h * .83, w, h * .03);
    // windows band
    const wy = h * .16, wh = h * .4;
    for (let i = 0; i < 8; i++) { const x = 70 + i * 116, gr = c.createLinearGradient(0, wy, 0, wy + wh); gr.addColorStop(0, '#5d7d95'); gr.addColorStop(1, '#16222e');
      c.fillStyle = '#1b1b1f'; c.fillRect(x - 4, wy - 4, 108, wh + 8); c.fillStyle = gr; c.fillRect(x, wy, 100, wh);
      c.fillStyle = 'rgba(255,255,255,.18)'; c.beginPath(); c.moveTo(x + 10, wy + wh); c.lineTo(x + 40, wy); c.lineTo(x + 55, wy); c.lineTo(x + 25, wy + wh); c.fill(); }
    noiseFill(c, w, h, 6, 50);
  });
  const doorTex = ctex(256, 256, (c, w, h) => { c.fillStyle = '#1c1d22'; c.fillRect(0, 0, w, h); c.fillStyle = '#3b5468'; c.fillRect(14, 14, w / 2 - 20, h - 40); c.fillRect(w / 2 + 6, 14, w / 2 - 20, h - 40); c.fillStyle = '#c9ccd0'; c.fillRect(w / 2 - 3, 0, 6, h); });
  const bodyM = new THREE.MeshPhysicalMaterial({ map: tex, roughness: .35, clearcoat: .8, clearcoatRoughness: .2 });
  const plain = new THREE.MeshPhysicalMaterial({ color: '#f6f1e6', roughness: .35, clearcoat: .8 });
  const body = new THREE.Mesh(new RoundedBoxGeometry(L, H, W, 4, .35), [plain, plain, plain, plain, bodyM, bodyM]);
  // RoundedBox has one group; apply side map by using UV-mapped single material instead
  body.material = bodyM; body.position.y = H / 2 + .45; g.add(body);
  // fix UVs: project side UVs from x/y so the livery wraps both long sides
  { const p = body.geometry.attributes.position, uv = body.geometry.attributes.uv; for (let i = 0; i < p.count; i++) uv.setXY(i, p.getX(i) / L + .5, p.getY(i) / H + .5); uv.needsUpdate = true; }
  const door = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 2.3), new THREE.MeshStandardMaterial({ map: doorTex, roughness: .3 })); door.position.set(-L / 2 + 1.6, 1.75, W / 2 + .01); g.add(door);
  const glass = new THREE.MeshPhysicalMaterial({ color: '#1c2a36', roughness: .05, metalness: .2, clearcoat: 1 });
  const ws = new THREE.Mesh(new THREE.PlaneGeometry(W - .3, 1.5), glass); ws.position.set(-L / 2 - .01, 2.6, 0); ws.rotation.y = -Math.PI / 2; g.add(ws);
  const chrome = new THREE.MeshStandardMaterial({ color: '#d9dde2', metalness: 1, roughness: .2 });
  const bump = new THREE.Mesh(new RoundedBoxGeometry(.25, .35, W + .05, 2, .08), chrome); bump.position.set(-L / 2 - .05, .7, 0); g.add(bump);
  const hl = new THREE.MeshStandardMaterial({ color: '#fff7d8', emissive: '#fff2c0', emissiveIntensity: .6 });
  for (const s of [-1, 1]) { const h = new THREE.Mesh(new THREE.CylinderGeometry(.16, .16, .06, 16), hl); h.rotation.z = Math.PI / 2; h.position.set(-L / 2 - .02, 1.05, s * .85); g.add(h); }
  const tl = new THREE.MeshStandardMaterial({ color: '#d42a2a', emissive: '#a01010', emissiveIntensity: .4 });
  for (const s of [-1, 1]) { const h = new THREE.Mesh(new THREE.BoxGeometry(.06, .4, .2), tl); h.position.set(L / 2 + .02, 1.2, s * 1.0); g.add(h); }
  const mir = new THREE.Mesh(new THREE.BoxGeometry(.1, .4, .25), new THREE.MeshStandardMaterial({ color: '#1b1b1f' })); mir.position.set(-L / 2 - .3, 2.7, W / 2 + .1); g.add(mir);
  const tyre = new THREE.MeshStandardMaterial({ color: '#1a1a1c', roughness: .9 }), hub = new THREE.MeshStandardMaterial({ color: '#cfd3d8', metalness: .9, roughness: .3 });
  for (const x of [-L / 2 + 2.1, L / 2 - 2.4]) for (const s of [-1, 1]) {
    const w = new THREE.Mesh(new THREE.CylinderGeometry(.55, .55, .35, 24), tyre); w.rotation.x = Math.PI / 2; w.position.set(x, .55, s * (W / 2 - .12)); g.add(w);
    const hb = new THREE.Mesh(new THREE.CylinderGeometry(.28, .28, .37, 16), hub); hb.rotation.x = Math.PI / 2; hb.position.copy(w.position); g.add(hb);
  }
  const rack = new THREE.Mesh(new RoundedBoxGeometry(L * .6, .25, W * .7, 2, .06), new THREE.MeshStandardMaterial({ color: '#d4d7db', metalness: .6, roughness: .4 })); rack.position.set(.5, H + .55, 0); g.add(rack);
  // soft contact shadow
  const cs = new THREE.Mesh(new THREE.PlaneGeometry(L + 1.4, W + 1.4), new THREE.MeshBasicMaterial({ map: blobTex(), transparent: true, depthWrite: false, opacity: .55 }));
  cs.rotation.x = -Math.PI / 2; cs.position.y = .02; g.add(cs);
  shadow(g); cs.castShadow = false;
  return g;
}

let _blob; export function blobTex() {
  if (_blob) return _blob;
  _blob = ctex(128, 128, (g, w, h) => { const gr = g.createRadialGradient(64, 64, 4, 64, 64, 64); gr.addColorStop(0, 'rgba(30,25,40,.85)'); gr.addColorStop(.6, 'rgba(30,25,40,.35)'); gr.addColorStop(1, 'rgba(30,25,40,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  return _blob;
}
export function contactShadow(w, d, op = .5) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshBasicMaterial({ map: blobTex(), transparent: true, depthWrite: false, opacity: op }));
  m.rotation.x = -Math.PI / 2; m.position.y = .012; m.renderOrder = 1; return m;
}

export function suitcase(col, s = 1, handleUp = false) {
  const g = new THREE.Group();
  const m = new THREE.MeshPhysicalMaterial({ color: col, roughness: .35, clearcoat: .7 });
  const b = new THREE.Mesh(new RoundedBoxGeometry(.42 * s, .62 * s, .24 * s, 3, .05 * s), m); b.position.y = .36 * s; g.add(b);
  const rib = new THREE.MeshStandardMaterial({ color: new THREE.Color(col).multiplyScalar(.8), roughness: .4 });
  for (const x of [-.1, .1]) { const r = new THREE.Mesh(new RoundedBoxGeometry(.03 * s, .6 * s, .25 * s, 2, .01), rib); r.position.set(x * s, .36 * s, 0); g.add(r); }
  const dark = new THREE.MeshStandardMaterial({ color: '#202024', roughness: .5 }), metal = new THREE.MeshStandardMaterial({ color: '#c8ccd2', metalness: 1, roughness: .3 });
  for (const x of [-.16, .16]) for (const z of [-.08, .08]) { const w = new THREE.Mesh(new THREE.CylinderGeometry(.03 * s, .03 * s, .03 * s, 10), dark); w.rotation.x = Math.PI / 2; w.position.set(x * s, .03 * s, z * s); g.add(w); }
  const hh = handleUp ? .38 : .04;
  for (const x of [-.09, .09]) { const p = new THREE.Mesh(new THREE.CylinderGeometry(.008 * s, .008 * s, hh * s + .04 * s, 8), metal); p.position.set(x * s, (.67 + hh / 2) * s, -.06 * s); g.add(p); }
  const top = new THREE.Mesh(new RoundedBoxGeometry(.22 * s, .03 * s, .03 * s, 2, .01), dark); top.position.set(0, (.69 + hh) * s, -.06 * s); g.add(top);
  const tag = new THREE.Mesh(new THREE.BoxGeometry(.06 * s, .08 * s, .005), new THREE.MeshStandardMaterial({ color: '#f5e6b8' })); tag.position.set(.15 * s, .62 * s, .125 * s); g.add(tag);
  g.userData.handleY = (.69 + hh) * s;
  shadow(g); g.add(contactShadow(.7 * s, .5 * s, .6));
  return g;
}

function signTex() {
  return ctex(1024, 192, (g, w, h) => {
    g.fillStyle = '#f3ead6'; g.fillRect(0, 0, w, h);
    g.fillStyle = '#1e3a5f'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.font = 'bold 64px "DejaVu Sans", sans-serif'; g.fillText('زانكۆی ژیان · جامعة الحياة', w / 2, h * .38);
    g.font = '600 40px "Inter", sans-serif'; g.fillText('UNIVERSITY OF ZHIAN', w / 2, h * .76);
    g.strokeStyle = '#b8923f'; g.lineWidth = 8; g.strokeRect(10, 10, w - 20, h - 20);
  });
}
function gate() {
  const g = new THREE.Group();
  const stone = new THREE.MeshStandardMaterial({ map: facadeTex(1, 1, 77, '#e9dcc0'), roughness: .9 });
  const st = new THREE.MeshStandardMaterial({ color: '#e7dcc4', roughness: .85 });
  for (const s of [-1, 1]) {
    const p = new THREE.Mesh(new THREE.BoxGeometry(1.4, 5.4, 1.4), st); p.position.set(s * 4.2, 2.7, 0); g.add(p);
    const cap = new THREE.Mesh(new THREE.BoxGeometry(1.7, .35, 1.7), new THREE.MeshStandardMaterial({ color: '#f5ecd8' })); cap.position.set(s * 4.2, 5.55, 0); g.add(cap);
    const lamp = new THREE.Mesh(new THREE.SphereGeometry(.28, 16, 12), new THREE.MeshStandardMaterial({ color: '#fff4d6', emissive: '#ffe6a8', emissiveIntensity: .3 })); lamp.position.set(s * 4.2, 6.0, 0); g.add(lamp);
    const wall = new THREE.Mesh(new THREE.BoxGeometry(9, 1.5, .5), st); wall.position.set(s * 9.5, .75, 0); g.add(wall);
    for (let i = 0; i < 10; i++) { const bar = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, 1.2, 6), new THREE.MeshStandardMaterial({ color: '#2b2f36', metalness: .6, roughness: .4 })); bar.position.set(s * (5.4 + i * .85), 2.1, 0); g.add(bar); }
  }
  // arch beam with the sign
  const beam = new THREE.Mesh(new THREE.BoxGeometry(9.8, 1.3, 1.0), st); beam.position.set(0, 5.0, 0); g.add(beam);
  const arch = new THREE.Mesh(new THREE.TorusGeometry(3.5, .35, 10, 40, Math.PI), st); arch.position.set(0, 3.4, 0); arch.scale.y = .45; g.add(arch);
  const sign = new THREE.Mesh(new THREE.PlaneGeometry(7.6, 1.0), new THREE.MeshStandardMaterial({ map: signTex(), roughness: .6 })); sign.position.set(0, 5.0, .51); g.add(sign);
  return shadow(g);
}

function groundTex() {
  // paving: warm sandstone tiles, a darker asphalt bus lane, grass verges; painted at 40 px / m over 60 × 60 m
  const S = 40, W = 60 * S;
  const t = ctex(W, W, (g) => {
    const r = rnd(3);
    g.fillStyle = '#5aa63e'; g.fillRect(0, 0, W, W);
    const P = (x, z) => [(x + 30) * S, (z + 30) * S];
    // plaza paving
    const pav = (x0, z0, x1, z1) => { const [a, b] = P(x0, z0), [c, d] = P(x1, z1);
      g.fillStyle = '#e6cfaa'; g.fillRect(a, b, c - a, d - b);
      for (let y = b; y < d; y += S * .5) for (let x = a + ((y - b) / (S * .5) % 2) * S * .25; x < c; x += S * .5) {
        const k = (r() - .5) * 30; g.fillStyle = `rgb(${226 + k},${204 + k},${168 + k * .8})`; g.fillRect(x + 1, y + 1, S * .5 - 2, S * .5 - 2); } };
    pav(-30, -12, 30, 8);
    pav(-4, -24, 4, -12);
    // asphalt bus lane
    { const [a, b] = P(-30, -6), [c, d] = P(30, -1.2); g.fillStyle = '#3c3f46'; g.fillRect(a, b, c - a, d - b);
      for (let i = 0; i < 9000; i++) { g.fillStyle = r() < .5 ? 'rgba(255,255,255,.05)' : 'rgba(0,0,0,.08)'; g.fillRect(a + r() * (c - a), b + r() * (d - b), 3, 3); }
      g.fillStyle = '#f2efe6'; for (let x = a; x < c; x += S * 3) g.fillRect(x, (b + d) / 2 - 3, S * 1.6, 6);
      g.fillStyle = '#f0c23a'; g.fillRect(a, d - 10, c - a, 8);
      // curb
      g.fillStyle = '#d9d2c4'; g.fillRect(a, d - 2, c - a, 10); g.fillRect(a, b - 8, c - a, 10);
      // painted bay
      g.strokeStyle = '#f2efe6'; g.lineWidth = 6; const [bx] = P(-1.5, 0), [ex] = P(12, 0); g.setLineDash([24, 18]); g.strokeRect(bx, b + 8, ex - bx, d - b - 24); g.setLineDash([]); }
    // stains
    for (let i = 0; i < 260; i++) { const x = r() * W, y = r() * W, rr = 10 + r() * 50; const gr = g.createRadialGradient(x, y, 0, x, y, rr); gr.addColorStop(0, 'rgba(60,40,20,.08)'); gr.addColorStop(1, 'rgba(60,40,20,0)'); g.fillStyle = gr; g.fillRect(x - rr, y - rr, rr * 2, rr * 2); }
    noiseFill(g, W, W, 10, 9);
  });
  return t;
}

export function buildCampus(scene) {
  const g = new THREE.Group(); scene.add(g);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ map: groundTex(), roughness: .92 }));
  ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; g.add(ground);
  // far terrain: rolling green hills of the region
  const hillM = new THREE.MeshStandardMaterial({ color: '#7fae58', roughness: 1 });
  for (let i = 0; i < 7; i++) { const h = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12), hillM); h.scale.set(18 + i * 3, 5 + (i % 3) * 3, 10); h.position.set(-50 + i * 17, -1, -52 - (i % 2) * 8); g.add(h); }
  const far = new THREE.Mesh(new THREE.PlaneGeometry(200, 120), new THREE.MeshStandardMaterial({ color: '#8fbb64', roughness: 1 })); far.rotation.x = -Math.PI / 2; far.position.y = -.02; far.position.z = -60; g.add(far);

  // buildings around the plaza (low to mid-rise)
  const B = [[-14, -20, 14, 8, 3, 11, '#e8d8b8'], [11, -21, 16, 8, 3, 12, '#ead9bb'], [-22, -2, 8, 14, 2, 13, '#e3d1b0'], [23, -4, 8, 16, 3, 14, '#e9dcc2'], [0, -34, 22, 8, 4, 15, '#e6d5b6']];
  for (const [x, z, w, d, f, s, c] of B) { const b = building(w, d, f, s, c); b.position.set(x, 0, z); g.add(b); }
  const gt = gate(); gt.position.set(0, 0, -12.5); g.add(gt);
  // trees, cypress rows and beds
  const T = [[-7, -9], [7, -9], [-12, 4], [13, 5], [-17, -9], [17, -10], [-9, 7.5], [9, 8], [-20, 8]];
  T.forEach(([x, z], i) => { const t = tree(i + 3, .9 + (i % 3) * .1); t.position.set(x, 0, z); g.add(t); });
  for (let i = 0; i < 6; i++) { const c = cypress(i, 1); c.position.set(-5.5 + (i < 3 ? -i * 1.4 : -((i - 3) * -1.4) + 11), 0, -11.5); if (i >= 3) c.position.x = 5.5 + (i - 3) * 1.4; g.add(c); }
  const beds = [[-6, 4.5, 4, 1.4], [6.5, 4.5, 4, 1.4], [-3.4, -10, 2.2, 1.2], [3.4, -10, 2.2, 1.2], [-13, -8.5, 3, 1.2], [13, -8.5, 3, 1.2]];
  beds.forEach(([x, z, w, d], i) => { const b = flowerBed(w, d, i + 11); b.position.set(x, 0, z); g.add(b); });
  // benches and lamp posts
  const pole = new THREE.MeshStandardMaterial({ color: '#2b2f36', metalness: .5, roughness: .4 }), lampM = new THREE.MeshStandardMaterial({ color: '#fff5dc', emissive: '#ffe2a0', emissiveIntensity: .25 });
  for (const x of [-12.5, -6.5, 6.5, 12.5]) { const p = new THREE.Mesh(new THREE.CylinderGeometry(.06, .08, 3.6, 8), pole); p.position.set(x, 1.8, -0.6); g.add(p); const l = new THREE.Mesh(new THREE.SphereGeometry(.2, 12, 8), lampM); l.position.set(x, 3.7, -0.6); g.add(l); }
  const wood = new THREE.MeshStandardMaterial({ color: '#a8743f', roughness: .8 });
  for (const x of [-8, 8]) { const b = new THREE.Mesh(new RoundedBoxGeometry(1.8, .12, .5, 2, .03), wood); b.position.set(x, .48, 6.4); g.add(b); const bk = new THREE.Mesh(new RoundedBoxGeometry(1.8, .4, .08, 2, .03), wood); bk.position.set(x, .8, 6.65); g.add(bk);
    for (const s of [-.7, .7]) { const l = new THREE.Mesh(new THREE.BoxGeometry(.08, .45, .45), pole); l.position.set(x + s, .22, 6.45); g.add(l); } }
  shadow(g);
  ground.castShadow = false;
  return g;
}
