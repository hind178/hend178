// HIND — royal-blue hijab, off-white blouse, blue patchwork skirt, brown crossbody bag, beads, gold watch, loafers.
const { f, lerp, ease, mkRng, smooth, clamp } = require('../lib/util');
const { P } = require('../lib/defs');
const R = require('./rig');
const sk = P.hind;
const CX = 500;

/* ---------- static, cached pieces ---------- */
const WAIST_Y = 790, HEM_Y = 1662;
function hw(y) {
  if (y <= WAIST_Y) return 110;
  if (y <= 905) return lerp(110, 160, ease((y - WAIST_Y) / (905 - WAIST_Y)));
  return lerp(160, 254, Math.pow((y - 905) / (HEM_Y - 905), 0.95));
}
function hemY(x) { const t = (x - (CX - 254)) / 508; return HEM_Y + Math.sin(t * Math.PI * 11) * 6 + Math.sin(t * Math.PI) * 6; }
function skirtOutline() {
  const left = [], right = [];
  for (let y = WAIST_Y; y <= HEM_Y - 4; y += 26) { left.push([CX - hw(y), y]); right.unshift([CX + hw(y), y]); }
  const hem = []; for (let x = CX - 254; x <= CX + 254; x += 11) hem.push([x, hemY(x)]);
  return smooth([...left, ...hem, ...right], true, 0.9);
}
let SKIRT = null;
function skirtStatic() {
  if (SKIRT) return SKIRT;
  const rnd = mkRng(7);
  const outline = skirtOutline();
  const quad = (u0, u1, y0, y1) => `M${f(CX + u0 * hw(y0))},${y0} L${f(CX + u1 * hw(y0))},${y0} L${f(CX + u1 * hw(y1))},${y1} L${f(CX + u0 * hw(y1))},${y1} Z`;
  const seamLine = (u0, u1, y) => `M${f(CX + u0 * hw(y))},${y} L${f(CX + u1 * hw(y))},${y}`;
  const rows = [[WAIST_Y, 870, 'main'], [870, 884, 'band'], [884, 990, 'main'], [990, 1090, 'main'], [1090, 1104, 'band'], [1104, 1215, 'main'], [1215, 1322, 'main'], [1322, 1336, 'band'], [1336, 1448, 'main'], [1448, 1552, 'main'], [1552, 1566, 'band'], [1566, 1630, 'main'], [1630, 1644, 'band'], [1644, 1700, 'hem']];
  const pats = ['pNavyFloral', 'pCreamIkat', 'pRoyalLattice', 'pLightCross', 'pMedallion', 'pCreamDots', 'pSpeckle'];
  let panels = '', seams = '', prev = '';
  rows.forEach(([y0, y1, kind]) => {
    if (kind === 'hem') { panels += `<path d="${quad(-1.2, 1.2, y0, y1)}" fill="url(#pCreamIkat)"/>`; return; }
    if (kind === 'band') { panels += `<path d="${quad(-1.2, 1.2, y0, y1)}" fill="url(#pBand)"/>`; return; }
    const n = 4 + Math.floor(rnd() * 3);
    const us = [-1.25]; for (let i = 1; i < n; i++) us.push(-1.25 + (2.5 * i) / n + (rnd() - 0.5) * 0.18); us.push(1.25);
    for (let i = 0; i < n; i++) {
      let p; do { p = pats[Math.floor(rnd() * pats.length)]; } while (p === prev); prev = p;
      if (rnd() < 0.3 && y1 - y0 > 90) {
        const ym = (y0 + y1) / 2 + (rnd() - 0.5) * 20; let p2; do { p2 = pats[Math.floor(rnd() * pats.length)]; } while (p2 === p);
        panels += `<path d="${quad(us[i], us[i + 1], y0, ym)}" fill="url(#${p})"/><path d="${quad(us[i], us[i + 1], ym, y1)}" fill="url(#${p2})"/>`;
        seams += seamLine(us[i], us[i + 1], ym);
      } else panels += `<path d="${quad(us[i], us[i + 1], y0, y1)}" fill="url(#${p})"/>`;
      if (i > 0) seams += `M${f(CX + us[i] * hw(y0))},${y0} L${f(CX + us[i] * hw(y1))},${y1} `;
    }
    seams += seamLine(-1.25, 1.25, y1);
  });
  let folds = '';
  const N = 13;
  for (let i = 0; i < N; i++) {
    const uw = -0.95 + (1.9 * i) / (N - 1), uh = uw * 1.04 + (rnd() - 0.5) * 0.05;
    const xw = CX + uw * hw(WAIST_Y + 6), xh = CX + uh * 254, wB = 24 + rnd() * 10, xm = lerp(xw, xh, 0.5), ym = (WAIST_Y + HEM_Y) / 2;
    folds += `<path d="M${f(xw - 4)},${WAIST_Y} Q${f(xm - wB * 0.6)},${ym} ${f(xh - wB)},${HEM_Y + 14} L${f(xh + wB)},${HEM_Y + 14} Q${f(xm + wB * 0.6)},${ym} ${f(xw + 4)},${WAIST_Y} Z" fill="url(#foldShadow)"/>`;
  }
  const wb = `M${CX - 112},${WAIST_Y - 20} C${CX - 60},${WAIST_Y - 24} ${CX + 60},${WAIST_Y - 24} ${CX + 112},${WAIST_Y - 20} L${CX + 113},${WAIST_Y + 6} C${CX + 60},${WAIST_Y + 2} ${CX - 60},${WAIST_Y + 2} ${CX - 113},${WAIST_Y + 6} Z`;
  SKIRT = `
    <clipPath id="hindSkirtClip"><path d="${outline}"/></clipPath>
    <g clip-path="url(#hindSkirtClip)">
      <rect x="200" y="${WAIST_Y - 30}" width="600" height="${HEM_Y - WAIST_Y + 60}" fill="${P.royal}"/>
      ${panels}
      <path d="${seams}" fill="none" stroke="${P.cream}" stroke-width="3.2"/>
      <path d="${seams}" fill="none" stroke="${P.navy}" stroke-width="1.3" stroke-dasharray="1.5 4" stroke-linecap="round"/>
      ${folds}
      <rect x="240" y="${WAIST_Y - 30}" width="520" height="${HEM_Y - WAIST_Y + 60}" fill="url(#skirtSide)"/>
    </g>
    <path d="${outline}" fill="none" stroke="#0f1d55" stroke-width="2.4" stroke-linejoin="round"/>
    <path d="${wb}" fill="url(#pRoyalLattice)"/><path d="${wb}" fill="#0b1645" opacity="0.2"/>
    <path d="${wb}" fill="none" stroke="#0f1d55" stroke-width="2"/>`;
  return SKIRT;
}

