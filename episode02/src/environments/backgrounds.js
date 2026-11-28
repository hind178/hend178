// Painted environment backdrops (vector), rendered once to PNG and cached.
// Canvas: 1350 x 2400 (frame 1080x1920 sits at offset 135,240 at zoom 1, leaving camera headroom).
const { f, lerp, mkRng, smooth } = require('../lib/util');
const BW = 1350, BH = 2400;

const common = `
  <filter id="bgBlur2"><feGaussianBlur stdDeviation="2"/></filter>
  <filter id="bgBlur6" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="bgBlur20" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="20"/></filter>
  <filter id="bgBlur40" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
  <filter id="paper" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="3" seed="2"/>
    <feColorMatrix type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.28  0 0 0 0 0.2  0 0 0 0.09 0"/></filter>
  <filter id="leafy" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="3" seed="5" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="26"/></filter>`;

const lg = (id, stops, x2 = 0, y2 = 1) => `<linearGradient id="${id}" x1="0" y1="0" x2="${x2}" y2="${y2}">${stops.map(([o, c, a = 1]) => `<stop offset="${o}" stop-color="${c}" stop-opacity="${a}"/>`).join('')}</linearGradient>`;
const rg = (id, stops, cx = 0.5, cy = 0.5, r = 0.5) => `<radialGradient id="${id}" cx="${cx}" cy="${cy}" r="${r}">${stops.map(([o, c, a = 1]) => `<stop offset="${o}" stop-color="${c}" stop-opacity="${a}"/>`).join('')}</radialGradient>`;

/* ------------------------------------------------ shared props */
function tree(x, y, s, seed, tint = 0) {
  const r = mkRng(seed);
  let blobs = '';
  const cols = tint ? ['#5f7d3c', '#77964a', '#8fae5a', '#4b6830'] : ['#4f7536', '#668d43', '#86ab55', '#3d5d2a'];
  for (let i = 0; i < 26; i++) {
    const a = r() * Math.PI * 2, d = Math.sqrt(r()) * 120;
    const cx = Math.cos(a) * d * 1.1, cy = Math.sin(a) * d * 0.85 - 40;
    const c = cols[Math.floor(r() * 3)];
    blobs += `<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(40 + r() * 40)}" fill="${c}"/>`;
  }
  let hl = '';
  for (let i = 0; i < 10; i++) { const a = -2.2 + r() * 1.4, d = 60 + r() * 70; hl += `<circle cx="${f(Math.cos(a) * d)}" cy="${f(Math.sin(a) * d * 0.8 - 40)}" r="${f(20 + r() * 22)}" fill="#b7cf78" opacity="0.55"/>`; }
  return `<g transform="translate(${x},${y}) scale(${s})">
    <path d="M-14,0 C-10,-80 -16,-140 -6,-200 L8,-200 C14,-140 10,-80 16,0 Z" fill="#6b4a32"/>
    <path d="M-4,-120 C-30,-150 -50,-170 -70,-180 M4,-140 C30,-170 50,-180 66,-190" stroke="#6b4a32" stroke-width="9" fill="none"/>
    <g transform="translate(0,-230)" filter="url(#leafy)">${blobs}${hl}<circle cx="60" cy="10" r="90" fill="#2c4420" opacity="0.25"/></g>
  </g>`;
}
function palm(x, y, s) {
  let fronds = '';
  for (let i = 0; i < 9; i++) {
    const a = -170 + i * 20;
    fronds += `<path d="M0,0 C40,-30 110,-30 170,10 C110,-10 50,-6 0,8 Z" fill="${i % 2 ? '#5d8a3c' : '#4a7430'}" transform="rotate(${a + 90})"/>`;
  }
  return `<g transform="translate(${x},${y}) scale(${s})">
    <path d="M-10,0 C-6,-150 6,-300 18,-430 L32,-430 C22,-300 14,-150 12,0 Z" fill="#8a6a48"/>
    ${Array.from({ length: 14 }, (_, i) => `<path d="M${-8 + i * 1.6},${-i * 31} l${20 - i * 0.2},-4" stroke="#6d5136" stroke-width="3"/>`).join('')}
    <g transform="translate(25,-430)">${fronds}</g></g>`;
}
function mountains(y0, cols, seed) {
  const r = mkRng(seed);
  let s = '';
  cols.forEach((c, li) => {
    const pts = [[-50, y0 + 300]];
    let x = -50;
    while (x < BW + 100) { pts.push([x, y0 + li * 70 - r() * (160 - li * 30) - 40]); x += 120 + r() * 140; }
    pts.push([BW + 100, y0 + 300]);
    s += `<path d="${smooth(pts, false, 0.6)} L${BW + 100},${y0 + 500} L-50,${y0 + 500} Z" fill="${c}"/>`;
  });
  return s;
}
function bus(x, y, s, opt = {}) {
  // side view coach, facing right; door near the front
  let win = '';
  for (let i = 0; i < 7; i++) win += `<rect x="${170 + i * 118}" y="70" width="104" height="120" rx="10" fill="url(#busGlass)" stroke="#2b3644" stroke-width="3"/>
      <path d="M${185 + i * 118},84 L${215 + i * 118},84 L${190 + i * 118},176 Z" fill="#fff" opacity="0.18"/>`;
  return `<g transform="translate(${x},${y}) scale(${s})">
    <ellipse cx="560" cy="392" rx="600" ry="26" fill="#000" opacity="0.28" filter="url(#bgBlur6)"/>
    <path d="M30,40 C30,18 46,8 70,8 L1060,8 C1100,8 1120,30 1124,70 L1130,330 C1130,352 1116,366 1094,366 L60,366 C40,366 30,352 30,334 Z" fill="url(#busBody)" stroke="#55606e" stroke-width="3"/>
    <rect x="30" y="230" width="1100" height="26" fill="#2f4fb8"/><rect x="30" y="260" width="1100" height="8" fill="#e0b44f"/>
    ${win}
    <path d="M1000,70 L1100,70 C1110,70 1118,90 1120,120 L1122,200 L1000,200 Z" fill="url(#busGlass)" stroke="#2b3644" stroke-width="3"/>
    <rect x="${opt.doorOpen ? 1004 : 1004}" y="210" width="${opt.doorOpen ? 20 : 0}" height="0"/>
    <rect x="1010" y="${opt.doorOpen ? 70 : 70}" width="0" height="0"/>
    <path d="M60,70 L150,70 L150,200 L60,200 C48,200 44,190 44,170 L44,90 C44,78 50,70 60,70 Z" fill="url(#busGlass)" stroke="#2b3644" stroke-width="3"/>
    <!-- door (front, right side) -->
    ${opt.doorOpen ? `<rect x="1000" y="208" width="90" height="150" fill="#1e2630"/><rect x="1006" y="214" width="78" height="40" fill="#3d4a5a"/>
      <path d="M1000,300 L1090,300 L1090,312 L1000,312 Z M1000,334 L1090,334 L1090,346 L1000,346 Z" fill="#5d6876"/>`
      : `<rect x="1000" y="208" width="90" height="150" fill="url(#busGlass)" stroke="#2b3644" stroke-width="3"/>`}
    <circle cx="230" cy="366" r="56" fill="#1d2127"/><circle cx="230" cy="366" r="28" fill="#9aa3ad"/><circle cx="230" cy="366" r="10" fill="#555"/>
    <circle cx="900" cy="366" r="56" fill="#1d2127"/><circle cx="900" cy="366" r="28" fill="#9aa3ad"/><circle cx="900" cy="366" r="10" fill="#555"/>
    <path d="M160,320 C170,290 290,290 300,320 Z M830,320 C840,290 960,290 970,320 Z" fill="#232a33"/>
    <rect x="1112" y="290" width="22" height="30" rx="4" fill="#ffe7a3"/><rect x="34" y="290" width="14" height="30" rx="4" fill="#d34a3a"/>
    <path d="M70,20 L1050,20" stroke="#fff" stroke-width="4" opacity="0.6"/>
  </g>`;
}
const busDefs = () => lg('busGlass', [[0, '#5b7590'], [0.5, '#30455c'], [1, '#1f2c3a']]) + lg('busBody', [[0, '#ffffff'], [0.6, '#eef1f4'], [1, '#c9d0d8']]);

