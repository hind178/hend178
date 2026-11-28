// Reusable 2D character rig parts (local units: body centre x=500, ground y=1850, ~1740 tall).
// Arms use forward kinematics (shoulder angle + elbow angle); faces are parametric.
const { f, lerp, clamp, tube, rad, rot, smooth } = require('../lib/util');

const DEFAULT_POSE = {
  x: 540, y: 1700, s: 0.5, turn: 0, tilt: 0, look: [0, 0], blink: 0, smileEyes: 0,
  smile: 0.35, open: 0, mouthO: 0, brow: 0, worry: 0, lean: 0,
  armR: { a: 6, e: -4, hand: 'relaxed' }, armL: { a: 6, e: -4, hand: 'relaxed' },
  walk: 0, walkAmp: 0, sit: false, breathe: 0, bob: 0, skirtSway: 0, opacity: 1,
};
const pose = (p) => ({ ...DEFAULT_POSE, ...p, armR: { ...DEFAULT_POSE.armR, ...(p.armR || {}) }, armL: { ...DEFAULT_POSE.armL, ...(p.armL || {}) } });

/* ---------------------------------------------------------------- EYES */
function eye(id, cx, cy, st, pz, mirror, sxExtra = 1) {
  const sx = (st.sx || 1) * sxExtra, sy = st.sy || 1;
  const blink = clamp(pz.blink);
  const lx = clamp(pz.look[0], -1, 1) * 5.5 * (mirror ? -1 : 1), ly = clamp(pz.look[1], -1, 1) * 3.5;
  const white = st.almond
    ? `M-28,1 C-20,-12 -5,-18 9,-16 C19,-14 25,-6 26,3 C17,9 3,11 -10,9 C-19,7 -24,4 -28,1 Z`
    : `M-26,0 C-19,-14 -4,-20 9,-18 C18,-16 23,-7 24,3 C16,10 3,13 -9,11 C-18,9 -23,5 -26,0 Z`;
  const wing = st.wing || 0;
  const lid = st.almond
    ? `M${-30 - wing},${-6 - wing * 0.45} C-29,-4 -28,-2 -27,0 C-19,-14 -4,-20 10,-18 C20,-16 26,-8 27,3 C22,-5 16,-10 9,-11 C-4,-13 -16,-9 -25,1.5 C-27,-1 ${-29 - wing * 0.5},${-4 - wing * 0.3} ${-30 - wing},${-6 - wing * 0.45} Z`
    : `M${-35 - wing},${-8 - wing * 0.4} C-30,-6 -27,-5 -25,-3 C-18,-17 -3,-23 10,-21 C19,-19 25,-10 26,3 C22,-5 16,-11 9,-12.5 C-4,-14.5 -15,-10 -23,0.5 C-26,-3 -30,-5.5 ${-35 - wing},${-8 - wing * 0.4} Z`;
  const ir = st.irisR || 13.6;
  const sq = clamp(pz.smileEyes);
  const scaleY = sy * (1 - blink * 0.93) * (1 - sq * 0.35);
  const lashes = (st.lashes || 6);
  let lashP = '';
  const L = [[-33, -7, -39, -15, 1.6], [-29, -8, -33, -17, 1.4], [-24, -10, -26, -20, 1.3], [-19, -14, -19, -23, 1.2], [-13, -16, -11, -24, 1], [-6, -18, -4, -23, 0.9]];
  for (let i = 0; i < Math.min(lashes, L.length); i++) {
    const [a, b, c, d, w] = L[i];
    lashP += `<path d="M${a},${b} C${(a + c) / 2 - 1},${(b + d) / 2 - 1} ${c},${d + 2} ${c},${d}" stroke-width="${w * (st.lashW || 1)}"/>`;
  }
  return `
  <g transform="translate(${f(cx)},${f(cy)}) scale(${f(mirror ? -sx : sx)},1)">
    <g transform="translate(0,3) scale(1,${scaleY.toFixed(3)}) translate(0,-3)">
      <clipPath id="${id}C"><path d="${white}"/></clipPath>
      <path d="${white}" fill="url(#sclera)"/>
      <g clip-path="url(#${id}C)">
        <circle cx="${f(1 + lx)}" cy="${f(-0.5 + ly)}" r="${ir}" fill="url(#${st.iris || 'irisBrown'})"/>
        <circle cx="${f(1 + lx)}" cy="${f(-0.5 + ly)}" r="${ir}" fill="none" stroke="#2a1208" stroke-width="1.4" opacity="0.85"/>
        <circle cx="${f(1 + lx)}" cy="${f(ly)}" r="${(ir * 0.44).toFixed(1)}" fill="#1c0d06"/>
        <path d="M-30,-22 L30,-22 L30,-6 C14,-11 -10,-12 -30,-4 Z" fill="#3a1d10" opacity="0.38" filter="url(#blur2)"/>
      </g>
      <path d="M-22,-16 C-11,-27 6,-29 19,-21" fill="none" stroke="#a46a58" stroke-width="1.4" opacity="${(0.6 * (1 - blink)).toFixed(2)}" stroke-linecap="round"/>
      <path d="${lid}" fill="#24130b"/>
      <g fill="none" stroke="#24130b" stroke-linecap="round">${lashP}</g>
      <path d="M-21,4 C-12,11 6,14 22,4" fill="none" stroke="#8a5242" stroke-width="1.1" opacity="0.55"/>
      <ellipse cx="21" cy="2.5" rx="2.6" ry="2" fill="#e5a59b"/>
    </g>
    ${blink > 0.75 ? `<path d="M-27,2 C-14,9 6,10 25,3" fill="none" stroke="#24130b" stroke-width="2.6" stroke-linecap="round"/>
      <g stroke="#24130b" stroke-width="1.3" stroke-linecap="round"><path d="M-24,5 L-29,10"/><path d="M-17,7 L-20,12"/><path d="M-9,8 L-10,13"/></g>` : ''}
    ${sq > 0.05 ? `<path d="M-30,${f(14 - sq * 5)} C-15,${f(4 - sq * 6)} 10,${f(4 - sq * 6)} 28,${f(12 - sq * 5)} L28,24 L-30,24 Z" fill="${st.skin}" opacity="${Math.min(1, sq * 1.4).toFixed(2)}"/>
      <path d="M-24,${f(10 - sq * 6)} C-10,${f(3 - sq * 6)} 8,${f(3 - sq * 6)} 22,${f(9 - sq * 5)}" fill="none" stroke="${st.skinLine}" stroke-width="1" opacity="${(sq * 0.7).toFixed(2)}"/>` : ''}
  </g>
  ${blink < 0.6 ? `<g fill="#ffffff" opacity="${(1 - blink * 1.5).toFixed(2)}"><ellipse cx="${f(cx - 4 * sx + lx * 0.8 * (mirror ? -1 : 1))}" cy="${f(cy - 7 + ly)}" rx="${f(4.2 * Math.abs(sx))}" ry="3.6"/><circle cx="${f(cx + 6 * sx + lx * 0.8 * (mirror ? -1 : 1))}" cy="${f(cy + 5 + ly)}" r="1.7" opacity="0.85"/></g>` : ''}`;
}

