// Episode 01 — shot list synchronised to the narration (see build/timeline.json for the aligned script).
const K = require('./scenes/kit');
const { cam, bg, extra, chatter, blink, idle, lip, grade, dust, rays, fade, kf, clamp, lerp, ease, easeInOut } = K;
const hind = require('./characters/hind'), loreen = require('./characters/loreen'), lizette = require('./characters/lizette');
const { toWorld } = require('./characters/rig');
const B = require('./environments/backgrounds');
const DUR = 107.075875;

// narration lines (start, end) from the pause-based alignment
const LINES = [
  [0.0, 5.86], [7.06, 13.72], [15.36, 17.42], [17.86, 23.15], [23.89, 27.72], [28.44, 34.23], [35.35, 38.14], [38.73, 43.71],
  [44.46, 50.15], [50.71, 53.54], [54.27, 57.65], [58.38, 61.25], [61.94, 65.06], [66.28, 71.25], [72.40, 76.03], [76.79, 78.82],
  [79.49, 83.88], [84.84, 86.04], [86.51, 90.67], [91.64, 92.85], [93.57, 98.81], [100.30, 105.6], [105.6, 106.9],
];

const live = (t, seed) => ({ ...idle(t, seed), blink: blink(t, seed) });
const H = (p, o) => hind.draw(p, o), LO = (p, o) => loreen.draw(p, o), LI = (p, o) => lizette.draw(p, o);
const walkP = (t, speed = 0.95) => t * Math.PI * 2 * speed;
/** Y that puts a character's face centre (local y=310) at screen y for scale s */
const faceY = (sy, s) => sy + 1540 * s;
const chatMouth = (t, ph) => Math.max(0, Math.sin(t * 9 + ph) * Math.sin(t * 2.3 + ph)) * 0.45;

const shots = [];
const shot = (a, b, render, xf = 0) => shots.push({ a, b, render, xf });