/* ------------------------------------------------ 1. university exterior */
function university(opt = {}) {
  const r = mkRng(11);
  let windows = '';
  for (let row = 0; row < 3; row++) for (let i = 0; i < 9; i++) {
    const x = 120 + i * 128, y = 730 + row * 150;
    if (x > 560 && x < 760 && row < 3) continue;
    windows += `<rect x="${x}" y="${y}" width="70" height="104" rx="4" fill="url(#winGlass)" stroke="#a98a62" stroke-width="4"/>
      <rect x="${x - 6}" y="${y + 104}" width="82" height="10" fill="#d8c09a"/><path d="M${x + 8},${y + 8} L${x + 30},${y + 8} L${x + 10},${y + 90} Z" fill="#fff" opacity="0.25"/>`;
  }
  let arches = '';
  for (let i = 0; i < 9; i++) {
    const x = 110 + i * 128;
    if (x > 560 && x < 760) continue;
    arches += `<path d="M${x},1330 L${x},1230 C${x},1190 ${x + 90},1190 ${x + 90},1230 L${x + 90},1330 Z" fill="#7a6146" opacity="0.85"/><path d="M${x},1330 L${x},1230 C${x},1190 ${x + 90},1190 ${x + 90},1230 L${x + 90},1330" fill="none" stroke="#c9ab84" stroke-width="6"/>`;
  }
  let tiles = '';
  for (let i = -14; i <= 14; i++) tiles += `<path d="M${675 + i * 30},1380 L${675 + i * 190},2400" stroke="#b9a483" stroke-width="2" opacity="0.5"/>`;
  for (let j = 0; j < 14; j++) { const y = 1380 + Math.pow(j / 14, 1.8) * 1020; tiles += `<path d="M0,${f(y)} L${BW},${f(y)}" stroke="#b9a483" stroke-width="2" opacity="0.45"/>`; }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${BW} ${BH}" width="${BW}" height="${BH}"><defs>${common}${busDefs()}
    ${lg('sky', [[0, '#8fb8e0'], [0.45, '#c9dcec'], [0.75, '#f6e2c6'], [1, '#fbe9d2']])}
    ${rg('sun', [[0, '#fff6dc', 1], [0.3, '#ffe2a8', 0.6], [1, '#ffd38a', 0]], 0.5, 0.5, 0.5)}
    ${lg('stone', [[0, '#efdcbc'], [1, '#d9bf98']])}
    ${lg('winGlass', [[0, '#9cb9cf'], [0.5, '#5f7f99'], [1, '#3f5a70']])}
    ${lg('ground', [[0, '#e2d0b2'], [1, '#c9b089']])}
    ${lg('haze', [[0, '#f6e7d3', 0], [1, '#f6e7d3', 0.85]])}
  </defs>
    <rect width="${BW}" height="1400" fill="url(#sky)"/>
    <circle cx="1080" cy="560" r="420" fill="url(#sun)"/>
    <g opacity="0.9">${mountains(1080, ['#b9b4c8', '#a7a7bd', '#9aa5b2'], 3)}</g>
    <rect y="900" width="${BW}" height="460" fill="url(#haze)"/>
    <!-- building -->
    <rect x="60" y="640" width="1230" height="700" fill="url(#stone)"/>
    <rect x="60" y="640" width="1230" height="700" filter="url(#paper)"/>
    <rect x="40" y="620" width="1270" height="30" fill="#c9ab84"/><rect x="60" y="690" width="1230" height="8" fill="#d6bb92"/>
    ${windows}${arches}
    <!-- central entrance tower -->
    <rect x="560" y="520" width="230" height="820" fill="#ead4ae" stroke="#c9ab84" stroke-width="4"/>
    <path d="M560,520 L675,440 L790,520 Z" fill="#c79f6c"/>
    <path d="M590,1340 L590,1080 C590,960 760,960 760,1080 L760,1340 Z" fill="#5a4632"/>
    <path d="M610,1340 L610,1090 C610,990 740,990 740,1090 L740,1340 Z" fill="url(#winGlass)" opacity="0.8"/>
    <circle cx="675" cy="640" r="54" fill="#f4e5c8" stroke="#b08a5a" stroke-width="6"/>
    <path d="M675,600 L675,640 L700,656" stroke="#6b5036" stroke-width="6" fill="none" stroke-linecap="round"/>
    <rect x="600" y="740" width="150" height="190" rx="70" fill="url(#winGlass)" stroke="#a98a62" stroke-width="5"/>
    <rect x="60" y="1330" width="1230" height="20" fill="#b49470"/>
    <!-- sun-lit edge & shadows -->
    <rect x="60" y="640" width="500" height="700" fill="#fff3dc" opacity="0.12"/>
    <rect x="790" y="640" width="500" height="700" fill="#7a5a3a" opacity="0.1"/>
    <!-- plaza -->
    <rect y="1340" width="${BW}" height="1060" fill="url(#ground)"/>
    ${tiles}
    <rect y="1340" width="${BW}" height="1060" filter="url(#paper)"/>
    <path d="M0,1400 L380,1400 L120,2400 L0,2400 Z" fill="#7da152" opacity="0.85"/>
    <path d="M1350,1400 L970,1400 L1230,2400 L1350,2400 Z" fill="#7da152" opacity="0.85"/>
    <path d="M0,1400 L380,1400" stroke="#b4c98a" stroke-width="6"/>
    ${tree(120, 1420, 1.25, 4)}${palm(330, 1400, 1.1)}${tree(1250, 1430, 1.3, 9)}${palm(1010, 1395, 1.0)}
    ${[260, 1090].map((x) => `<g><rect x="${x - 5}" y="1180" width="10" height="240" fill="#4a4a4f"/><path d="M${x - 24},1180 L${x + 24},1180 L${x + 14},1150 L${x - 14},1150 Z" fill="#3a3a40"/><ellipse cx="${x}" cy="1172" rx="10" ry="6" fill="#fff3c8"/></g>`).join('')}
    ${opt.bus ? bus(560, 1150, 0.74, { doorOpen: true }) : ''}
    ${opt.gate ? `<g><rect x="240" y="900" width="110" height="1180" fill="#d2b48a" stroke="#a48660" stroke-width="5"/><rect x="1000" y="900" width="110" height="1180" fill="#d2b48a" stroke="#a48660" stroke-width="5"/>
      <path d="M220,900 C300,700 1050,700 1130,900 L1130,960 C1050,780 300,780 220,960 Z" fill="#c9a676" stroke="#a48660" stroke-width="5"/>
      <rect x="220" y="880" width="140" height="40" fill="#b8956a"/><rect x="990" y="880" width="140" height="40" fill="#b8956a"/>
      <path d="M560,770 L790,770 L790,830 L560,830 Z" fill="#2f4fb8"/><circle cx="675" cy="800" r="20" fill="#e0b44f"/>
      <rect x="240" y="900" width="40" height="1180" fill="#fff" opacity="0.18"/></g>` : ''}
    <rect width="${BW}" height="${BH}" fill="url(#sun)" opacity="0.25"/>
  </svg>`;
}

/* ------------------------------------------------ 2. institute study room */
function studyRoom() {
  let books = '';
  const r = mkRng(5);
  const cols = ['#8c3b2f', '#2f4f7a', '#b38a3a', '#3f6b4a', '#6d4c7d', '#c9b48a', '#a0522d'];
  for (let sh = 0; sh < 4; sh++) {
    let x = 860;
    while (x < 1280) { const w = 18 + r() * 22, h = 120 + r() * 50; books += `<rect x="${f(x)}" y="${f(700 + sh * 230 - h)}" width="${f(w)}" height="${f(h)}" fill="${cols[Math.floor(r() * cols.length)]}" stroke="#2a1d14" stroke-width="1.5"/>`; x += w + 2; }
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${BW} ${BH}" width="${BW}" height="${BH}"><defs>${common}
    ${lg('wall', [[0, '#efe2cf'], [1, '#e2cfb5']])}${lg('win', [[0, '#cfe4f2'], [1, '#fdf2dc']])}
    ${rg('light', [[0, '#fff2d2', 0.9], [1, '#fff2d2', 0]], 0.3, 0.4, 0.6)}${lg('floor', [[0, '#b38b62'], [1, '#8a6544']])}
  </defs>
    <rect width="${BW}" height="${BH}" fill="url(#wall)"/>
    <rect width="${BW}" height="${BH}" filter="url(#paper)"/>
    <!-- window with daylight -->
    <rect x="90" y="420" width="560" height="800" fill="url(#win)" stroke="#a88b68" stroke-width="16"/>
    <path d="M370,420 L370,1220 M90,820 L650,820" stroke="#a88b68" stroke-width="12"/>
    <g opacity="0.7">${tree(260, 1220, 1.0, 21, 1)}</g>
    <path d="M60,400 C120,600 110,900 60,1260 L0,1260 L0,400 Z" fill="#7a9bc8" opacity="0.9"/>
    <path d="M680,400 C620,600 630,900 680,1260 L740,1260 L740,400 Z" fill="#7a9bc8" opacity="0.9"/>
    <path d="M650,1220 L1100,2400 L-200,2400 L90,1220 Z" fill="#fff4d8" opacity="0.25"/>
    <!-- bookshelf -->
    <rect x="840" y="440" width="460" height="980" fill="#7b5638" stroke="#4d3320" stroke-width="8"/>
    ${[0, 1, 2, 3].map((i) => `<rect x="848" y="${700 + i * 230}" width="444" height="18" fill="#5e3f27"/>`).join('')}
    ${books}
    <!-- certificate-free wall decor: plant + clock -->
    <circle cx="760" cy="330" r="60" fill="#fbf7ef" stroke="#6b5036" stroke-width="8"/><path d="M760,300 L760,330 L782,342" stroke="#333" stroke-width="5" fill="none"/>
    <rect y="1500" width="${BW}" height="900" fill="url(#floor)"/>
    <rect width="${BW}" height="${BH}" fill="url(#light)"/>
  </svg>`;
}