/* ---------------------------------------------------------------- BROWS */
function brows(st, pz, shift, sxL, sxR) {
  const raise = pz.brow * 7, w = pz.worry;
  const one = (mirror, sx) => {
    const innerY = -raise - w * 7, outerY = -raise * 0.6 + w * 2;
    const d = `M489,${f(272 + innerY)} C489,${f(267 + innerY)} 488,${f(265 + innerY)} 486,${f(263 + innerY)} C477,${f(257 + (innerY + outerY) / 2)} 464,${f(252 + outerY - (st.arch || 0))} 449,${f(252 + outerY - (st.arch || 0))} C437,${f(252 + outerY)} 426,${f(257 + outerY)} 419,${f(265 + outerY)} C425,${f(263 + outerY)} 432,${f(261 + outerY)} 440,${f(261 + outerY)} C452,${f(260 + outerY - (st.thick || 0))} 464,${f(261 + (innerY + outerY) / 2 - (st.thick || 0))} 474,${f(265 + innerY)} C480,${f(267 + innerY)} 485,${f(269 + innerY)} 489,${f(272 + innerY)} Z`;
    const tf = mirror ? `translate(${f(1000 + shift * 2)},0) scale(-1,1) translate(${f(shift)},0)` : `translate(${f(shift)},0)`;
    return `<g transform="${tf}"><g transform="translate(486,262) scale(${f(sx)},1) translate(-486,-262)"><path d="${d}" fill="${st.brow}"/></g></g>`;
  };
  return one(false, sxL) + one(true, sxR);
}

