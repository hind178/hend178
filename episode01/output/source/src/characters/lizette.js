// LIZETTE — black cap, long wavy brown hair with caramel highlights, off-shoulder black polka-dot top,
// black choker, silver hoops, white skinny jeans, black backpack, floral sandals.
const { f, lerp, ease, smooth, clamp } = require('../lib/util');
const { P } = require('../lib/defs');
const R = require('./rig');
const sk = P.lizette;
const CX = 500;

const FACE_SHAPE = `M405,236 C398,290 404,342 422,374 C442,404 472,420 500,421 C528,420 558,404 578,374 C596,342 602,290 595,236 C588,214 412,214 405,236 Z`;
const faceStyle = {
  ...sk, iris: 'irisDark', irisR: 14.6, sx: 1.1, sy: 1.08, wing: 3, lashes: 6, lashW: 1.25,
  brow: '#3e2416', arch: 2, thick: 2.5, lip: 'lipLizette', lipDeep: '#c86a5e', freckles: false, eyeGap: 45, eyeY: 302, mouthY: 380,
};

function wavy(pts, amp, freq, phase = 0) {
  // offset a polyline sideways with a gentle wave (for natural hair waves)
  return pts.map(([x, y], i) => [x + Math.sin(y / freq + phase) * amp * Math.min(1, Math.max(0, (y - 330) / 160)), y]);
}
function hairBack(sway) {
  const s = sway * 10;
  const left = [], right = [];
  for (let y = 240; y <= 740; y += 25) {
    const k = (y - 240) / 500;
    left.push([352 - Math.sin(k * Math.PI * 0.9) * 46 + s * k, y]);
    right.unshift([648 + Math.sin(k * Math.PI * 0.9) * 46 + s * k, y]);
  }
  const L = wavy(left, 10, 38), Rr = wavy(right, 10, 38, 1.4);
  const bottom = [[620 + s, 772], [560 + s, 750], [500 + s, 772], [440 + s, 752], [380 + s, 774]];
  const d = smooth([[500, 150], [420, 160], [364, 205], ...L, ...bottom.reverse().reverse(), ...Rr, [636, 205], [580, 160]].map((p, i, a) => p), true, 0.85);
  return `<path d="${d}" fill="url(#hairGrad)"/><path d="${d}" fill="url(#pHairStrands)" opacity="0.4"/>
    <path d="${d}" fill="none" stroke="${P.hairDeep}" stroke-width="2"/>`;
}
function hairFront(sway, turn) {
  const s = sway * 8, t = turn * 4;
  // locks falling over the shoulders in front of the chest, wavy edges
  const lock = (m) => {
    const X = (x) => m ? 1000 - x : x;
    const outer = [], inner = [];
    for (let y = 240; y <= 700; y += 20) {
      const k = (y - 240) / 460, w = 20 + Math.sin(k * Math.PI) * 16 - k * 6;
      const cx = 395 - k * 16 + Math.sin(y / 34 + (m ? 1.2 : 0)) * 9 * Math.min(1, k * 2.5) + s * k;
      outer.push([X(cx - w * 0.55) + t, y]); inner.unshift([X(cx + w * 0.55) + t, y]);
    }
    return smooth([...outer, [X(380) + s + t, 718], ...inner], true, 0.9);
  };
  const lockL = lock(false), lockR = lock(true);
  const hi = (d) => `<path d="${d}" fill="url(#hairSide)"/><path d="${d}" fill="url(#pHairStrands)" opacity="0.45"/><path d="${d}" fill="none" stroke="${P.hairDeep}" stroke-width="1.6"/>`;
  return `${hi(lockL)}${hi(lockR)}
    <g fill="none" stroke="${P.hairHi}" stroke-width="3" opacity="0.55" stroke-linecap="round" filter="url(#blur1)">
      <path d="M${f(410 + t)},300 C404,380 418,450 ${f(400 + s)},560"/><path d="M${f(590 + t)},300 C596,380 582,450 ${f(600 + s)},560"/>
      <path d="M${f(420 + s)},560 C${f(410 + s)},610 ${f(402 + s)},650 ${f(392 + s)},688"/><path d="M${f(580 + s)},560 C${f(590 + s)},610 ${f(598 + s)},650 ${f(608 + s)},688"/>
    </g>
    <!-- side-swept fringe under the brim -->
    <path d="M${f(430 + t)},236 C${f(450 + t)},262 ${f(470 + t)},268 ${f(500 + t)},262 C${f(470 + t)},270 ${f(446 + t)},282 ${f(424 + t)},300 Z" fill="url(#hairSide)" stroke="${P.hairDeep}" stroke-width="1.2"/>`;
}
function cap(turn) {
  const t = turn * 6;
  return `
    <path d="M384,232 C380,160 430,118 500,118 C570,118 620,160 616,232 C580,222 420,222 384,232 Z" fill="url(#capCrown)" stroke="#000" stroke-width="2"/>
    <path d="M500,120 L500,226 M440,128 C428,160 422,196 424,226 M560,128 C572,160 578,196 576,226" stroke="#3d3b44" stroke-width="1.5" fill="none"/>
    <circle cx="500" cy="122" r="6" fill="#2a2830" stroke="#000"/>
    <!-- custom white emblem (not a brand) -->
    <g transform="translate(${f(500 + t * 0.3)},178)" fill="none" stroke="#f4f4f6" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M-30,6 C-20,-12 -8,-12 0,2 C8,16 20,16 30,-2"/><path d="M-22,14 L22,14" stroke-width="3"/>
    </g>
    <!-- brim, angled slightly -->
    <path d="M${f(370 + t)},230 C${f(400 + t)},214 ${f(600 + t)},214 ${f(632 + t)},232 C${f(640 + t)},246 ${f(610 + t)},262 ${f(500 + t)},264 C${f(392 + t)},262 ${f(362 + t)},246 ${f(370 + t)},230 Z" fill="#1d1c22" stroke="#000" stroke-width="2"/>
    <path d="M${f(384 + t)},248 C${f(430 + t)},258 ${f(570 + t)},258 ${f(618 + t)},248" stroke="#3e3c45" stroke-width="2" fill="none"/>
    <path d="M${f(392 + t)},236 C${f(440 + t)},226 ${f(560 + t)},226 ${f(610 + t)},236" stroke="#55535e" stroke-width="2.5" fill="none" opacity="0.8"/>`;
}
function neckShoulders() {
  // neck, bare shoulders & collarbones down to the elastic neckline
  return `<path d="M468,384 L466,470 C440,486 380,494 344,506 C330,512 322,530 324,560 L676,560 C678,530 670,512 656,506 C620,494 560,486 534,470 L532,384 Z" fill="url(#lizetteNeck)" stroke="${sk.skinLine}" stroke-width="1.4"/>
    <path d="M468,410 C485,430 515,430 532,410 L532,438 C515,448 485,448 468,438 Z" fill="${sk.skinDeep}" opacity="0.4" filter="url(#blur2)"/>
    <path d="M420,512 C445,506 470,508 488,514 M580,512 C555,506 530,508 512,514" stroke="${sk.skinShade}" stroke-width="2.4" fill="none" opacity="0.7"/>
    <path d="M410,520 C440,516 470,518 490,524 M590,520 C560,516 530,518 510,524" stroke="#fff" stroke-width="2" fill="none" opacity="0.45"/>
    <path d="M466,446 C480,455 520,455 534,446 L534,462 C520,471 480,471 466,462 Z" fill="#141317" stroke="#000" stroke-width="1"/>`;
}
function hoops(turn) {
  return `${turn < 0.5 ? `<circle cx="402" cy="372" r="10" fill="none" stroke="url(#silverGrad)" stroke-width="2.6"/>` : ''}${turn > -0.5 ? `<circle cx="598" cy="372" r="10" fill="none" stroke="url(#silverGrad)" stroke-width="2.6"/>` : ''}`;
}
function top() {
  const t = `M318,552 C380,566 620,566 682,552 C690,600 684,660 676,720 C672,780 680,830 690,872 C620,892 380,892 310,872 C320,830 328,780 324,720 C316,660 310,600 318,552 Z`;
  let ruffle = '';
  for (let x = 322; x < 680; x += 16) ruffle += `<path d="M${x},${f(556 + Math.sin((x - 500) / 180) * 2)} q8,-9 16,0" fill="${P.dot}" stroke="#000" stroke-width="1"/>`;
  return `<clipPath id="lizTopClip"><path d="${t}"/></clipPath>
    <path d="${t}" fill="url(#pPolka)"/>
    <g clip-path="url(#lizTopClip)">
      <path d="M300,540 L700,540 L700,600 C600,590 400,590 300,600 Z" fill="#000" opacity="0.25" filter="url(#blur4)"/>
      <g fill="none" stroke="#000" stroke-width="6" opacity="0.4" filter="url(#blur4)"><path d="M420,620 C426,700 418,800 430,880"/><path d="M560,630 C566,720 572,800 566,880"/><path d="M640,600 C650,700 650,800 664,880"/></g>
      <g fill="none" stroke="#fff" stroke-width="5" opacity="0.12" filter="url(#blur4)"><path d="M380,600 C390,700 380,800 392,880"/><path d="M490,640 C496,720 492,800 500,880"/></g>
      <path d="M640,560 C670,640 670,780 690,880 L720,880 L720,540 Z" fill="#000" opacity="0.35" filter="url(#blur8)"/>
    </g>
    <path d="${t}" fill="none" stroke="#000" stroke-width="2"/>
    ${ruffle}
    <path d="M318,552 C380,566 620,566 682,552" stroke="#2c2a30" stroke-width="2" fill="none"/>`;
}
function jeans(pz) {
  const lift = (side) => pz.walkAmp ? Math.max(0, Math.sin(pz.walk + (side ? Math.PI : 0))) * 24 * pz.walkAmp : 0;
  const leg = (m, l) => {
    const X = (x) => m ? 1000 - x : x;
    const d = `M${X(378)},850 C${X(362)},960 ${X(380)},1110 ${X(404)},1250 C${X(416)},1400 ${X(426)},1560 ${X(430)},1736 L${X(482)},1736 C${X(484)},1560 ${X(490)},1400 ${X(496)},1250 C${X(502)},1120 ${X(506)},990 ${X(504)},880 Z`;
    const knee = `M${X(410)},1250 C${X(440)},1258 ${X(470)},1258 ${X(494)},1250`;
    const sandal = sandalFoot(X(456), m ? -4 : 4);
    return `<g transform="translate(0,${f(-l)})">
      <path d="${d}" fill="url(#denimGrad)" stroke="${P.denimDeep}" stroke-width="1.8"/>
      <path d="${knee}" stroke="${P.denimShade}" stroke-width="3" fill="none" opacity="0.9"/>
      <path d="M${X(452)},900 C${X(450)},1050 ${X(456)},1180 ${X(462)},1300" stroke="#fff" stroke-width="10" fill="none" opacity="0.6" filter="url(#blur4)"/>
      <path d="M${X(430)},1716 L${X(482)},1716 L${X(483)},1742 L${X(429)},1742 Z" fill="#fbfbfa" stroke="${P.denimDeep}" stroke-width="1.5"/>
      ${sandal}</g>`;
  };
  return leg(false, lift(0)) + leg(true, lift(1)) +
    `<path d="M378,850 C450,860 550,860 622,850 L618,904 C560,924 440,924 382,904 Z" fill="url(#denimGrad)" stroke="${P.denimDeep}" stroke-width="1.6"/>`;
}
function sandalFoot(cx, rot) {
  const flower = (x, y) => `<g transform="translate(${x},${y})">${[0, 72, 144, 216, 288].map((a) => `<ellipse rx="3.2" ry="5.5" transform="rotate(${a}) translate(0,-4)" fill="#fbfaf6" stroke="#cfc7b8" stroke-width="0.5"/>`).join('')}<circle r="2.3" fill="#e9c35a"/></g>`;
  return `<g transform="rotate(${rot} ${cx} 1800)">
    <path d="M${cx - 30},1828 C${cx - 33},1846 ${cx - 18},1856 ${cx},1856 C${cx + 18},1856 ${cx + 33},1846 ${cx + 30},1828 Z" fill="${P.sandal}" stroke="${P.sandalDeep}" stroke-width="1.5"/>
    <path d="M${cx - 16},1740 C${cx - 24},1770 ${cx - 28},1810 ${cx - 24},1838 C${cx - 12},1848 ${cx + 12},1848 ${cx + 24},1838 C${cx + 28},1810 ${cx + 24},1770 ${cx + 16},1740 Z" fill="url(#lizetteLimbV)" stroke="${sk.skinLine}" stroke-width="1.4"/>
    <g fill="#fbe0d4" stroke="${sk.skinShade}" stroke-width="0.6">${[-16, -8, 0, 8, 16].map((x, i) => `<ellipse cx="${cx + x}" cy="${1838 - Math.abs(x) * 0.2}" rx="${i === 0 ? 4.5 : 3.6}" ry="3.2"/>`).join('')}</g>
    <path d="M${cx - 26},1806 C${cx - 10},1798 ${cx + 10},1798 ${cx + 26},1806 L${cx + 26},1818 C${cx + 10},1810 ${cx - 10},1810 ${cx - 26},1818 Z" fill="${P.sandal}" stroke="${P.sandalDeep}" stroke-width="1.2"/>
    ${flower(cx - 12, 1806)}${flower(cx + 2, 1804)}${flower(cx + 15, 1808)}
    <path d="M${cx - 18},1772 C${cx - 6},1778 ${cx + 6},1778 ${cx + 18},1772" stroke="${P.sandal}" stroke-width="4" fill="none"/>
  </g>`;
}
function backpack(sway) {
  return `<g transform="rotate(${f(sway * 2)} 350 520)">
    <path d="M300,770 C292,820 292,900 300,960 C330,972 380,972 404,962 C412,900 412,820 404,770 C380,756 324,756 300,770 Z" fill="url(#packGrad)" stroke="#000" stroke-width="2"/>
    <path d="M306,800 C330,792 376,792 398,800 L398,860 C376,866 330,866 306,860 Z" fill="#232227" stroke="#000" stroke-width="1.5"/>
    <rect x="344" y="852" width="16" height="22" rx="2" fill="url(#silverGrad)"/>
    <path d="M318,900 L386,900" stroke="#3d3b44" stroke-width="2" stroke-dasharray="3 3"/>
    <path d="M330,770 C326,700 334,600 352,520" stroke="#141317" stroke-width="13" fill="none" stroke-linecap="round"/>
  </g>`;
}
function watch() {
  return `<g transform="translate(0,-14)"><path d="M-21,-6 C-10,0 10,0 21,-6 L21,6 C10,12 -10,12 -21,6 Z" fill="url(#silverGrad)" stroke="${P.silverDeep}" stroke-width="1"/>
    <circle cx="-4" cy="3" r="10" fill="url(#silverGrad)" stroke="${P.silverDeep}" stroke-width="1"/><circle cx="-4" cy="3" r="7.6" fill="url(#watchFace)"/>
    <path d="M-4,3 L-4,-2 M-4,3 L0,5" stroke="#555" stroke-width="1.1" stroke-linecap="round"/></g>`;
}
const ARM = {
  shoulder: [348, 528], len1: 246, len2: 232, handOffset: -4,
  skinUpper: [66, 56], skinFore: [52, 44],
  upper: { fill: 'url(#pPolka)', stroke: '#000', from: 0.12, to: 1.06, wfn: (t) => lerp(78, 100, Math.sin(t * Math.PI * 0.6)) },
  fore: { fill: 'url(#pPolka)', stroke: '#000', from: -0.08, to: 0.4, gathers: 4, wfn: (t) => t < 0.7 ? lerp(98, 90, t) : lerp(90, 56, (t - 0.7) / 0.3) },
};

