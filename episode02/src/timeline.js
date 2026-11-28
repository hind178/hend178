// Episode 02 — "The beginning of a beautiful friendship": shot list locked to the narration (tools/script.json).
const K = require('./scenes/kit');
const { cam, bg, extra, chatter, blink, idle, lip, grade, dust, rays, fade, kf, clamp, lerp, ease, easeInOut } = K;
const PR = require('./scenes/props2');
const hind = require('./characters/hind'), loreen = require('./characters/loreen'), lizette = require('./characters/lizette');
const { toWorld } = require('./characters/rig');
const DUR = 115.9575;

const live = (t, seed) => ({ ...idle(t, seed), blink: blink(t, seed) });
const H = (p, o) => hind.draw(p, o), HC = (p, o) => hind.drawComfy(p, o), LO = (p, o) => loreen.draw(p, o), LI = (p, o) => lizette.draw(p, o);
const walkP = (t, sp = 0.95) => t * Math.PI * 2 * sp;
const faceY = (sy, s) => sy + 1540 * s;
const chatMouth = (t, ph) => Math.max(0, Math.sin(t * 9 + ph) * Math.sin(t * 2.3 + ph)) * 0.45;
const GRIP = { a: 4, e: -152, fs: 0.55, hand: 'grip' };       // Hind holding her bag strap
const LAP = { a: 2, e: -38, fs: 0.75 };                      // hands resting in the lap
const shots = [];
const shot = (a, b, render, xf = 0) => shots.push({ a, b, render, xf });

/* 01 — reception: each room is for two students */
shot(0, 4.5, (t) => {
  const c = kf(t, [[0, [540, 980, 1.0]], [4.5, [520, 1060, 1.12]]]);
  return cam(c, bg('lobby'), 0.7)
    + cam(c, extra('e2_A_R', 680, 1430, 0.34, { t, bob: true }) + chatter('e5', 'R', 1000, 1590, 0.4, t, 2) + chatter('e1', 'L', 90, 1600, 0.4, t, 1), 0.9)
    + cam(c, K.suitcase(120, 1580, 0.5, 0) + K.suitcase(960, 1590, 0.5, 0)
      + LI({ x: 250, y: 1870, s: 0.55, ...live(t, 4), turn: 0.35, look: [1, -0.1], smile: 0.6, open: chatMouth(t, 1) })
      + LO({ x: 800, y: 1880, s: 0.56, ...live(t, 3), turn: -0.35, look: [-1, -0.1], smile: 0.6, open: chatMouth(t, 3) })
      + H({ x: 525, y: 1890, s: 0.56, ...live(t, 1), turn: kf(t, [[0, -0.1], [1.6, -0.45], [2.8, 0.45], [4.0, 0.45]]), look: [kf(t, [[1.6, -1], [2.8, 1]]), 0], smile: 0.2, worry: kf(t, [[1, 0], [3, 0.35]]), armL: GRIP }))
    + grade({ warm: 0.08, vig: 0.55 }) + fade(1 - t / 0.5);
});

/* 02 — Loreen will not enter her room until Hind's problem is solved */
shot(4.5, 9.3, (t) => {
  const turn = kf(t, [[4.5, 0.5], [5.6, 0.5], [6.2, -0.5]]);
  const walk = t > 7.2;
  const lx = kf(t, [[7.2, 700], [9.3, 560]]);
  const c = kf(t, [[4.5, [640, 980, 1.15]], [9.3, [560, 1000, 1.05]]]);
  return cam(c, bg('hotel_corridor'), 0.6)
    + cam(c, PR.door(930, 1700, 0.95, 0) + H({ x: 240, y: 1640, s: 0.36, ...live(t, 1), turn: 0.4, look: [1, 0], smile: 0.1, worry: 0.3, armL: GRIP }) + K.suitcase(170, 1450, 0.33, 0), 0.9)
    + cam(c, LI({ x: 860, y: 1840, s: 0.55, ...live(t, 4), turn: kf(t, [[4.5, 0.3], [6.5, -0.4]]), look: [kf(t, [[6.5, 1], [7, -1]]), 0], smile: 0.6 })
      + LO({ x: lx, y: 1860, s: 0.58, ...live(t, 3), walk: walkP(t), walkAmp: walk ? 1 : 0, turn, look: [turn * 2, 0], smile: kf(t, [[5.8, 0.5], [6.4, 0.25]]), brow: kf(t, [[5.8, 0], [6.4, -0.3]]),
        armL: { a: kf(t, [[4.5, 30], [5.8, 30], [6.2, 6]]), e: kf(t, [[4.5, -100], [5.8, -100], [6.2, -6]]), fs: 0.8, hand: 'grip' } }))
    + grade({ warm: 0.1, vig: 0.55 });
}, 0.3);