/* ---------------------------------------------------------------- MOUTH */
function mouth(st, pz, cx, cy) {
  const sm = pz.smile, op = clamp(pz.open), o = clamp(pz.mouthO);
  const w = 22 * (1 + sm * 0.12) * (1 - o * 0.35);
  const cY = cy - sm * 5 + o * 2;
  const openH = op * 13 + o * 12;
  let s = '';
  if (openH > 1.2) {
    const top = cy - 1, bot = cy + openH;
    s += `<path d="M${f(cx - w)},${f(cY)} C${f(cx - w * 0.6)},${f(top - 2)} ${f(cx + w * 0.6)},${f(top - 2)} ${f(cx + w)},${f(cY)} C${f(cx + w * 0.7)},${f(bot)} ${f(cx - w * 0.7)},${f(bot)} ${f(cx - w)},${f(cY)} Z" fill="#6e2b2c"/>`;
    s += `<path d="M${f(cx - w * 0.7)},${f(top + 0.5)} C${f(cx - w * 0.3)},${f(top - 1)} ${f(cx + w * 0.3)},${f(top - 1)} ${f(cx + w * 0.7)},${f(top + 0.5)} L${f(cx + w * 0.6)},${f(top + Math.min(4.5, openH * 0.4))} C${f(cx)},${f(top + Math.min(5.5, openH * 0.45))} ${f(cx)},${f(top + Math.min(5.5, openH * 0.45))} ${f(cx - w * 0.6)},${f(top + Math.min(4.5, openH * 0.4))} Z" fill="#fbf6f2"/>`;
    s += `<ellipse cx="${f(cx)}" cy="${f(bot - openH * 0.25)}" rx="${f(w * 0.5)}" ry="${f(openH * 0.22)}" fill="#c9636a"/>`;
    // upper lip
    s += `<path d="M${f(cx - w - 1)},${f(cY)} C${f(cx - w * 0.6)},${f(cy - 6)} ${f(cx - 4)},${f(cy - 8)} ${f(cx)},${f(cy - 5.5)} C${f(cx + 4)},${f(cy - 8)} ${f(cx + w * 0.6)},${f(cy - 6)} ${f(cx + w + 1)},${f(cY)} C${f(cx + w * 0.6)},${f(top - 1.5)} ${f(cx - w * 0.6)},${f(top - 1.5)} ${f(cx - w - 1)},${f(cY)} Z" fill="url(#${st.lip})" opacity="0.95"/>`;
    // lower lip
    s += `<path d="M${f(cx - w * 0.85)},${f(cY + 1 + openH * 0.4)} C${f(cx - w * 0.6)},${f(bot + 1)} ${f(cx + w * 0.6)},${f(bot + 1)} ${f(cx + w * 0.85)},${f(cY + 1 + openH * 0.4)} C${f(cx + w * 0.6)},${f(bot + 7)} ${f(cx - w * 0.6)},${f(bot + 7)} ${f(cx - w * 0.85)},${f(cY + 1 + openH * 0.4)} Z" fill="url(#${st.lip})"/>`;
  } else {
    s += `<path d="M${f(cx - w + 2)},${f(cY + 1)} C${f(cx - 14)},${f(cy - 4)} ${f(cx - 8)},${f(cy - 7)} ${f(cx - 3)},${f(cy - 5)} C${f(cx - 1)},${f(cy - 4)} ${f(cx + 1)},${f(cy - 4)} ${f(cx + 3)},${f(cy - 5)} C${f(cx + 8)},${f(cy - 7)} ${f(cx + 14)},${f(cy - 4)} ${f(cx + w - 2)},${f(cY + 1)} C${f(cx + 12)},${f(cy + 2.5)} ${f(cx - 12)},${f(cy + 2.5)} ${f(cx - w + 2)},${f(cY + 1)} Z" fill="${st.lipDeep}"/>`;
    s += `<path d="M${f(cx - w + 4)},${f(cY + 2)} C${f(cx - 10)},${f(cy + 13 - sm * 2)} ${f(cx + 10)},${f(cy + 13 - sm * 2)} ${f(cx + w - 4)},${f(cY + 2)} C${f(cx + 10)},${f(cy + 4)} ${f(cx - 10)},${f(cy + 4)} ${f(cx - w + 4)},${f(cY + 2)} Z" fill="url(#${st.lip})"/>`;
    s += `<path d="M${f(cx - w - 2)},${f(cY - 1)} C${f(cx - 12)},${f(cy + 4 - sm * 1.5)} ${f(cx + 12)},${f(cy + 4 - sm * 1.5)} ${f(cx + w + 2)},${f(cY - 1)}" fill="none" stroke="#9c4f4c" stroke-width="1.5" stroke-linecap="round"/>`;
    if (sm > 0.2) s += `<path d="M${f(cx - w - 4)},${f(cY - 3)} C${f(cx - w - 3)},${f(cY)} ${f(cx - w - 2)},${f(cY + 1)} ${f(cx - w)},${f(cY + 1.5)} M${f(cx + w + 4)},${f(cY - 3)} C${f(cx + w + 3)},${f(cY)} ${f(cx + w + 2)},${f(cY + 1)} ${f(cx + w)},${f(cY + 1.5)}" fill="none" stroke="#b4706a" stroke-width="1.2" stroke-linecap="round" opacity="${(sm * 0.9).toFixed(2)}"/>`;
    s += `<ellipse cx="${f(cx + 2)}" cy="${f(cy + 7)}" rx="7" ry="2" fill="#ffe3dc" opacity="0.55" filter="url(#blur2)"/>`;
  }
  return `<g id="mouth">${s}</g>`;
}

