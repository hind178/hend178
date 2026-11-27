// LOREEN — floral turban, pink bow-collar blouse with pintucks, black belt, long black skirt, plaid handbag, black sneakers.
const { f, lerp, ease, smooth, clamp } = require('../lib/util');
const { P } = require('../lib/defs');
const R = require('./rig');
const sk = P.loreen;
const CX = 500;

const FACE_SHAPE = `M407,236 C402,290 409,338 426,368 C444,399 472,417 500,419 C528,417 556,399 574,368 C591,338 598,290 593,236 C585,212 415,212 407,236 Z`;
const TURBAN = `M500,86 C440,82 394,108 378,156 C364,198 366,250 384,300 C394,292 402,280 408,266 C420,238 452,222 500,221 C548,222 580,238 592,266 C598,280 606,292 616,300 C634,250 636,198 622,156 C606,108 560,82 500,86 Z`;

const faceStyle = {
  ...sk, iris: 'irisHazel', irisR: 12.8, sx: 1.1, sy: 0.96, almond: true, wing: 7, lashes: 5, lashW: 1.1,
  brow: '#3a2216', arch: 3, thick: 1.5, lip: 'lipLoreen', lipDeep: '#c26f72', freckles: false, eyeGap: 45, eyeY: 300, mouthY: 378,
};