/* 01 — HOOK: Hind alone among groups of friends at the trip bus */
shot(0, 3.75, (t) => {
  const c = kf(t, [[0, [540, 980, 1.0]], [3.75, [500, 1120, 1.16]]]);
  const turn = kf(t, [[0, -0.45], [1.2, -0.45], [2.0, 0.05], [2.8, 0.5], [3.75, 0.5]]);
  return cam(c, bg('uni_bus'), 0.55)
    + cam(c, chatter('e5', 'R', 930, 1430, 0.26, t, 1, { blur: 2 }) + chatter('e6', 'L', 1000, 1436, 0.26, t, 2, { blur: 2 })
      + chatter('e1', 'R', 700, 1500, 0.32, t, 0) + chatter('e2', 'L', 790, 1506, 0.32, t, 1.4)
      + chatter('e3', 'R', 110, 1560, 0.36, t, 0.7) + chatter('e4', 'L', 210, 1566, 0.36, t, 2.2), 0.85)
    + cam(c, H({ x: 450, y: 1850, s: 0.56, ...live(t, 1), turn, look: [turn * 1.6, 0.05], smile: 0.12, worry: 0.25,
      armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' }, armR: { a: 7, e: -6 } }))
    + cam(c, extra('e3_B_L', 1010, 2380, 0.95, { blur: 8, t, bob: true }), 1.25)
    + rays(t) + dust(t) + grade({ warm: 0.1, leak: 0.35 }) + fade(1 - t / 0.5);
});

/* 02 — close-up: her eyes follow two laughing friends */
shot(3.75, 7.06, (t) => {
  const lt = t - 3.75, s = lerp(2.9, 3.15, lt / 3.3);
  const look = kf(t, [[3.75, [-0.8, 0.05]], [5.4, [-0.8, 0.05]], [6.1, [0.1, 0.55]], [7.06, [0.1, 0.6]]]);
  return bg('bokeh_warm', { x: -135 - lt * 20 })
    + chatter('e1', 'R', 200, 2100, 1.0, t, 0, { blur: 14, op: 0.85 }) + chatter('e2', 'L', 420, 2110, 1.0, t, 1.4, { blur: 14, op: 0.85 })
    + H({ x: 590, y: faceY(860, s), s, ...live(t, 1), turn: -0.18, look, smile: kf(t, [[3.75, 0.15], [6, 0.02]]), worry: kf(t, [[3.75, 0.2], [6, 0.45]]) })
    + dust(t, 18, 7) + grade({ warm: 0.1, vig: 0.6 });
}, 0.3);

/* 03 — the mystery: a girl, out of focus, who will change everything */
shot(7.06, 13.72, (t) => {
  const lt = t - 7.06;
  const c = kf(t, [[7.06, [540, 900, 1.0]], [13.72, [560, 860, 1.12]]]);
  const lx = kf(t, [[7.06, 1040], [13.72, 760]]);
  const turn = kf(t, [[7.06, -0.1], [10.2, -0.1], [11.0, 0.45], [13.72, 0.45]]);
  return cam(c, bg('uni_bus', { blur: 4 }), 0.5)
    + cam(c, chatter('e4', 'L', 240, 1500, 0.34, t, 0, { blur: 4 }) + chatter('e5', 'R', 330, 1505, 0.34, t, 1, { blur: 4 }), 0.8)
    + cam(c, `<g filter="url(#blur8)" opacity="0.9">${LO({ x: lx, y: 1560, s: 0.4, walk: walkP(t, 0.8), walkAmp: 0.8, turn: -0.4, smile: 0.5, ...live(t, 3) })}</g>`, 0.8)
    + cam(c, H({ x: 470, y: 2260, s: 1.0, ...live(t, 1), turn, look: [turn * 1.8, kf(t, [[7, 0.5], [10, 0.4], [11, 0]])],
      brow: kf(t, [[10.8, 0], [11.6, 0.45]]), smile: kf(t, [[7, 0.05], [11.5, 0.3]]), worry: kf(t, [[7, 0.35], [11.5, 0]]),
      armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } }))
    + rays(t, 1000, -100, 0.25) + dust(t) + grade({ warm: 0.12, leak: 0.45 }) + fade(kf(t, [[12.6, 0], [13.72, 1]]), '#fff8ec');
});

/* 04 — flashback: third year at university (white dissolve in) */
shot(13.72, 17.86, (t) => {
  const x = kf(t, [[13.72, 260], [17.86, 760]], (u) => u);
  const c = [lerp(480, 600, (t - 13.72) / 4.1), 980, 1.05];
  const P = { x, y: 1820, s: 0.5, ...live(t, 1), walk: walkP(t), walkAmp: 1, turn: 0.3, look: [0.4, 0], smile: 0.45,
    armR: { a: -6, e: -150, fs: 0.5, hand: 'grip' } };
  const j = {};
  const fig = H(P, { joints: j });
  const w = toWorld(P, j.R.W);
  return cam(c, bg('uni_plain'), 0.5)
    + cam(c, chatter('e5', 'R', 820, 1480, 0.3, t, 0) + chatter('e6', 'L', 900, 1486, 0.3, t, 2) + chatter('e2', 'R', 150, 1500, 0.32, t, 1), 0.8)
    + cam(c, fig + K.books(w[0] + 8, w[1] + 12, 0.5, -6))
    + dust(t) + grade({ warm: 0.14, leak: 0.3, tint: '#ffcf8a' }) + fade(kf(t, [[13.72, 1], [14.9, 0]]), '#fff8ec');
});

/* 05 — the institute: diligent study (flashback warm grade) */
shot(17.86, 20.39, (t) => {
  const c = kf(t, [[17.86, [560, 1000, 1.08]], [20.39, [520, 960, 1.0]]]);
  const write = Math.sin(t * 9) * 4;
  return cam(c, bg('study'), 0.6)
    + cam(c, H({ x: 540, y: 2470, s: 1.15, sit: true, ...live(t, 2), turn: -0.05, tilt: -5, look: [0.1, 0.95], smile: 0.12, blink: 0,
      armR: { a: 2 + write * 0.3, e: -38 + write, fs: 0.85, hand: 'grip' }, armL: { a: 2, e: -32, fs: 0.85, hand: 'relaxed' } }))
    + cam(c, K.desk(540, 1560, 1400) + K.laptopNotebooks(470, 1560, 1.05, t), 1.05)
    + grade({ warm: 0.22, tint: '#e2a96a', leak: 0.4, vig: 0.65 }) + dust(t, 16, 9);
}, 0.35);

/* 06 — entering the university directly into the second year */
shot(20.39, 23.89, (t) => {
  const u = (t - 20.39) / 3.5;
  const s = lerp(0.34, 0.6, u), y = lerp(1500, 1880, u);
  const c = [540, lerp(900, 1000, u), lerp(1.0, 1.06, u)];
  return cam(c, bg('uni_gate'), 0.7)
    + cam(c, H({ x: 540, y, s, ...live(t, 1), walk: walkP(t, 0.9), walkAmp: 0.85, turn: kf(t, [[20.4, 0.2], [22, -0.2], [23.9, 0.1]]),
      look: [0, kf(t, [[20.4, -0.6], [22.5, -0.2]])], smile: 0.6, brow: 0.2, armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } }))
    + rays(t, 900, -150, 0.3) + dust(t) + grade({ warm: 0.12, leak: 0.4 });
}, 0.35);

/* 07 — little time to get to know classmates: everyone already has their circle */
shot(23.89, 28.44, (t) => {
  const u = (t - 23.89) / 4.55;
  const s = lerp(0.4, 0.58, u), y = lerp(1640, 1880, u);
  const turn = kf(t, [[23.9, 0], [24.8, -0.55], [25.8, -0.55], [26.6, 0.55], [27.5, 0.55], [28.4, 0]]);
  const c = [540, 980, lerp(1.0, 1.05, u)];
  return cam(c, bg('corridor'), 0.6)
    + cam(c, chatter('e2', 'R', 520, 1400, 0.2, t, 0, { blur: 2 }) + chatter('e5', 'L', 590, 1402, 0.2, t, 1, { blur: 2 })
      + chatter('e1', 'R', 190, 1620, 0.42, t, 0.4) + chatter('e3', 'L', 300, 1626, 0.42, t, 1.8)
      + chatter('e4', 'R', 800, 1580, 0.4, t, 2.6) + chatter('e6', 'L', 900, 1586, 0.4, t, 0.9), 0.9)
    + cam(c, H({ x: 545, y, s, ...live(t, 1), walk: walkP(t, 0.85), walkAmp: 0.8, turn, look: [turn * 1.5, 0], smile: kf(t, [[24, 0.3], [25, 0.45], [28, 0.25]]),
      armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } }))
    + dust(t, 14) + grade({ warm: 0.08 });
}, 0.3);