/* ---------------------------------------------------------------- NOSE */
function nose(st, shift) {
  const x = 500 + shift;
  return `<g>
    <path d="M${f(x + 7 - shift * 0.3)},300 C${f(x + 10)},318 ${f(x + 13)},334 ${f(x + 14)},346" fill="none" stroke="${st.skinShade}" stroke-width="5" opacity="0.6" filter="url(#blur2)"/>
    <path d="M${f(x - 6)},304 C${f(x - 7)},320 ${f(x - 8)},334 ${f(x - 9)},342" fill="none" stroke="#fff4ec" stroke-width="3" opacity="0.6" filter="url(#blur2)"/>
    <path d="M${f(x - 11)},351 C${f(x - 7)},357 ${f(x + 7)},357 ${f(x + 11)},351" fill="none" stroke="${st.skinLine}" stroke-width="1.5" stroke-linecap="round" opacity="0.8"/>
    <path d="M${f(x - 14)},348 C${f(x - 16)},352 ${f(x - 14)},355 ${f(x - 10)},355 M${f(x + 14)},348 C${f(x + 16)},352 ${f(x + 14)},355 ${f(x + 10)},355" fill="none" stroke="${st.skinLine}" stroke-width="1.2" opacity="0.6"/>
    <ellipse cx="${f(x)}" cy="346" rx="5" ry="3" fill="#fff4ec" opacity="0.7" filter="url(#blur2)"/>
  </g>`;
}

