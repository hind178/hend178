/*
 * Hind — Front View (full body)
 * Semi-realistic 2D vector illustration generated as layered SVG.
 *
 * Editable source: every body part, garment and accessory is its own
 * function + <g id="..."> group so it can be tweaked or animated later.
 *
 * Run:  node hind_front.js            -> ../output/Hind_Front.svg
 *       node render.js ../output/Hind_Front.svg ../output/Hind_Front.png 2
 */
const fs = require('fs');
const path = require('path');

const W = 1000, H = 1900;
const CX = 500; // body centre line

/* ------------------------------------------------------------------ */
/*  PALETTE (taken from the reference colour palette)                 */
/* ------------------------------------------------------------------ */
const C = {
  bgTop: '#f7f1ec', bgBot: '#ece2da',
  // hijab — royal blue
  hij: '#2f4fb8', hijLight: '#4d6fd3', hijShade: '#223d98', hijDeep: '#16296c', hijLine: '#142460',
  // under-cap
  cap: '#f6f1ea', capShade: '#dcd2c5',
  // skin
  skin: '#f7d5c3', skinLight: '#fde8dc', skinShade: '#eab49d', skinDeep: '#d89780', skinLine: '#b9735f',
  blush: '#f29b98',
  // blouse — warm off‑white
  bl: '#f6f1e8', blLight: '#fffdf8', blShade: '#e2d8ca', blDeep: '#c8baa8', blLine: '#a99883',
  // skirt
  navy: '#1c3282', royal: '#2c4fb4', mid: '#4b6fcc', light: '#8ea7e0', pale: '#c3d0ef', cream: '#efe9dc',
  // leather
  bag: '#a0602f', bagLight: '#c8844c', bagShade: '#7c4321', bagDeep: '#5a2d13',
  shoe: '#6a3c27', shoeLight: '#a06a4c', shoeDeep: '#3a1f13',
  // metals & beads
  gold: '#d9b35b', goldLight: '#f6e0a0', goldDeep: '#a77d2c',
  bead: '#2b4fc0', beadDeep: '#132a78',
  // eyes
  irisIn: '#b9834d', irisOut: '#5a3017', pupil: '#1c0d06', lash: '#24130b', brow: '#4b2c1d',
  lip: '#d98680', lipDeep: '#bf6a68',
};

/* ------------------------------------------------------------------ */
/*  HELPERS                                                           */
/* ------------------------------------------------------------------ */
const f = (n) => (Math.round(n * 10) / 10).toString();
let seed = 7;
const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };

/** Smooth curve through points (Catmull‑Rom -> cubic Bézier). */
function smooth(pts, closed = false, tension = 1) {
  const p = pts;
  const n = p.length;
  let d = `M${f(p[0][0])},${f(p[0][1])}`;
  const get = (i) => closed ? p[(i + n) % n] : p[Math.max(0, Math.min(n - 1, i))];
  const last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = get(i - 1), p1 = get(i), p2 = get(i + 1), p3 = get(i + 2);
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6 * tension, p1[1] + (p2[1] - p0[1]) / 6 * tension];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6 * tension, p2[1] - (p3[1] - p1[1]) / 6 * tension];
    d += ` C${f(c1[0])},${f(c1[1])} ${f(c2[0])},${f(c2[1])} ${f(p2[0])},${f(p2[1])}`;
  }
  return closed ? d + ' Z' : d;
}
const lerp = (a, b, t) => a + (b - a) * t;
const ease = (t) => t * t * (3 - 2 * t);

/* ------------------------------------------------------------------ */
/*  DEFS: gradients, filters, fabric patterns                         */
/* ------------------------------------------------------------------ */
function defs() {
  return `
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${C.bgTop}"/><stop offset="1" stop-color="${C.bgBot}"/>
    </linearGradient>
    <radialGradient id="bgGlow" cx="0.5" cy="0.38" r="0.6">
      <stop offset="0" stop-color="#fffaf6" stop-opacity="0.9"/><stop offset="1" stop-color="#fffaf6" stop-opacity="0"/>
    </radialGradient>

    <!-- soft blur filters used for painterly shading -->
    <filter id="blur2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2"/></filter>
    <filter id="blur4" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>
    <filter id="blur8" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="8"/></filter>
    <filter id="blur14" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>

    <!-- woven fabric grain -->
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="4" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.1 0.9"/>
    </filter>
    <filter id="linen" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.02 0.9" numOctaves="2" seed="9" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.38  0 0 0 0 0.3  0 0 0 -1.3 0.95"/>
    </filter>

    <!-- skin -->
    <radialGradient id="faceGrad" cx="0.45" cy="0.42" r="0.62">
      <stop offset="0" stop-color="${C.skinLight}"/><stop offset="0.55" stop-color="${C.skin}"/><stop offset="1" stop-color="${C.skinShade}"/>
    </radialGradient>
    <linearGradient id="handGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="${C.skinShade}"/><stop offset="0.45" stop-color="${C.skin}"/><stop offset="1" stop-color="${C.skinLight}"/>
    </linearGradient>
    <linearGradient id="legGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="${C.skinShade}"/><stop offset="0.5" stop-color="${C.skin}"/><stop offset="1" stop-color="${C.skinShade}"/>
    </linearGradient>

    <!-- eyes -->
    <radialGradient id="irisGrad" cx="0.5" cy="0.62" r="0.6">
      <stop offset="0" stop-color="#d9a066"/><stop offset="0.35" stop-color="${C.irisIn}"/><stop offset="0.8" stop-color="${C.irisOut}"/><stop offset="1" stop-color="#2e160a"/>
    </radialGradient>
    <linearGradient id="scleraGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e9dcd6"/><stop offset="0.45" stop-color="#fbf7f4"/><stop offset="1" stop-color="#f3ebe7"/>
    </linearGradient>
    <linearGradient id="lipGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${C.lipDeep}"/><stop offset="1" stop-color="${C.lip}"/>
    </linearGradient>

    <!-- hijab -->
    <radialGradient id="hijabGrad" cx="0.38" cy="0.22" r="0.85">
      <stop offset="0" stop-color="${C.hijLight}"/><stop offset="0.45" stop-color="${C.hij}"/><stop offset="1" stop-color="${C.hijShade}"/>
    </radialGradient>
    <linearGradient id="hijabTailGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="${C.hijShade}"/><stop offset="0.4" stop-color="${C.hij}"/><stop offset="1" stop-color="${C.hijDeep}"/>
    </linearGradient>
    <linearGradient id="capGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${C.cap}"/><stop offset="1" stop-color="${C.capShade}"/>
    </linearGradient>

    <!-- blouse -->
    <linearGradient id="blouseGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="${C.blShade}"/><stop offset="0.3" stop-color="${C.blLight}"/><stop offset="0.6" stop-color="${C.bl}"/><stop offset="1" stop-color="${C.blShade}"/>
    </linearGradient>
    <linearGradient id="sleeveGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="${C.blShade}"/><stop offset="0.35" stop-color="${C.blLight}"/><stop offset="0.75" stop-color="${C.bl}"/><stop offset="1" stop-color="${C.blDeep}"/>
    </linearGradient>

    <!-- skirt shading -->
    <linearGradient id="foldShadow" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#0b1645" stop-opacity="0"/><stop offset="0.5" stop-color="#0b1645" stop-opacity="0.55"/><stop offset="1" stop-color="#0b1645" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="foldLight" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0"/><stop offset="0.5" stop-color="#ffffff" stop-opacity="0.12"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="skirtSide" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#0b1645" stop-opacity="0.45"/><stop offset="0.18" stop-color="#0b1645" stop-opacity="0.05"/>
      <stop offset="0.4" stop-color="#ffffff" stop-opacity="0.07"/><stop offset="0.75" stop-color="#0b1645" stop-opacity="0.1"/>
      <stop offset="1" stop-color="#0b1645" stop-opacity="0.55"/>
    </linearGradient>
    <linearGradient id="skirtTop" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b1645" stop-opacity="0.45"/><stop offset="0.08" stop-color="#0b1645" stop-opacity="0"/>
      <stop offset="0.92" stop-color="#0b1645" stop-opacity="0"/><stop offset="1" stop-color="#0b1645" stop-opacity="0.25"/>
    </linearGradient>

    <!-- leather & metal -->
    <linearGradient id="bagGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="${C.bagLight}"/><stop offset="0.45" stop-color="${C.bag}"/><stop offset="1" stop-color="${C.bagShade}"/>
    </linearGradient>
    <linearGradient id="flapGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${C.bagLight}"/><stop offset="0.6" stop-color="${C.bag}"/><stop offset="1" stop-color="${C.bagShade}"/>
    </linearGradient>
    <linearGradient id="strapGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="${C.bagShade}"/><stop offset="0.5" stop-color="${C.bagLight}"/><stop offset="1" stop-color="${C.bag}"/>
    </linearGradient>
    <linearGradient id="goldGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="${C.goldLight}"/><stop offset="0.5" stop-color="${C.gold}"/><stop offset="1" stop-color="${C.goldDeep}"/>
    </linearGradient>
    <radialGradient id="shoeGrad" cx="0.4" cy="0.35" r="0.75">
      <stop offset="0" stop-color="${C.shoeLight}"/><stop offset="0.55" stop-color="${C.shoe}"/><stop offset="1" stop-color="${C.shoeDeep}"/>
    </radialGradient>
    <radialGradient id="beadGrad" cx="0.35" cy="0.3" r="0.75">
      <stop offset="0" stop-color="#8fa9ff"/><stop offset="0.35" stop-color="${C.bead}"/><stop offset="1" stop-color="${C.beadDeep}"/>
    </radialGradient>
    <radialGradient id="watchFace" cx="0.4" cy="0.35" r="0.7">
      <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#e9e3d6"/>
    </radialGradient>

    ${skirtPatterns()}
  </defs>`;
}