/* 08 — the scientific trip is announced on the notice board */
shot(28.44, 35.35, (t) => {
  const c = kf(t, [[28.44, [1010, 700, 2.7]], [30.2, [1000, 720, 2.5]], [32.2, [720, 1000, 1.12]], [35.35, [700, 1000, 1.18]]]);
  const hx = kf(t, [[30.6, -150], [32.6, 330]]);
  const walking = t > 30.6 && t < 32.6;
  return cam(c, bg('corridor'))
    + cam(c, `<g opacity="${ease((t - 31.2) / 0.8).toFixed(3)}">` + extra(Math.sin(t * 2) > 0 ? 'e2_B_R' : 'e2_A_R', 700, 1520, 0.36, { t, bob: true, ph: 1 }) + extra(Math.sin(t * 2.3 + 1) > 0 ? 'e4_B_R' : 'e4_A_R', 820, 1600, 0.42, { t, bob: true })
      + extra(Math.sin(t * 1.9 + 2) > 0 ? 'e6_B_R' : 'e6_A_R', 560, 1660, 0.46, { t, bob: true, ph: 2 }) + '</g>')
    + cam(c, H({ x: hx, y: 1860, s: 0.56, ...live(t, 1), walk: walkP(t), walkAmp: walking ? 1 : 0, turn: 0.6, look: [1, -0.35],
      smile: kf(t, [[32, 0.2], [33.6, 0.75]]), brow: kf(t, [[32.4, 0], [33.4, 0.55]]), smileEyes: kf(t, [[33, 0], [34, 0.3]]),
      armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } }))
    + dust(t, 14) + grade({ warm: 0.1 });
}, 0.35);

/* 09a — her two close friends decide not to go */
shot(35.35, 36.95, (t) => {
  const c = [540, 960, kf(t, [[35.35, 1.0], [36.95, 1.06]])];
  return cam(c, bg('uni_plain', { blur: 4 }), 0.5)
    + cam(c, extra('e1_A_R', 260, 1880, 0.62, { t, rock: 3.5, rockF: 7, blur: 2 }) + extra('e2_A_R', 470, 1900, 0.62, { t, rock: 3.5, rockF: 7, ph: 1, blur: 2 }), 0.9)
    + cam(c, H({ x: 760, y: 2300, s: 1.0, ...live(t, 1), turn: -0.45, look: [kf(t, [[35.4, -1], [36.3, -0.6]]), kf(t, [[35.4, 0], [36.4, 0.5]])],
      smile: kf(t, [[35.4, 0.25], [36.3, -0.12]]), worry: kf(t, [[35.4, 0], [36.2, 0.6]]), brow: kf(t, [[35.4, 0.3], [36, 0]]),
      armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } }))
    + grade({ warm: 0.05, vig: 0.6 });
}, 0.3);

/* 09b — she looks at her travel bag... and decides to go anyway */
shot(36.95, 38.73, (t) => {
  const c = [560, 1020, kf(t, [[36.95, 1.0], [38.73, 1.08]])];
  const decide = ease((t - 37.7) / 0.8);
  return cam(c, bg('bedroom'), 0.6)
    + cam(c, K.suitcase(330, 1340, 0.62, 0) + H({ x: 720, y: 1900, s: 0.62, ...live(t, 2), turn: lerp(-0.45, -0.1, decide), look: [lerp(-0.9, -0.1, decide), lerp(0.8, -0.1, decide)],
      smile: lerp(0, 0.35, decide), worry: lerp(0.45, 0, decide), brow: lerp(0, 0.2, decide), tilt: lerp(-4, 2, decide),
      armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } }))
    + grade({ warm: 0.14, tint: '#ffb070', vig: 0.55 });
}, 0.25);

/* 10 — Loreen & Lizette: inseparable friends */
shot(38.73, 44.46, (t) => {
  const mid = kf(t, [[38.73, 230], [44.46, 760]], (u) => u);
  const c = kf(t, [[38.73, [mid, 1000, 1.0]], [40.8, [kf(40.8, [[38.73, 230], [44.46, 760]], (u) => u), 1000, 1.0]], [41.8, [600, 900, 1.3]], [42.9, [640, 900, 1.3]], [43.8, [470, 930, 1.3]], [44.46, [480, 930, 1.3]]]);
  const cc = [lerp(c[0], mid, t < 40.8 ? 1 : 0), c[1], c[2]];
  const ph = walkP(t, 0.9);
  return cam(cc, bg('uni_plain'), 0.5)
    + cam(cc, chatter('e5', 'L', 120, 1480, 0.3, t, 0) + chatter('e6', 'R', 980, 1480, 0.3, t, 1), 0.8)
    + cam(cc, LI({ x: mid - 140, y: 1800, s: 0.5, ...live(t, 4), walk: ph + Math.PI * 0.5, walkAmp: 0.85, turn: 0.55, look: [1, 0], smile: 0.75, open: chatMouth(t, 0), smileEyes: 0.2 })
      + LO({ x: mid + 140, y: 1800, s: 0.5, ...live(t, 3), walk: ph, walkAmp: 0.85, turn: kf(t, [[38.7, -0.5], [41.2, -0.5], [41.7, 0.15], [42.8, 0.15], [43.3, -0.5]]),
        look: [-0.9, 0], smile: 0.7, open: chatMouth(t, 2), smileEyes: kf(t, [[39.5, 0], [40.2, 0.6], [41, 0]]) }))
    + rays(t) + dust(t) + grade({ warm: 0.1, leak: 0.3 });
}, 0.35);