/* 03 — the university starts handing out rooms: every two girls get one */
shot(9.3, 15.4, (t) => {
  const c = kf(t, [[9.3, [700, 1000, 1.25]], [12.6, [560, 1000, 1.1]], [15.4, [480, 1040, 1.12]]]);
  const pairGo = (t0, x0, v1, v2) => { const u = ease((t - t0) / 1.6); return extra(`${v1}_A_R`, x0 - u * 600, 1560, 0.4, { t, bob: true, op: 1 - u }) + extra(`${v2}_A_R`, x0 + 80 - u * 600, 1566, 0.4, { t, bob: true, ph: 1, op: 1 - u }); };
  return cam(c, bg('lobby'), 0.7)
    + cam(c, extra('e2_B_R', 690, 1430, 0.34, { t, bob: true }) + pairGo(11.2, 640, 'e1', 'e3') + pairGo(13.4, 860, 'e5', 'e6'), 0.9)
    + cam(c, LI({ x: 260, y: 1880, s: 0.56, ...live(t, 4), turn: 0.4, look: [1, 0], smile: 0.55 }) + LO({ x: 420, y: 1885, s: 0.57, ...live(t, 3), turn: 0.3, look: [1, -0.2], smile: 0.4 })
      + H({ x: 620, y: 1895, s: 0.56, ...live(t, 1), turn: 0.4, look: [1, -0.2], smile: 0.15, worry: 0.2, armL: GRIP }))
    + grade({ warm: 0.08, vig: 0.55 });
}, 0.3);

/* 04 — Hind assumes Loreen & Lizette will stay together, and she'll go elsewhere */
shot(15.4, 20.7, (t) => {
  const dream = ease((t - 16.2) / 0.7) * (1 - ease((t - 19.9) / 0.6));
  const s = lerp(1.25, 1.35, (t - 15.4) / 5.3);
  const ix = kf(t, [[16.5, 760], [19.5, 900]]);
  const inset = `<g mask="url(#dream)" opacity="${(dream * 0.9).toFixed(3)}" style="filter:saturate(0.7)">
      <g transform="translate(540,560) scale(0.55) translate(-675,-1300)">${bg('room_day')}</g>
      ${LI({ x: 470, y: 820, s: 0.26, turn: 0.4, smile: 0.8, smileEyes: 0.4 })}${LO({ x: 600, y: 822, s: 0.26, turn: -0.4, smile: 0.8 })}
      ${H({ x: ix, y: 830, s: 0.24, walk: walkP(t), walkAmp: 0.8, turn: 0.3, smile: 0.1, armL: GRIP })}
      <rect width="1080" height="1920" fill="#f7efe2" opacity="0.2"/></g>`;
  return bg('lobby', { blur: 8 })
    + `<g filter="url(#blur8)">${LI({ x: 120, y: faceY(1400, 1.2), s: 1.2, turn: 0.4, smile: 0.7, open: chatMouth(t, 0) })}</g>`
    + inset
    + H({ x: 640, y: faceY(1280, s), s, ...live(t, 1), turn: -0.25, look: [kf(t, [[15.5, -0.8], [16.4, -0.2]]), kf(t, [[15.5, 0], [16.4, -0.7], [19.8, -0.7], [20.4, 0.2]])], smile: 0.18, worry: 0.35, armL: GRIP })
    + grade({ warm: 0.08, vig: 0.6 });
}, 0.3);

/* 05 — «لورين، عادي حبيبتي، آني أبقى ويا أي بنت ثانية» */
shot(20.7, 26.0, (t) => {
  const g = ease((t - 22.8) / 0.5) * (1 - ease((t - 25.3) / 0.5));
  const s = lerp(1.5, 1.6, (t - 20.7) / 5.3);
  return bg('lobby', { blur: 6, x: -60 })
    + `<g filter="url(#blur8)">${LO({ x: -40, y: faceY(980, 1.5), s: 1.5, ...live(t, 3), turn: 0.45, smile: 0.4 }, { noBag: true })}</g>`
    + H({ x: 620, y: faceY(900, s), s, ...live(t, 1), turn: kf(t, [[20.7, -0.4], [23.4, -0.4], [24.0, 0.3], [24.8, 0.3], [25.4, -0.4]]), look: [kf(t, [[23.4, -1], [24, 1], [24.8, 1], [25.4, -1]]), 0],
      smile: kf(t, [[20.8, 0.2], [22, 0.45]]), worry: 0.15, open: lip(t, 21.97, 25.59) * 0.75,
      armL: { a: 6 + g * 44, e: -6 - g * 42, hand: g > 0.3 ? 'open' : 'relaxed', hr: -20 * g } })
    + grade({ warm: 0.09 });
}, 0.3);