/** Full set of facial features; st = character face style, pz = pose */
function features(prefix, st, pz) {
  const t = clamp(pz.turn, -1, 1);
  const shift = t * 15;
  const sxL = 1 - Math.max(0, -t) * 0.25, sxR = 1 - Math.max(0, t) * 0.25;
  const ex = st.eyeGap || 44;
  return `
    <g clip-path="url(#${prefix}FaceClip)">
      <ellipse cx="${f(447 + shift)}" cy="342" rx="24" ry="13" fill="${st.blush}" opacity="${(0.42 + clamp(pz.smile) * 0.1).toFixed(2)}" filter="url(#blur8)"/>
      <ellipse cx="${f(553 + shift)}" cy="342" rx="24" ry="13" fill="${st.blush}" opacity="${(0.42 + clamp(pz.smile) * 0.1).toFixed(2)}" filter="url(#blur8)"/>
      <ellipse cx="${f(500 - ex + shift)}" cy="293" rx="30" ry="17" fill="${st.skinShade}" opacity="0.35" filter="url(#blur4)"/>
      <ellipse cx="${f(500 + ex + shift)}" cy="293" rx="30" ry="17" fill="${st.skinShade}" opacity="0.4" filter="url(#blur4)"/>
      <ellipse cx="${f(452 + shift)}" cy="320" rx="14" ry="7" fill="#fff6ef" opacity="0.55" filter="url(#blur4)"/>
      ${st.freckles ? `<g fill="#c98a6e" opacity="0.45">
        <circle cx="${f(474 + shift)}" cy="330" r="1.2"/><circle cx="${f(481 + shift)}" cy="336" r="1"/><circle cx="${f(468 + shift)}" cy="338" r="1.1"/>
        <circle cx="${f(526 + shift)}" cy="330" r="1.2"/><circle cx="${f(519 + shift)}" cy="336" r="1"/><circle cx="${f(532 + shift)}" cy="338" r="1.1"/></g>` : ''}
    </g>
    ${brows(st, pz, shift, sxL, sxR)}
    ${eye(prefix + 'EyL', 500 - ex + shift - Math.max(0, t) * 3, st.eyeY || 299, st, pz, false, sxL)}
    ${eye(prefix + 'EyR', 500 + ex + shift - Math.min(0, t) * 3, st.eyeY || 299, st, pz, true, sxR)}
    ${nose(st, shift * 1.25)}
    ${mouth(st, pz, 500 + shift * 1.15, st.mouthY || 377)}`;
}