function turban(turn) {
  const s = turn * 4;
  return `
    <path d="${TURBAN}" transform="translate(0,8)" fill="#3b2a20" opacity="0.25" filter="url(#blur8)"/>
    <path d="${TURBAN}" fill="url(#pTurban)"/>
    <clipPath id="lorTurbClip"><path d="${TURBAN}"/></clipPath>
    <g clip-path="url(#lorTurbClip)">
      <path d="${TURBAN}" fill="url(#turbanShade)"/>
      <!-- front twist: two crossing bands -->
      <path d="M${f(418 + s)},236 C${f(440 + s)},200 ${f(500 + s)},150 ${f(590 + s)},126 L${f(620 + s)},160 C${f(560 + s)},176 ${f(510 + s)},206 ${f(478 + s)},230 Z" fill="url(#pTurban)"/>
      <path d="M${f(418 + s)},236 C${f(440 + s)},200 ${f(500 + s)},150 ${f(590 + s)},126" fill="none" stroke="#7d725f" stroke-width="2" opacity="0.6"/>
      <path d="M${f(478 + s)},230 C${f(510 + s)},206 ${f(560 + s)},176 ${f(620 + s)},160" fill="none" stroke="#7d725f" stroke-width="5" opacity="0.35" filter="url(#blur2)"/>
      <path d="M${f(582 + s)},236 C${f(560 + s)},200 ${f(500 + s)},150 ${f(410 + s)},126 L${f(380 + s)},160 C${f(440 + s)},176 ${f(490 + s)},206 ${f(522 + s)},230 Z" fill="url(#pTurban)"/>
      <path d="M${f(582 + s)},236 C${f(560 + s)},200 ${f(500 + s)},150 ${f(410 + s)},126" fill="none" stroke="#7d725f" stroke-width="2" opacity="0.6"/>
      <path d="M${f(522 + s)},230 C${f(490 + s)},206 ${f(440 + s)},176 ${f(380 + s)},160" fill="none" stroke="#5a5040" stroke-width="7" opacity="0.3" filter="url(#blur4)"/>
      <!-- wrapped folds around the sides -->
      <g fill="none" stroke="#6f6553" stroke-linecap="round" opacity="0.45">
        <path d="M370,250 C380,200 410,170 446,156" stroke-width="2.4"/><path d="M366,284 C372,240 392,210 420,192" stroke-width="2"/>
        <path d="M630,250 C620,200 590,170 554,156" stroke-width="2.4"/><path d="M634,284 C628,240 608,210 580,192" stroke-width="2"/>
      </g>
      <path d="M384,150 C420,100 480,88 520,90" stroke="#ffffff" stroke-width="10" opacity="0.35" fill="none" filter="url(#blur8)"/>
      <path d="M616,200 C632,240 630,280 620,310" stroke="#3b3020" stroke-width="16" opacity="0.25" fill="none" filter="url(#blur8)"/>
      <!-- inner edge shadow on the fabric -->
      <path d="M376,314 C388,304 398,286 406,266 C418,238 452,222 500,221 C548,222 582,238 594,266 C602,286 612,304 624,314" stroke="#5c5141" stroke-width="6" fill="none" opacity="0.35" filter="url(#blur2)"/>
    </g>
    <path d="${TURBAN}" fill="none" stroke="#867b67" stroke-width="2"/>`;
}
function earsPearls(turn) {
  const ear = (x, m) => `<path d="M${x},312 C${x - m * 9},310 ${x - m * 12},332 ${x - m * 6},346 C${x - m * 3},352 ${x + m * 2},350 ${x + m * 4},344 Z" fill="url(#loreenFace)" stroke="${sk.skinLine}" stroke-width="1.2"/>
    <circle cx="${x - m * 6}" cy="352" r="4.6" fill="#fbf7ef" stroke="#c9bfae" stroke-width="0.8"/><circle cx="${x - m * 7.5}" cy="350.5" r="1.4" fill="#fff"/>`;
  return (turn < 0.5 ? ear(412, 1) : '') + (turn > -0.5 ? ear(588, -1) : '');
}
function neck() {
  return `<path d="M468,380 L466,478 C480,490 520,490 534,478 L532,380 Z" fill="url(#loreenNeck)" stroke="${sk.skinLine}" stroke-width="1.4"/>
    <path d="M468,405 C485,425 515,425 532,405 L532,430 C515,440 485,440 468,430 Z" fill="${sk.skinDeep}" opacity="0.4" filter="url(#blur2)"/>
    <path d="M466,446 C480,455 520,455 534,446 L534,462 C520,471 480,471 466,462 Z" fill="${P.blk}" stroke="#000" stroke-width="1"/>
    <path d="M468,450 C482,457 518,457 532,450" stroke="#555" stroke-width="1.2" fill="none" opacity="0.7"/>`;
}
function torso() {
  const t = `M344,522 C328,560 330,610 340,650 C350,690 366,722 378,748 L622,748 C634,722 650,690 660,650 C670,610 672,560 656,522 C630,496 570,482 534,476 L466,476 C430,482 370,496 344,522 Z`;
  let tucks = '';
  for (let y = 560; y <= 690; y += 13) tucks += `M360,${y} C420,${y + 4} 580,${y + 4} 640,${y} `;
  const collarL = `M500,492 L458,466 C446,478 440,500 444,524 L488,512 Z`;
  return `<clipPath id="lorTorsoClip"><path d="${t}"/></clipPath>
    <path d="${t}" fill="url(#pinkGrad)"/>
    <g clip-path="url(#lorTorsoClip)">
      <path d="${tucks}" fill="none" stroke="${P.pinkDeep}" stroke-width="1.6" opacity="0.45"/>
      <path d="${tucks}" transform="translate(0,3)" fill="none" stroke="#ffffff" stroke-width="1.4" opacity="0.4"/>
      <path d="M392,600 C420,640 470,650 496,632" stroke="${P.pinkShade}" stroke-width="10" fill="none" opacity="0.55" filter="url(#blur4)"/>
      <path d="M640,520 C660,600 655,700 625,760 L700,760 L700,500 Z" fill="${P.pinkDeep}" opacity="0.35" filter="url(#blur8)"/>
      <path d="M500,520 L500,750" stroke="${P.pinkDeep}" stroke-width="1.5" opacity="0.6"/>
      ${[700, 732].map((y) => `<circle cx="505" cy="${y}" r="3.8" fill="#fbe6ea" stroke="${P.pinkDeep}" stroke-width="1"/>`).join('')}
    </g>
    <path d="${t}" fill="none" stroke="${P.pinkLine}" stroke-width="1.8"/>
    <!-- collar -->
    <path d="${collarL}" fill="url(#pinkGrad)" stroke="${P.pinkLine}" stroke-width="1.6"/>
    <path d="${collarL}" transform="translate(1000,0) scale(-1,1)" fill="url(#pinkGrad)" stroke="${P.pinkLine}" stroke-width="1.6"/>`;
}
function bow(sway) {
  const s = sway * 6;
  return `<g stroke="${P.pinkLine}" stroke-width="1.5" stroke-linejoin="round">
    <path d="M492,506 C484,560 ${f(470 + s)},610 ${f(462 + s)},654 L${f(478 + s)},660 C${f(486 + s)},612 498,560 502,512 Z" fill="${P.pink}"/>
    <path d="M508,506 C516,556 ${f(530 + s)},604 ${f(540 + s)},646 L${f(524 + s)},652 C${f(516 + s)},606 504,556 498,512 Z" fill="${P.pinkShade}"/>
    <path d="M498,500 C480,480 450,478 444,496 C440,512 466,520 496,508 Z" fill="url(#pinkGrad)"/>
    <path d="M502,500 C520,480 550,478 556,496 C560,512 534,520 504,508 Z" fill="url(#pinkGrad)"/>
    <ellipse cx="500" cy="505" rx="9" ry="8" fill="${P.pink}"/>
  </g>
  <path d="M452,494 C460,488 478,490 490,500" stroke="#fff" stroke-width="2" fill="none" opacity="0.6"/>`;
}
function belt() {
  return `<path d="M376,742 C440,752 560,752 624,742 L626,800 C560,810 440,810 374,800 Z" fill="url(#blackGrad)" stroke="#000" stroke-width="1.6"/>
    <path d="M378,750 C440,760 560,760 622,750" stroke="#4a4752" stroke-width="1" fill="none" stroke-dasharray="3 3"/>
    <path d="M378,792 C440,802 560,802 622,792" stroke="#4a4752" stroke-width="1" fill="none" stroke-dasharray="3 3"/>
    <rect x="474" y="752" width="52" height="42" rx="4" fill="none" stroke="url(#silverGrad)" stroke-width="5"/>
    <rect x="497" y="752" width="5" height="42" fill="url(#silverGrad)"/>`;
}
let SKIRT = null;
function skirtStatic() {
  if (SKIRT) return SKIRT;
  const W0 = 800, HEM = 1690;
  const hw = (y) => y < 900 ? lerp(124, 170, ease((y - W0) / 100)) : lerp(170, 272, (y - 900) / (HEM - 900));
  const left = [], right = [];
  for (let y = W0; y <= HEM; y += 30) { left.push([CX - hw(y), y]); right.unshift([CX + hw(y), y]); }
  const hem = []; for (let x = CX - 272; x <= CX + 272; x += 17) hem.push([x, HEM + Math.sin((x - CX) / 272 * Math.PI * 7) * 7 + 4]);
  const outline = smooth([...left, ...hem, ...right], true, 0.9);
  let folds = '';
  for (let i = 0; i < 11; i++) {
    const u = -0.92 + i * 0.184, xw = CX + u * 120, xh = CX + u * 268;
    folds += `<path d="M${f(xw - 3)},${W0} Q${f(lerp(xw, xh, 0.5) - 10)},1250 ${f(xh - 20)},${HEM + 14} L${f(xh + 20)},${HEM + 14} Q${f(lerp(xw, xh, 0.5) + 10)},1250 ${f(xw + 3)},${W0} Z" fill="#000" opacity="0.45"/>`;
    folds += `<path d="M${f(xw + 14)},${W0} Q${f(lerp(xw, xh, 0.5) + 14)},1250 ${f(xh + 28)},${HEM + 14} L${f(xh + 36)},${HEM + 14} Q${f(lerp(xw, xh, 0.5) + 18)},1250 ${f(xw + 16)},${W0} Z" fill="#6a6773" opacity="0.28"/>`;
  }
  SKIRT = `<clipPath id="lorSkirtClip"><path d="${outline}"/></clipPath>
    <path d="${outline}" fill="url(#blackSkirt)"/>
    <g clip-path="url(#lorSkirtClip)" filter="url(#blur2)">${folds}</g>
    <path d="${outline}" fill="none" stroke="#000" stroke-width="2.2"/>`;
  return SKIRT;
}
function legsShoes(pz) {
  const lift = (side) => pz.walkAmp ? Math.max(0, Math.sin(pz.walk + (side ? Math.PI : 0))) * 22 * pz.walkAmp : 0;
  const leg = (cx) => `<path d="M${cx - 25},1680 C${cx - 26},1710 ${cx - 21},1740 ${cx - 16},1770 L${cx + 16},1770 C${cx + 20},1740 ${cx + 25},1710 ${cx + 24},1680 Z" fill="url(#loreenLimbV)" stroke="${sk.skinLine}" stroke-width="1.5"/>`;
  const shoe = (cx, rot) => `<g transform="rotate(${rot} ${cx} 1800)">
    <path d="M${cx - 44},1808 C${cx - 46},1840 ${cx - 28},1858 ${cx},1858 C${cx + 28},1858 ${cx + 46},1840 ${cx + 44},1808 Z" fill="#f4f4f2" stroke="#9c9ca4" stroke-width="1.6"/>
    <path d="M${cx - 42},1842 C${cx - 20},1852 ${cx + 20},1852 ${cx + 42},1842" fill="none" stroke="#b7b7bd" stroke-width="1.4"/>
    <path d="M${cx - 20},1760 C${cx - 34},1770 ${cx - 42},1792 ${cx - 41},1816 C${cx - 30},1828 ${cx + 30},1828 ${cx + 41},1816 C${cx + 42},1792 ${cx + 34},1770 ${cx + 20},1760 C${cx + 8},1767 ${cx - 8},1767 ${cx - 20},1760 Z" fill="url(#blackGrad)" stroke="#000" stroke-width="1.8"/>
    <path d="M${cx - 16},1770 C${cx - 6},1776 ${cx + 6},1776 ${cx + 16},1770" stroke="#55525c" stroke-width="2" fill="none"/>
    <text x="${cx - 30}" y="1812" font-family="Arial Black, Arial" font-weight="900" font-size="15" fill="#fff" transform="rotate(-8 ${cx - 30} 1812)">38</text>
    <ellipse cx="${cx + 12}" cy="1794" rx="10" ry="5" fill="#fff" opacity="0.18" filter="url(#blur2)"/></g>`;
  const l1 = lift(0), l2 = lift(1);
  return `<g transform="translate(0,${f(-l1)})">${leg(456)}${shoe(452, 5)}</g><g transform="translate(0,${f(-l2)})">${leg(544)}${shoe(548, -5)}</g>`;
}
function handbag(angle) {
  // hangs from the grip point, counter-rotated so it stays vertical
  return `<g transform="translate(-2,62) rotate(${f(-angle)})">
    <path d="M-36,0 C-38,-14 -22,-20 -14,-6 M36,0 C38,-14 22,-20 14,-6" fill="none" stroke="#141215" stroke-width="5" stroke-linecap="round"/>
    <path d="M-48,40 C-40,6 -20,-2 -12,-4 L12,-4 C20,-2 40,6 48,40" fill="none" stroke="#141215" stroke-width="6" stroke-linecap="round"/>
    <circle cx="-44" cy="38" r="5" fill="none" stroke="url(#goldGrad)" stroke-width="3"/><circle cx="44" cy="38" r="5" fill="none" stroke="url(#goldGrad)" stroke-width="3"/>
    <path d="M-74,44 C-78,80 -76,130 -70,156 C-30,166 30,166 70,156 C76,130 78,80 74,44 C30,36 -30,36 -74,44 Z" fill="url(#pPlaid)" stroke="#141215" stroke-width="3"/>
    <path d="M-74,44 C-30,36 30,36 74,44 L75,60 C30,52 -30,52 -75,60 Z" fill="#1a181c"/>
    <path d="M-73,82 C-30,76 30,76 73,82 L73,96 C30,90 -30,90 -73,96 Z" fill="#1a181c"/><path d="M-73,87 C-30,82 30,82 73,87" stroke="#fff" stroke-width="1.5" fill="none" opacity="0.8"/>
    <circle cx="0" cy="88" r="7" fill="url(#goldGrad)" stroke="#8a6a20" stroke-width="1"/>
    <path d="M-70,150 C-30,160 30,160 70,150" stroke="#141215" stroke-width="5" fill="none"/>
    <path d="M-74,44 C-78,80 -76,130 -70,156 C-30,166 30,166 70,156 C76,130 78,80 74,44" fill="#000" opacity="0.18"/>
    <path d="M-60,64 L-60,140" stroke="#fff" stroke-width="8" opacity="0.18" filter="url(#blur2)"/>
  </g>`;
}
function watch() {
  return `<g transform="translate(0,-14)"><path d="M-22,-6 C-10,0 10,0 22,-6 L22,6 C10,12 -10,12 -22,6 Z" fill="#1a181c"/>
    <circle cx="-4" cy="3" r="10.5" fill="url(#goldGrad)" stroke="#8a6a20" stroke-width="1"/><circle cx="-4" cy="3" r="8" fill="url(#watchFace)"/>
    <path d="M-4,3 L-4,-3 M-4,3 L0,5" stroke="#555" stroke-width="1.2" stroke-linecap="round"/></g>`;
}
const ARM = {
  shoulder: [350, 524], len1: 252, len2: 240, handOffset: -4,
  upper: { fill: 'url(#pinkSleeve)', stroke: P.pinkLine, wfn: (t) => t < 0.3 ? lerp(78, 62, ease(t / 0.3)) : lerp(62, 56, (t - 0.3) / 0.7) },
  fore: { fill: 'url(#pinkSleeve)', stroke: P.pinkLine, from: -0.04, to: 0.9, gathers: 5, wfn: (t) => t < 0.75 ? lerp(58, 62, t) : lerp(62, 54, (t - 0.75) / 0.25) },
  cuff: { from: 0.86, to: 0.99, w: 54, fill: P.pink, stroke: P.pinkLine, button: '#fbe6ea' },
};