/* 06 — not because she didn't want to... she feared being a burden */
shot(26.0, 35.6, (t) => {
  const s = lerp(2.9, 3.25, (t - 26) / 9.6);
  return bg('bokeh_lobby', { x: -135 - (t - 26) * 8 })
    + H({ x: 540, y: faceY(900, s), s, ...live(t, 1), turn: kf(t, [[26, -0.2], [29.5, -0.2], [30.5, 0.05], [33.2, 0.05], [34, 0.3]]),
      look: [kf(t, [[26, -0.9], [29.6, -0.9], [30.4, 0], [33.2, 0], [34, 0.8]]), kf(t, [[26, 0], [29.6, 0], [30.4, 0.75], [33.2, 0.75], [34, 0.1]])],
      smile: kf(t, [[26.3, 0.2], [27.5, 0.55], [29.5, 0.45], [30.5, 0.05]]), smileEyes: kf(t, [[26.5, 0], [27.5, 0.25], [29.6, 0]]), worry: kf(t, [[29.6, 0], [30.6, 0.55]]) })
    + dust(t, 12, 4) + grade({ warm: 0.1, vig: 0.62 });
}, 0.3);

/* 07 — Loreen: «شلون يعني؟ إحنا ثلاثتنا نبقى سوه!» (Lizette agrees) */
shot(35.6, 41.0, (t) => {
  const c = [540, 960, kf(t, [[35.6, 1.0], [41, 1.08]])];
  const g = ease((t - 39.2) / 0.4);
  const nod = Math.sin((t - 39.6) * 10) * 3 * (t > 39.6 && t < 40.8 ? 1 : 0);
  return cam(c, bg('lobby', { blur: 4 }), 0.6)
    + cam(c, LI({ x: 230, y: 2250, s: 0.95, ...live(t, 4), turn: 0.3, look: [0.7, 0], smile: kf(t, [[38, 0.5], [39.5, 0.9]]), tilt: nod, smileEyes: 0.3 })
      + LO({ x: 600, y: 2270, s: 1.0, ...live(t, 3), turn: kf(t, [[35.6, 0.1], [36.0, 0.35]]), look: [kf(t, [[35.6, 0], [36.1, 0.9]]), 0],
        brow: kf(t, [[36, 0], [37.6, 0.45], [38.2, -0.2], [39.2, 0.3]]), smile: kf(t, [[36, 0.4], [38, 0.3], [39.3, 0.85]]), open: lip(t, 38.08, 40.47) * 0.85,
        armL: { a: 6 + g * 50, e: -6 - g * 40, hand: g > 0.3 ? 'open' : 'relaxed', hr: 20 * g } }, { noBag: true })
      + `<g filter="url(#blur4)">${H({ x: 1080, y: 2300, s: 1.0, turn: -0.4, smile: 0.2, armL: GRIP })}</g>`)
    + grade({ warm: 0.1, leak: 0.2 });
}, 0.3);

/* 08 — the three carry a big floor mattress down the corridor */
shot(41.0, 45.1, (t) => {
  const mid = kf(t, [[41, 260], [45.1, 760]], (u) => u);
  const ph = walkP(t, 0.85);
  const carry = { a: -4, e: -150, fs: 0.5, hand: 'grip' }, carry2 = { a: -4, e: -146, fs: 0.5, hand: 'grip' };
  const c = [lerp(460, 620, (t - 41) / 4.1), 1000, 1.05];
  const bob = Math.sin(ph * 2) * 4;
  return cam(c, bg('hotel_corridor'), 0.6)
    + cam(c, LI({ x: mid - 300, y: 1830, s: 0.52, ...live(t, 4), walk: ph + 2, walkAmp: 0.8, turn: 0.4, smile: 0.85, armR: carry, armL: carry2 })
      + H({ x: mid, y: 1850, s: 0.53, ...live(t, 1), walk: ph + 1, walkAmp: 0.8, turn: -0.2, smile: 0.7, smileEyes: 0.2, armR: carry, armL: carry2 })
      + LO({ x: mid + 300, y: 1855, s: 0.54, ...live(t, 3), walk: ph, walkAmp: 0.8, turn: -0.4, smile: 0.8, armR: carry, armL: carry2 }, { noBag: true })
      + PR.mattress(mid, 1360 + bob, 0.95, Math.sin(ph) * 1.2, 900, 110))
    + grade({ warm: 0.12, vig: 0.5 });
}, 0.3);