/* ---------------------------------------------------------------- HANDS */
// local: wrist at (0,0), fingers toward +y, thumb toward +x (towards body centre)
function hand(type, sk, id) {
  const st = `stroke="${sk.skinLine}" stroke-width="1.4" stroke-linejoin="round"`;
  const fill = `url(#${id}Limb)`;
  const finger = (x0, y0, x1, y1, w = 10.5, fl = fill) => `<path d="${tube([x0, y0], [x1, y1], (t) => w * (1 - t * 0.18))}" fill="${fl}" ${st}/>`;
  const nail = (x, y, a = 0) => `<ellipse cx="${x}" cy="${y}" rx="3" ry="3.8" transform="rotate(${a} ${x} ${y})" fill="#fbe1d8" stroke="${sk.skinShade}" stroke-width="0.6"/>`;
  if (type === 'open') {
    return `${finger(-15, 50, -20, 92, 10)}${finger(-5, 52, -6, 104, 11)}${finger(5, 52, 7, 106, 11)}${finger(14, 50, 19, 96, 10)}
      <path d="M-20,-2 C-23,20 -23,40 -20,56 C-10,62 8,62 19,56 C21,40 21,18 19,-2 Z" fill="${fill}" ${st}/>
      ${finger(15, 14, 34, 50, 12, sk.skin)}
      ${nail(-20, 88, 6)}${nail(-6, 100)}${nail(7, 102)}${nail(19, 92, -6)}${nail(33, 46, -35)}
      <g fill="none" stroke="${sk.skinShade}" stroke-width="1" opacity="0.8"><path d="M-12,40 C-4,46 6,46 12,40"/></g>`;
  }
  if (type === 'point') {
    return `<path d="M-20,-2 C-24,22 -24,44 -19,62 C-14,78 -4,84 6,82 C14,80 19,70 19,56 C20,38 21,18 19,-2 Z" fill="${fill}" ${st}/>
      <g fill="none" stroke="${sk.skinShade}" stroke-width="1.4"><path d="M-18,62 C-12,70 -4,72 4,70"/><path d="M-19,50 C-12,58 -2,60 6,58"/></g>
      ${finger(9, 54, 12, 112, 11)}${nail(12, 106)}
      ${finger(14, 14, 24, 52, 12, sk.skin)}`;
  }
  if (type === 'grip') {
    return `<path d="M-20,-2 C-24,22 -24,42 -20,58 C-14,74 4,76 16,66 C21,56 21,30 19,-2 Z" fill="${fill}" ${st}/>
      <g fill="${fill}" ${st}>
        <path d="M-21,52 C-24,62 -18,72 -10,70 C-6,66 -8,58 -10,52 Z"/>
        <path d="M-10,56 C-12,68 -4,76 3,72 C6,68 4,60 2,54 Z"/>
        <path d="M2,54 C2,66 10,72 16,66 C18,60 15,54 13,50 Z"/>
      </g>
      ${finger(13, 14, 14, 48, 12, sk.skin)}`;
  }
  // relaxed
  return `<path d="M-19,0 C-21,18 -22,36 -21,50 C-21,62 -19,74 -15,84 C-12,92 -6,98 0,100 C6,100 10,96 12,90 C14,84 14,76 15,68 C16,60 17,52 18,44 C19,30 19,14 18,0 Z" fill="${fill}" ${st}/>
    <g fill="none" stroke="${sk.skinShade}" stroke-width="1.5" stroke-linecap="round"><path d="M-11,56 C-11,70 -9,84 -6,95"/><path d="M-2,56 C-1,70 1,84 3,97"/><path d="M7,54 C8,66 9,78 10,90"/></g>
    <g fill="${sk.skinLight}" opacity="0.85"><ellipse cx="-15" cy="52" rx="3.6" ry="2.4"/><ellipse cx="-6" cy="53" rx="3.8" ry="2.4"/><ellipse cx="3" cy="52" rx="3.6" ry="2.4"/></g>
    ${nail(-10, 88)}${nail(0, 93)}
    <path d="M12,12 C21,22 25,36 23,50 C22,58 18,62 14,59 C12,50 10,38 8,26 Z" fill="${sk.skin}" ${st}/>`;
}