/* 11a — always together: sitting side by side in class */
shot(44.46, 47.4, (t) => {
  const laugh = clamp(Math.sin((t - 44.46) * 2.2) * 1.5);
  const c = [540, 1000, kf(t, [[44.46, 1.0], [47.4, 1.07]])];
  return cam(c, bg('classroom'), 0.6)
    + cam(c, LI({ x: 360, y: 2420, s: 0.86, sit: true, ...live(t, 4), turn: 0.5, tilt: 4 * laugh, look: [1, 0], smile: 0.7 + laugh * 0.2, open: laugh * 0.5, smileEyes: laugh * 0.9,
      armR: { a: -8, e: -110, fs: 0.5 }, armL: { a: -8, e: -100, fs: 0.5 } })
      + LO({ x: 720, y: 2420, s: 0.86, sit: true, noBag: true, ...live(t, 3), turn: -0.5, tilt: -4 * laugh, look: [-1, 0], smile: 0.65 + laugh * 0.25, open: laugh * 0.45, smileEyes: laugh * 0.8,
        armR: { a: -8, e: -110, fs: 0.5 }, armL: { a: -8, e: -110, fs: 0.5 } }, { noBag: true }))
    + cam(c, K.desk(540, 1500, 1200) + K.books(380, 1500, 0.9) + K.books(760, 1500, 0.8, 4), 1.05)
    + grade({ warm: 0.08 });
}, 0.3);

/* 11b — laughing together during the break */
shot(47.4, 50.71, (t) => {
  const laugh = 0.5 + 0.5 * Math.sin((t - 47.4) * 3.1);
  const c = [540, 980, kf(t, [[47.4, 1.0], [50.71, 1.06]])];
  return cam(c, bg('uni_plain', { blur: 4 }), 0.5)
    + cam(c, LI({ x: 360, y: 2330, s: 0.95, ...live(t, 4), turn: 0.45, tilt: 5 * laugh, look: [0.9, 0], smile: 0.9, open: 0.25 + laugh * 0.45, smileEyes: 0.4 + laugh * 0.5,
      armR: { a: -10, e: -70, hand: 'relaxed' } })
      + LO({ x: 730, y: 2350, s: 0.95, ...live(t, 3), turn: -0.45, tilt: -5 * laugh, look: [-0.9, 0], smile: 0.85, open: 0.2 + laugh * 0.4, smileEyes: 0.3 + laugh * 0.6,
        armL: { a: -14, e: -150, fs: 0.5, hand: 'relaxed' } }))
    + rays(t) + dust(t) + grade({ warm: 0.1, leak: 0.35 });
}, 0.3);

/* 12 — the whole college talks about their friendship */
shot(50.71, 54.27, (t) => {
  const mid = kf(t, [[50.71, 300], [54.27, 780]], (u) => u);
  const c = [lerp(480, 600, (t - 50.71) / 3.6), 1000, 1.05];
  const ph = walkP(t, 0.9);
  return cam(c, bg('uni_plain'), 0.5)
    + cam(c, LI({ x: mid - 80, y: 1580, s: 0.38, ...live(t, 4), walk: ph + 1.5, walkAmp: 0.85, turn: 0.5, smile: 0.8, open: chatMouth(t, 1) })
      + LO({ x: mid + 80, y: 1580, s: 0.38, ...live(t, 3), walk: ph, walkAmp: 0.85, turn: -0.5, smile: 0.8, open: chatMouth(t, 3) }), 0.9)
    + cam(c, extra(Math.sin(t * 2) > 0.3 ? 'e1_B_R' : 'e1_A_R', 130, 2000, 0.62, { t, bob: true }) + extra('e5_A_L', 300, 2010, 0.62, { t, bob: true, ph: 1 })
      + extra('e6_A_L', 930, 1980, 0.6, { t, bob: true, ph: 2 }), 1.1)
    + rays(t) + dust(t) + grade({ warm: 0.1, leak: 0.3 });
}, 0.3);

/* 13 — with Hind: polite colleagues, nothing more */
shot(54.27, 58.38, (t) => {
  const wave = (a, b) => ease((t - a) / 0.4) * (1 - ease((t - b) / 0.4));
  const hw = wave(55.0, 56.6), lw = wave(55.5, 57.0);
  const c = [540, 980, kf(t, [[54.27, 1.0], [58.38, 1.06]])];
  return cam(c, bg('corridor'), 0.6)
    + cam(c, chatter('e2', 'R', 560, 1420, 0.22, t, 0, { blur: 2 }) + chatter('e3', 'L', 630, 1424, 0.22, t, 1, { blur: 2 }), 0.85)
    + cam(c, LI({ x: 190, y: 1780, s: 0.48, ...live(t, 4), turn: 0.5, look: [1, 0], smile: 0.75, armL: { a: 6 + lw * 26, e: -6 + lw * 140, hand: lw > 0.3 ? 'open' : 'relaxed' } })
      + LO({ x: 380, y: 1800, s: 0.5, ...live(t, 3), turn: 0.55, look: [1, 0], smile: 0.8, brow: lw * 0.3, armL: { a: 6 + lw * 28, e: -6 + lw * 142, hand: lw > 0.3 ? 'open' : 'relaxed' } })
      + H({ x: 800, y: 1850, s: 0.54, ...live(t, 1), turn: -0.55, look: [-1, 0], smile: 0.5 + hw * 0.15, brow: hw * 0.25,
        armR: { a: 6 + hw * 26, e: -6 + hw * 142, hand: hw > 0.3 ? 'open' : 'relaxed' }, armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } }))
    + dust(t, 14) + grade({ warm: 0.08 });
}, 0.3);

