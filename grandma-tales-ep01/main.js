// My Grandmother's Tales — Ep01 style test. One continuous shot, 5 s.
// window.render(t) is deterministic: every frame is computed from t alone.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { makeDoll } from './doll.js';
import { buildCampus, makeBus, suitcase, contactShadow } from './env.js';
import { makeTiltShift } from './tiltshift.js';

const Q = new URLSearchParams(location.search);
const MODE = Q.get('mode') || 'film';
const W = innerWidth, H = innerHeight;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a), 0, 1);
const ss = t => t * t * (3 - 2 * t);
const eio = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };

// ---------- renderer ----------
const canvas = document.createElement('canvas'); document.body.appendChild(canvas);
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, powerPreference: 'high-performance' });
const SSAA = +(Q.get('ssaa') || 1.25);
renderer.setPixelRatio(SSAA); renderer.setSize(W, H);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.NoToneMapping;
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;

const scene = new THREE.Scene();
scene.background = new THREE.Color('#bcd9f2');
scene.fog = new THREE.Fog('#cfe2f0', 45, 120);
const pm = new THREE.PMREMGenerator(renderer);
scene.environment = pm.fromScene(new RoomEnvironment(), .04).texture;
scene.environmentIntensity = .35;

const camera = new THREE.PerspectiveCamera(30, W / H, .1, 400);
const post = makeTiltShift(renderer, scene, camera, W, H, SSAA);

// light: hard warm sun + sky/ground fill
const hemi = new THREE.HemisphereLight('#b9d4ff', '#d9b083', 1.05); scene.add(hemi);
const sun = new THREE.DirectionalLight('#ffe3bd', 3.3); sun.castShadow = true;
sun.shadow.mapSize.set(4096, 4096); sun.shadow.bias = -.0004; sun.shadow.normalBias = .02; sun.shadow.radius = 2;
const sc = sun.shadow.camera; sc.near = 1; sc.far = 120; scene.add(sun, sun.target);

// ---------- world ----------
buildCampus(scene);
const bus = makeBus(); bus.position.set(5.6, 0, -3.6); scene.add(bus);
const BUS_DOOR = new THREE.Vector3(1.7, 0, -2.2);

// heroes
const hind = makeDoll('hind'), loreen = makeDoll('loreen'), lizette = makeDoll('lizette');
for (const d of [hind, loreen, lizette]) { scene.add(d.root); d.root.add(shadowBlob(.42)); }
function shadowBlob(s) { const m = contactShadow(s, s, .55); m.position.y = .006; m.scale.setScalar(1); return m; }
const HIND_POS = new THREE.Vector3(-1.6, 0, 1.55);
const hindCase = suitcase('#c58a4a', 1.2, true); hindCase.position.set(-2.15, 0, 1.15); hindCase.rotation.y = .5; scene.add(hindCase);

// luggage piled at the bus
const caseCols = ['#d9534f', '#2f6fb3', '#3a3a40', '#e0a93b', '#4c9a72', '#8d5bb0', '#f1ede4'];
const piles = [];
for (let i = 0; i < 9; i++) { const c = suitcase(caseCols[i % caseCols.length], 1.05 + hash(i) * .25); c.position.set(3.4 + i * .62 + hash(i + 3) * .3, 0, -.75 - hash(i + 7) * .6); c.rotation.y = (hash(i + 1) - .5) * .8; scene.add(c); piles.push(c); }