/* ------------------------------------------------ 3. corridor with notice board */
function corridor() {
  const vx = 640, vy = 1180;
  let s = '';
  // floor tiles in perspective
  for (let i = -12; i <= 12; i++) s += `<path d="M${vx + i * 8},${vy + 30} L${vx + i * 160},2400" stroke="#c9bba5" stroke-width="2" opacity="0.6"/>`;
  for (let j = 1; j < 16; j++) { const y = vy + 30 + Math.pow(j / 16, 2) * 1200; s += `<path d="M0,${f(y)} L${BW},${f(y)}" stroke="#c9bba5" stroke-width="2" opacity="0.5"/>`; }
  let wins = '';
  for (let k = 0; k < 4; k++) {
    const t0 = k / 4, t1 = (k + 0.6) / 4;
    const X = (t) => lerp(0, vx - 150, Math.pow(t, 0.7)), T = (t) => lerp(300, vy - 120, Math.pow(t, 0.7)), B = (t) => lerp(1700, vy + 10, Math.pow(t, 0.7));
    wins += `<path d="M${f(X(t0))},${f(T(t0) + 100)} L${f(X(t1))},${f(T(t1) + 60)} L${f(X(t1))},${f(B(t1) - 260)} L${f(X(t0))},${f(B(t0) - 400)} Z" fill="url(#corrWin)" stroke="#b9a37f" stroke-width="6"/>`;
    // light patches on floor
    wins += `<path d="M${f(X(t0) + 60)},${f(B(t0) - 10)} L${f(X(t1) + 120)},${f(B(t1) + 10)} L${f(X(t1) + 420)},${f(B(t1) + 140)} L${f(X(t0) + 520)},${f(B(t0) + 160)} Z" fill="#fff1cf" opacity="0.45" filter="url(#bgBlur6)"/>`;
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${BW} ${BH}" width="${BW}" height="${BH}"><defs>${common}
    ${lg('cw', [[0, '#f1e6d4'], [1, '#e0cfb4']])}${lg('cf', [[0, '#d9cbb2'], [1, '#b8a385']])}${lg('corrWin', [[0, '#d6e8f4'], [1, '#fff3da']])}
    ${lg('board', [[0, '#a7744a'], [1, '#8a5c37']])}
  </defs>
    <rect width="${BW}" height="${BH}" fill="url(#cw)"/>
    <path d="M0,0 L${vx - 150},${vy - 140} L${vx + 150},${vy - 140} L${BW},0 Z" fill="#f7efe2"/>
    <path d="M0,2400 L${vx - 150},${vy + 30} L${vx + 150},${vy + 30} L${BW},2400 Z" fill="url(#cf)"/>
    <path d="M${vx - 150},${vy - 140} L${vx + 150},${vy - 140} L${vx + 150},${vy + 30} L${vx - 150},${vy + 30} Z" fill="#fff3dc"/>
    <path d="M${BW},0 L${vx + 150},${vy - 140} L${vx + 150},${vy + 30} L${BW},2400 Z" fill="#e6d6bd"/>
    ${s}${wins}
    ${[0.25, 0.55].map((t) => { const x = lerp(BW, vx + 150, Math.pow(t, 0.7)), x2 = lerp(BW, vx + 150, Math.pow(t + 0.12, 0.7)), top = lerp(250, vy - 120, Math.pow(t, 0.7)), b = lerp(2200, vy + 20, Math.pow(t, 0.7)), top2 = lerp(250, vy - 120, Math.pow(t + 0.12, 0.7)), b2 = lerp(2200, vy + 20, Math.pow(t + 0.12, 0.7)); return `<path d="M${f(x)},${f(top + 200)} L${f(x2)},${f(top2 + 150)} L${f(x2)},${f(b2)} L${f(x)},${f(b)} Z" fill="#9c7a56" stroke="#6b4d32" stroke-width="5"/>`; }).join('')}
    <!-- ceiling lights -->
    ${[0.15, 0.4, 0.65].map((t) => { const y = lerp(80, vy - 150, Math.pow(t, 0.7)), w = lerp(260, 50, Math.pow(t, 0.7)); return `<rect x="${f(vx - w / 2)}" y="${f(y)}" width="${f(w)}" height="${f(w * 0.12)}" fill="#fffbe9"/>`; }).join('')}
    <!-- notice board (right wall, near) -->
    <g transform="translate(980,700) skewY(14)">
      <rect x="0" y="0" width="330" height="430" fill="url(#board)" stroke="#5b3a20" stroke-width="10"/>
      <rect x="20" y="30" width="130" height="160" fill="#fffdf6" transform="rotate(-3 85 110)"/><rect x="170" y="24" width="140" height="120" fill="#fde9a8" transform="rotate(2 240 84)"/>
      <rect x="40" y="220" width="120" height="150" fill="#d8ecff" transform="rotate(2 100 295)"/>
      ${[[40, 60], [60, 80], [50, 100]].map(([x, y]) => `<rect x="${x}" y="${y}" width="80" height="6" fill="#9a9a9a" transform="rotate(-3 85 110)"/>`).join('')}
      <!-- the trip poster -->
      <g id="tripPoster" transform="translate(180,170) rotate(-2)">
        <rect x="0" y="0" width="140" height="200" fill="#ffffff" stroke="#2f4fb8" stroke-width="5"/>
        <rect x="0" y="0" width="140" height="44" fill="#2f4fb8"/>
        <g transform="translate(14,70) scale(0.1)">${bus(0, 0, 1)}</g>
        <path d="M14,140 L40,112 L62,132 L86,104 L126,140 Z" fill="#7da152"/>
        <rect x="40" y="150" width="60" height="36" rx="4" fill="#fff" stroke="#c0392b" stroke-width="3"/><text x="70" y="180" text-anchor="middle" font-family="Arial" font-weight="700" font-size="28" fill="#c0392b">5</text>
      </g>
      ${[[85, 32], [240, 26], [100, 222], [250, 172]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="7" fill="#d34a3a"/>`).join('')}
    </g>
    <rect width="${BW}" height="${BH}" filter="url(#paper)"/>
  </svg>`;
}

/* ------------------------------------------------ 4. Hind's bedroom */
function bedroom() {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${BW} ${BH}" width="${BW}" height="${BH}"><defs>${common}
    ${lg('bw', [[0, '#e9dccd'], [1, '#d8c5ad']])}${lg('bwin', [[0, '#f9d9a7'], [1, '#f2b98a']])}${lg('bfloor', [[0, '#a57e5b'], [1, '#7d5a3e']])}
    ${rg('lamp', [[0, '#ffe2a8', 0.8], [1, '#ffe2a8', 0]])}
  </defs>
    <rect width="${BW}" height="${BH}" fill="url(#bw)"/><rect width="${BW}" height="${BH}" filter="url(#paper)"/>
    <rect x="800" y="400" width="440" height="700" fill="url(#bwin)" stroke="#9b7a58" stroke-width="16"/>
    <path d="M1020,400 L1020,1100 M800,750 L1240,750" stroke="#9b7a58" stroke-width="10"/>
    <path d="M770,380 C840,600 820,900 770,1140 L730,1140 L730,380 Z" fill="#c98a8a"/><path d="M1270,380 C1200,600 1220,900 1270,1140 L1310,1140 L1310,380 Z" fill="#c98a8a"/>
    <rect y="1480" width="${BW}" height="920" fill="url(#bfloor)"/>
    <!-- bed -->
    <rect x="-40" y="1180" width="760" height="360" rx="20" fill="#f3ede4" stroke="#bfb2a0" stroke-width="5"/>
    <rect x="-40" y="1000" width="60" height="560" fill="#8a6446"/><path d="M-40,1240 C200,1210 500,1220 720,1260 L720,1560 L-40,1560 Z" fill="#9db4d8"/>
    <path d="M-40,1300 C200,1270 500,1280 720,1320" stroke="#7f98c0" stroke-width="5" fill="none"/>
    <ellipse cx="160" cy="1200" rx="140" ry="50" fill="#fbf8f3" stroke="#cfc4b4" stroke-width="4"/>
    <circle cx="1100" cy="300" r="180" fill="url(#lamp)"/>
    <rect width="${BW}" height="${BH}" fill="#ffc98a" opacity="0.08"/>
  </svg>`;
}

/* ------------------------------------------------ 5. classroom */
function classroom() {
  let rows = '';
  for (let k = 3; k >= 0; k--) {
    const y = 1240 + k * 150, sc = 0.55 + k * 0.17;
    for (let i = -2; i <= 2; i++) {
      const x = 675 + i * 330 * sc;
      rows += `<g transform="translate(${f(x)},${f(y)}) scale(${f(sc)})"><rect x="-130" y="0" width="260" height="22" fill="#b98c5f" stroke="#7a5638" stroke-width="3"/><rect x="-120" y="22" width="12" height="120" fill="#555"/><rect x="108" y="22" width="12" height="120" fill="#555"/>
        <rect x="-60" y="-110" width="120" height="100" rx="10" fill="#3f6b9a" opacity="0.9"/></g>`;
    }
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${BW} ${BH}" width="${BW}" height="${BH}"><defs>${common}
    ${lg('cw2', [[0, '#eef0e6'], [1, '#dcdccb']])}${lg('cwin', [[0, '#d6ecf8'], [1, '#fff4dc']])}${lg('cflo', [[0, '#c4b39a'], [1, '#9e8a6c']])}
  </defs>
    <rect width="${BW}" height="${BH}" fill="url(#cw2)"/><rect width="${BW}" height="${BH}" filter="url(#paper)"/>
    <rect x="300" y="520" width="750" height="420" fill="#f9faf7" stroke="#8f979c" stroke-width="14"/>
    <path d="M360,620 C420,600 480,640 540,620 M360,700 L700,700 M360,760 L620,760" stroke="#7f8fae" stroke-width="6" fill="none" opacity="0.6"/>
    <circle cx="860" cy="720" r="80" fill="none" stroke="#c9787a" stroke-width="5" opacity="0.6"/>
    ${[0, 1].map((i) => `<rect x="${40 + i * 1100}" y="460" width="190" height="600" fill="url(#cwin)" stroke="#a7a395" stroke-width="10"/>`).join('')}
    <rect y="1150" width="${BW}" height="1250" fill="url(#cflo)"/>
    ${rows}
    <path d="M40,1060 L700,2400 L-100,2400 Z" fill="#fff4d8" opacity="0.2"/>
  </svg>`;
}

/* ------------------------------------------------ 6. bus interior */
function busInterior() {
  const vx = 675, vy = 1050;
  let seats = '', wins = '';
  for (let k = 6; k >= 0; k--) {
    const t = Math.pow(k / 7, 1.4), sc = lerp(1, 0.22, t);
    for (const side of [-1, 1]) {
      const x = lerp(side < 0 ? 250 : 1100, vx + side * 120, t), y = lerp(1500, vy + 90, t);
      seats += `<g transform="translate(${f(x)},${f(y)}) scale(${f(sc)})">
        <path d="M-150,-420 C-150,-470 150,-470 150,-420 L160,40 L-160,40 Z" fill="url(#seatG)" stroke="#1d2a44" stroke-width="5"/>
        <path d="M-120,-390 L120,-390 L126,-150 L-126,-150 Z" fill="#2c4a86" opacity="0.6"/>
        <rect x="-110" y="-470" width="220" height="70" rx="18" fill="#e9e4da" stroke="#b9b2a5" stroke-width="3"/>
      </g>`;
    }
    const wx0 = lerp(0, vx - 200, t), wy0 = lerp(380, vy - 220, t), wh = lerp(700, 120, t);
    if (k < 6) wins += `<path d="M${f(wx0 + 30 * (1 - t))},${f(wy0)} L${f(lerp(0, vx - 200, Math.pow((k + 0.75) / 7, 1.4)))},${f(lerp(380, vy - 220, Math.pow((k + 0.75) / 7, 1.4)))} L${f(lerp(0, vx - 200, Math.pow((k + 0.75) / 7, 1.4)))},${f(lerp(380, vy - 220, Math.pow((k + 0.75) / 7, 1.4)) + lerp(700, 120, Math.pow((k + 0.75) / 7, 1.4)))} L${f(wx0 + 30 * (1 - t))},${f(wy0 + wh)} Z" fill="url(#bwinG)" stroke="#3a4250" stroke-width="5"/>`;
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${BW} ${BH}" width="${BW}" height="${BH}"><defs>${common}
    ${lg('bwall', [[0, '#d7d5d0'], [1, '#b9b6b0']])}${lg('seatG', [[0, '#3a5ea8'], [1, '#22396b']])}${lg('bwinG', [[0, '#bfe0f5'], [1, '#fff3d6']])}
    ${lg('aisle', [[0, '#7c7a78'], [1, '#55524f']])}
  </defs>
    <rect width="${BW}" height="${BH}" fill="url(#bwall)"/>
    <path d="M0,0 L${vx - 200},${vy - 260} L${vx + 200},${vy - 260} L${BW},0 Z" fill="#ecebe7"/>
    <path d="M0,330 L${vx - 200},${vy - 230} M${BW},330 L${vx + 200},${vy - 230}" stroke="#8d8a85" stroke-width="40"/>
    <path d="M0,360 L${vx - 200},${vy - 220}" stroke="#2f4fb8" stroke-width="10"/>
    ${wins}
    ${wins.replace(/M(-?[\d.]+),/g, (m, x) => `M${f(BW - x)},`).replace(/L(-?[\d.]+),/g, (m, x) => `L${f(BW - x)},`)}
    <path d="M${vx - 200},${vy - 260} L${vx + 200},${vy - 260} L${vx + 200},${vy + 120} L${vx - 200},${vy + 120} Z" fill="#cfd6dd"/>
    <path d="M${vx - 160},${vy - 220} L${vx + 160},${vy - 220} L${vx + 160},${vy - 40} L${vx - 160},${vy - 40} Z" fill="url(#bwinG)" stroke="#3a4250" stroke-width="6"/>
    <path d="M300,2400 L${vx - 60},${vy + 120} L${vx + 60},${vy + 120} L1050,2400 Z" fill="url(#aisle)"/>
    ${seats}
    <rect width="${BW}" height="${BH}" filter="url(#paper)"/>
  </svg>`;
}

/* ------------------------------------------------ 7. mountain road (landscape, bus drawn live) */
function mountainRoad() {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${BW} ${BH}" width="${BW}" height="${BH}"><defs>${common}
    ${lg('msky', [[0, '#7fb0e0'], [0.6, '#cfe2ef'], [1, '#f8e7cd']])}${rg('msun', [[0, '#fff7e0'], [0.4, '#ffe6b0', 0.5], [1, '#ffe6b0', 0]])}
    ${lg('mhaze', [[0, '#eef2f5', 0], [1, '#eef2f5', 0.8]])}
  </defs>
    <rect width="${BW}" height="${BH}" fill="url(#msky)"/>
    <circle cx="300" cy="560" r="380" fill="url(#msun)"/>
    ${mountains(900, ['#a9b7cc', '#8fa4bd'], 7)}
    <rect y="700" width="${BW}" height="500" fill="url(#mhaze)"/>
    ${mountains(1150, ['#7f9a86', '#6b8a64', '#5c7d4c'], 12)}
    <path d="M0,1500 C300,1420 600,1440 900,1380 C1100,1340 1250,1350 1400,1320 L1400,2400 L0,2400 Z" fill="#7a9a52"/>
    <path d="M-50,1640 C300,1560 700,1520 1000,1470 C1150,1446 1300,1440 1420,1430 L1420,1500 C1300,1510 1160,1520 1010,1546 C720,1600 330,1650 -50,1740 Z" fill="#6b6b6e"/>
    <path d="M-50,1690 C300,1606 700,1563 1005,1508 C1150,1483 1300,1474 1420,1466" stroke="#f4f1e6" stroke-width="5" stroke-dasharray="40 30" fill="none"/>
    <path d="M0,1760 C400,1700 800,1650 1400,1560 L1400,2400 L0,2400 Z" fill="#5f8a45"/>
    ${tree(120, 2000, 1.6, 31)}${tree(1220, 1930, 1.4, 33)}${tree(700, 1500, 0.5, 35, 1)}${tree(860, 1470, 0.45, 36, 1)}
  </svg>`;
}

/* ------------------------------------------------ 8. hotel exterior */
function hotelExterior() {
  let win = '';
  for (let r = 0; r < 6; r++) for (let i = 0; i < 6; i++) win += `<rect x="${170 + i * 170}" y="${360 + r * 140}" width="100" height="96" rx="4" fill="url(#hwin)" stroke="#8b7a68" stroke-width="4"/><rect x="${160 + i * 170}" y="${456 + r * 140}" width="120" height="10" fill="#d8cdbf"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${BW} ${BH}" width="${BW}" height="${BH}"><defs>${common}${busDefs()}
    ${lg('hsky', [[0, '#e9a873'], [0.5, '#f6cf9c'], [1, '#fbe6c6']])}${lg('hwall', [[0, '#f4ece0'], [1, '#ddcfbd']])}${lg('hwin', [[0, '#ffd99a'], [1, '#e9a764']])}
    ${lg('hground', [[0, '#cbbba3'], [1, '#a89478']])}
  </defs>
    <rect width="${BW}" height="1400" fill="url(#hsky)"/>
    ${mountains(1000, ['#c9a7a2', '#b39a9c'], 17)}
    <rect x="100" y="260" width="1150" height="1120" fill="url(#hwall)" stroke="#b9a68e" stroke-width="6"/>
    ${win}
    <rect x="100" y="230" width="1150" height="40" fill="#8f6a4c"/>
    <rect x="440" y="160" width="470" height="80" rx="10" fill="#2a2f3a"/>
    <text x="675" y="218" text-anchor="middle" font-family="Georgia, serif" font-size="54" fill="#f6d27a" letter-spacing="10">HOTEL</text>
    <path d="M400,1200 L950,1200 L1010,1100 L340,1100 Z" fill="#3a2f2a"/>
    <rect x="470" y="1200" width="410" height="200" fill="url(#hwin)" stroke="#5d4a3a" stroke-width="8"/>
    <path d="M675,1200 L675,1400" stroke="#5d4a3a" stroke-width="6"/>
    <rect y="1390" width="${BW}" height="1010" fill="url(#hground)"/>
    ${palm(260, 1450, 1.0)}${palm(1100, 1450, 1.05)}
    ${bus(-260, 1260, 0.62, { doorOpen: false })}
    <rect width="${BW}" height="${BH}" fill="#ff9a50" opacity="0.06"/>
    <rect width="${BW}" height="${BH}" filter="url(#paper)"/>
  </svg>`;
}

/* ------------------------------------------------ 9. hotel lobby */
function lobby() {
  let floor = '';
  for (let i = -10; i <= 10; i++) floor += `<path d="M${675 + i * 40},1300 L${675 + i * 260},2400" stroke="#cdbfa9" stroke-width="2" opacity="0.6"/>`;
  for (let j = 1; j < 12; j++) { const y = 1300 + Math.pow(j / 12, 1.8) * 1100; floor += `<path d="M0,${f(y)} L${BW},${f(y)}" stroke="#cdbfa9" stroke-width="2" opacity="0.5"/>`; }
  let keys = '';
  for (let r = 0; r < 4; r++) for (let i = 0; i < 6; i++) keys += `<rect x="${470 + i * 70}" y="${640 + r * 80}" width="54" height="60" fill="#6b4b30" stroke="#3e2a1a" stroke-width="3"/><circle cx="${497 + i * 70}" cy="${678 + r * 80}" r="7" fill="url(#lkey)"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${BW} ${BH}" width="${BW}" height="${BH}"><defs>${common}
    ${lg('lw', [[0, '#efe3cf'], [1, '#dcc8a8']])}${lg('lf', [[0, '#eee5d6'], [1, '#d3c4ab']])}${lg('desk', [[0, '#7a5232'], [1, '#4e321d']])}
    ${lg('lkey', [[0, '#f6e0a0'], [1, '#a77d2c']], 1, 1)}${rg('chand', [[0, '#fff3cf', 1], [0.35, '#ffe1a0', 0.6], [1, '#ffe1a0', 0]])}
  </defs>
    <rect width="${BW}" height="${BH}" fill="url(#lw)"/><rect width="${BW}" height="${BH}" filter="url(#paper)"/>
    ${[150, 1100].map((x) => `<rect x="${x}" y="300" width="90" height="1000" fill="#e6d4b4" stroke="#b9a07a" stroke-width="5"/><rect x="${x - 15}" y="290" width="120" height="30" fill="#c9ad84"/>`).join('')}
    <rect x="420" y="560" width="510" height="380" fill="#8a6446" stroke="#3e2a1a" stroke-width="8"/>${keys}
    <rect y="1290" width="${BW}" height="1110" fill="url(#lf)"/>${floor}
    <path d="M280,1080 L1070,1080 L1110,1360 L240,1360 Z" fill="url(#desk)" stroke="#2e1c10" stroke-width="5"/>
    <rect x="260" y="1060" width="830" height="34" rx="6" fill="#d9c7a6" stroke="#8c7350" stroke-width="3"/>
    <path d="M330,1140 L1020,1140 M320,1220 L1040,1220" stroke="#a27a52" stroke-width="4" opacity="0.6"/>
    <rect x="800" y="980" width="120" height="80" rx="6" fill="#2b2f36"/><rect x="808" y="988" width="104" height="60" fill="#8fb4d8"/>
    <path d="M520,1060 C520,1030 560,1030 560,1060" stroke="#e0b44f" stroke-width="6" fill="none"/>
    <circle cx="675" cy="230" r="260" fill="url(#chand)"/>
    <g transform="translate(675,150)"><path d="M0,-150 L0,0" stroke="#a77d2c" stroke-width="4"/>${Array.from({ length: 7 }, (_, i) => `<path d="M0,0 Q${-120 + i * 40},40 ${-120 + i * 40},70" stroke="#d9b35b" stroke-width="5" fill="none"/><ellipse cx="${-120 + i * 40}" cy="76" rx="10" ry="16" fill="#fff6d8"/>`).join('')}</g>
    ${[80, 1270].map((x) => `<g transform="translate(${x},1460)"><path d="M-50,0 L50,0 L36,120 L-36,120 Z" fill="#c9ad84"/>${Array.from({ length: 9 }, (_, i) => `<path d="M0,0 C${-80 + i * 20},-120 ${-100 + i * 25},-220 ${-60 + i * 15},-300" stroke="#4f7536" stroke-width="14" fill="none" stroke-linecap="round"/>`).join('')}</g>`).join('')}
    <rect width="${BW}" height="${BH}" fill="#ffcf8a" opacity="0.07"/>
  </svg>`;
}

/* ------------------------------------------------ soft bokeh backdrop for close-ups */
function bokeh(base = ['#f6d8b0', '#cfdcea'], seed = 3) {
  const r = mkRng(seed);
  let c = '';
  for (let i = 0; i < 40; i++) c += `<circle cx="${f(r() * BW)}" cy="${f(r() * BH)}" r="${f(40 + r() * 140)}" fill="${['#fff6e0', '#ffe2b0', '#d8e8f5', '#b8d08a'][Math.floor(r() * 4)]}" opacity="${f(0.15 + r() * 0.35)}"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${BW} ${BH}" width="${BW}" height="${BH}"><defs>${common}${lg('bk', [[0, base[1]], [1, base[0]]])}</defs>
    <rect width="${BW}" height="${BH}" fill="url(#bk)"/><g filter="url(#bgBlur20)">${c}</g></svg>`;
}

module.exports = { BW, BH, bus, busDefs, tree, university, studyRoom, corridor, bedroom, classroom, busInterior, mountainRoad, hotelExterior, lobby, bokeh };