/* 14 — the trip morning: Hind sees them, smiles politely, but does not intrude */
shot(58.38, 61.94, (t) => {
  const x = kf(t, [[58.38, 60], [60.6, 330]]);
  const walking = t < 60.6;
  const c = kf(t, [[58.38, [480, 1000, 1.0]], [61.94, [560, 980, 1.08]]]);
  const P = { x, y: 1860, s: 0.56, ...live(t, 1), walk: walkP(t), walkAmp: walking ? 1 : kf(t, [[60.6, 0.4], [60.9, 0]]), turn: kf(t, [[58.4, 0.1], [59.4, 0.55]]),
    look: [kf(t, [[58.4, 0.2], [59.4, 1]]), 0], smile: kf(t, [[59.5, 0.1], [60.2, 0.4], [61.5, 0.2]]), worry: kf(t, [[60.5, 0], [61.5, 0.25]]),
    armR: { a: 14, e: -2, hand: 'grip' }, armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } };
  const j = {};
  const fig = H(P, { joints: j });
  const w = toWorld(P, j.R.W);
  return cam(c, bg('uni_bus'), 0.55)
    + cam(c, LI({ x: 740, y: 1600, s: 0.42, ...live(t, 4), turn: 0.5, look: [1, 0], smile: 0.7, open: chatMouth(t, 0) })
      + LO({ x: 880, y: 1606, s: 0.42, ...live(t, 3), turn: -0.5, look: [-1, 0], smile: 0.7, open: chatMouth(t, 2) })
      + chatter('e1', 'R', 600, 1480, 0.3, t, 0, { blur: 2 }), 0.85)
    + cam(c, K.suitcase(w[0] - 12, w[1] + 22, 0.5, -10) + fig)
    + rays(t) + dust(t) + grade({ warm: 0.1, leak: 0.35 });
}, 0.35);

/* 15 — she prepares herself to spend most of the trip alone (imagined empty seat) */
shot(61.94, 66.28, (t) => {
  const dream = ease((t - 62.4) / 0.8) * (1 - ease((t - 65.5) / 0.7));
  const s = lerp(1.9, 2.05, (t - 61.94) / 4.3);
  return bg('bokeh_warm')
    + `<g mask="url(#dream)" opacity="${(dream * 0.92).toFixed(3)}" style="filter:saturate(0.55) blur(1px)">
        <g transform="translate(540,560) scale(${(0.62 + (t - 62) * 0.01).toFixed(3)}) translate(-300,-1150)">${bg('bus_interior')}</g>
        <rect width="1080" height="1920" fill="#f7efe2" opacity="0.25"/></g>`
    + H({ x: 560, y: faceY(1250, s), s, ...live(t, 1), turn: 0.15, look: [-0.25, kf(t, [[62, 0.3], [62.8, -0.7], [65.4, -0.7], [66, 0.4]])],
      smile: kf(t, [[62, 0.1], [64.5, 0.22]]), worry: kf(t, [[62, 0.35], [64.5, 0.12]]), armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } })
    + dust(t, 16, 3) + grade({ warm: 0.12, vig: 0.65 });
}, 0.4);

/* 16 — Loreen notices her... and her face lights up */
shot(66.28, 72.40, (t) => {
  const notice = 68.3, go = 69.2;
  const u = clamp((t - go) / 3.0);
  const lx = lerp(300, 610, ease(u)), ls = lerp(0.42, 0.58, ease(u)), ly = lerp(1620, 1830, ease(u));
  const c = kf(t, [[66.28, [540, 1000, 1.0]], [68.3, [460, 1000, 1.1]], [72.4, [560, 1000, 1.06]]]);
  const lor = { x: lx, y: ly, s: ls, ...live(t, 3), walk: walkP(t, 1.1), walkAmp: u > 0 && u < 1 ? 1 : 0,
    turn: kf(t, [[66.3, -0.5], [notice, -0.5], [notice + 0.35, 0.45]]), look: [kf(t, [[notice, -1], [notice + 0.35, 1]]), 0],
    smile: kf(t, [[notice, 0.55], [notice + 0.5, 0.95]]), brow: kf(t, [[notice, 0], [notice + 0.4, 0.7]]), mouthO: kf(t, [[notice, 0], [notice + 0.3, 0.35], [notice + 1.2, 0]]),
    smileEyes: kf(t, [[notice + 0.5, 0], [notice + 1, 0.35]]), armL: u > 0.2 ? { a: 6 + 22 * ease((t - 69.8) / 0.5), e: -6 + 120 * ease((t - 69.8) / 0.5), hand: 'open' } : { a: 6, e: -6 } };
  return cam(c, bg('uni_bus'), 0.55)
    + cam(c, chatter('e5', 'R', 900, 1470, 0.28, t, 0, { blur: 2 }) + chatter('e2', 'L', 980, 1474, 0.28, t, 1, { blur: 2 }), 0.85)
    + cam(c, LI({ x: lerp(160, 400, ease(clamp((t - go - 0.4) / 3))), y: lerp(1600, 1780, ease(clamp((t - go - 0.4) / 3))), s: lerp(0.41, 0.52, ease(clamp((t - go - 0.4) / 3))), ...live(t, 4),
      walk: walkP(t, 1.05) + 1, walkAmp: t > go + 0.4 && t < go + 3.4 ? 0.9 : 0, turn: kf(t, [[66.3, 0.5], [notice + 0.3, 0.5], [notice + 0.8, 0.35]]), look: [1, 0], smile: kf(t, [[notice, 0.6], [notice + 1, 0.85]]), open: t < notice ? chatMouth(t, 1) : 0 })
      + LO(lor))
    + cam(c, H({ x: 900, y: 1960, s: 0.66, ...live(t, 1), turn: kf(t, [[66.3, -0.3], [69, -0.55]]), look: [-1, 0],
      brow: kf(t, [[69.4, 0], [70, 0.75]]), mouthO: kf(t, [[69.5, 0], [70.1, 0.4]]), smile: kf(t, [[66.3, 0.15], [69.5, 0.05]]), worry: kf(t, [[66.3, 0.2], [69.5, 0]]),
      armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } }), 1.06)
    + rays(t, 300, -100, 0.28) + dust(t) + grade({ warm: 0.13, leak: 0.45 });
}, 0.35);