/* ---------------------------------------------------------------- ARM (viewer-left side; mirror for the other) */
// spec: { upper:{fill,stroke,w:[w0,w1]}, fore:{fill,stroke,wfn}, cuff:{...}, skinFore: bool, upperSkinTo: t, hand id }
function arm(sp, a, e, handType, sk, id, extra = {}) {
  const S = sp.shoulder;
  const L1 = sp.len1 || 252, L2 = (sp.len2 || 238) * (extra.fs || 1);
  const dir = (ang) => [-Math.sin(rad(ang)), Math.cos(rad(ang))];
  const d1 = dir(a), d2 = dir(a + e);
  const E = [S[0] + d1[0] * L1, S[1] + d1[1] * L1];
  const Wp = [E[0] + d2[0] * L2, E[1] + d2[1] * L2];
  let s = '';
  // skin under the sleeve where needed (forearm / bare shoulders)
  if (sp.skinUpper) s += `<path d="${tube(S, E, (t) => lerp(sp.skinUpper[0], sp.skinUpper[1], t))}" fill="url(#${id}Limb)" stroke="${sk.skinLine}" stroke-width="1.4"/>`;
  if (sp.skinFore) s += `<path d="${tube(E, Wp, (t) => lerp(sp.skinFore[0], sp.skinFore[1], t))}" fill="url(#${id}Limb)" stroke="${sk.skinLine}" stroke-width="1.4"/>`;
  // hand (drawn before sleeves so cuffs overlap the wrist)
  const handAng = a + e + (extra.handRot || 0);
  s += `<g transform="translate(${f(Wp[0])},${f(Wp[1])}) rotate(${f(handAng)}) translate(0,${sp.handOffset || -6})">${hand(handType, sk, id)}${extra.inHand || ''}</g>`;
  // sleeves
  if (sp.fore) {
    const Fa = [lerp(E[0], Wp[0], sp.fore.from || 0), lerp(E[1], Wp[1], sp.fore.from || 0)];
    const Fb = [lerp(E[0], Wp[0], sp.fore.to || 1), lerp(E[1], Wp[1], sp.fore.to || 1)];
    s += `<path d="${tube(Fa, Fb, sp.fore.wfn, 14)}" fill="${sp.fore.fill}" stroke="${sp.fore.stroke}" stroke-width="1.8" stroke-linejoin="round"/>`;
    // gather lines towards the cuff
    if (sp.fore.gathers) {
      const n = sp.fore.gathers;
      for (let i = 0; i < n; i++) {
        const u = (i + 0.5) / n - 0.5, t0 = 0.55, t1 = (sp.fore.to || 1) - 0.04;
        const nx = -d2[1], ny = d2[0];
        const w0 = sp.fore.wfn(0.6) * u * 0.8, w1 = sp.fore.wfn(0.97) * u * 0.8;
        const P0 = [lerp(E[0], Wp[0], t0) + nx * w0, lerp(E[1], Wp[1], t0) + ny * w0];
        const P1 = [lerp(E[0], Wp[0], t1) + nx * w1, lerp(E[1], Wp[1], t1) + ny * w1];
        s += `<path d="M${f(P0[0])},${f(P0[1])} L${f(P1[0])},${f(P1[1])}" stroke="${sp.fore.stroke}" stroke-width="1.2" opacity="0.45"/>`;
      }
    }
    // highlight along forearm
    const nx = -d2[1], ny = d2[0], hw = sp.fore.wfn(0.5) * 0.25;
    s += `<path d="M${f(lerp(E[0], Wp[0], 0.1) + nx * hw)},${f(lerp(E[1], Wp[1], 0.1) + ny * hw)} L${f(lerp(E[0], Wp[0], 0.8) + nx * hw)},${f(lerp(E[1], Wp[1], 0.8) + ny * hw)}" stroke="#ffffff" stroke-width="6" opacity="0.25" filter="url(#blur4)"/>`;
  }
  if (sp.cuff) {
    const C0 = [lerp(E[0], Wp[0], sp.cuff.from), lerp(E[1], Wp[1], sp.cuff.from)];
    const C1 = [lerp(E[0], Wp[0], sp.cuff.to), lerp(E[1], Wp[1], sp.cuff.to)];
    s += `<path d="${tube(C0, C1, () => sp.cuff.w, 4)}" fill="${sp.cuff.fill}" stroke="${sp.cuff.stroke}" stroke-width="1.6"/>`;
    const nx = -d2[1], ny = d2[0];
    const bx = lerp(C0[0], C1[0], 0.5) + nx * sp.cuff.w * 0.35, by = lerp(C0[1], C1[1], 0.5) + ny * sp.cuff.w * 0.35;
    if (sp.cuff.button) s += `<circle cx="${f(bx)}" cy="${f(by)}" r="3.4" fill="${sp.cuff.button}" stroke="${sp.cuff.stroke}" stroke-width="1"/>`;
  }
  if (sp.upper) {
    const Ua = [lerp(S[0], E[0], sp.upper.from || 0), lerp(S[1], E[1], sp.upper.from || 0)];
    const Ub = [lerp(S[0], E[0], sp.upper.to || 1), lerp(S[1], E[1], sp.upper.to || 1)];
    s += `<path d="${tube(Ua, Ub, sp.upper.wfn, 12)}" fill="${sp.upper.fill}" stroke="${sp.upper.stroke}" stroke-width="1.8" stroke-linejoin="round"/>`;
    const nx = -d1[1], ny = d1[0];
    s += `<path d="M${f(lerp(S[0], E[0], 0.2) - nx * 14)},${f(lerp(S[1], E[1], 0.2) - ny * 14)} L${f(lerp(S[0], E[0], 0.9) - nx * 10)},${f(lerp(S[1], E[1], 0.9) - ny * 10)}" stroke="#000" stroke-width="10" opacity="0.08" filter="url(#blur4)"/>`;
    s += `<path d="M${f(lerp(S[0], E[0], 0.15) + nx * 12)},${f(lerp(S[1], E[1], 0.15) + ny * 12)} L${f(lerp(S[0], E[0], 0.85) + nx * 10)},${f(lerp(S[1], E[1], 0.85) + ny * 10)}" stroke="#fff" stroke-width="7" opacity="0.3" filter="url(#blur4)"/>`;
  }
  if (extra.wrist) s += `<g transform="translate(${f(Wp[0])},${f(Wp[1])}) rotate(${f(a + e)})">${extra.wrist}</g>`;
  return { svg: s, E, W: Wp };
}