function draw(p, opt = {}) {
  const pz = R.pose(p);
  const sway = pz.skirtSway + (pz.walkAmp ? Math.sin(pz.walk) * 2.2 * pz.walkAmp : 0);
  const A = R.arms(ARM, pz, sk, 'lizette', { L: { wrist: watch() } });
  if (opt.joints) { opt.joints.R = A.jR; opt.joints.L = A.jL; opt.joints.k = 0.99; }
  const breathe = 1 + Math.sin(pz.breathe * 2 * Math.PI / 3.2) * 0.007;
  const head = R.headGroup(pz, `
    <g transform="translate(${f(pz.turn * 4)},0)"><path d="${FACE_SHAPE}" fill="url(#lizetteFace)" stroke="${sk.skinLine}" stroke-width="1.3"/></g>
    <clipPath id="lizetteFaceClip"><path d="${FACE_SHAPE}"/></clipPath>
    <g clip-path="url(#lizetteFaceClip)"><path d="M582,250 C594,300 586,350 560,398" stroke="${sk.skinShade}" stroke-width="18" fill="none" opacity="0.5" filter="url(#blur8)"/>
      <path d="M400,250 C460,240 540,240 600,250 L600,275 C540,262 460,262 400,275 Z" fill="#3a2418" opacity="0.35" filter="url(#blur4)"/></g>
    ${R.features('lizette', faceStyle, pz)}
    ${hoops(pz.turn)}
    ${hairFront(sway * 0.3, pz.turn)}
    ${cap(pz.turn)}`);
  const inner = `
    ${R.headGroup(pz, hairBack(sway * 0.3))}
    ${pz.sit ? '' : R.groundShadow(230) + jeans(pz)}
    ${neckShoulders()}
    <g transform="translate(500,800) scale(1.07,${breathe.toFixed(4)}) translate(-500,-800)">${top()}</g>
    ${opt.noPack ? '' : backpack(sway * 0.2)}
    ${A.R}${A.L}
    ${head}`;
  return R.place(pz, `<g transform="translate(500,1850) scale(0.99) translate(-500,-1850)">${inner}</g>`, opt.tag || 'lizette');
}
module.exports = { draw, faceStyle, ARM };