/* 17 — «هند! إنتِ هم جاية؟ شكد فرحت من شفتچ!» (Loreen close-up, lip-synced) */
shot(72.40, 74.54, (t) => {
  const s = lerp(3.0, 3.2, (t - 72.4) / 2.1);
  return bg('bokeh_warm', { x: -235 })
    + LO({ x: 540, y: faceY(1080, s), s, ...live(t, 3), turn: 0.12, look: [0.25, 0], smile: 0.95, brow: 0.6, smileEyes: 0.25, open: lip(t, 72.4, 76.03) * 0.85 })
    + dust(t, 14, 5) + grade({ warm: 0.14, leak: 0.5, vig: 0.55 });
}, 0.15);

/* 18 — Hind: surprised... then touched */
shot(74.54, 76.79, (t) => {
  const s = lerp(3.0, 3.25, (t - 74.54) / 2.2);
  return bg('bokeh_warm', { x: -60 })
    + H({ x: 540, y: faceY(900, s), s, ...live(t, 1), turn: -0.12, look: [-0.25, 0], brow: kf(t, [[74.6, 0.8], [75.8, 0.3]]),
      mouthO: kf(t, [[74.6, 0.45], [75.4, 0]]), smile: kf(t, [[75.1, 0], [76.3, 0.7]]), smileEyes: kf(t, [[75.6, 0], [76.5, 0.25]]) })
    + dust(t, 14, 6) + grade({ warm: 0.14, leak: 0.5, vig: 0.55 });
}, 0.15);

/* 19 — the three walk to the bus together */
shot(76.79, 79.49, (t) => {
  const u = (t - 76.79) / 2.7, mid = lerp(260, 600, u);
  const c = [lerp(480, 580, u), 1000, 1.04];
  const ph = walkP(t, 1.0);
  return cam(c, bg('uni_plain', { blur: 2 }), 0.5)
    + cam(c, B.bus(-520, 820, 1.18, { doorOpen: true }), 0.75)
    + cam(c, LI({ x: mid - 210, y: 1790, s: 0.5, ...live(t, 4), walk: ph + 1, walkAmp: 0.9, turn: 0.45, look: [1, 0], smile: 0.8 })
      + H({ x: mid, y: 1830, s: 0.52, ...live(t, 1), walk: ph + 2, walkAmp: 0.9, turn: -0.3, look: [-0.6, 0], smile: 0.65, armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } })
      + LO({ x: mid + 220, y: 1840, s: 0.52, ...live(t, 3), walk: ph, walkAmp: 0.9, turn: -0.45, look: [-1, 0], smile: 0.85, open: chatMouth(t, 2) }))
    + rays(t) + dust(t) + grade({ warm: 0.12, leak: 0.4 });
}, 0.3);

/* 20 — in the bus: «كل مرة نبدّل أماكننا...» */
shot(79.49, 84.84, (t) => {
  const pL = ease((t - 79.9) / 0.4) * (1 - ease((t - 81.7) / 0.4));
  const pR = ease((t - 82.0) / 0.4) * (1 - ease((t - 83.9) / 0.4));
  const c = [540, 980, kf(t, [[79.49, 1.0], [84.84, 1.06]])];
  return cam(c, bg('bus_interior'), 0.6)
    + cam(c, LI({ x: 250, y: 2250, s: 0.8, ...live(t, 4), turn: 0.4, look: [0.8, 0], smile: 0.75, tilt: Math.sin(t * 5) * 3 * (t > 82 && t < 83.5 ? 1 : 0), smileEyes: 0.2 })
      + H({ x: 820, y: 2270, s: 0.8, ...live(t, 1), turn: -0.45, look: [-1, 0], brow: kf(t, [[80.5, 0.1], [81.5, 0.55]]), smile: kf(t, [[79.5, 0.4], [82, 0.25]]), armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } })
      + LO({ x: 540, y: 2300, s: 0.86, ...live(t, 3), turn: kf(t, [[79.5, -0.2], [80, -0.45], [81.8, 0.45], [83.9, 0.45], [84.3, 0.1]]), look: [kf(t, [[80, -1], [81.8, 1]]), 0.1], smile: 0.8, brow: 0.3,
        open: lip(t, 79.49, 83.88) * 0.8, armR: { a: 6 + pL * 58, e: -6 - pL * 14, hand: pL > 0.3 ? 'point' : 'relaxed' }, armL: { a: 6 + pR * 58, e: -6 - pR * 14, hand: pR > 0.3 ? 'point' : 'relaxed' } }, { noBag: true }))
    + cam(c, K.seatBack(60, 1620, 0.95) + K.seatBack(1030, 1620, 0.95), 1.12)
    + grade({ warm: 0.08, leak: 0.2 });
}, 0.3);