/* Fabric motifs of the patchwork skirt (each a repeating tile). */
function skirtPatterns() {
  return `
    <!-- navy with white four-petal flowers -->
    <pattern id="pNavyFloral" width="26" height="26" patternUnits="userSpaceOnUse" patternTransform="rotate(0)">
      <rect width="26" height="26" fill="${C.navy}"/>
      <g fill="${C.cream}" transform="translate(13,13)">
        <ellipse rx="2" ry="4.6"/><ellipse rx="4.6" ry="2"/>
        <circle r="1.6" fill="${C.mid}"/>
      </g>
      <g fill="${C.light}"><circle cx="0" cy="0" r="1.6"/><circle cx="26" cy="0" r="1.6"/><circle cx="0" cy="26" r="1.6"/><circle cx="26" cy="26" r="1.6"/></g>
    </pattern>
    <!-- cream ikat diamonds -->
    <pattern id="pCreamIkat" width="34" height="34" patternUnits="userSpaceOnUse">
      <rect width="34" height="34" fill="${C.cream}"/>
      <path d="M17,3 L29,17 L17,31 L5,17 Z" fill="${C.royal}"/>
      <path d="M17,9 L24,17 L17,25 L10,17 Z" fill="${C.cream}"/>
      <circle cx="17" cy="17" r="2.6" fill="${C.navy}"/>
      <g fill="${C.mid}"><circle cx="0" cy="0" r="2"/><circle cx="34" cy="0" r="2"/><circle cx="0" cy="34" r="2"/><circle cx="34" cy="34" r="2"/></g>
    </pattern>
    <!-- royal lattice -->
    <pattern id="pRoyalLattice" width="22" height="22" patternUnits="userSpaceOnUse">
      <rect width="22" height="22" fill="${C.royal}"/>
      <path d="M0,0 L22,22 M22,0 L0,22" stroke="${C.light}" stroke-width="1.4"/>
      <circle cx="11" cy="11" r="2.2" fill="${C.cream}"/>
      <g fill="${C.cream}"><circle cx="0" cy="0" r="1.5"/><circle cx="22" cy="0" r="1.5"/><circle cx="0" cy="22" r="1.5"/><circle cx="22" cy="22" r="1.5"/></g>
    </pattern>
    <!-- light blue with navy crosses -->
    <pattern id="pLightCross" width="28" height="28" patternUnits="userSpaceOnUse">
      <rect width="28" height="28" fill="${C.mid}"/>
      <path d="M14,6 L16,12 L22,14 L16,16 L14,22 L12,16 L6,14 L12,12 Z" fill="${C.navy}"/>
      <circle cx="14" cy="14" r="2" fill="${C.cream}"/>
      <g fill="${C.pale}"><circle cx="0" cy="0" r="1.8"/><circle cx="28" cy="0" r="1.8"/><circle cx="0" cy="28" r="1.8"/><circle cx="28" cy="28" r="1.8"/></g>
    </pattern>
    <!-- deep navy with cream medallion star -->
    <pattern id="pMedallion" width="42" height="42" patternUnits="userSpaceOnUse">
      <rect width="42" height="42" fill="#172a6e"/>
      <path d="M21,5 L25,15 L36,13 L28,21 L36,29 L25,27 L21,37 L17,27 L6,29 L14,21 L6,13 L17,15 Z" fill="${C.cream}"/>
      <path d="M21,12 L26,21 L21,30 L16,21 Z" fill="${C.royal}"/>
      <circle cx="21" cy="21" r="2.2" fill="${C.cream}"/>
      <g fill="${C.light}"><circle cx="0" cy="0" r="2"/><circle cx="42" cy="0" r="2"/><circle cx="0" cy="42" r="2"/><circle cx="42" cy="42" r="2"/></g>
    </pattern>
    <!-- cream with tiny navy dots and squares -->
    <pattern id="pCreamDots" width="18" height="18" patternUnits="userSpaceOnUse">
      <rect width="18" height="18" fill="${C.pale}"/>
      <rect x="6" y="6" width="6" height="6" fill="${C.royal}" transform="rotate(45 9 9)"/>
      <g fill="${C.navy}"><circle cx="0" cy="0" r="1.5"/><circle cx="18" cy="0" r="1.5"/><circle cx="0" cy="18" r="1.5"/><circle cx="18" cy="18" r="1.5"/></g>
    </pattern>
    <!-- narrow border band: cream with blue zig-zag -->
    <pattern id="pBand" width="16" height="16" patternUnits="userSpaceOnUse">
      <rect width="16" height="16" fill="${C.cream}"/>
      <path d="M0,11 L4,5 L8,11 L12,5 L16,11" fill="none" stroke="${C.royal}" stroke-width="2"/>
      <circle cx="4" cy="13" r="1.2" fill="${C.navy}"/><circle cx="12" cy="13" r="1.2" fill="${C.navy}"/>
    </pattern>
    <!-- solid mid blue with fine speckle -->
    <pattern id="pSpeckle" width="12" height="12" patternUnits="userSpaceOnUse">
      <rect width="12" height="12" fill="#2442a0"/>
      <circle cx="3" cy="3" r="1.1" fill="${C.light}"/><circle cx="9" cy="9" r="1.1" fill="${C.pale}"/>
    </pattern>`;
}

/* ------------------------------------------------------------------ */
/*  BACKGROUND                                                        */
/* ------------------------------------------------------------------ */
function background() {
  return `
  <g id="background">
    <rect width="${W}" height="${H}" fill="url(#bgGrad)"/>
    <rect width="${W}" height="${H}" fill="url(#bgGlow)"/>
    <ellipse cx="${CX}" cy="1842" rx="230" ry="26" fill="#8a6f63" opacity="0.28" filter="url(#blur8)"/>
    <ellipse cx="${CX}" cy="1840" rx="140" ry="12" fill="#6e5348" opacity="0.3" filter="url(#blur4)"/>
  </g>`;
}

/* ------------------------------------------------------------------ */
/*  SKIRT  (patchwork panels following the flare + gathered folds)    */
/* ------------------------------------------------------------------ */
const WAIST_Y = 790, HEM_Y = 1662;
function hw(y) { // skirt half‑width at height y
  if (y <= WAIST_Y) return 110;
  if (y <= 905) return lerp(110, 160, ease((y - WAIST_Y) / (905 - WAIST_Y)));
  return lerp(160, 254, Math.pow((y - 905) / (HEM_Y - 905), 0.95));
}
function hemY(x) { // gentle wave of the gathered hem
  const t = (x - (CX - 254)) / 508;
  return HEM_Y + Math.sin(t * Math.PI * 11) * 6 + Math.sin(t * Math.PI) * 6;
}
function skirtOutline() {
  const left = [], right = [];
  for (let y = WAIST_Y; y <= HEM_Y - 4; y += 26) { left.push([CX - hw(y), y]); right.unshift([CX + hw(y), y]); }
  const hem = [];
  for (let x = CX - 254; x <= CX + 254; x += 11) hem.push([x, hemY(x)]);
  return smooth([...left, ...hem, ...right], true, 0.9);
}