/* 09 — push the two beds together, then lay the mattress on top */
shot(45.1, 48.9, (t) => {
  const push = easeInOut(clamp((t - 45.3) / 1.4));
  const drop = easeInOut(clamp((t - 47.1) / 1.3));
  const b1 = lerp(250, 380, push), b2 = lerp(830, 700, push);
  const c = [540, 1000, kf(t, [[45.1, 1.06], [48.9, 1.0]])];
  const pushR = { a: -72, e: -8, hand: 'open', hr: -70 }, pushL = { a: 72, e: 8, hand: 'open', hr: 70 };
  const hold = { a: kf(t, [[47.1, 150], [48.4, 100]]), e: kf(t, [[47.1, 25], [48.4, 40]]), hand: 'grip' };
  return cam(c, bg('room_day'), 0.6)
    + cam(c, LO({ x: 540, y: 1640, s: 0.45, ...live(t, 3), turn: 0, smile: 0.75, look: [0, 0.4], armR: t > 46.8 ? hold : LAP, armL: t > 46.8 ? hold : LAP }, { noBag: true }))
    + cam(c, PR.bed(b1, 1780, 0.62) + PR.bed(b2, 1780, 0.62))
    + cam(c, t > 46.8 ? PR.mattress(540, lerp(1320, 1610, drop), 0.82, 0, 1000, 120) : '')
    + cam(c, LI({ x: b1 - 240, y: 1880, s: 0.5, ...live(t, 4), turn: 0.5, look: [1, 0.3], smile: 0.7, brow: 0.2, armR: t < 46.9 ? pushR : LAP, armL: t < 46.9 ? pushL : LAP })
      + H({ x: b2 + 240, y: 1885, s: 0.5, ...live(t, 1), turn: -0.5, look: [-1, 0.3], smile: 0.6, armR: t < 46.9 ? { ...pushL, a: -72, e: -8, hr: -70 } : LAP, armL: t < 46.9 ? { a: 72, e: 8, hand: 'open', hr: 70 } : GRIP }))
    + grade({ warm: 0.1, leak: 0.25 });
}, 0.3);

/* 10 — a room meant for two becomes a room for three friends */
shot(48.9, 54.0, (t) => {
  const c = kf(t, [[48.9, [540, 1080, 1.18]], [54, [540, 1000, 1.0]]]);
  const flop = ease((t - 51.9) / 0.5);
  return cam(c, bg('room_day'), 0.6)
    + cam(c, PR.bed(380, 1780, 0.62, { noPillow: true }) + PR.bed(700, 1780, 0.62, { noPillow: true }) + PR.mattress(540, 1610, 0.82, 0, 1000, 120)
      + `<g>${[380, 540, 700].map((x) => `<ellipse cx="${x}" cy="1520" rx="62" ry="26" fill="#fffdf8" stroke="#d8cdbb" stroke-width="3"/>`).join('')}</g>`)
    + cam(c, LI({ x: 270, y: lerp(1880, 1800, flop), s: 0.5, ...live(t, 4), turn: 0.5, smile: 0.95, smileEyes: 0.6, open: 0.35 * flop, tilt: 6 * flop,
        armR: { a: 6 + flop * 30, e: -6 + flop * 130, hand: 'open' }, armL: { a: 6 + flop * 30, e: -6 + flop * 130, hand: 'open' } })
      + H({ x: 540, y: 1900, s: 0.5, ...live(t, 1), turn: kf(t, [[49, -0.4], [51, 0.4], [52.5, 0]]), look: [kf(t, [[49, -1], [51, 1], [52.5, 0]]), 0], smile: 0.8, smileEyes: 0.35, armL: GRIP })
      + LO({ x: 820, y: 1905, s: 0.51, ...live(t, 3), turn: -0.45, look: [-1, 0], smile: 0.9, smileEyes: 0.3 }, { noBag: true }))
    + rays(t, 600, 300, 0.2) + dust(t, 18) + grade({ warm: 0.12, leak: 0.35 });
}, 0.3);

/* 11 — night: laughing, talking, enjoying their time */
shot(54.0, 57.9, (t) => {
  const laugh = 0.5 + 0.5 * Math.sin((t - 54) * 3.2);
  const c = [540, 1000, kf(t, [[54, 1.0], [57.9, 1.07]])];
  const duvetFront = `<path d="M-50,1720 C300,1680 780,1680 1130,1720 L1130,2200 L-50,2200 Z" fill="url(#duvet)" stroke="#bfb2a0" stroke-width="4"/><path d="M-50,1730 C300,1690 780,1690 1130,1730" stroke="#d8ccb8" stroke-width="8" fill="none"/>`;
  return cam(c, bg('room_night'), 0.6)
    + cam(c, LI({ x: 260, y: 2420, s: 0.88, sit: true, ...live(t, 4), turn: 0.45, tilt: 5 * laugh, look: [1, 0], smile: 0.95, open: 0.2 + laugh * 0.45, smileEyes: 0.4 + laugh * 0.5, armR: LAP, armL: LAP })
      + LO({ x: 820, y: 2430, s: 0.9, sit: true, ...live(t, 3), turn: -0.45, tilt: -4 * laugh, look: [-1, 0], smile: 0.9, open: chatMouth(t, 1) + laugh * 0.2, smileEyes: 0.3 + laugh * 0.4, armR: LAP, armL: { a: 30, e: 110, hand: 'open' } }, { noBag: true })
      + H({ x: 545, y: 2460, s: 0.9, sit: true, ...live(t, 1), turn: kf(t, [[54, -0.35], [55.8, -0.35], [56.4, 0.35]]), look: [kf(t, [[55.8, -1], [56.4, 1]]), 0], smile: 0.85, open: laugh * 0.35, smileEyes: 0.3 + laugh * 0.5, armL: LAP, armR: LAP })
      + duvetFront)
    + grade({ warm: 0.2, tint: '#ff9a50', vig: 0.65 });
}, 0.4);