/* 21 — Hind: «لا لورين، إنتن صديقات ومقربات، عادي آني أگعد وحدي» */
shot(84.84, 91.64, (t) => {
  const g = ease((t - 87.6) / 0.5) * (1 - ease((t - 90.4) / 0.5));
  const s = lerp(2.2, 2.35, (t - 84.84) / 6.8);
  return bg('bokeh_bus')
    + `<g filter="url(#blur8)">${LO({ x: -60, y: faceY(980, 1.3), s: 1.3, ...live(t, 3), turn: 0.4, smile: 0.7 }, { noBag: true })}</g>`
    + H({ x: 600, y: faceY(820, s), s, ...live(t, 1), turn: kf(t, [[84.9, -0.35], [88, -0.35], [88.6, 0.25], [89.6, 0.25], [90.2, -0.3]]), look: [kf(t, [[88, -1], [88.6, 0.8], [89.6, 0.8], [90.2, -1]]), 0],
      brow: kf(t, [[84.9, 0.6], [86.4, 0.3]]), worry: kf(t, [[86.3, 0], [87, 0.45]]), smile: kf(t, [[84.9, 0.1], [87, 0.15]]), open: lip(t, 86.51, 90.67) * 0.75,
      armL: { a: 6 + g * 42, e: -6 - g * 40, hand: g > 0.3 ? 'open' : 'relaxed', hr: -20 * g } })
    + grade({ warm: 0.08 });
}, 0.3);

/* 22 — Loreen won't hear of it */
shot(91.64, 93.57, (t) => {
  const shake = Math.sin((t - 91.7) * 11) * 0.28 * (1 - ease((t - 92.6) / 0.4)) * ease((t - 91.7) / 0.2);
  const g = ease((t - 92.4) / 0.4);
  return bg('bokeh_bus', { x: -200 })
    + LO({ x: 520, y: faceY(820, 2.2), s: 2.2, ...live(t, 3), turn: 0.15 + shake, look: [0.4, 0], smile: 0.85, brow: 0.2, smileEyes: 0.3,
      armR: { a: 6 + g * 48, e: -6 - g * 50, hand: g > 0.3 ? 'open' : 'relaxed', hr: 30 * g } }, { noBag: true })
    + grade({ warm: 0.1 });
}, 0.2);

/* 23 — seated together: her shoulders finally relax */
shot(93.57, 95.8, (t) => {
  const relax = ease((t - 94.0) / 1.0);
  const c = [540, 980, kf(t, [[93.57, 1.0], [95.8, 1.06]])];
  return cam(c, bg('bus_interior', { blur: 2 }), 0.6)
    + cam(c, LO({ x: 360, y: 2480, s: 0.9, sit: true, ...live(t, 3), turn: 0.45, look: [1, 0], smile: 0.85, smileEyes: 0.2, armL: { a: 2, e: -38, fs: 0.75 }, armR: { a: 2, e: -38, fs: 0.75 } }, { noBag: true })
      + H({ x: 700, y: 2480 + relax * 10, s: 0.9, sit: true, ...live(t, 1), turn: -0.4, look: [-1, 0.05], smile: lerp(0.2, 0.7, relax), smileEyes: relax * 0.3, worry: lerp(0.25, 0, relax),
        tilt: lerp(0, -3, relax), armL: { a: 2, e: -38, fs: 0.75 }, armR: { a: 2, e: -38, fs: 0.75 } }))
    + cam(c, K.seatBack(330, 1640, 1.25) + K.seatBack(760, 1640, 1.25), 1.1)
    + grade({ warm: 0.1, leak: 0.3 });
}, 0.3);

/* 24 — the journey: the bus leaves the city for the mountains */
shot(95.8, 97.6, (t) => {
  const u = (t - 95.8) / 1.8;
  const bx = lerp(-260, 420, u), by = lerp(1360, 1230, u), bs = lerp(0.36, 0.28, u);
  const c = [lerp(500, 620, u), 980, 1.04];
  return cam(c, bg('mountain_road'), 0.6)
    + cam(c, B.bus(bx, by, bs) , 0.8)
    + cam(c, B.tree(lerp(1200, 600, u), 2250, 1.9, 51), 1.4)
    + rays(t, 200, -100, 0.25) + grade({ warm: 0.1, leak: 0.35 });
}, 0.35);

/* 25 — seats swapped: Lizette laughs beside her; Hind gazes out of the window */
shot(97.6, 100.3, (t) => {
  const c = [540, 980, kf(t, [[97.6, 1.0], [100.3, 1.07]])];
  const laugh = 0.5 + 0.5 * Math.sin((t - 97.6) * 3);
  const look = kf(t, [[97.6, -0.4], [98.6, -0.4], [99.2, 0.5]]);
  const win = `<clipPath id="winClip"><rect x="760" y="560" width="420" height="560" rx="40"/></clipPath>
    <g clip-path="url(#winClip)"><image href="${K.BG('mountain_road')}" x="${-((t * 260) % 1350) + 300}" y="-160" width="1350" height="2400"/><image href="${K.BG('mountain_road')}" x="${-((t * 260) % 1350) + 1650}" y="-160" width="1350" height="2400"/></g>
    <rect x="760" y="560" width="420" height="560" rx="40" fill="none" stroke="#3a4250" stroke-width="22"/>
    <path d="M760,560 C800,700 790,900 760,1120 L740,1120 L740,560 Z" fill="#c9a26a"/>`;
  return `<rect width="1080" height="1920" fill="#d7d5d0"/>` + cam(c, win, 0.7)
    + cam(c, LI({ x: 320, y: 2480, s: 0.9, sit: true, armL: { a: 2, e: -38, fs: 0.75 }, armR: { a: 2, e: -38, fs: 0.75 }, ...live(t, 4), turn: 0.5, look: [1, 0], smile: 0.9, open: 0.2 + laugh * 0.4, smileEyes: 0.3 + laugh * 0.5, tilt: 4 * laugh })
      + H({ x: 690, y: 2490, s: 0.9, sit: true, ...live(t, 1), turn: look, look: [look * 1.8, -0.05], smile: 0.65, smileEyes: 0.2, armL: { a: 2, e: -38, fs: 0.75 }, armR: { a: 2, e: -38, fs: 0.75 } }))
    + cam(c, K.seatBack(300, 1650, 1.25) + K.seatBack(730, 1650, 1.25), 1.1)
    + `<rect width="1080" height="1920" fill="url(#leak)" opacity="0.35"/>` + grade({ warm: 0.1 });
}, 0.3);