function skirt() {
  const outline = skirtOutline();
  // patchwork rows: [y0, y1, kind]
  const rows = [
    [WAIST_Y, 870, 'main'], [870, 884, 'band'], [884, 990, 'main'], [990, 1090, 'main'],
    [1090, 1104, 'band'], [1104, 1215, 'main'], [1215, 1322, 'main'], [1322, 1336, 'band'],
    [1336, 1448, 'main'], [1448, 1552, 'main'], [1552, 1566, 'band'], [1566, 1630, 'main'], [1630, 1644, 'band'], [1644, 1700, 'hem'],
  ];
  const pats = ['pNavyFloral', 'pCreamIkat', 'pRoyalLattice', 'pLightCross', 'pMedallion', 'pCreamDots', 'pSpeckle'];
  let panels = '', seams = '';
  let prev = '';
  rows.forEach(([y0, y1, kind], ri) => {
    if (kind === 'hem') {
      panels += `<path d="${quad(-1.2, 1.2, y0, y1)}" fill="url(#pCreamIkat)"/>`;
      return;
    }
    if (kind === 'band') {
      const q = quad(-1.2, 1.2, y0, y1);
      panels += `<path d="${q}" fill="url(#pBand)"/>`;
      return;
    }
    // split row into 4–6 panels with jittered edges
    const n = 4 + Math.floor(rnd() * 3);
    const us = [-1.25];
    for (let i = 1; i < n; i++) us.push(-1.25 + (2.5 * i) / n + (rnd() - 0.5) * 0.18);
    us.push(1.25);
    for (let i = 0; i < n; i++) {
      let p; do { p = pats[Math.floor(rnd() * pats.length)]; } while (p === prev);
      prev = p;
      // occasionally split a panel horizontally into two blocks
      if (rnd() < 0.3 && y1 - y0 > 90) {
        const ym = (y0 + y1) / 2 + (rnd() - 0.5) * 20;
        let p2; do { p2 = pats[Math.floor(rnd() * pats.length)]; } while (p2 === p);
        panels += `<path d="${quad(us[i], us[i + 1], y0, ym)}" fill="url(#${p})"/>`;
        panels += `<path d="${quad(us[i], us[i + 1], ym, y1)}" fill="url(#${p2})"/>`;
        seams += seamLine(us[i], us[i + 1], ym);
      } else {
        panels += `<path d="${quad(us[i], us[i + 1], y0, y1)}" fill="url(#${p})"/>`;
      }
      if (i > 0) seams += `<path d="M${f(CX + us[i] * hw(y0))},${y0} L${f(CX + us[i] * hw(y1))},${y1}" />`;
    }
    seams += seamLine(-1.25, 1.25, y1);
  });

  // gathered folds fanning out from the waist
  let folds = '';
  const N = 13;
  for (let i = 0; i < N; i++) {
    const uw = -0.95 + (1.9 * i) / (N - 1);
    const uh = uw * 1.04 + (rnd() - 0.5) * 0.05;
    const xw = CX + uw * hw(WAIST_Y + 6), xh = CX + uh * 254;
    const wTop = 4, wBot = 24 + rnd() * 10;
    const xm = lerp(xw, xh, 0.5) + (rnd() - 0.5) * 6;
    const ym = (WAIST_Y + HEM_Y) / 2;
    folds += `<path d="M${f(xw - wTop)},${WAIST_Y} Q${f(xm - wBot * 0.6)},${ym} ${f(xh - wBot)},${HEM_Y + 14} L${f(xh + wBot)},${HEM_Y + 14} Q${f(xm + wBot * 0.6)},${ym} ${f(xw + wTop)},${WAIST_Y} Z" fill="url(#foldShadow)"/>`;
    if (i < N - 1) {
      const uw2 = uw + 0.95 / (N - 1), xl = CX + uw2 * hw(WAIST_Y + 6), xlh = CX + uw2 * 1.04 * 254;
      const xlm = lerp(xl, xlh, 0.5);
      folds += `<path d="M${f(xl - 2)},${WAIST_Y} Q${f(xlm - 9)},${ym} ${f(xlh - 14)},${HEM_Y + 14} L${f(xlh + 14)},${HEM_Y + 14} Q${f(xlm + 9)},${ym} ${f(xl + 2)},${WAIST_Y} Z" fill="url(#foldLight)"/>`;
    }
  }

  // crisp fold lines near the hem where the cloth turns
  let creases = '';
  for (let i = 0; i < 12; i++) {
    const x = CX - 230 + i * 42 + (rnd() - 0.5) * 10;
    creases += `<path d="M${f(x)},${HEM_Y - 210 - rnd() * 120} Q${f(x - 4)},${HEM_Y - 90} ${f(x + (rnd() - 0.5) * 6)},${f(hemY(x) - 2)}" />`;
  }

  // waistband (gathered)
  const wb = `M${CX - 112},${WAIST_Y - 20} C${CX - 60},${WAIST_Y - 24} ${CX + 60},${WAIST_Y - 24} ${CX + 112},${WAIST_Y - 20} L${CX + 113},${WAIST_Y + 6} C${CX + 60},${WAIST_Y + 2} ${CX - 60},${WAIST_Y + 2} ${CX - 113},${WAIST_Y + 6} Z`;
  let gathers = '';
  for (let x = CX - 104; x <= CX + 104; x += 9) gathers += `<path d="M${x},${WAIST_Y - 16} L${x + 1},${WAIST_Y + 3}"/>`;

  return `
  <g id="skirt">
    <clipPath id="skirtClip"><path d="${outline}"/></clipPath>
    <g clip-path="url(#skirtClip)">
      <rect x="200" y="${WAIST_Y - 30}" width="600" height="${HEM_Y - WAIST_Y + 60}" fill="${C.royal}"/>
      ${panels}
      <g fill="none" stroke="${C.cream}" stroke-width="3.2" opacity="0.95">${seams}</g>
      <g fill="none" stroke="${C.navy}" stroke-width="1.3" stroke-dasharray="1.5 4" stroke-linecap="round">${seams}</g>
      <rect x="200" y="${WAIST_Y - 30}" width="600" height="${HEM_Y - WAIST_Y + 60}" filter="url(#grain)" opacity="0.22" style="mix-blend-mode:multiply"/>
      ${folds}
      <g fill="none" stroke="#0b1645" stroke-width="2" opacity="0.28" filter="url(#blur2)">${creases}</g>
      <rect x="${CX - 260}" y="${WAIST_Y - 30}" width="520" height="${HEM_Y - WAIST_Y + 60}" fill="url(#skirtSide)"/>
      <rect x="${CX - 260}" y="${WAIST_Y}" width="520" height="${HEM_Y - WAIST_Y + 20}" fill="url(#skirtTop)"/>
    </g>
    <path d="${outline}" fill="none" stroke="#0f1d55" stroke-width="2.4" stroke-linejoin="round"/>
    <!-- hem inner lip -->
    <path d="${smooth(Array.from({ length: 47 }, (_, i) => { const x = CX - 250 + i * 10.9; return [x, hemY(x) - 3]; }))}" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.25"/>
    <g id="waistband">
      <path d="${wb}" fill="url(#pRoyalLattice)"/>
      <path d="${wb}" fill="#0b1645" opacity="0.18"/>
      <g stroke="#0b1645" stroke-width="1.4" opacity="0.35">${gathers}</g>
      <path d="${wb}" fill="none" stroke="#0f1d55" stroke-width="2"/>
    </g>
  </g>`;

  function quad(u0, u1, y0, y1) {
    return `M${f(CX + u0 * hw(y0))},${y0} L${f(CX + u1 * hw(y0))},${y0} L${f(CX + u1 * hw(y1))},${y1} L${f(CX + u0 * hw(y1))},${y1} Z`;
  }
  function seamLine(u0, u1, y) { return `M${f(CX + u0 * hw(y))},${y} L${f(CX + u1 * hw(y))},${y}`; }
}