/* 12 — next day: Hind returns and changes into comfortable clothes to rest */
shot(57.9, 63.1, (t) => {
  const open = ease((t - 58.1) / 0.5) * (1 - ease((t - 59.6) / 0.5));
  const x = kf(t, [[58.5, 900], [60.3, 620]]);
  const change = ease((t - 60.4) / 0.7);
  const sit = t > 61.6;
  const c = [kf(t, [[57.9, 700], [63.1, 560]]), 1000, 1.06];
  const pose = { x: sit ? 600 : x, y: sit ? 2120 : 1880, s: sit ? 0.6 : 0.5, sit, ...live(t, 1), walk: walkP(t), walkAmp: t > 58.5 && t < 60.3 ? 1 : 0, turn: -0.3, look: [-0.6, 0.1],
    smile: kf(t, [[58.5, 0.2], [62.5, 0.45]]), armL: sit ? LAP : GRIP, armR: sit ? LAP : { a: 8, e: -6 } };
  return cam(c, bg('room_day'), 0.6)
    + cam(c, PR.door(1010, 1820, 0.75, open) + PR.bed(380, 1780, 0.62, { noPillow: true }) + PR.bed(700, 1780, 0.62, { noPillow: true }) + PR.mattress(540, 1610, 0.82, 0, 1000, 120))
    + cam(c, `<g opacity="${(1 - change).toFixed(3)}">${H(pose)}</g><g opacity="${change.toFixed(3)}">${HC(pose)}</g>`
      + (change > 0.5 ? `<path d="M760,1700 L860,1700 L850,1780 L770,1780 Z" fill="#a0602f" stroke="#5a2d13" stroke-width="3" transform="rotate(-8 810 1740)"/>` : ''))
    + `<rect width="1080" height="1920" fill="#fff8ec" opacity="${(Math.sin(Math.PI * clamp((t - 60.3) / 0.9)) * 0.55).toFixed(3)}"/>`
    + grade({ warm: 0.1, leak: 0.3 });
}, 0.4);

/* 13 — Loreen bursts in: «هند! يلا نطلع نجيب أكل وبقلاوة!» */
shot(63.1, 68.0, (t) => {
  const open = ease((t - 63.2) / 0.4);
  const lx = kf(t, [[63.5, 980], [64.6, 760]]);
  const c = [kf(t, [[63.1, 720], [68, 640]]), 980, kf(t, [[63.1, 1.0], [68, 1.12]])];
  const g = ease((t - 65.2) / 0.4);
  return cam(c, bg('room_day'), 0.6)
    + cam(c, PR.door(1010, 1820, 0.75, open) + PR.bed(380, 1780, 0.62, { noPillow: true }) + PR.bed(700, 1780, 0.62, { noPillow: true }) + PR.mattress(540, 1610, 0.82, 0, 1000, 120))
    + cam(c, HC({ x: 360, y: 2120, s: 0.6, sit: true, ...live(t, 1), turn: 0.45, look: [1, 0], brow: kf(t, [[63.3, 0], [63.8, 0.45]]), smile: 0.4, armL: LAP, armR: LAP })
      + LI({ x: lerp(1060, 940, ease((t - 64) / 1)), y: 1880, s: 0.5, ...live(t, 4), walk: walkP(t), walkAmp: t > 64 && t < 65 ? 0.8 : 0, turn: -0.4, smile: 0.85, smileEyes: 0.3 })
      + LO({ x: lx, y: 1890, s: 0.53, ...live(t, 3), walk: walkP(t, 1.1), walkAmp: t > 63.5 && t < 64.6 ? 1 : 0, turn: -0.45, look: [-1, 0], smile: 0.95, brow: 0.55, open: lip(t, 64.87, 67.25) * 0.85,
        armR: { a: 6 + g * 30, e: -6 + g * 130, hand: g > 0.3 ? 'open' : 'relaxed' } }, { noBag: true }))
    + grade({ warm: 0.1, leak: 0.3 });
}, 0.3);