/* 26 — arrival at the hotel */
shot(100.3, 101.7, (t) => {
  const c = kf(t, [[100.3, [540, 900, 1.0]], [101.7, [560, 1000, 1.08]]]);
  return cam(c, bg('hotel_ext'), 0.7)
    + cam(c, LI({ x: 420, y: 1640, s: 0.3, walk: walkP(t), walkAmp: 0.8, turn: 0.2, smile: 0.6 }) + H({ x: 540, y: 1650, s: 0.31, walk: walkP(t) + 1, walkAmp: 0.8, smile: 0.5, armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } })
      + LO({ x: 660, y: 1655, s: 0.32, walk: walkP(t) + 2, walkAmp: 0.8, turn: -0.2, smile: 0.6 }))
    + grade({ warm: 0.14, tint: '#ff9a50', leak: 0.3 });
}, 0.35);

/* 27 — the lobby: room assignments... Loreen notices something (cliffhanger push-in) */
shot(101.7, 105.6, (t) => {
  const push = easeInOut(clamp((t - 102.9) / 2.7));
  const lorFace = [800, 1880 + (310 - 1850) * 0.56 * 1.045];
  const c = [lerp(540, lorFace[0], push), lerp(1000, lorFace[1] + 40, push), lerp(1.0, 2.9, push)];
  return cam(c, bg('lobby'), 0.7)
    + cam(c, extra('e2_A_R', 700, 1430, 0.34, { t, bob: true }) + chatter('e6', 'L', 140, 1600, 0.4, t, 1) + chatter('e5', 'R', 1000, 1590, 0.4, t, 2)
      + K.suitcase(60, 1400, 0.42, 0) + K.suitcase(1020, 1390, 0.42, 0), 0.9)
    + cam(c, LI({ x: 250, y: 1870, s: 0.55, ...live(t, 4), turn: 0.3, look: [0.6, -0.2], smile: 0.5 })
      + H({ x: 520, y: 1880, s: 0.56, ...live(t, 1), turn: kf(t, [[101.7, 0.4], [102.6, 0.4], [103.2, -0.35], [104.2, -0.35], [104.8, 0.4]]), look: [kf(t, [[102.6, 1], [103.2, -1], [104.2, -1], [104.8, 1]]), 0], smile: 0.3, worry: 0.2,
        armL: { a: 4, e: -152, fs: 0.55, hand: 'grip' } })
      + LO({ x: 800, y: 1880, s: 0.56, ...live(t, 3), turn: kf(t, [[101.7, 0.4], [102.6, 0.3], [103.2, -0.35]]), look: [kf(t, [[102.6, 0.4], [103.2, -1]]), kf(t, [[103, 0], [104, 0.05]])],
        smile: kf(t, [[102.4, 0.5], [103.2, 0.12], [105.3, 0.22]]), brow: kf(t, [[102.4, 0], [103.4, -0.35]]), worry: 0 }))
    + grade({ warm: 0.06, tint: '#8aa0c8', vig: kf(t, [[102.5, 0.5], [105.5, 0.85]]) });
}, 0.3);

/* 28 — يتبع… */
shot(105.6, DUR, (t) => {
  const a = ease((t - 105.6) / 0.6);
  const glow = `<radialGradient id="endGlow" cx="0.5" cy="0.47" r="0.5"><stop offset="0" stop-color="#3b2a1e"/><stop offset="1" stop-color="#0b0705"/></radialGradient>`;
  return `<defs>${glow}</defs><rect width="1080" height="1920" fill="url(#endGlow)"/>`
    + `<g opacity="${a.toFixed(3)}">` + K.textCard([
      { y: 860, size: 160, text: 'يتبع…', fill: '#f6e3c3' },
      { y: 1040, size: 70, text: 'الحلقة الثانية', fill: '#d9b98a', fill2: 1 },
      { y: 1170, size: 96, text: 'سريران وثلاث صديقات', fill: '#ffffff' },
    ]) + `</g>` + dust(t, 20, 8, '#ffdca0');
}, 0.25);

/* ------------------------------------------------ frame compositor */
function frame(t) {
  let i = shots.findIndex((s) => t >= s.a && t < s.b);
  if (i < 0) i = shots.length - 1;
  const s = shots[i];
  let out = s.render(t);
  if (s.xf && i > 0 && t < s.a + s.xf) {
    const p = (t - s.a) / s.xf;
    out = shots[i - 1].render(t) + `<g opacity="${ease(p).toFixed(3)}">${out}</g>`;
  }
  return out;
}
module.exports = { frame, shots, LINES, DUR };