const FACE_HOLE = `M500,200 C450,200 417,226 413,262 C409,300 415,336 429,364 C445,391 472,407 500,408 C528,407 555,391 571,364 C585,336 591,300 587,262 C583,226 550,200 500,200 Z`;
const HIJAB_HEAD = `M500,128 C432,126 384,158 368,212 C355,256 353,312 359,362 C365,404 377,436 392,458 C366,474 338,494 322,520 C326,540 352,552 386,556 C410,566 440,578 470,576 C500,584 540,580 568,568 C600,560 632,544 652,524 L670,510 C656,492 634,476 614,462 C626,436 638,404 643,360 C649,310 647,256 634,212 C618,158 568,126 500,128 Z`;
const FACE_SHAPE = `M408,230 C402,280 408,334 424,366 C442,396 470,414 500,415 C530,414 558,396 576,366 C592,334 598,280 592,230 C570,204 430,204 408,230 Z`;

const faceStyle = {
  ...sk, iris: 'irisBrown', irisR: 13.8, sx: 1.06, sy: 1.06, wing: 0, lashes: 6, brow: '#4b2c1d', arch: 0, thick: 0,
  lip: 'lipHind', lipDeep: '#bf6a68', freckles: true, eyeGap: 44, eyeY: 299, mouthY: 377,
};