/* 14 — Hind: «آني بدّلت ملابسي، روحن إنتن، عادي» */
shot(68.0, 72.5, (t) => {
  const g = ease((t - 69.8) / 0.4) * (1 - ease((t - 71.6) / 0.4));
  const s = lerp(1.55, 1.65, (t - 68) / 4.5);
  return bg('room_day', { blur: 6, x: -300 })
    + HC({ x: 560, y: faceY(860, s), s, ...live(t, 1), turn: 0.3, look: [kf(t, [[68, 0.8], [70.4, 0], [70.9, 0.8]]), kf(t, [[68, 0], [70.4, 0.6], [70.9, 0]])], smile: kf(t, [[68.2, 0.35], [69.5, 0.3]]), worry: 0.15, open: lip(t, 69.38, 71.78) * 0.75,
      armR: { a: -6 - g * 40, e: -6 - g * 100, fs: 0.7, hand: g > 0.3 ? 'open' : 'relaxed', hr: -40 * g }, armL: { a: 6 + g * 30, e: -6 - g * 30, hand: g > 0.3 ? 'open' : 'relaxed' } })
    + grade({ warm: 0.1 });
}, 0.3);

/* 15 — Loreen: «مستحيل نطلع ونخليچ وحدچ! البسي أي شي وتعالي ويانا» */
shot(72.5, 79.0, (t) => {
  const shake = Math.sin((t - 74.2) * 11) * 0.25 * clamp((t - 74.2) / 0.2) * (1 - ease((t - 75.6) / 0.3));
  const beckon = t > 76.6 && t < 78.3 ? Math.sin((t - 76.6) * 9) : 0;
  const c = [540, 960, kf(t, [[72.5, 1.0], [79, 1.08]])];
  return cam(c, bg('room_day', { blur: 4 }), 0.6)
    + cam(c, LI({ x: 260, y: 2260, s: 0.95, ...live(t, 4), turn: 0.35, look: [0.8, 0], smile: 0.85, tilt: t > 77 ? Math.sin(t * 9) * 3 : 0, smileEyes: 0.3 })
      + LO({ x: 640, y: 2270, s: 1.0, ...live(t, 3), turn: -0.3 + shake, look: [-0.7, 0.2], smile: kf(t, [[73, 0.7], [74.4, 0.4], [76.4, 0.9]]), brow: kf(t, [[74, 0.1], [74.5, -0.25], [76.5, 0.4]]), open: lip(t, 74.16, 78.26) * 0.85,
        armR: t > 76.4 ? { a: 40, e: -60 + beckon * 18, hand: 'open', hr: -40 } : { a: 6, e: -6 } }, { noBag: true }))
    + grade({ warm: 0.1, leak: 0.25 });
}, 0.3);

/* 16 — she smiles, gets ready, and the three leave the hotel together */
shot(79.0, 82.6, (t) => {
  const mid = kf(t, [[79, 520], [82.6, 640]], (u) => u);
  const u = (t - 79) / 3.6;
  const ph = walkP(t, 0.95);
  return cam([540, 960, lerp(1.0, 1.08, u)], bg('hotel_ext'), 0.7)
    + cam([540, 960, lerp(1.0, 1.08, u)], LI({ x: mid - 190, y: lerp(1600, 1880, u), s: lerp(0.34, 0.5, u), walk: ph + 1, walkAmp: 0.9, ...live(t, 4), turn: 0.4, smile: 0.9, open: chatMouth(t, 1) })
      + HC({ x: mid, y: lerp(1610, 1900, u), s: lerp(0.34, 0.5, u), walk: ph + 2, walkAmp: 0.9, ...live(t, 1), turn: -0.2, smile: 0.75, smileEyes: 0.2, armL: { a: 6, e: -6 }, armR: { a: 6, e: -6 } })
      + LO({ x: mid + 200, y: lerp(1615, 1905, u), s: lerp(0.35, 0.52, u), walk: ph, walkAmp: 0.9, ...live(t, 3), turn: -0.4, look: [-1, 0], smile: 0.9 }))
    + grade({ warm: 0.16, tint: '#ff9a50', leak: 0.35 });
}, 0.35);

/* 17 — pizza, and laughter all the way */
shot(82.6, 86.5, (t) => {
  const laugh = 0.5 + 0.5 * Math.sin((t - 82.6) * 3.4);
  const bites = Math.floor(clamp((t - 82.8) / 3.5) * 5);
  const reach = ease((t - 83.4) / 0.5) * (1 - ease((t - 84.6) / 0.5));
  const c = [540, 980, kf(t, [[82.6, 1.0], [86.5, 1.07]])];
  return cam(c, bg('restaurant'), 0.6)
    + cam(c, LI({ x: 230, y: 2380, s: 0.86, sit: true, ...live(t, 4), turn: 0.45, tilt: 5 * laugh, smile: 0.95, open: 0.25 + laugh * 0.45, smileEyes: 0.4 + laugh * 0.5, armR: LAP, armL: { a: -30 * reach + 2, e: -40 - reach * 60, fs: 0.8, hand: 'grip' } })
      + HC({ x: 540, y: 2400, s: 0.86, sit: true, ...live(t, 1), turn: kf(t, [[82.6, -0.35], [84.4, -0.35], [85, 0.35]]), look: [kf(t, [[84.4, -1], [85, 1]]), 0], smile: 0.9, open: laugh * 0.4, smileEyes: 0.3 + laugh * 0.5, armR: LAP, armL: LAP })
      + LO({ x: 850, y: 2410, s: 0.88, sit: true, ...live(t, 3), turn: -0.45, tilt: -4 * laugh, look: [-1, 0], smile: 0.95, open: 0.2 + laugh * 0.35, smileEyes: 0.3 + laugh * 0.5, armR: LAP, armL: LAP }, { noBag: true })
      + PR.pizzaTable(540, 1560, 1.05, bites))
    + grade({ warm: 0.16, tint: '#ff9a50', vig: 0.55 });
}, 0.3);

