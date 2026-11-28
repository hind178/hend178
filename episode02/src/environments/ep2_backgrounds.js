// Episode 02 environments (1350x2400 canvases, cached to JPG). Reuses the Episode 01 painting helpers.
const { f, lerp, mkRng, smooth } = require('../lib/util');
const B = require('./backgrounds');
const BW = 1350, BH = 2400;
const lg = (id, stops, x2 = 0, y2 = 1) => `<linearGradient id="${id}" x1="0" y1="0" x2="${x2}" y2="${y2}">${stops.map(([o, c, a = 1]) => `<stop offset="${o}" stop-color="${c}" stop-opacity="${a}"/>`).join('')}</linearGradient>`;
const rg = (id, stops, cx = 0.5, cy = 0.5, r = 0.5) => `<radialGradient id="${id}" cx="${cx}" cy="${cy}" r="${r}">${stops.map(([o, c, a = 1]) => `<stop offset="${o}" stop-color="${c}" stop-opacity="${a}"/>`).join('')}</radialGradient>`;
const head = (d) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${BW} ${BH}" width="${BW}" height="${BH}"><defs>
  <filter id="paper" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="3" seed="2"/><feColorMatrix type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.28  0 0 0 0 0.2  0 0 0 0.09 0"/></filter>
  <filter id="bgBlur6" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="bgBlur20" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="20"/></filter>
  <filter id="leafy" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="3" seed="5" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="26"/></filter>
  ${B.busDefs()}${d}</defs>`;

/* hotel corridor with room doors */
function hotelCorridor() {
  const vx = 675, vy = 1100;
  let doors = '', lamps = '';
  for (const side of [-1, 1]) for (let k = 0; k < 4; k++) {
    const t0 = Math.pow(k / 4.3, 0.8), t1 = Math.pow((k + 0.45) / 4.3, 0.8);
    const X = (t) => side < 0 ? lerp(0, vx - 170, t) : lerp(BW, vx + 170, t);
    const T = (t) => lerp(420, vy - 130, t), Bt = (t) => lerp(2150, vy + 60, t);
    doors += `<path d="M${f(X(t0))},${f(T(t0))} L${f(X(t1))},${f(T(t1))} L${f(X(t1))},${f(Bt(t1))} L${f(X(t0))},${f(Bt(t0))} Z" fill="#7a4e30" stroke="#4a2e1a" stroke-width="5"/>
      <circle cx="${f(lerp(X(t0), X(t1), 0.8))}" cy="${f(lerp(T(t0), Bt(t0), 0.55))}" r="${f(lerp(10, 3, t0))}" fill="#e0b44f"/>
      <rect x="${f(lerp(X(t0), X(t1), 0.35))}" y="${f(lerp(T(t0), T(t1), 0.5) - 60 * (1 - t0))}" width="${f(40 * (1 - t0) + 8)}" height="${f(22 * (1 - t0) + 5)}" fill="#e9d6a8"/>`;
    lamps += `<ellipse cx="${f(X(lerp(t0, t1, 1.4)))}" cy="${f(lerp(T(t0), Bt(t0), 0.25))}" rx="${f(26 * (1 - t0) + 6)}" ry="${f(40 * (1 - t0) + 8)}" fill="#ffe2a8" opacity="0.9"/>`;
  }
  return head(`${lg('hw', [[0, '#e8d6bb'], [1, '#d2b993']])}${lg('carpet', [[0, '#7a2f35'], [1, '#5a1f26']])}${rg('glow', [[0, '#ffe2a8', 0.55], [1, '#ffe2a8', 0]])}`) + `
    <rect width="${BW}" height="${BH}" fill="url(#hw)"/>
    <path d="M0,0 L${vx - 170},${vy - 150} L${vx + 170},${vy - 150} L${BW},0 Z" fill="#f2e6d2"/>
    <path d="M0,${BH} L${vx - 170},${vy + 70} L${vx + 170},${vy + 70} L${BW},${BH} Z" fill="url(#carpet)"/>
    ${Array.from({ length: 9 }, (_, i) => `<path d="M${vx - 120 + i * 30},${vy + 70} L${-400 + i * 270},${BH}" stroke="#c9a15a" stroke-width="3" opacity="0.35"/>`).join('')}
    <rect x="${vx - 170}" y="${vy - 150}" width="340" height="220" fill="#f6ead4"/><rect x="${vx - 60}" y="${vy - 120}" width="120" height="170" fill="#7a4e30"/>
    ${doors}${lamps}
    ${[0.1, 0.35, 0.6].map((t) => `<circle cx="${vx}" cy="${f(lerp(120, vy - 160, t))}" r="${f(lerp(200, 40, t))}" fill="url(#glow)"/>`).join('')}
    <rect width="${BW}" height="${BH}" filter="url(#paper)"/>`;
}

/* hotel room (no beds — beds are animated props). night: lamp-lit */
function hotelRoom(night) {
  return head(`${lg('rw', night ? [[0, '#6d5a52'], [1, '#4d3e3a']] : [[0, '#efe2cf'], [1, '#dcc6a6']])}
    ${lg('rwin', night ? [[0, '#1c2a4a'], [1, '#3a3d63']] : [[0, '#cfe6f5'], [1, '#fff1d6']])}
    ${lg('rfl', night ? [[0, '#5b4436'], [1, '#3d2c22']] : [[0, '#b99470'], [1, '#90694a']])}
    ${rg('lampG', [[0, '#ffd28a', 0.95], [0.4, '#ffb85c', 0.45], [1, '#ffb85c', 0]])}`) + `
    <rect width="${BW}" height="${BH}" fill="url(#rw)"/>
    <rect x="0" y="420" width="${BW}" height="40" fill="${night ? '#5a4842' : '#d6bf9c'}"/>
    <rect x="380" y="560" width="590" height="640" fill="url(#rwin)" stroke="${night ? '#3a2c26' : '#a88b68'}" stroke-width="16"/>
    ${night ? Array.from({ length: 40 }, (_, i) => `<circle cx="${400 + (i * 137) % 550}" cy="${600 + (i * 89) % 560}" r="${1.5 + (i % 3)}" fill="#ffe9b8" opacity="0.8"/>`).join('') + `<circle cx="800" cy="680" r="50" fill="#fff6dc" opacity="0.9"/>` : B.tree(560, 1200, 0.9, 41, 1)}
    <path d="M360,540 C430,760 410,1000 360,1240 L250,1240 L250,540 Z" fill="${night ? '#7b4a52' : '#c98a8a'}"/><path d="M990,540 C920,760 940,1000 990,1240 L1100,1240 L1100,540 Z" fill="${night ? '#7b4a52' : '#c98a8a'}"/>
    <rect x="240" y="520" width="870" height="24" rx="10" fill="#6b4a32"/>
    <rect y="1380" width="${BW}" height="1020" fill="url(#rfl)"/>
    <rect y="1380" width="${BW}" height="1020" filter="url(#paper)"/>
    <!-- framed picture & wardrobe -->
    <rect x="80" y="700" width="200" height="260" fill="#d9c7a6" stroke="#6b4a32" stroke-width="10"/><path d="M100,920 L160,820 L210,880 L250,840 L260,940 L100,940 Z" fill="#7da152"/>
    <rect x="1130" y="560" width="200" height="900" fill="#8a6446" stroke="#4d3320" stroke-width="6"/><path d="M1230,560 L1230,1460" stroke="#4d3320" stroke-width="4"/>
    <!-- nightstands with lamps -->
    ${[130, 1220].map((x) => `<rect x="${x - 80}" y="1280" width="160" height="180" fill="#7a5232" stroke="#4d3320" stroke-width="5"/>
      <path d="M${x - 50},1180 L${x + 50},1180 L${x + 36},1110 L${x - 36},1110 Z" fill="${night ? '#ffd892' : '#f4ecd8'}"/><rect x="${x - 5}" y="1180" width="10" height="100" fill="#3a2a1e"/>
      ${night ? `<circle cx="${x}" cy="1160" r="420" fill="url(#lampG)"/>` : ''}`).join('')}
    ${night ? '<rect width="1350" height="2400" fill="#1a1020" opacity="0.18"/>' : '<path d="M380,1200 L1100,2400 L-100,2400 Z" fill="#fff4d8" opacity="0.18"/>'}`;
}

/* cozy pizza restaurant */
function restaurant() {
  let bulbs = '';
  for (let i = 0; i < 14; i++) { const x = 40 + i * 95, y = 300 + Math.sin(i * 0.9) * 30 + 40; bulbs += `<circle cx="${x}" cy="${f(y)}" r="12" fill="#ffd98a"/><circle cx="${x}" cy="${f(y)}" r="40" fill="#ffd98a" opacity="0.18"/>`; }
  return head(`${lg('brick', [[0, '#9a4f36'], [1, '#6f3524']])}${lg('rfloor', [[0, '#6b4a32'], [1, '#3e2a1c']])}${rg('oven', [[0, '#ffcf6a'], [0.5, '#ff7a2a'], [1, '#5a1c0a']])}`) + `
    <rect width="${BW}" height="${BH}" fill="url(#brick)"/>
    ${Array.from({ length: 40 }, (_, r) => `<path d="M0,${r * 40} L${BW},${r * 40}" stroke="#5a2a1c" stroke-width="3" opacity="0.5"/>` + Array.from({ length: 12 }, (_, c) => `<path d="M${c * 120 + (r % 2) * 60},${r * 40} L${c * 120 + (r % 2) * 60},${r * 40 + 40}" stroke="#5a2a1c" stroke-width="3" opacity="0.5"/>`).join('')).join('')}
    <path d="M500,500 C500,330 850,330 850,500 L850,900 L500,900 Z" fill="#3a2016"/><path d="M560,900 L560,620 C560,520 790,520 790,620 L790,900 Z" fill="url(#oven)"/>
    <rect x="460" y="880" width="430" height="60" fill="#7a5a44"/>
    <path d="M0,330 C300,420 1000,260 ${BW},360" stroke="#3a2a1e" stroke-width="3" fill="none"/>${bulbs}
    <rect x="80" y="560" width="300" height="180" fill="#2a2a2a" stroke="#6b4a32" stroke-width="10"/>
    <text x="230" y="630" text-anchor="middle" font-family="Georgia" font-size="44" fill="#f4e2b8">PIZZA</text><path d="M120,670 L340,670 M120,700 L300,700" stroke="#f4e2b8" stroke-width="4" opacity="0.7"/>
    <rect x="1000" y="600" width="260" height="380" fill="#cfe2ea" stroke="#6b4a32" stroke-width="10"/>
    <rect y="1300" width="${BW}" height="1100" fill="url(#rfloor)"/>
    ${Array.from({ length: 12 }, (_, i) => `<path d="M${i * 120},1300 L${-300 + i * 180},2400" stroke="#2a1a10" stroke-width="3" opacity="0.4"/>`).join('')}
    ${[[150, 1300], [1200, 1290]].map(([x, y]) => `<g transform="translate(${x},${y})"><ellipse cx="0" cy="0" rx="130" ry="30" fill="#d84a3a"/><rect x="-10" y="0" width="20" height="200" fill="#3a2a1e"/></g>`).join('')}
    <rect width="${BW}" height="${BH}" fill="#ff9a40" opacity="0.08"/><rect width="${BW}" height="${BH}" filter="url(#paper)"/>`;
}

/* traditional sweets shop with baklava trays */
function sweetsShop() {
  let trays = '';
  for (let r = 0; r < 3; r++) for (let i = 0; i < 4; i++) {
    const x = 170 + i * 260, y = 820 + r * 220;
    let pieces = '';
    for (let a = 0; a < 5; a++) for (let b = 0; b < 3; b++) pieces += `<path d="M${x - 90 + a * 40},${y - 30 + b * 26} l20,-12 l20,12 l-20,12 Z" fill="${r === 1 ? '#c98a3a' : '#d9a04a'}" stroke="#8a5a1c" stroke-width="1.5"/><circle cx="${x - 70 + a * 40}" cy="${y - 30 + b * 26}" r="3" fill="#6b9a3a"/>`;
    trays += `<ellipse cx="${x}" cy="${y}" rx="120" ry="58" fill="url(#copper)" stroke="#7a4a1c" stroke-width="5"/>${pieces}`;
  }
  return head(`${lg('sw', [[0, '#f2e1c0'], [1, '#e0c597']])}${lg('copper', [[0, '#f0b86a'], [1, '#a5632a']], 1, 1)}${lg('glass', [[0, '#ffffff', 0.25], [1, '#ffffff', 0.05]])}${lg('wood', [[0, '#7a4e2c'], [1, '#4a2e18']])}`) + `
    <rect width="${BW}" height="${BH}" fill="url(#sw)"/>
    ${Array.from({ length: 14 }, (_, i) => `<path d="M${i * 100},0 l50,60 l-50,60 l-50,-60 Z" fill="#2f4fb8" opacity="0.15"/>`).join('')}
    <path d="M150,420 C150,250 1200,250 1200,420 Z" fill="#2f4fb8"/><text x="675" y="400" text-anchor="middle" font-family="Amiri" font-weight="700" font-size="80" fill="#f6d27a" direction="rtl">حلويات</text>
    <rect x="80" y="640" width="1190" height="760" fill="url(#wood)" stroke="#3a2210" stroke-width="8"/>
    <rect x="100" y="660" width="1150" height="700" fill="#fbf1dc" opacity="0.4"/>
    ${trays}
    <rect x="100" y="660" width="1150" height="700" fill="url(#glass)"/><path d="M140,680 L320,1340" stroke="#fff" stroke-width="18" opacity="0.18"/>
    <rect x="60" y="1400" width="1230" height="120" fill="#5a361c"/><rect y="1520" width="${BW}" height="880" fill="#8a6446"/>
    ${[260, 1090].map((x) => `<g transform="translate(${x},160)"><path d="M0,0 L0,120" stroke="#a77d2c" stroke-width="4"/><path d="M-50,120 C-50,60 50,60 50,120 L30,200 L-30,200 Z" fill="#d9a03a"/><circle cx="0" cy="170" r="60" fill="#ffd98a" opacity="0.3"/></g>`).join('')}
    <rect width="${BW}" height="${BH}" fill="#ffb060" opacity="0.07"/><rect width="${BW}" height="${BH}" filter="url(#paper)"/>`;
}

/* evening street with string lights */
function nightStreet() {
  let shops = '', lights = '';
  const cols = ['#e0a86a', '#c97a5a', '#d9b98a', '#a9c0d6', '#e3c070'];
  for (let i = 0; i < 6; i++) {
    const x = i * 240 - 40, h = 700 + (i % 3) * 120;
    shops += `<rect x="${x}" y="${1350 - h}" width="230" height="${h}" fill="${['#5a4a5e', '#4a3e52', '#6a5262'][i % 3]}"/>`;
    for (let w = 0; w < 3; w++) for (let k = 0; k < 2; k++) shops += `<rect x="${x + 30 + k * 100}" y="${1350 - h + 60 + w * 150}" width="70" height="90" fill="${cols[(i + w + k) % 5]}" opacity="0.85"/>`;
    shops += `<rect x="${x + 20}" y="1150" width="190" height="200" fill="#ffd98a" opacity="0.8"/><path d="M${x + 10},1150 L${x + 220},1150 L${x + 200},1110 L${x + 30},1110 Z" fill="${['#c0392b', '#2f4fb8', '#3f7a5a'][i % 3]}"/>`;
  }
  for (let i = 0; i < 26; i++) { const x = i * 55, y = 520 + Math.sin(i * 0.25) * 60 + (i % 2) * 8; lights += `<circle cx="${x}" cy="${f(y)}" r="9" fill="#ffe2a0"/><circle cx="${x}" cy="${f(y)}" r="34" fill="#ffe2a0" opacity="0.2"/>`; }
  return head(`${lg('nsky', [[0, '#141a3a'], [0.6, '#3a2f5a'], [1, '#c9786a']])}${lg('pave', [[0, '#5a5058'], [1, '#2e2a30']])}`) + `
    <rect width="${BW}" height="1400" fill="url(#nsky)"/>
    ${Array.from({ length: 60 }, (_, i) => `<circle cx="${(i * 223) % BW}" cy="${(i * 97) % 500}" r="${1 + (i % 3) * 0.7}" fill="#fff" opacity="0.7"/>`).join('')}
    <circle cx="1080" cy="260" r="60" fill="#fff4d6"/>
    ${shops}
    <path d="M0,480 C400,640 900,420 ${BW},560" stroke="#2a2030" stroke-width="3" fill="none"/>${lights}
    <rect y="1350" width="${BW}" height="1050" fill="url(#pave)"/>
    ${Array.from({ length: 10 }, (_, i) => `<path d="M0,${1350 + Math.pow(i / 10, 1.8) * 1050} L${BW},${1350 + Math.pow(i / 10, 1.8) * 1050}" stroke="#ffd98a" stroke-width="2" opacity="0.15"/>`).join('')}
    <rect y="1350" width="${BW}" height="400" fill="#ffd98a" opacity="0.08"/>
    <rect width="${BW}" height="${BH}" filter="url(#paper)"/>`;
}

/* amusement park wide: ferris wheel, carousel, and a towering thrill ride */
function amusementPark() {
  let wheel = '';
  for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2, x = Math.cos(a) * 300, y = Math.sin(a) * 300; wheel += `<path d="M0,0 L${f(x)},${f(y)}" stroke="#e8e2f0" stroke-width="5"/><g transform="translate(${f(x)},${f(y)})"><path d="M-22,0 L22,0 L18,40 L-18,40 Z" fill="${['#e74c3c', '#f1c40f', '#3498db', '#2ecc71'][i % 4]}"/></g>`; }
  let coaster = '';
  const pts = [];
  for (let x = -50; x <= 1400; x += 50) pts.push([x, 1100 - Math.max(0, Math.sin((x - 300) / 230)) * 380 - (x > 900 ? (x - 900) * 0.2 : 0)]);
  coaster = `<path d="${smooth(pts)}" stroke="#d0392f" stroke-width="12" fill="none"/>` + pts.map(([x, y]) => `<path d="M${x},${f(y)} L${x},1350" stroke="#8a8f9a" stroke-width="4"/>`).join('');
  return head(`${lg('psky', [[0, '#5a9be0'], [0.6, '#bfd9ef'], [1, '#ffe2bd']])}${lg('tower', [[0, '#3a3f4a'], [1, '#22262e']], 1, 0)}${lg('grass', [[0, '#7ab04f'], [1, '#55853a']])}`) + `
    <rect width="${BW}" height="${BH}" fill="url(#psky)"/>
    <g opacity="0.85">${B.tree(80, 1360, 0.8, 61, 1)}${B.tree(1290, 1360, 0.8, 62, 1)}</g>
    <g transform="translate(330,800)">${wheel}<circle r="300" fill="none" stroke="#f5f0ff" stroke-width="10"/><circle r="40" fill="#8e44ad"/><path d="M-120,560 L0,0 L120,560" stroke="#d8d2e2" stroke-width="16" fill="none"/></g>
    ${coaster}
    <!-- the giant drop tower -->
    <rect x="930" y="120" width="90" height="1260" fill="url(#tower)"/>
    ${Array.from({ length: 24 }, (_, i) => `<path d="M930,${160 + i * 50} L1020,${185 + i * 50}" stroke="#5a606c" stroke-width="3"/>`).join('')}
    <rect x="900" y="80" width="150" height="60" rx="10" fill="#e74c3c"/><circle cx="975" cy="70" r="16" fill="#f1c40f"/>
    <rect x="880" y="330" width="190" height="70" rx="12" fill="#f1c40f" stroke="#a6800a" stroke-width="4"/>
    ${Array.from({ length: 6 }, (_, i) => `<rect x="${892 + i * 30}" y="400" width="18" height="34" fill="#2f4fb8"/>`).join('')}
    <!-- carousel -->
    <g transform="translate(640,1180)"><path d="M-200,0 L0,-140 L200,0 Z" fill="#e74c3c"/>${Array.from({ length: 8 }, (_, i) => `<path d="M${-200 + i * 50},0 L${-175 + i * 50},30 L${-150 + i * 50},0" fill="${i % 2 ? '#fff' : '#f1c40f'}"/>`).join('')}
      <rect x="-190" y="30" width="380" height="170" fill="#fbe8c8"/>${Array.from({ length: 6 }, (_, i) => `<path d="M${-160 + i * 64},30 L${-160 + i * 64},200" stroke="#d9b35b" stroke-width="5"/><ellipse cx="${-160 + i * 64}" cy="${120 + (i % 2) * 30}" rx="22" ry="14" fill="${['#fff', '#e8a0b0', '#a0c8e8'][i % 3]}"/>`).join('')}
      <rect x="-210" y="200" width="420" height="24" fill="#a0522d"/></g>
    ${Array.from({ length: 12 }, (_, i) => `<path d="M${i * 120},1300 L${i * 120 + 50},1260 L${i * 120 + 100},1300" fill="${['#e74c3c', '#f1c40f', '#3498db'][i % 3]}"/>`).join('')}
    <rect y="1380" width="${BW}" height="1020" fill="url(#grass)"/>
    <path d="M500,1380 L850,1380 L1250,2400 L100,2400 Z" fill="#d9c39a"/>
    ${Array.from({ length: 8 }, (_, i) => `<circle cx="${150 + i * 150}" cy="${f(1300 - (i % 3) * 30)}" r="22" fill="${['#e74c3c', '#f1c40f', '#3498db', '#e88fd0'][i % 4]}"/><path d="M${150 + i * 150},${f(1322 - (i % 3) * 30)} L${150 + i * 150},1400" stroke="#555" stroke-width="2"/>`).join('')}
    <rect width="${BW}" height="${BH}" filter="url(#paper)"/>`;
}
module.exports = { hotelCorridor, hotelRoom, restaurant, sweetsShop, nightStreet, amusementPark };