function hijabFrame(turn) {
  const frame = `${HIJAB_HEAD} ${FACE_HOLE}`;
  return `
    <clipPath id="hindHijabClip"><path d="${frame}" clip-rule="evenodd"/></clipPath>
    <path d="${frame}" fill-rule="evenodd" fill="url(#hijabGrad)"/>
    <g clip-path="url(#hindHijabClip)" fill="none" stroke-linecap="round">
      <path d="M380,190 C420,140 520,124 600,150" stroke="${P.hijLight}" stroke-width="7" opacity="0.55" filter="url(#blur4)"/>
      <path d="M372,232 C420,170 540,156 630,200" stroke="${P.hijDeep}" stroke-width="3" opacity="0.45" filter="url(#blur2)"/>
      <path d="M370,270 C384,215 430,184 480,176" stroke="${P.hijDeep}" stroke-width="2.4" opacity="0.45" filter="url(#blur2)"/>
      <path d="M612,180 C640,220 650,280 646,340" stroke="${P.hijDeep}" stroke-width="10" opacity="0.4" filter="url(#blur8)"/>
      <path d="M366,300 C362,350 368,400 384,440" stroke="${P.hijLight}" stroke-width="6" opacity="0.45" filter="url(#blur4)"/>
      <path d="M394,262 C392,320 404,380 430,420" stroke="${P.hijDeep}" stroke-width="2.4" opacity="0.5" filter="url(#blur2)"/>
      <path d="${FACE_HOLE}" stroke="${P.hijDeep}" stroke-width="10" opacity="0.55" filter="url(#blur4)"/>
    </g>
    <path d="${frame}" fill-rule="evenodd" fill="none" stroke="${P.hijLine}" stroke-width="2.2" stroke-linejoin="round"/>`;
}
function hijabWrap() {
  const wrap = `M587,296 C592,352 572,396 534,412 C512,420 488,420 466,414 C440,430 410,460 384,488 C366,506 346,520 326,528 C352,546 392,552 430,542 C480,530 540,508 590,474 C616,452 632,420 640,380 C645,350 647,320 646,300 C628,288 604,288 587,296 Z`;
  return `
    <path d="${wrap}" transform="translate(0,8)" fill="#0b1645" opacity="0.4" filter="url(#blur4)"/>
    <path d="${wrap}" fill="url(#hijabGrad)"/>
    <clipPath id="hindWrapClip"><path d="${wrap}"/></clipPath>
    <g clip-path="url(#hindWrapClip)" fill="none" stroke-linecap="round">
      <path d="M612,320 C606,390 560,440 470,470 C420,488 380,505 340,526" stroke="${P.hijLight}" stroke-width="8" opacity="0.5" filter="url(#blur4)"/>
      <path d="M630,360 C618,420 566,470 480,500 C430,516 390,530 350,536" stroke="${P.hijDeep}" stroke-width="2.4" opacity="0.6" filter="url(#blur2)"/>
      <path d="M596,300 C600,360 570,402 520,420" stroke="${P.hijDeep}" stroke-width="6" opacity="0.5" filter="url(#blur4)"/>
      <path d="M470,416 C440,440 410,470 380,494" stroke="${P.hijDeep}" stroke-width="3" opacity="0.5" filter="url(#blur2)"/>
    </g>
    <path d="${wrap}" fill="none" stroke="${P.hijLine}" stroke-width="2" stroke-linejoin="round"/>
    <path d="M466,414 C440,430 410,460 384,488 C366,506 346,520 326,528" fill="none" stroke="${P.hijLight}" stroke-width="1.4" opacity="0.8"/>`;
}
function hijabTail(sway) {
  const s = sway * 14;
  const tail = `M606,462 C630,478 650,500 660,528 C${f(672 + s * 0.3)},590 ${f(676 + s * 0.6)},670 ${f(672 + s * 0.8)},750 C${f(670 + s)},784 ${f(668 + s)},808 ${f(666 + s)},830 C${f(652 + s)},840 ${f(630 + s)},842 ${f(612 + s)},834 C${f(616 + s * 0.8)},790 ${f(616 + s * 0.6)},740 ${f(612 + s * 0.4)},690 C606,624 598,566 584,526 C592,504 598,484 606,462 Z`;
  return `
    <path d="${tail}" transform="translate(6,6)" fill="#0b1645" opacity="0.25" filter="url(#blur4)"/>
    <path d="${tail}" fill="url(#hijabTailGrad)"/>
    <clipPath id="hindTailClip"><path d="${tail}"/></clipPath>
    <g clip-path="url(#hindTailClip)" fill="none" stroke-linecap="round">
      <path d="M622,520 C636,590 642,690 ${f(638 + s)},836" stroke="${P.hijDeep}" stroke-width="3" opacity="0.6" filter="url(#blur2)"/>
      <path d="M634,515 C650,590 656,690 ${f(652 + s)},836" stroke="${P.hijLight}" stroke-width="7" opacity="0.5" filter="url(#blur4)"/>
      <path d="M662,560 C668,640 668,740 ${f(662 + s)},830" stroke="${P.hijDeep}" stroke-width="6" opacity="0.5" filter="url(#blur4)"/>
    </g>
    <path d="${tail}" fill="none" stroke="${P.hijLine}" stroke-width="2" stroke-linejoin="round"/>`;
}
function underCap() {
  const band = `M412,272 C412,226 450,202 500,202 C550,202 588,226 588,272 C580,246 550,229 500,229 C450,229 420,246 412,272 Z`;
  return `<path d="M416,266 C420,246 454,231 500,231 C546,231 580,246 584,266" fill="none" stroke="${sk.skinShade}" stroke-width="6" opacity="0.6" filter="url(#blur2)"/>
    <path d="${band}" fill="url(#capGrad)" stroke="${P.capShade}" stroke-width="1.2"/>
    <path d="M440,214 C470,204 530,204 560,214" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.8" filter="url(#blur2)"/>`;
}
function torso() {
  const t = `M330,505 C318,545 322,605 334,655 C346,705 366,745 386,775 C440,786 560,786 614,775 C634,745 654,705 666,655 C678,605 682,545 670,505 C600,478 400,478 330,505 Z`;
  const blousing = `M384,766 C392,782 410,792 430,790 C450,796 470,792 490,795 C510,792 530,797 552,791 C574,794 596,788 616,766 C600,772 580,776 560,774 C540,778 460,778 440,774 C420,776 400,772 384,766 Z`;
  return `<clipPath id="hindTorsoClip"><path d="${t}"/></clipPath>
    <path d="${t}" fill="url(#blouseGrad)"/>
    <g clip-path="url(#hindTorsoClip)">
      <path d="M380,610 C410,650 460,660 490,640" stroke="${P.blShade}" stroke-width="10" fill="none" opacity="0.7" filter="url(#blur4)"/>
      <path d="M520,640 C550,662 600,650 625,610" stroke="${P.blDeep}" stroke-width="10" fill="none" opacity="0.55" filter="url(#blur4)"/>
      <g fill="none" stroke="${P.blDeep}" stroke-width="2" opacity="0.5"><path d="M420,660 C425,700 432,740 440,772"/><path d="M548,670 C545,710 540,745 534,774"/><path d="M585,655 C580,700 572,740 562,772"/></g>
      <path d="M640,520 C660,600 655,700 620,780 L700,780 L700,500 Z" fill="${P.blDeep}" opacity="0.35" filter="url(#blur8)"/>
      <path d="M500,545 L500,780" stroke="${P.blDeep}" stroke-width="1.6" opacity="0.8"/><path d="M509,545 L509,780" stroke="${P.blShade}" stroke-width="1.2"/>
      ${[680, 735].map((y) => `<circle cx="504.5" cy="${y}" r="4.2" fill="#fbf8f1" stroke="${P.blDeep}" stroke-width="1.2"/>`).join('')}
    </g>
    <path d="${t}" fill="none" stroke="${P.blLine}" stroke-width="2"/>
    <path d="${blousing}" fill="${P.bl}" stroke="${P.blLine}" stroke-width="1.6" stroke-linejoin="round"/>`;
}
function necklace() {
  const P0 = [408, 540], P1 = [500, 770], P2 = [592, 540];
  const q = (t) => [(1 - t) ** 2 * P0[0] + 2 * (1 - t) * t * P1[0] + t * t * P2[0], (1 - t) ** 2 * P0[1] + 2 * (1 - t) * t * P1[1] + t * t * P2[1]];
  let b = `<path d="M${P0} Q${P1} ${P2}" fill="none" stroke="#8c7a55" stroke-width="1" opacity="0.6"/>`;
  for (let i = 0; i <= 34; i++) {
    const [x, y] = q(i / 34);
    b += i % 2 === 0 ? `<circle cx="${f(x)}" cy="${f(y)}" r="6.8" fill="url(#beadGrad)" stroke="${P.beadDeep}" stroke-width="0.8"/><circle cx="${f(x - 2)}" cy="${f(y - 2.4)}" r="1.8" fill="#fff" opacity="0.85"/>`
      : `<circle cx="${f(x)}" cy="${f(y)}" r="2.8" fill="url(#goldGrad)"/>`;
  }
  return b;
}
function bag(sway) {
  const body = `M664,826 C662,880 664,930 670,968 C700,980 770,980 806,968 C812,930 814,880 812,826 C790,814 690,814 664,826 Z`;
  const flap = `M662,822 C690,808 788,808 814,822 L814,868 C808,904 790,918 738,920 C688,918 668,904 662,868 Z`;
  return `<g transform="rotate(${f(sway * 3)} 680 500)">
    <path d="M793,814 C788,788 764,768 724,758" fill="none" stroke="${P.bagShade}" stroke-width="12" stroke-linecap="round"/>
    <path d="${body}" transform="translate(5,8)" fill="#3b2116" opacity="0.3" filter="url(#blur8)"/>
    <rect x="667" y="804" width="14" height="18" rx="5" fill="none" stroke="url(#goldGrad)" stroke-width="3.5"/>
    <rect x="786" y="804" width="14" height="18" rx="5" fill="none" stroke="url(#goldGrad)" stroke-width="3.5"/>
    <path d="${body}" fill="url(#bagGrad)" stroke="${P.bagDeep}" stroke-width="2"/>
    <path d="${flap}" fill="url(#flapGrad)" stroke="${P.bagDeep}" stroke-width="2"/>
    <path d="M668,828 C694,816 784,816 808,828 L808,866 C803,898 786,910 738,912 C690,910 673,898 668,866 Z" fill="none" stroke="${P.bagLight}" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.85"/>
    <path d="M728,872 L748,872 L748,950 L728,950 Z" fill="${P.bagShade}" stroke="${P.bagDeep}" stroke-width="1.6"/>
    <rect x="723" y="895" width="30" height="26" rx="4" fill="none" stroke="url(#goldGrad)" stroke-width="4"/>
    <rect x="736" y="895" width="4" height="26" fill="url(#goldGrad)"/>
  </g>`;
}
function strap() {
  const s = `M638,488 C652,500 662,540 666,600 C670,680 672,760 674,808 L688,808 C686,760 684,680 680,600 C676,535 666,496 652,480 Z`;
  return `<path d="${s}" fill="url(#strapGrad)" stroke="${P.bagDeep}" stroke-width="1.6"/>
    <path d="M647,492 C660,520 668,570 671,620 C674,700 676,760 678,806" fill="none" stroke="#ffd2a3" stroke-width="1" stroke-dasharray="3 3" opacity="0.75"/>`;
}
function watch() {
  return `<g transform="translate(0,-14)"><path d="M-22,-6 C-10,0 10,0 22,-6 L22,6 C10,12 -10,12 -22,6 Z" fill="url(#goldGrad)" stroke="${P.goldDeep}" stroke-width="1"/>
    <circle cx="-4" cy="3" r="11" fill="url(#goldGrad)" stroke="${P.goldDeep}" stroke-width="1.2"/><circle cx="-4" cy="3" r="8.2" fill="url(#watchFace)"/>
    <path d="M-4,3 L-4,-3 M-4,3 L0,5" stroke="#6d5a3a" stroke-width="1.2" stroke-linecap="round"/></g>`;
}
function legsShoes(pz) {
  const lift = (side) => pz.walkAmp ? Math.max(0, Math.sin(pz.walk + (side ? Math.PI : 0))) * 22 * pz.walkAmp : 0;
  const leg = (cx) => `<path d="M${cx - 28},1640 C${cx - 31},1684 ${cx - 24},1728 ${cx - 16},1770 L${cx + 16},1770 C${cx + 23},1728 ${cx + 29},1684 ${cx + 27},1640 Z" fill="url(#hindLimbV)" stroke="${sk.skinLine}" stroke-width="1.6"/>`;
  const shoe = (cx, rot) => `<g transform="rotate(${rot} ${cx} 1800)">
      <path d="M${cx - 41},1816 C${cx - 43},1840 ${cx - 26},1853 ${cx},1853 C${cx + 26},1853 ${cx + 43},1840 ${cx + 41},1816 Z" fill="${P.shoeDeep}"/>
      <path d="M${cx - 19},1762 C${cx - 31},1772 ${cx - 39},1792 ${cx - 40},1814 C${cx - 41},1834 ${cx - 25},1846 ${cx},1846 C${cx + 25},1846 ${cx + 41},1834 ${cx + 40},1814 C${cx + 39},1792 ${cx + 31},1772 ${cx + 19},1762 C${cx + 8},1769 ${cx - 8},1769 ${cx - 19},1762 Z" fill="url(#shoeGrad)" stroke="${P.shoeDeep}" stroke-width="2"/>
      <path d="M${cx - 27},1802 C${cx - 26},1782 ${cx + 26},1782 ${cx + 27},1802" fill="none" stroke="${P.shoeDeep}" stroke-width="2"/>
      <path d="M${cx - 24},1790 C${cx - 10},1796 ${cx + 10},1796 ${cx + 24},1790 L${cx + 22},1800 C${cx + 10},1805 ${cx - 10},1805 ${cx - 22},1800 Z" fill="${P.shoe}" stroke="${P.shoeDeep}" stroke-width="1.4"/>
      <g stroke="${P.shoeDeep}" stroke-width="1.2" fill="${P.shoe}"><path d="M${cx - 13},1814 C${cx - 12},1828 ${cx - 5},1830 ${cx - 5},1814 Z"/><path d="M${cx + 13},1814 C${cx + 12},1828 ${cx + 5},1830 ${cx + 5},1814 Z"/></g>
      <ellipse cx="${cx - 10}" cy="1824" rx="11" ry="5" fill="#fff" opacity="0.22" filter="url(#blur2)"/></g>`;
  const l1 = lift(0), l2 = lift(1);
  return `<g transform="translate(0,${f(-l1)})">${leg(454)}${shoe(450, 5)}</g><g transform="translate(0,${f(-l2)})">${leg(546)}${shoe(550, -5)}</g>`;
}
const ARM = {
  shoulder: [342, 520], len1: 250, len2: 238, handOffset: -4,
  upper: { fill: 'url(#sleeveGrad)', stroke: P.blLine, wfn: (t) => lerp(76, 66, t) },
  fore: { fill: 'url(#sleeveGrad)', stroke: P.blLine, from: -0.04, to: 0.9, gathers: 6, wfn: (t) => t < 0.72 ? lerp(66, 92, Math.sin(t / 0.72 * Math.PI / 2)) : lerp(92, 60, (t - 0.72) / 0.28) },
  cuff: { from: 0.86, to: 0.99, w: 58, fill: P.bl, stroke: P.blLine, button: '#fbf8f1' },
};