/* 18 — baklava: with every moment, the distance between them shrinks */
shot(86.5, 92.5, (t) => {
  const close = ease((t - 88.3) / 2.2);
  const give = ease((t - 87.0) / 0.6) * (1 - ease((t - 88.6) / 0.5));
  const c = [540, 980, kf(t, [[86.5, 1.0], [92.5, 1.1]])];
  const P = { x: lerp(820, 700, close), y: 1880, s: 0.56, ...live(t, 3), turn: -0.45, look: [-1, 0], smile: 0.9, smileEyes: 0.3,
    armR: { a: -10 - give * 50, e: -20 - give * 20, hand: 'grip' } };
  const j = {};
  const lor = LO(P, { joints: j, noBag: true });
  const w = toWorld(P, j.R.W, 1.045);
  return cam(c, bg('sweets'), 0.6)
    + cam(c, LI({ x: lerp(220, 330, close), y: 1880, s: 0.55, ...live(t, 4), turn: 0.4, look: [1, 0], smile: 0.9, open: chatMouth(t, 1), smileEyes: 0.4 })
      + HC({ x: lerp(500, 520, close), y: 1890, s: 0.55, ...live(t, 1), turn: kf(t, [[86.5, 0.4], [89.5, 0.4], [90.2, -0.3]]), look: [kf(t, [[89.5, 1], [90.2, -1]]), 0], smile: kf(t, [[86.6, 0.6], [88, 0.95]]), smileEyes: 0.35, brow: give * 0.3,
        armL: { a: 6 + give * 28, e: -6 - give * 70, fs: 0.8, hand: 'grip' } })
      + lor + (t < 88.9 ? PR.baklavaBox(w[0] - 20, w[1] + 20, 0.55, -6) : PR.baklavaBox(475, 1530, 0.5, 4)))
    + dust(t, 14) + grade({ warm: 0.14, leak: 0.3 });
}, 0.3);

/* 19 — like a little sister: Loreen notices even the smallest details */
shot(92.5, 99.6, (t) => {
  const stop = t > 95.4;
  const mid = kf(t, [[92.5, 280], [95.4, 560]], (u) => u);
  const fix = ease((t - 96.6) / 0.6) * (1 - ease((t - 98.6) / 0.5));
  const c = kf(t, [[92.5, [mid, 980, 1.05]], [95.4, [560, 980, 1.05]], [97, [560, 900, 1.35]], [99.6, [560, 880, 1.4]]]);
  const cc = t < 95.4 ? [mid, 980, 1.05] : c;
  const ph = walkP(t, 0.85);
  return cam(cc, bg('night_street'), 0.55)
    + cam(cc, LI({ x: mid - 260, y: 1820, s: 0.5, walk: ph + 1, walkAmp: stop ? 0 : 0.85, ...live(t, 4), turn: 0.4, smile: 0.8, open: chatMouth(t, 2) })
      + HC({ x: mid - 20, y: 1860, s: 0.52, walk: ph + 2, walkAmp: stop ? 0 : 0.85, ...live(t, 1), turn: kf(t, [[92.5, 0.4], [96.4, 0.4], [96.8, 0.55]]), look: [1, kf(t, [[96.5, 0], [97, -0.3]])], smile: kf(t, [[92.6, 0.7], [97.5, 0.95]]), smileEyes: kf(t, [[96.8, 0.2], [97.8, 0.55]]), brow: fix * 0.2,
        armL: { a: 6, e: -6 }, armR: { a: 6, e: -6 } })
      + LO({ x: mid + 190, y: 1866, s: 0.54, walk: ph, walkAmp: stop ? 0 : 0.85, ...live(t, 3), turn: -0.45, look: [-1, 0.15], smile: 0.85, smileEyes: 0.2,
        armR: { a: -6 - fix * 62, e: -30 - fix * 70, hand: fix > 0.3 ? 'open' : 'relaxed', fs: 0.9 } }))
    + dust(t, 20, 4, '#ffdca0') + grade({ warm: 0.14, tint: '#ff9a50', vig: 0.6 });
}, 0.35);