/* ------------------------------------------------------------------ */
/*  LEGS & LOAFERS                                                    */
/* ------------------------------------------------------------------ */
function legsAndShoes() {
  const leg = (cx, dir) => {
    // slender calf → ankle, slight inward taper; dir mirrors the ankle bone
    const d = `M${cx - 28},1640 C${cx - 31},1684 ${cx - 24},1728 ${cx - 16},1770 L${cx + 16},1770 C${cx + 23},1728 ${cx + 29},1684 ${cx + 27},1640 Z`;
    return `
      <path d="${d}" fill="url(#legGrad)" stroke="${C.skinLine}" stroke-width="1.6"/>
      <ellipse cx="${cx + dir * 12}" cy="1752" rx="4" ry="6" fill="${C.skinShade}" opacity="0.7" filter="url(#blur2)"/>
      <path d="M${cx - 6},1650 C${cx - 8},1690 ${cx - 6},1725 ${cx - 4},1760" stroke="${C.skinLight}" stroke-width="5" opacity="0.6" fill="none" filter="url(#blur2)"/>`;
  };
  const shoe = (cx, rot) => `
    <g transform="rotate(${rot} ${cx} 1800)">
      <!-- sole -->
      <path d="M${cx - 41},1816 C${cx - 43},1840 ${cx - 26},1853 ${cx},1853 C${cx + 26},1853 ${cx + 43},1840 ${cx + 41},1816 L${cx + 38},1816 C${cx + 38},1834 ${cx + 24},1844 ${cx},1844 C${cx - 24},1844 ${cx - 38},1834 ${cx - 38},1816 Z" fill="${C.shoeDeep}"/>
      <!-- upper -->
      <path d="M${cx - 19},1762 C${cx - 31},1772 ${cx - 39},1792 ${cx - 40},1814 C${cx - 41},1834 ${cx - 25},1846 ${cx},1846 C${cx + 25},1846 ${cx + 41},1834 ${cx + 40},1814 C${cx + 39},1792 ${cx + 31},1772 ${cx + 19},1762 C${cx + 8},1769 ${cx - 8},1769 ${cx - 19},1762 Z"
        fill="url(#shoeGrad)" stroke="${C.shoeDeep}" stroke-width="2" stroke-linejoin="round"/>
      <!-- apron (moc‑toe) stitching -->
      <path d="M${cx - 27},1800 C${cx - 26},1780 ${cx + 26},1780 ${cx + 27},1800" fill="none" stroke="${C.shoeDeep}" stroke-width="2"/>
      <path d="M${cx - 25},1803 C${cx - 24},1785 ${cx + 24},1785 ${cx + 25},1803" fill="none" stroke="${C.shoeLight}" stroke-width="1" stroke-dasharray="2 2.5" opacity="0.8"/>
      <!-- saddle strap -->
      <path d="M${cx - 24},1790 C${cx - 10},1796 ${cx + 10},1796 ${cx + 24},1790 L${cx + 22},1800 C${cx + 10},1805 ${cx - 10},1805 ${cx - 22},1800 Z" fill="${C.shoe}" stroke="${C.shoeDeep}" stroke-width="1.4"/>
      <!-- tassels -->
      <g stroke="${C.shoeDeep}" stroke-width="1.2">
        <path d="M${cx - 6},1798 C${cx - 9},1806 ${cx - 10},1812 ${cx - 9},1818" fill="none"/>
        <path d="M${cx + 6},1798 C${cx + 9},1806 ${cx + 10},1812 ${cx + 9},1818" fill="none"/>
        <path d="M${cx - 13},1816 C${cx - 12},1828 ${cx - 5},1830 ${cx - 5},1816 Z" fill="${C.shoe}"/>
        <path d="M${cx + 13},1816 C${cx + 12},1828 ${cx + 5},1830 ${cx + 5},1816 Z" fill="${C.shoe}"/>
        <rect x="${cx - 13}" y="1813" width="8" height="4" rx="1.5" fill="${C.shoeDeep}"/>
        <rect x="${cx + 5}" y="1813" width="8" height="4" rx="1.5" fill="${C.shoeDeep}"/>
      </g>
      <!-- toe shine -->
      <ellipse cx="${cx - 10}" cy="1822" rx="11" ry="5" fill="#ffffff" opacity="0.25" filter="url(#blur2)"/>
      <path d="M${cx - 18},1766 C${cx - 6},1772 ${cx + 6},1772 ${cx + 18},1766" fill="none" stroke="${C.shoeLight}" stroke-width="1.4" opacity="0.7"/>
    </g>`;
  return `
  <g id="legs">${leg(CX - 46, 1)}${leg(CX + 46, -1)}</g>
  <g id="shoes">${shoe(CX - 50, 5)}${shoe(CX + 50, -5)}</g>`;
}

/* ------------------------------------------------------------------ */
/*  TORSO / BLOUSE                                                    */
/* ------------------------------------------------------------------ */
function blouse() {
  const torso = `M330,505 C318,545 322,605 334,655 C346,705 366,745 386,775 C440,786 560,786 614,775 C634,745 654,705 666,655 C678,605 682,545 670,505 C600,478 400,478 330,505 Z`;
  // soft blousing over the waistband
  const blousing = `M384,766 C392,782 410,792 430,790 C450,796 470,792 490,795 C510,792 530,797 552,791 C574,794 596,788 616,766 C600,772 580,776 560,774 C540,778 460,778 440,774 C420,776 400,772 384,766 Z`;
  return `
  <g id="blouse">
    <clipPath id="torsoClip"><path d="${torso}"/></clipPath>
    <path d="${torso}" fill="url(#blouseGrad)"/>
    <g clip-path="url(#torsoClip)">
      <rect x="300" y="470" width="400" height="330" filter="url(#linen)" opacity="0.16"/>
      <!-- bust & waist form shading -->
      <path d="M380,610 C410,650 460,660 490,640" stroke="${C.blShade}" stroke-width="10" fill="none" opacity="0.7" filter="url(#blur4)"/>
      <path d="M520,640 C550,662 600,650 625,610" stroke="${C.blDeep}" stroke-width="10" fill="none" opacity="0.55" filter="url(#blur4)"/>
      <!-- fabric drape lines toward the waist -->
      <g fill="none" stroke="${C.blDeep}" stroke-width="2" opacity="0.5" filter="url(#blur2)">
        <path d="M420,660 C425,700 432,740 440,772"/><path d="M455,670 C458,710 462,745 468,774"/>
        <path d="M548,670 C545,710 540,745 534,774"/><path d="M585,655 C580,700 572,740 562,772"/>
        <path d="M600,700 C596,730 592,752 590,772"/>
      </g>
      <!-- right-side body shadow -->
      <path d="M640,520 C660,600 655,700 620,780 L700,780 L700,500 Z" fill="${C.blDeep}" opacity="0.35" filter="url(#blur8)"/>
      <!-- button placket -->
      <path d="M500,545 L500,780" stroke="${C.blDeep}" stroke-width="1.6" opacity="0.8"/>
      <path d="M509,545 L509,780" stroke="${C.blShade}" stroke-width="1.2" opacity="0.8"/>
      ${[680, 735].map((y) => `<circle cx="504.5" cy="${y}" r="4.2" fill="#fbf8f1" stroke="${C.blDeep}" stroke-width="1.2"/><circle cx="503.5" cy="${y - 1}" r="1.4" fill="#ffffff"/>`).join('')}
    </g>
    <path d="${torso}" fill="none" stroke="${C.blLine}" stroke-width="2"/>
    <path d="${blousing}" fill="${C.bl}" stroke="${C.blLine}" stroke-width="1.6" stroke-linejoin="round"/>
    <path d="M420,782 C440,786 456,786 470,783 M530,784 C548,787 566,786 584,780" stroke="${C.blDeep}" stroke-width="1.4" fill="none" opacity="0.7"/>
  </g>`;
}