// students around the bus (seen in time-lapse)
const extras = [];
const EX = [
  // [x, z, yaw, mode, seed]  mode: chat (stand + gesture), mill (wander), board (walk to the door)
  [3.3, .1, -2.6, 'chat', 1], [3.9, -.4, -1.9, 'chat', 2], [4.5, .25, 3.0, 'chat', 3],
  [6.2, -.2, 2.4, 'chat', 4], [6.9, .35, -2.9, 'chat', 5], [7.5, -.3, -1.2, 'mill', 6],
  [8.8, .2, -2.0, 'mill', 7], [9.6, -.5, 2.2, 'chat', 8], [2.6, -1.0, -2.2, 'board', 9],
  [5.2, .9, 3.1, 'mill', 10], [10.6, .6, -2.5, 'mill', 11], [-5.5, -2.4, .4, 'chat', 12],
  [-6.2, -1.9, 2.2, 'chat', 13], [-9.0, -.8, 1.2, 'mill', 14], [1.2, -6.8, 0, 'mill', 15], [-3.0, -7.2, .6, 'mill', 16],
];
for (const [x, z, yaw, mode, seed] of EX) { const d = makeDoll('extra', { seed }); d.root.add(shadowBlob(.42)); scene.add(d.root); extras.push({ d, x, z, yaw, mode, seed }); }

// ---------- time: time-lapse clock ----------
// speed ×20 until 1.1 s, eases to ×1 by 2.4 s. World time w(t) = ∫ speed.
const speed = t => lerp(20, 1, ss(seg(t, 1.1, 2.4)));
function worldTime(t) { let w = 0; const n = Math.ceil(t * 120); const dt = t / Math.max(n, 1); for (let i = 0; i < n; i++) w += speed((i + .5) * dt) * dt; return w; }
// stutter: in fast-forward the world updates at 8 Hz; it melts into smooth motion as speed nears ×1
function steppedWorld(t) { const s = speed(t); if (s < 2.2) return worldTime(t); const q = Math.floor(t * 8) / 8; return worldTime(q); }

// ---------- poses ----------
function walkPose(ph, amp = 1) {
  const s = Math.sin(ph), c = Math.cos(ph);
  return {
    legR: { flex: .36 * s * amp, knee: .6 * Math.max(0, Math.sin(ph + 2.2)) * amp, ankle: -.15 * s * amp },
    legL: { flex: -.36 * s * amp, knee: .6 * Math.max(0, Math.sin(ph + 2.2 + Math.PI)) * amp, ankle: .15 * s * amp },
    armR: { flex: -.32 * s * amp, abd: .14, bend: .35 + .15 * Math.max(0, -s) },
    armL: { flex: .32 * s * amp, abd: .14, bend: .35 + .15 * Math.max(0, s) },
    bob: -.006 * Math.abs(c) * amp, sway: .025 * s * amp, twist: .06 * s * amp, skirtX: .05 * Math.abs(s) * amp, skirtZ: .03 * s * amp,
  };
}
const idle = (t, k) => ({ breath: t * 1.7 * Math.PI * .5 + k, sway: .012 * Math.sin(t * .9 + k), headZ: .02 * Math.sin(t * .7 + k * 2) });
const blink = (t, times) => { let b = 0; for (const bt of times) b = Math.max(b, 1 - Math.abs(t - bt) / .07); return clamp(b, 0, 1); };
function face(o) { return { smile: 0, open: 0, brow: 0, inner: 0, lid: 0, blink: 0, gx: 0, gy: 0, ...o }; }
const place = (d, x, z, yaw) => { d.root.position.set(x, 0, z); d.root.rotation.y = yaw; };