/* 20 — for the first time this trip, she forgot she came without her friends */
shot(99.6, 105.9, (t) => {
  const s = lerp(2.6, 2.95, (t - 99.6) / 6.3);
  return bg('night_street', { blur: 14, x: -135 - (t - 99.6) * 10 })
    + `<g filter="url(#blur8)" opacity="0.9">${LO({ x: 1040, y: faceY(1000, 1.6), s: 1.6, turn: -0.4, smile: 0.85 }, { noBag: true })}</g>`
    + HC({ x: 520, y: faceY(920, s), s, ...live(t, 1), turn: kf(t, [[99.6, 0.25], [102, 0.25], [103, -0.05]]), look: [kf(t, [[99.6, 0.7], [102, 0.7], [103, 0]]), kf(t, [[102, 0], [103, -0.35]])],
      smile: kf(t, [[99.7, 0.6], [101.8, 0.95]]), smileEyes: kf(t, [[101, 0.2], [102.5, 0.55]]) })
    + dust(t, 22, 9, '#ffdca0') + grade({ warm: 0.16, tint: '#ff9a50', leak: 0.3, vig: 0.6 });
}, 0.4);

/* 21 — the last day: Hind suggests a ride at the amusement park */
shot(105.9, 112.3, (t) => {
  const c = kf(t, [[105.9, [540, 760, 1.0]], [108.2, [600, 900, 1.0]], [112.3, [620, 1020, 1.12]]]);
  const pt = ease((t - 108.6) / 0.5);
  const jump = Math.max(0, Math.sin((t - 109.2) * 7)) * 20 * (t > 109.2 && t < 111.4 ? 1 : 0);
  return cam(c, bg('park'), 0.6)
    + cam(c, chatter('e4', 'R', 120, 1560, 0.3, t, 0) + chatter('e1', 'L', 980, 1555, 0.3, t, 1), 0.85)
    + cam(c, LI({ x: 250, y: 1880 - jump, s: 0.52, ...live(t, 4), turn: 0.3, look: [0.5, -0.8], smile: 0.95, open: 0.3, smileEyes: 0.4, brow: 0.5,
        armR: { a: 20 + pt * 20, e: 120, hand: 'open' }, armL: { a: 20 + pt * 20, e: 120, hand: 'open' } })
      + H({ x: 540, y: 1890, s: 0.53, ...live(t, 1), turn: 0.35, look: [0.6, -0.9], smile: 0.9, brow: 0.55, smileEyes: 0.2, open: chatMouth(t, 0) * 0.8,
        armL: { a: 6 + pt * 150, e: -6 + pt * 6, hand: pt > 0.3 ? 'point' : 'relaxed' }, armR: { a: 7, e: -6 } })
      + LO({ x: 830, y: 1900, s: 0.55, ...live(t, 3), turn: kf(t, [[106, -0.3], [109, 0.2]]), look: [0.3, -0.8], smile: kf(t, [[106, 0.6], [109.3, 0.05]]), worry: kf(t, [[109, 0], [110, 0.75]]), brow: kf(t, [[109, 0], [110, 0.3]]),
        armR: { a: -4, e: -150, fs: 0.5, hand: 'relaxed' } }))
    + rays(t, 300, -100, 0.22) + dust(t) + grade({ warm: 0.1, leak: 0.3 });
}, 0.4);

/* 22 — a suggestion she would regret with all her heart... (suspense) */
shot(112.3, DUR, (t) => {
  const u = easeInOut(clamp((t - 112.3) / 2.8));
  const c = [lerp(860, 960, u), lerp(1300, 300, u), lerp(1.3, 2.4, u)];
  const end = ease((t - 114.9) / 0.6);
  return cam(c, bg('park'), 1)
    + `<rect width="1080" height="1920" fill="#120a1e" opacity="${(0.1 + u * 0.45).toFixed(3)}"/>`
    + grade({ warm: 0.04, tint: '#6a7aa8', vig: 0.85 })
    + fade(end * 0.92)
    + `<g opacity="${ease((t - 115.1) / 0.5).toFixed(3)}">${K.textCard([{ y: 960, size: 150, text: 'يتبع…', fill: '#f6e3c3' }])}</g>`;
}, 0.3);

function frame(t) {
  let i = shots.findIndex((s) => t >= s.a && t < s.b);
  if (i < 0) i = shots.length - 1;
  const s = shots[i];
  let out = s.render(t);
  if (s.xf && i > 0 && t < s.a + s.xf) out = shots[i - 1].render(t) + `<g opacity="${ease((t - s.a) / s.xf).toFixed(3)}">${out}</g>`;
  return out;
}
module.exports = { frame, shots, DUR };