function arms(sp, pz, sk, id, extras = {}) {
  const swing = Math.sin(pz.walk) * 10 * pz.walkAmp;
  const R = arm(sp, pz.armR.a + swing, pz.armR.e - Math.abs(swing) * 0.3, pz.armR.hand, sk, id, { ...(extras.R || {}), handRot: pz.armR.hr || 0, fs: pz.armR.fs || 1 });
  const L = arm(sp, pz.armL.a - swing, pz.armL.e - Math.abs(swing) * 0.3, pz.armL.hand, sk, id, { ...(extras.L || {}), handRot: pz.armL.hr || 0, fs: pz.armL.fs || 1 });
  return {
    R: `<g class="armR">${R.svg}</g>`,
    L: `<g class="armL" transform="translate(1000,0) scale(-1,1)">${L.svg}</g>`,
    jR: R, jL: { E: [1000 - L.E[0], L.E[1]], W: [1000 - L.W[0], L.W[1]] },
  };
}

/** Wrap a character's local drawing with world placement + breathing/bob */
function place(pz, inner, tag) {
  const bob = pz.walkAmp ? -Math.abs(Math.sin(pz.walk)) * 12 * pz.walkAmp : 0;
  return `<g id="${tag}" opacity="${pz.opacity}" transform="translate(${f(pz.x)},${f(pz.y)}) scale(${pz.s}) translate(-500,${f(-1850 + bob + (pz.bob || 0))})">${inner}</g>`;
}
function headGroup(pz, inner) {
  return `<g transform="rotate(${f(pz.tilt)} 500 450)">${inner}</g>`;
}
/** Ground contact shadow */
function groundShadow(w = 230) {
  return `<ellipse cx="500" cy="1848" rx="${w}" ry="24" fill="#3c2a22" opacity="0.28" filter="url(#blur8)"/>`;
}

module.exports = { pose, eye, brows, mouth, nose, features, hand, arm, arms, place, headGroup, groundShadow, DEFAULT_POSE };
/** convert a character-local point (after draw with opt.joints) into frame coordinates */
module.exports.toWorld = (p, pt, k = 1) => {
  const q = pose(p);
  return [q.x + (500 + (pt[0] - 500) * k - 500) * q.s, q.y + (1850 + (pt[1] - 1850) * k - 1850 + (q.bob || 0)) * q.s];
};