// Hind: watches the bus, unsure; turns when the friends arrive
function poseHind(t) {
  const turnH = eio(seg(t, 3.62, 4.12)), turnB = eio(seg(t, 3.78, 4.45));
  place(hind, HIND_POS.x, HIND_POS.z, lerp(1.05, .7, turnB));
  const glance = .08 * Math.sin(t * 1.3) * (1 - turnH);
  const surprise = Math.sin(Math.PI * seg(t, 3.85, 4.5)), warm = ss(seg(t, 4.15, 4.8));
  hind.pose({
    ...idle(t, 0),
    headY: lerp(.32, .25, turnH) + glance - .05 * (1 - turnB) * turnH, headX: lerp(.1, -.04, turnH) + .02 * Math.sin(t * 1.1), headZ: lerp(.05, -.04, turnH),
    lean: .02,
    armR: { flex: .22, abd: .1, twist: .95, bend: 1.15, wflex: .1, wtw: .2, curl: .6 },
    armL: { flex: .2, abd: .1, twist: -.95, bend: 1.2, wflex: .1, wtw: -.2, curl: .55 },
    legR: { flex: .02 }, legL: { flex: -.02, abd: .02 },
    skirtZ: .01 * Math.sin(t * 1.4), skirtX: .008 * Math.sin(t * 1.1),
    face: face({ smile: lerp(.08, .85, warm) * (1 - .3 * surprise), open: .38 * surprise + .12 * warm * (1 - surprise), brow: .9 * surprise + .2 * warm, inner: .55 * (1 - turnH),
      lid: .15 * (1 - turnH), blink: blink(t, [2.05, 3.66, 4.92]), gx: lerp(.75, -.55, turnH), gy: lerp(.05, -.1, turnH) }),
  });
  hind.chest.userData.tail && (hind.chest.userData.tail.rotation.x = -.12 + .03 * Math.sin(t * 2.1) + .05 * turnB * Math.sin(Math.PI * seg(t, 3.8, 4.6)));
}

// Loreen & Lizette walk from the bus door to Hind; Loreen sees her and smiles
const L0 = new THREE.Vector3(2.35, 0, -1.05), L1 = new THREE.Vector3(-.5, 0, 1.75);
const Z0 = new THREE.Vector3(3.05, 0, -.65), Z1 = new THREE.Vector3(.38, 0, 1.3);
function walker(d, t, P0, P1, t0, t1, endYaw, extra) {
  const D = P0.distanceTo(P1), u = seg(t, t0, t1), k = eio(u);
  const p = P0.clone().lerp(P1, k), dir = P1.clone().sub(P0).normalize();
  const walkYaw = Math.atan2(dir.x, dir.z), settle = ss(seg(t, t1 - .35, t1 + .25));
  place(d, p.x, p.z, lerp(walkYaw, endYaw, settle));
  const ph = (D * k) / (1.25 * d.H / 1.94) * Math.PI * 2;
  const moving = Math.sin(Math.PI * u) > 0 ? clamp(Math.min(u / .12, (1 - u) / .15), 0, 1) : 0;
  const w = walkPose(ph, moving);
  const x = extra(t, moving); for (const k in x) if (x[k] === undefined) delete x[k];
  return { ...idle(t, d.H), ...w, ...x };
}
function poseFriends(t) {
  const notice = ss(seg(t, 3.25, 3.85)), wave = Math.sin(Math.PI * seg(t, 3.95, 4.85));
  loreen.pose(walker(loreen, t, L0, L1, 2.35, 4.3, -.82, (t, m) => ({
    headY: lerp(.25, -.12, notice), headX: .03,
    armL: m > .2 ? undefined : { flex: .35 + .5 * wave, abd: .25 + .35 * wave, bend: .6 + 1.5 * wave, wtw: -.6 * wave, curl: .2 },
    armR: { flex: .04, abd: .12, twist: .3, bend: .25, curl: .75 },
    face: face({ smile: lerp(.35, 1, notice), open: .12 * notice, brow: .25 * notice, blink: blink(t, [3.05, 4.55]), gx: lerp(.2, -.5, notice), gy: -.05 }),
  })));
  lizette.pose(walker(lizette, t, Z0, Z1, 2.5, 4.45, -.62, (t, m) => ({
    headY: lerp(.1, -.2, ss(seg(t, 3.6, 4.2))), headZ: .06,
    armR: m > .2 ? undefined : { flex: .08, abd: .16, twist: .9, bend: .9, wflex: .2, curl: .5 },
    armL: m > .2 ? undefined : { flex: .04, abd: .14, twist: -.2, bend: .3, curl: .4 },
    face: face({ smile: .82, open: .22 + .1 * Math.sin(t * 7) * (m > .2 ? 1 : 0), brow: .3, blink: blink(t, [2.9, 4.25]), gx: -.4, gy: .0 }),
  })));
  // hair sways a little with the walk
  if (lizette.head.userData.hair) lizette.head.userData.hair.rotation.x = .04 * Math.sin(t * 9) * (seg(t, 2.5, 2.7) - seg(t, 4.2, 4.45));
}