/* ------------------------------------------------------------------ */
/*  ARM (sleeve + cuff + hand).  Drawn for the viewer‑left arm, and   */
/*  mirrored for the other side.                                      */
/* ------------------------------------------------------------------ */
function arm(id, mirror) {
  const sleeve = `M338,500 C306,506 291,532 288,576 C285,640 282,712 276,780 C270,842 262,896 278,934 C292,954 344,956 357,940 C370,910 369,866 362,826 C357,770 357,700 359,622 C360,580 356,540 338,500 Z`;
  const cuff = `M285,934 C283,958 285,984 290,1000 C305,1007 335,1007 349,1000 C351,984 352,960 351,938 C331,947 305,946 285,934 Z`;
  const hand = `M298,998 C291,1020 288,1046 290,1068 C291,1087 296,1104 305,1115 C312,1124 326,1125 334,1117 C340,1109 343,1095 344,1081 C348,1069 355,1058 357,1046 C359,1034 353,1025 345,1021 C345,1012 345,1005 345,998 Z`;
  return `
  <g id="${id}" ${mirror ? `transform="translate(${2 * CX},0) scale(-1,1)"` : ''}>
    <!-- sleeve -->
    <path d="${sleeve}" fill="url(#sleeveGrad)" stroke="${C.blLine}" stroke-width="2" stroke-linejoin="round"/>
    <clipPath id="${id}SleeveClip"><path d="${sleeve}"/></clipPath>
    <g clip-path="url(#${id}SleeveClip)">
      <rect x="260" y="490" width="110" height="470" filter="url(#linen)" opacity="0.14"/>
      <g fill="none" stroke="${C.blDeep}" stroke-width="2.2" opacity="0.55" filter="url(#blur2)">
        <path d="M300,560 C298,620 296,690 297,760"/>
        <path d="M335,600 C332,680 330,760 332,840"/>
        <path d="M290,840 C300,880 312,910 318,940"/>
        <path d="M345,850 C340,890 335,915 330,942"/>
        <path d="M305,770 C315,800 318,820 316,860"/>
      </g>
      <path d="M345,520 C360,620 358,800 352,950 L380,950 L380,500 Z" fill="${C.blDeep}" opacity="0.45" filter="url(#blur4)"/>
      <path d="M298,540 C292,640 290,800 294,920" stroke="#ffffff" stroke-width="6" opacity="0.6" fill="none" filter="url(#blur4)"/>
      <!-- gathers into the cuff -->
      <g stroke="${C.blDeep}" stroke-width="1.3" opacity="0.6">
        <path d="M292,935 L296,918"/><path d="M302,940 L304,920"/><path d="M314,942 L314,922"/><path d="M326,942 L325,920"/><path d="M338,940 L336,918"/>
      </g>
    </g>
    <!-- cuff -->
    <path d="${cuff}" fill="url(#sleeveGrad)" stroke="${C.blLine}" stroke-width="1.8" stroke-linejoin="round"/>
    <path d="M287,948 C305,957 333,957 350,950" fill="none" stroke="${C.blShade}" stroke-width="1.3"/>
    <circle cx="343" cy="976" r="3.6" fill="#fbf8f1" stroke="${C.blDeep}" stroke-width="1.1"/>
    <!-- hand: relaxed, fingers gently curled, thumb in front -->
    <g transform="translate(320,998)">
      <path d="M-20,2 C-8,8 8,8 19,2" fill="none" stroke="${C.skinDeep}" stroke-width="6" opacity="0.5" filter="url(#blur2)"/>
      <path d="M-19,0 C-21,18 -22,36 -21,50 C-21,62 -19,74 -15,84 C-12,92 -6,98 0,100 C6,100 10,96 12,90 C14,84 14,76 15,68 C16,60 17,52 18,44 C19,30 19,14 18,0 Z"
        fill="url(#handGrad)" stroke="${C.skinLine}" stroke-width="1.4" stroke-linejoin="round"/>
      <!-- finger separations -->
      <g fill="none" stroke="${C.skinShade}" stroke-width="1.6" stroke-linecap="round">
        <path d="M-11,56 C-11,70 -9,84 -6,95"/><path d="M-2,56 C-1,70 1,84 3,97" /><path d="M7,54 C8,66 9,78 10,90"/>
      </g>
      <g fill="none" stroke="${C.skinLine}" stroke-width="0.9" stroke-linecap="round" opacity="0.7">
        <path d="M-11,60 C-11,72 -9,84 -6,95"/><path d="M-2,60 C-1,72 1,84 3,97"/><path d="M7,58 C8,68 9,78 10,90"/>
      </g>
      <!-- knuckles -->
      <g fill="${C.skinLight}" opacity="0.85">
        <ellipse cx="-15" cy="52" rx="3.6" ry="2.4"/><ellipse cx="-6" cy="53" rx="3.8" ry="2.4"/><ellipse cx="3" cy="52" rx="3.6" ry="2.4"/>
      </g>
      <path d="M-14,10 C-16,26 -16,40 -15,50" stroke="${C.skinLight}" stroke-width="4" opacity="0.6" fill="none" filter="url(#blur2)"/>
      <!-- nails -->
      <g fill="#fbe1d8" stroke="${C.skinShade}" stroke-width="0.7">
        <path d="M-12,88 C-12,84 -8,84 -8,88 C-8,92 -12,92 -12,88 Z"/>
        <path d="M-2,93 C-2,89 2,89 2,93 C2,97 -2,97 -2,93 Z"/>
      </g>
      <!-- thumb -->
      <path d="M12,12 C21,22 25,36 23,50 C22,58 18,62 14,59 C12,50 10,38 8,26 Z" fill="${C.skin}" stroke="${C.skinLine}" stroke-width="1.3" stroke-linejoin="round"/>
      <path d="M15,50 C15,46 20,46 21,50 C21,55 16,56 15,50 Z" fill="#fbe1d8" stroke="${C.skinShade}" stroke-width="0.7"/>
      <!-- ring -->
      <path d="M-11,72 C-8,75 -3,75 0,72" fill="none" stroke="url(#goldGrad)" stroke-width="2.6" stroke-linecap="round"/>
    </g>
  </g>`;
}

/* ------------------------------------------------------------------ */
/*  NECKLACE — royal blue beads with small gold spacers               */
/* ------------------------------------------------------------------ */
function necklace() {
  const P0 = [408, 540], P1 = [500, 770], P2 = [592, 540];
  const q = (t) => [
    (1 - t) ** 2 * P0[0] + 2 * (1 - t) * t * P1[0] + t * t * P2[0],
    (1 - t) ** 2 * P0[1] + 2 * (1 - t) * t * P1[1] + t * t * P2[1],
  ];
  let beads = '';
  const n = 34;
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    const [x, y] = q(t);
    if (i % 2 === 0) {
      beads += `<circle cx="${f(x)}" cy="${f(y + 1.5)}" r="7.2" fill="#0b1645" opacity="0.25" filter="url(#blur2)"/>`;
      beads += `<circle cx="${f(x)}" cy="${f(y)}" r="6.8" fill="url(#beadGrad)" stroke="${C.beadDeep}" stroke-width="0.8"/>`;
      beads += `<circle cx="${f(x - 2)}" cy="${f(y - 2.4)}" r="1.8" fill="#ffffff" opacity="0.85"/>`;
    } else {
      beads += `<circle cx="${f(x)}" cy="${f(y)}" r="2.8" fill="url(#goldGrad)" stroke="${C.goldDeep}" stroke-width="0.5"/>`;
    }
  }
  return `
  <g id="necklace">
    <path d="M${P0} Q${P1} ${P2}" fill="none" stroke="#8c7a55" stroke-width="1" opacity="0.6"/>
    ${beads}
  </g>`;
}

/* ------------------------------------------------------------------ */
/*  HIJAB — back mass, face frame (with face opening) and the tail    */
/* ------------------------------------------------------------------ */
const FACE_HOLE = `M500,200 C450,200 417,226 413,262 C409,300 415,336 429,364 C445,391 472,407 500,408 C528,407 555,391 571,364 C585,336 591,300 587,262 C583,226 550,200 500,200 Z`;
const HIJAB_HEAD = `M500,128 C432,126 384,158 368,212 C355,256 353,312 359,362 C365,404 377,436 392,458 C366,474 338,494 322,520 C326,540 352,552 386,556 C410,566 440,578 470,576 C500,584 540,580 568,568 C600,560 632,544 652,524 L670,510 C656,492 634,476 614,462 C626,436 638,404 643,360 C649,310 647,256 634,212 C618,158 568,126 500,128 Z`;