/** draw Hind. options: { headOnly } */
function draw(p, opt = {}) {
  const pz = R.pose(p);
  const sway = pz.skirtSway + (pz.walkAmp ? Math.sin(pz.walk) * 2.2 * pz.walkAmp : 0);
  const A = R.arms(ARM, pz, sk, 'hind', { L: { wrist: watch() } });
  if (opt.joints) { opt.joints.R = A.jR; opt.joints.L = A.jL; opt.joints.k = 1; }
  const breathe = 1 + Math.sin(pz.breathe * 2 * Math.PI / 3.6) * 0.006;
  const head = R.headGroup(pz, `
      <path d="${FACE_SHAPE}" fill="url(#hindFace)"/>
      <clipPath id="hindFaceClip"><path d="${FACE_HOLE}"/></clipPath>
      <g clip-path="url(#hindFaceClip)"><path d="${FACE_HOLE}" fill="none" stroke="${sk.skinDeep}" stroke-width="12" opacity="0.5" filter="url(#blur4)"/>
        <path d="M575,250 C585,300 580,350 555,392" stroke="${sk.skinShade}" stroke-width="18" fill="none" opacity="${(0.5 + pz.turn * 0.2).toFixed(2)}" filter="url(#blur8)"/></g>
      ${R.features('hind', faceStyle, pz)}
      ${underCap()}
      ${hijabFrame(pz.turn)}
      ${hijabWrap()}`);
  const body = `
    <path d="${HIJAB_HEAD}" transform="translate(0,6)" fill="#0b1645" opacity="0.3" filter="url(#blur8)"/>
    ${pz.sit ? '' : R.groundShadow(240) + legsShoes(pz) + `<g transform="translate(500,790) skewX(${f(sway)}) translate(-500,-790)">${skirtStatic()}</g>`}
    <g transform="translate(500,780) scale(1,${breathe.toFixed(4)}) translate(-500,-780)">${torso()}${necklace()}</g>
    ${pz.sit || opt.noBag ? '' : bag(sway * 0.2)}
    ${A.R}${A.L}
    ${head}
    ${hijabTail(sway * 0.2 + Math.sin(pz.breathe * 1.3) * 0.15)}
    ${opt.noBag ? '' : strap()}
    ${pz.sit ? '' : ''}`;
  return R.place(pz, body, opt.tag || 'hind');
}
/** Day-2 comfortable outfit: same face, hijab, necklace & watch; soft lilac loungewear dress. */
function drawComfy(p, opt = {}) {
  return draw(p, { ...opt, noBag: true })
    .replace(/url\(#(blouseGrad|sleeveGrad)\)/g, 'url(#comfyTop)').replace(/fill="#f6f1e8"/g, 'fill="#e4daf0"')
    .replace(/url\(#p(NavyFloral|CreamIkat|RoyalLattice|LightCross|Medallion|CreamDots|Band|Speckle)\)/g, 'url(#comfyDress)')
    .replace(/url\(#skirtSide\)/g, 'url(#skirtSide)');
}
module.exports = { draw, drawComfy, faceStyle, ARM };