function poseExtras(w) {
  extras.forEach((e, i) => {
    const k = e.seed * 1.7;
    let x = e.x, z = e.z, yaw = e.yaw, p = { ...idle(w, k) };
    if (e.mode === 'chat') {
      const g = Math.sin(w * .9 + k);
      p.armR = { flex: .3 + .25 * Math.max(0, g), abd: .2, bend: .9 + .6 * Math.max(0, g), curl: .3 };
      p.headY = .25 * Math.sin(w * .5 + k); p.face = face({ smile: .6, open: .2 * Math.max(0, Math.sin(w * 3 + k)) });
    } else if (e.mode === 'mill') {
      const a = w * .22 + k, r = 1.1;
      x += Math.sin(a) * r; z += Math.sin(a * 1.3) * .4;
      const dx = Math.cos(a) * r, dz = Math.cos(a * 1.3) * .52; yaw = Math.atan2(dx, dz);
      Object.assign(p, walkPose(w * 5.2 + k));
      p.face = face({ smile: .4 });
    } else if (e.mode === 'board') {
      // queue: step to the door, hand a case up, step back
      const c = (w * .12 + hash(k)) % 1, toDoor = Math.sin(c * Math.PI * 2);
      x = lerp(e.x, BUS_DOOR.x + .4, .5 + .5 * toDoor); z = lerp(e.z, BUS_DOOR.z + .5, .5 + .5 * toDoor);
      yaw = toDoor > 0 ? Math.PI : 0; Object.assign(p, walkPose(w * 5 + k, .8)); p.face = face({ smile: .3 });
    }
    place(e.d, x, z, yaw); e.d.pose(p);
  });
}

// ---------- camera ----------
const KEYS = [
  { t: 0.0, p: [9.5, 31, 27], c: [2.6, .6, -2.4], fov: 30 },
  { t: 1.5, p: [3.6, 10.2, 14.6], c: [.5, .9, -.4], fov: 30 },
  { t: 3.0, p: [.55, 2.15, 5.0], c: [-1.45, 1.45, 1.55], fov: 27 },
  { t: 5.0, p: [-.6, 2.35, 11.2], c: [-.6, 1.32, 1.45], fov: 30 },
];
const curP = new THREE.CatmullRomCurve3(KEYS.map(k => new THREE.Vector3(...k.p)), false, 'centripetal');
const curC = new THREE.CatmullRomCurve3(KEYS.map(k => new THREE.Vector3(...k.c)), false, 'centripetal');
// monotone time → curve parameter, gentle start and settle
function camU(t) {
  const xs = KEYS.map(k => k.t), ys = KEYS.map((k, i) => i / (KEYS.length - 1));
  const m = xs.map((x, i) => i === 0 || i === xs.length - 1 ? 0 : (ys[i + 1] - ys[i - 1]) / (xs[i + 1] - xs[i - 1]));
  m[0] = .05; m[m.length - 1] = .02;
  let i = 0; while (i < xs.length - 2 && t > xs[i + 1]) i++;
  const h = xs[i + 1] - xs[i], s = clamp((t - xs[i]) / h, 0, 1), s2 = s * s, s3 = s2 * s;
  return (2 * s3 - 3 * s2 + 1) * ys[i] + (s3 - 2 * s2 + s) * h * m[i] + (-2 * s3 + 3 * s2) * ys[i + 1] + (s3 - s2) * h * m[i + 1];
}
const headWorld = (d) => { const v = new THREE.Vector3(); d.head.getWorldPosition(v); return v; };