function hijabBack() {
  // part of the scarf that falls behind the shoulders (seen at the sides)
  return `
  <g id="hijab-back">
        <path d="${HIJAB_HEAD}" transform="translate(0,6)" fill="#0b1645" opacity="0.35" filter="url(#blur8)"/>
  </g>`;
}

function hijabFront() {
  // Frame = head silhouette with the face cut out (even‑odd)
  const frame = `${HIJAB_HEAD} ${FACE_HOLE}`;
  return `
  <g id="hijab">
    <clipPath id="hijabClip"><path d="${frame}" clip-rule="evenodd"/></clipPath>
    <path d="${frame}" fill-rule="evenodd" fill="url(#hijabGrad)"/>
    <g clip-path="url(#hijabClip)">
      <rect x="330" y="100" width="350" height="470" filter="url(#grain)" opacity="0.18" style="mix-blend-mode:multiply"/>
      <!-- crown wrap folds -->
      <g fill="none" stroke-linecap="round">
        <path d="M380,190 C420,140 520,124 600,150" stroke="${C.hijLight}" stroke-width="7" opacity="0.55" filter="url(#blur4)"/>
        <path d="M372,232 C420,170 540,156 630,200" stroke="${C.hijDeep}" stroke-width="3" opacity="0.45" filter="url(#blur2)"/>
        <path d="M370,270 C384,215 430,184 480,176" stroke="${C.hijDeep}" stroke-width="2.4" opacity="0.45" filter="url(#blur2)"/>
        <path d="M612,180 C640,220 650,280 646,340" stroke="${C.hijDeep}" stroke-width="10" opacity="0.4" filter="url(#blur8)"/>
        <path d="M366,300 C362,350 368,400 384,440" stroke="${C.hijLight}" stroke-width="6" opacity="0.45" filter="url(#blur4)"/>
        <path d="M394,262 C392,320 404,380 430,420" stroke="${C.hijDeep}" stroke-width="2.4" opacity="0.5" filter="url(#blur2)"/>
        <path d="M606,262 C610,320 598,380 572,420" stroke="${C.hijDeep}" stroke-width="2.4" opacity="0.55" filter="url(#blur2)"/>
      </g>
      <!-- cowl drape under the chin -->
      <g fill="none" stroke-linecap="round">
        <path d="M440,420 C470,446 530,446 560,420" stroke="${C.hijDeep}" stroke-width="10" opacity="0.6" filter="url(#blur4)"/>
        <path d="M420,450 C455,488 545,488 590,446" stroke="${C.hijDeep}" stroke-width="2.6" opacity="0.55" filter="url(#blur2)"/>
        <path d="M425,462 C460,498 545,498 585,458" stroke="${C.hijLight}" stroke-width="5" opacity="0.5" filter="url(#blur2)"/>
        <path d="M390,482 C440,530 565,530 625,478" stroke="${C.hijDeep}" stroke-width="2.6" opacity="0.5" filter="url(#blur2)"/>
        <path d="M396,496 C446,540 562,540 618,492" stroke="${C.hijLight}" stroke-width="5" opacity="0.4" filter="url(#blur2)"/>
        <path d="M352,505 C410,552 480,562 520,560" stroke="${C.hijDeep}" stroke-width="2.4" opacity="0.5" filter="url(#blur2)"/>
      </g>
      <!-- ambient occlusion around the face opening -->
      <path d="${FACE_HOLE}" fill="none" stroke="${C.hijDeep}" stroke-width="10" opacity="0.55" filter="url(#blur4)"/>
    </g>
    <path d="${frame}" fill-rule="evenodd" fill="none" stroke="${C.hijLine}" stroke-width="2.2" stroke-linejoin="round"/>
    ${hijabWrap()}
  </g>`;
}

function hijabWrap() {
  // the scarf layer that wraps from her left cheek, under the chin, to her right shoulder
  const wrap = `M587,296 C592,352 572,396 534,412 C512,420 488,420 466,414 C440,430 410,460 384,488 C366,506 346,520 326,528 C352,546 392,552 430,542 C480,530 540,508 590,474 C616,452 632,420 640,380 C645,350 647,320 646,300 C628,288 604,288 587,296 Z`;
  return `
    <g id="hijab-wrap">
      <path d="${wrap}" transform="translate(0,8)" fill="#0b1645" opacity="0.4" filter="url(#blur4)"/>
      <path d="${wrap}" fill="url(#hijabGrad)"/>
      <clipPath id="wrapClip"><path d="${wrap}"/></clipPath>
      <g clip-path="url(#wrapClip)" fill="none" stroke-linecap="round">
        <rect x="320" y="280" width="330" height="280" filter="url(#grain)" opacity="0.18" style="mix-blend-mode:multiply" stroke="none"/>
        <path d="M612,320 C606,390 560,440 470,470 C420,488 380,505 340,526" stroke="${C.hijLight}" stroke-width="8" opacity="0.5" filter="url(#blur4)"/>
        <path d="M630,360 C618,420 566,470 480,500 C430,516 390,530 350,536" stroke="${C.hijDeep}" stroke-width="2.4" opacity="0.6" filter="url(#blur2)"/>
        <path d="M596,300 C600,360 570,402 520,420" stroke="${C.hijDeep}" stroke-width="6" opacity="0.5" filter="url(#blur4)"/>
        <path d="M470,416 C440,440 410,470 380,494" stroke="${C.hijDeep}" stroke-width="3" opacity="0.5" filter="url(#blur2)"/>
      </g>
      <path d="${wrap}" fill="none" stroke="${C.hijLine}" stroke-width="2" stroke-linejoin="round"/>
      <path d="M466,414 C440,430 410,460 384,488 C366,506 346,520 326,528" fill="none" stroke="${C.hijLight}" stroke-width="1.4" opacity="0.8"/>
    </g>`;
}

function hijabTail() {
  // the long end falling forward over her left shoulder (viewer right)
  const tail = `M606,462 C630,478 650,500 660,528 C672,590 676,670 672,750 C670,784 668,808 666,830 C652,840 630,842 612,834 C616,790 616,740 612,690 C606,624 598,566 584,526 C592,504 598,484 606,462 Z`;
  return `
  <g id="hijab-tail">
    <path d="${tail}" transform="translate(6,6)" fill="#0b1645" opacity="0.25" filter="url(#blur4)"/>
    <path d="${tail}" fill="url(#hijabTailGrad)"/>
    <clipPath id="tailClip"><path d="${tail}"/></clipPath>
    <g clip-path="url(#tailClip)">
      <rect x="580" y="450" width="110" height="400" filter="url(#grain)" opacity="0.18" style="mix-blend-mode:multiply"/>
      <g fill="none" stroke-linecap="round">
        <path d="M622,520 C636,590 642,690 638,836" stroke="${C.hijDeep}" stroke-width="3" opacity="0.6" filter="url(#blur2)"/>
        <path d="M634,515 C650,590 656,690 652,836" stroke="${C.hijLight}" stroke-width="7" opacity="0.5" filter="url(#blur4)"/>
        <path d="M600,530 C612,600 620,700 622,840" stroke="${C.hijLight}" stroke-width="4" opacity="0.35" filter="url(#blur4)"/>
        <path d="M662,560 C668,640 668,740 662,830" stroke="${C.hijDeep}" stroke-width="6" opacity="0.5" filter="url(#blur4)"/>
      </g>
    </g>
    <path d="${tail}" fill="none" stroke="${C.hijLine}" stroke-width="2" stroke-linejoin="round"/>
    <!-- slightly frayed hem edge -->
    <path d="M613,834 C630,842 652,840 666,830" fill="none" stroke="${C.hijLight}" stroke-width="1.4" opacity="0.8"/>
  </g>`;
}