function draw(p, opt = {}) {
  const pz = R.pose(p);
  const sway = pz.skirtSway + (pz.walkAmp ? Math.sin(pz.walk) * 2.2 * pz.walkAmp : 0);
  const bagAng = pz.armR.a + pz.armR.e + (pz.walkAmp ? Math.sin(pz.walk) * 10 * pz.walkAmp : 0);
  const A = R.arms(ARM, pz, sk, 'loreen', { R: opt.noBag ? {} : { inHand: handbag(bagAng) }, L: { wrist: watch() } });
  if (opt.joints) { opt.joints.R = A.jR; opt.joints.L = A.jL; opt.joints.k = 1.045; }
  const breathe = 1 + Math.sin(pz.breathe * 2 * Math.PI / 3.4) * 0.006;
  const head = R.headGroup(pz, `
    <g transform="translate(${f(pz.turn * 4)},0)"><path d="${FACE_SHAPE}" fill="url(#loreenFace)" stroke="${sk.skinLine}" stroke-width="1.3"/></g>
    <clipPath id="loreenFaceClip"><path d="${FACE_SHAPE}"/></clipPath>
    <g clip-path="url(#loreenFaceClip)"><path d="M578,250 C590,300 584,350 558,394" stroke="${sk.skinShade}" stroke-width="18" fill="none" opacity="0.5" filter="url(#blur8)"/></g>
    ${earsPearls(pz.turn)}
    ${R.features('loreen', faceStyle, pz)}
    ${turban(pz.turn)}`);
  const inner = `
    ${pz.sit ? '' : R.groundShadow(250) + legsShoes(pz) + `<g transform="translate(500,800) skewX(${f(sway)}) translate(-500,-800)">${skirtStatic()}</g>`}
    ${neck()}
    <g transform="translate(500,780) scale(1,${breathe.toFixed(4)}) translate(-500,-780)">${torso()}${belt()}</g>
    ${A.R}${A.L}
    ${bow(sway * 0.3 + Math.sin(pz.breathe * 1.7) * 0.2)}
    ${head}`;
  // Loreen is slightly taller
  return R.place(pz, `<g transform="translate(500,1850) scale(1.045) translate(-500,-1850)">${inner}</g>`, opt.tag || 'loreen');
}
module.exports = { draw, faceStyle, ARM };