function shotFilm(t) {
  const u = camU(t);
  camera.position.copy(curP.getPoint(u)); camera.lookAt(curC.getPoint(u));
  // fov follows the keys
  let i = 0; while (i < KEYS.length - 2 && t > KEYS[i + 1].t) i++;
  camera.fov = lerp(KEYS[i].fov, KEYS[i + 1].fov, ss(seg(t, KEYS[i].t, KEYS[i + 1].t)));
  camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  // focus subject: the crowd at the bus → Hind → the meeting
  const crowd = new THREE.Vector3(3.6, 1.0, -.6), h = headWorld(hind), lo = headWorld(loreen);
  const meet = h.clone().lerp(lo, .5);
  let f = crowd.clone().lerp(h, ss(seg(t, 1.0, 2.5)));
  f.lerp(meet, ss(seg(t, 3.7, 4.6)));
  const P = post.P, dist = camera.position.distanceTo(f);
  const sy = f.clone().project(camera).y * .5 + .5;
  const near = ss(seg(t, 1.3, 2.8));
  Object.assign(P, {
    focus: dist, bandY: sy,
    bandW: lerp(.06, .085, near) + .03 * ss(seg(t, 3.7, 4.7)),
    amp: lerp(26, 22, near) + 12 * ss(seg(t, 3.5, 5)), mixv: lerp(.85, .6, near), aper: lerp(220, 40, near) + 50 * ss(seg(t, 3.5, 5)), maxCoc: 22,
  });
}
function shotPortrait(d, yawOff = 0) {
  const p = d.root.position, yaw = d.root.rotation.y + yawOff, h = d.H;
  camera.fov = 24;
  camera.position.set(p.x + Math.sin(yaw) * 5.6, h * .78, p.z + Math.cos(yaw) * 5.6);
  camera.lookAt(p.x, h * .5, p.z); camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  Object.assign(post.P, { focus: 5.6, bandY: .52, bandW: .3, amp: 14, mixv: .25, aper: 40, maxCoc: 18 });
}
function shotDiorama() {
  camera.fov = 28; camera.position.set(14, 30, 34); camera.lookAt(1.5, 0, -4); camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  const sy = new THREE.Vector3(3, 1, -2.5).project(camera).y * .5 + .5;
  Object.assign(post.P, { focus: 44, bandY: sy, bandW: .07, amp: 26, mixv: .9, aper: 200, maxCoc: 22 });
}

function lightFor(t) {
  // the sun swings during the time-lapse so the faces we land on are front-lit
  const k = ss(seg(t, 0, 3));
  const dir = new THREE.Vector3(lerp(-.55, .18, k), lerp(.72, .76, k), lerp(.42, .64, k)).normalize();
  const c = new THREE.Vector3(0, 0, -1);
  sun.position.copy(c).addScaledVector(dir, 50); sun.target.position.copy(c);
  sc.left = -20; sc.right = 20; sc.top = 20; sc.bottom = -20; sc.updateProjectionMatrix();
}

window.DUR = 5;
window.render = (t) => {
  t = clamp(t, 0, 5);
  const T = MODE === 'film' ? t : MODE === 'diorama' ? .6 : 4.9;
  lightFor(MODE === 'diorama' ? 3 : T);
  poseHind(T); poseFriends(T); poseExtras(steppedWorld(T));
  scene.updateMatrixWorld(true);
  if (MODE === 'film' || MODE === 'group') shotFilm(MODE === 'group' ? 5 : T);
  else if (MODE === 'hind') shotPortrait(hind, -.35);
  else if (MODE === 'loreen') shotPortrait(loreen, .3);
  else if (MODE === 'lizette') shotPortrait(lizette, .25);
  else if (MODE === 'diorama') shotDiorama();
  post.render();
};
document.fonts.ready.then(() => { window.render(0); window.READY = true; });