/* ------------------------------------------------------------------ */
/*  FACE                                                              */
/* ------------------------------------------------------------------ */
function eye(cx, cy, mirror) {
  // local coordinates: outer corner at x = -24, inner corner at x = +23
  const white = `M-26,0 C-19,-14 -4,-20 9,-18 C18,-16 23,-7 24,3 C16,10 3,13 -9,11 C-18,9 -23,5 -26,0 Z`;
  const lid = `M-35,-8 C-30,-6 -27,-5 -25,-3 C-18,-17 -3,-23 10,-21 C19,-19 25,-10 26,3 C22,-5 16,-11 9,-12.5 C-4,-14.5 -15,-10 -23,0.5 C-26,-3 -30,-5.5 -35,-8 Z`;
  const id = mirror ? 'eyeR' : 'eyeL';
  return `
    <g id="${id}" transform="translate(${cx},${cy}) scale(${mirror ? -1.06 : 1.06},1.06)">
      <clipPath id="${id}Clip"><path d="${white}"/></clipPath>
      <path d="${white}" fill="url(#scleraGrad)"/>
      <g clip-path="url(#${id}Clip)">
        <circle cx="1" cy="-0.5" r="13.6" fill="url(#irisGrad)"/>
        <circle cx="1" cy="-0.5" r="13.6" fill="none" stroke="#2a1208" stroke-width="1.4" opacity="0.85"/>
        <g stroke="#e2ad74" stroke-width="0.6" opacity="0.45">
          ${Array.from({ length: 14 }, (_, i) => { const a = i / 14 * Math.PI * 2; return `<path d="M${f(1 + Math.cos(a) * 6.5)},${f(Math.sin(a) * 6.5)} L${f(1 + Math.cos(a) * 11)},${f(Math.sin(a) * 11)}"/>`; }).join('')}
        </g>
        <circle cx="1" cy="0" r="6" fill="${C.pupil}"/>
        <!-- upper‑lid shadow on the eyeball -->
        <path d="M-26,-20 L26,-20 L26,-6 C14,-11 -10,-12 -26,-4 Z" fill="#3a1d10" opacity="0.38" filter="url(#blur2)"/>
      </g>
      <path d="${white}" fill="none" stroke="#9c6a5c" stroke-width="0.8" opacity="0.6"/>
      <!-- crease -->
      <path d="M-22,-16 C-11,-27 6,-29 19,-21" fill="none" stroke="#a46a58" stroke-width="1.4" opacity="0.6" stroke-linecap="round"/>
      <path d="M-20,-17 C-10,-27 6,-29 18,-23" fill="none" stroke="${C.skinShade}" stroke-width="5" opacity="0.4" filter="url(#blur2)"/>
      <!-- upper lid line -->
      <path d="${lid}" fill="${C.lash}"/>
      <!-- lashes: fine curved strands -->
      <g fill="none" stroke="${C.lash}" stroke-linecap="round">
        <path d="M-33,-7 C-36,-9 -38,-12 -39,-15" stroke-width="1.6"/>
        <path d="M-29,-8 C-32,-11 -33,-14 -33,-17" stroke-width="1.4"/>
        <path d="M-24,-10 C-26,-14 -27,-17 -26,-20" stroke-width="1.3"/>
        <path d="M-19,-14 C-20,-18 -20,-21 -19,-23" stroke-width="1.2"/>
        <path d="M-13,-16 C-13,-19 -13,-22 -11,-24" stroke-width="1"/>
        <path d="M-6,-18 C-6,-20 -5,-22 -4,-23" stroke-width="0.9" opacity="0.8"/>
      </g>
      <!-- lower lid & waterline -->
      <path d="M-21,4 C-12,11 6,14 22,4" fill="none" stroke="#8a5242" stroke-width="1.1" opacity="0.55"/>
      <path d="M-20,7 L-23,10 M-14,10 L-16,13 M-7,12 L-8,15" stroke="${C.lash}" stroke-width="0.8" opacity="0.45" stroke-linecap="round"/>
      <ellipse cx="21" cy="2.5" rx="2.6" ry="2" fill="#e5a59b"/>
    </g>`;
}

function face() {
  const faceShape = `M408,230 C402,280 408,334 424,366 C442,396 470,414 500,415 C530,414 558,396 576,366 C592,334 598,280 592,230 C570,204 430,204 408,230 Z`;
  const brow = (mirror) => `
    <g transform="${mirror ? 'translate(1000,0) scale(-1,1)' : ''}">
      <path d="M489,272 C489,267 488,265 486,263 C477,257 464,252 449,252 C437,252 426,257 419,265 C425,263 432,261 440,261 C452,260 464,261 474,265 C480,267 485,269 489,272 Z" fill="${C.brow}"/>
      <g stroke="#6b4331" stroke-width="0.9" opacity="0.6" stroke-linecap="round">
        <path d="M484,268 L480,262"/><path d="M477,265 L472,258"/><path d="M469,262 L463,256"/><path d="M460,261 L454,255"/><path d="M450,261 L444,256"/><path d="M440,262 L434,258"/>
      </g>
    </g>`;
  return `
  <g id="face">
    <path d="${faceShape}" fill="url(#faceGrad)"/>
    <clipPath id="faceClip"><path d="${FACE_HOLE}"/></clipPath>
    <g clip-path="url(#faceClip)">
      <path d="${FACE_HOLE}" fill="none" stroke="${C.skinDeep}" stroke-width="12" opacity="0.5" filter="url(#blur4)"/>
      <!-- form shading -->
      <path d="M575,250 C585,300 580,350 555,392" stroke="${C.skinShade}" stroke-width="18" fill="none" opacity="0.55" filter="url(#blur8)"/>
      <path d="M425,260 C420,300 428,350 448,385" stroke="${C.skinShade}" stroke-width="12" fill="none" opacity="0.35" filter="url(#blur8)"/>
      <path d="M470,404 C488,414 512,414 530,404" stroke="${C.skinShade}" stroke-width="8" fill="none" opacity="0.4" filter="url(#blur4)"/>
      <!-- cheeks -->
      <ellipse cx="447" cy="342" rx="24" ry="13" fill="${C.blush}" opacity="0.45" filter="url(#blur8)"/>
      <ellipse cx="553" cy="342" rx="24" ry="13" fill="${C.blush}" opacity="0.45" filter="url(#blur8)"/>
      <!-- forehead & cheekbone highlights -->
      <ellipse cx="490" cy="235" rx="34" ry="10" fill="#fff6ef" opacity="0.6" filter="url(#blur8)"/>
      <ellipse cx="452" cy="320" rx="14" ry="7" fill="#fff6ef" opacity="0.55" filter="url(#blur4)"/>
      <!-- eye socket depth -->
      <ellipse cx="457" cy="293" rx="30" ry="17" fill="${C.skinShade}" opacity="0.35" filter="url(#blur4)"/>
      <ellipse cx="543" cy="293" rx="30" ry="17" fill="${C.skinShade}" opacity="0.4" filter="url(#blur4)"/>
      <!-- freckles -->
      <g fill="#c98a6e" opacity="0.45">
        <circle cx="474" cy="330" r="1.2"/><circle cx="481" cy="336" r="1"/><circle cx="468" cy="338" r="1.1"/><circle cx="487" cy="327" r="0.9"/>
        <circle cx="526" cy="330" r="1.2"/><circle cx="519" cy="336" r="1"/><circle cx="532" cy="338" r="1.1"/><circle cx="513" cy="327" r="0.9"/>
        <circle cx="456" cy="350" r="1"/><circle cx="544" cy="350" r="1"/>
      </g>
    </g>
    ${brow(false)}${brow(true)}
    ${eye(456, 299, false)}
    ${eye(544, 299, true)}
    <!-- catchlights (same light direction on both eyes) -->
    <g fill="#ffffff">
      <ellipse cx="452" cy="292" rx="4.2" ry="3.6"/><circle cx="462" cy="304" r="1.7" opacity="0.85"/>
      <ellipse cx="540" cy="292" rx="4.2" ry="3.6"/><circle cx="550" cy="304" r="1.7" opacity="0.85"/>
    </g>
    <!-- nose -->
    <g id="nose">
      <path d="M507,300 C510,318 513,334 514,346" fill="none" stroke="${C.skinShade}" stroke-width="5" opacity="0.6" filter="url(#blur2)"/>
      <path d="M494,304 C493,320 492,334 491,342" fill="none" stroke="#fff4ec" stroke-width="3" opacity="0.6" filter="url(#blur2)"/>
      <path d="M489,351 C493,357 507,357 511,351" fill="none" stroke="${C.skinLine}" stroke-width="1.5" stroke-linecap="round" opacity="0.8"/>
      <path d="M486,348 C484,352 486,355 490,355 M514,348 C516,352 514,355 510,355" fill="none" stroke="${C.skinLine}" stroke-width="1.2" opacity="0.6"/>
      <ellipse cx="500" cy="346" rx="5" ry="3" fill="#fff4ec" opacity="0.7" filter="url(#blur2)"/>
    </g>
    <!-- mouth: soft closed smile -->
    <g id="mouth">
      <path d="M480,375 C486,371 492,368 497,370 C499,371 501,371 503,370 C508,368 514,371 520,375 C512,377 506,377.5 500,377.5 C494,377.5 488,377 480,375 Z" fill="${C.lipDeep}"/>
      <path d="M482,377 C489,389 511,389 518,377 C510,379.5 490,379.5 482,377 Z" fill="url(#lipGrad)"/>
      <path d="M476,373.5 C485,379 494,378.5 500,378.5 C506,378.5 515,379 524,373.5" fill="none" stroke="#9c4f4c" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M474,371 C475,373.5 476,375 479,375.5 M526,371 C525,373.5 524,375 521,375.5" fill="none" stroke="#b4706a" stroke-width="1.2" stroke-linecap="round" opacity="0.8"/>
      <ellipse cx="502" cy="385" rx="7" ry="2" fill="#ffe3dc" opacity="0.6" filter="url(#blur2)"/>
      <path d="M492,397 C497,400 503,400 508,397" fill="none" stroke="${C.skinShade}" stroke-width="2" opacity="0.6" filter="url(#blur2)"/>
    </g>
  </g>`;
}

function underCap() {
  // white inner cap visible on the forehead
  const band = `M412,272 C412,226 450,202 500,202 C550,202 588,226 588,272 C580,246 550,229 500,229 C450,229 420,246 412,272 Z`;
  return `
  <g id="under-cap">
    <path d="M416,266 C420,246 454,231 500,231 C546,231 580,246 584,266" fill="none" stroke="${C.skinShade}" stroke-width="6" opacity="0.6" filter="url(#blur2)"/>
    <path d="${band}" fill="url(#capGrad)" stroke="${C.capShade}" stroke-width="1.2"/>
    <path d="M440,214 C470,204 530,204 560,214" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.8" filter="url(#blur2)"/>
  </g>`;
}

/* ------------------------------------------------------------------ */
/*  BAG + STRAP                                                       */
/* ------------------------------------------------------------------ */
function bagBackStrap() {
  return `<path d="M793,814 C788,788 764,768 724,758" fill="none" stroke="${C.bagShade}" stroke-width="12" stroke-linecap="round"/>
  <path d="M793,814 C788,788 764,768 724,758" fill="none" stroke="${C.bagDeep}" stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>`;
}
function bag() {
  const body = `M664,826 C662,880 664,930 670,968 C700,980 770,980 806,968 C812,930 814,880 812,826 C790,814 690,814 664,826 Z`;
  const flap = `M662,822 C690,808 788,808 814,822 L814,868 C808,904 790,918 738,920 C688,918 668,904 662,868 Z`;
  return `
  <g id="bag">
    <path d="${body}" transform="translate(5,8)" fill="#3b2116" opacity="0.3" filter="url(#blur8)"/>
    <!-- metal rings -->
    <rect x="667" y="804" width="14" height="18" rx="5" fill="none" stroke="url(#goldGrad)" stroke-width="3.5"/>
    <rect x="786" y="804" width="14" height="18" rx="5" fill="none" stroke="url(#goldGrad)" stroke-width="3.5"/>
    <path d="${body}" fill="url(#bagGrad)" stroke="${C.bagDeep}" stroke-width="2"/>
    <path d="M670,958 C700,968 772,968 806,958" fill="none" stroke="${C.bagLight}" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.8"/>
    <path d="M674,930 C676,950 680,960 690,966" fill="none" stroke="${C.bagLight}" stroke-width="3" opacity="0.4" filter="url(#blur2)"/>
    <!-- flap -->
    <path d="${flap}" fill="url(#flapGrad)" stroke="${C.bagDeep}" stroke-width="2" stroke-linejoin="round"/>
    <path d="M668,828 C694,816 784,816 808,828 L808,866 C803,898 786,910 738,912 C690,910 673,898 668,866 Z" fill="none" stroke="${C.bagLight}" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.85"/>
    <path d="M676,830 C700,822 740,820 770,824" fill="none" stroke="#ffd9b0" stroke-width="5" opacity="0.35" filter="url(#blur2)"/>
    <!-- buckle strap & buckle -->
    <path d="M728,872 L748,872 L748,950 L728,950 Z" fill="${C.bagShade}" stroke="${C.bagDeep}" stroke-width="1.6"/>
    <rect x="723" y="895" width="30" height="26" rx="4" fill="none" stroke="url(#goldGrad)" stroke-width="4"/>
    <rect x="736" y="895" width="4" height="26" fill="url(#goldGrad)"/>
    <path d="M725,897 L751,897" stroke="${C.goldLight}" stroke-width="1" opacity="0.9"/>
  </g>`;
}
function bagFrontStrap() {
  const strap = `M638,488 C652,500 662,540 666,600 C670,680 672,760 674,808 L688,808 C686,760 684,680 680,600 C676,535 666,496 652,480 Z`;
  return `
  <g id="bag-strap">
    <path d="${strap}" transform="translate(3,4)" fill="#3b2116" opacity="0.3" filter="url(#blur2)"/>
    <path d="${strap}" fill="url(#strapGrad)" stroke="${C.bagDeep}" stroke-width="1.6" stroke-linejoin="round"/>
    <path d="M647,492 C660,520 668,570 671,620 C674,700 676,760 678,806" fill="none" stroke="#ffd2a3" stroke-width="1" stroke-dasharray="3 3" opacity="0.75"/>
  </g>`;
}

/* ------------------------------------------------------------------ */
/*  WATCH on her left wrist (viewer right)                            */
/* ------------------------------------------------------------------ */
function watch() {
  return `
  <g id="watch">
    <path d="M659,1000 C668,1005 692,1005 701,1000 L701,1014 C692,1019 668,1019 659,1014 Z" fill="url(#goldGrad)" stroke="${C.goldDeep}" stroke-width="1"/>
    <g stroke="${C.goldDeep}" stroke-width="0.8" opacity="0.7">${[664, 670, 690, 696].map((x) => `<path d="M${x},1003 L${x},1016"/>`).join('')}</g>
    <circle cx="680" cy="1009" r="12.5" fill="url(#goldGrad)" stroke="${C.goldDeep}" stroke-width="1.2"/>
    <circle cx="680" cy="1009" r="9.5" fill="url(#watchFace)"/>
    <g stroke="#6d5a3a" stroke-linecap="round">
      <path d="M680,1009 L680,1002" stroke-width="1.3"/><path d="M680,1009 L685,1011" stroke-width="1.1"/>
    </g>
    <g fill="#9b8a66">${[0, 1, 2, 3].map((i) => { const a = i * Math.PI / 2; return `<circle cx="${f(680 + Math.cos(a) * 7.5)}" cy="${f(1009 + Math.sin(a) * 7.5)}" r="0.8"/>`; }).join('')}</g>
    <path d="M673,1003 C676,1000 681,1000 684,1001" stroke="#ffffff" stroke-width="1.2" fill="none" opacity="0.8"/>
  </g>`;
}

/* ------------------------------------------------------------------ */
/*  ASSEMBLE (back → front)                                           */
/* ------------------------------------------------------------------ */
function build() {
  seed = 7;
  const body = [
    background(),
    `<g id="hind" >`,
    hijabBack(),
    legsAndShoes(),
    skirt(),
    blouse(),
    necklace(),
    bagBackStrap(),
    arm('arm-right', false),   // her right arm (viewer left)
    arm('arm-left', true),     // her left arm (viewer right)
    watch(),
    face(),
    underCap(),
    hijabFront(),
    hijabTail(),
    bag(),
    bagFrontStrap(),
    `</g>`,
  ].join('\n');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">
  <title>Hind — Front View</title>
  ${defs()}
  ${body}
</svg>`;
}

const out = path.join(__dirname, '..', 'output', 'Hind_Front.svg');
fs.writeFileSync(out, build());
console.log('wrote', out);
