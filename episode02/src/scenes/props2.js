// Episode 02 animated props (frame coordinates). All drawn as layered vector art.
const { f } = require('../lib/util');
const defs2 = `
  <linearGradient id="comfyTop" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#cfc2e0"/><stop offset="0.35" stop-color="#f1ebf8"/><stop offset="1" stop-color="#bfb0d6"/></linearGradient>
  <pattern id="comfyDress" width="24" height="24" patternUnits="userSpaceOnUse"><rect width="24" height="24" fill="#b9a8d8"/><circle cx="6" cy="6" r="1.6" fill="#ece4f6"/><circle cx="18" cy="18" r="1.6" fill="#ece4f6"/></pattern>
  <pattern id="duvet" width="60" height="60" patternUnits="userSpaceOnUse"><rect width="60" height="60" fill="#f4efe6"/><path d="M0,30 L60,30 M30,0 L30,60" stroke="#e3d8c6" stroke-width="2"/><circle cx="30" cy="30" r="5" fill="#c9b9e0"/></pattern>
  <pattern id="mattressP" width="40" height="40" patternUnits="userSpaceOnUse"><rect width="40" height="40" fill="#7fa3d9"/><path d="M20,6 C26,14 26,20 20,26 C14,20 14,14 20,6 Z" fill="#f4efe6"/><circle cx="6" cy="32" r="3" fill="#2f4fb8"/></pattern>
  <linearGradient id="woodBed" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a5f3a"/><stop offset="1" stop-color="#5a3a20"/></linearGradient>
  <radialGradient id="pizzaG" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#f6c45a"/><stop offset="0.8" stop-color="#e9a03a"/><stop offset="1" stop-color="#b56a22"/></radialGradient>`;

/** single bed seen from the foot end; (x,y) = floor centre-front */
function bed(x, y, s, opt = {}) {
  return `<g transform="translate(${f(x)},${f(y)}) scale(${s})">
    <ellipse cx="0" cy="10" rx="300" ry="30" fill="#000" opacity="0.25"/>
    <path d="M-250,-470 C-250,-520 250,-520 250,-470 L250,-140 L-250,-140 Z" fill="url(#woodBed)" stroke="#3a2412" stroke-width="5"/>
    <rect x="-270" y="-170" width="540" height="190" rx="14" fill="url(#woodBed)" stroke="#3a2412" stroke-width="5"/>
    <rect x="-262" y="-240" width="524" height="90" rx="26" fill="#fbf8f2" stroke="#cfc4b2" stroke-width="4"/>
    ${opt.noPillow ? '' : `<ellipse cx="-110" cy="-262" rx="100" ry="40" fill="#fffdf8" stroke="#d8cdbb" stroke-width="3"/><ellipse cx="110" cy="-262" rx="100" ry="40" fill="#fffdf8" stroke="#d8cdbb" stroke-width="3"/>`}
    <path d="M-266,-215 C-150,-230 150,-230 266,-215 L272,-60 C150,-48 -150,-48 -272,-60 Z" fill="url(#duvet)" stroke="#bfb2a0" stroke-width="3"/>
    <path d="M-262,-150 C-100,-160 100,-160 262,-150" stroke="#cfc2ad" stroke-width="4" fill="none"/>
  </g>`;
}
/** big floor mattress (دوشگ); horizontal slab, w x h in local px */
function mattress(x, y, s, rot = 0, w = 1000, h = 120) {
  return `<g transform="translate(${f(x)},${f(y)}) rotate(${f(rot)}) scale(${s})">
    <rect x="${-w / 2 + 6}" y="${-h / 2 + 14}" width="${w}" height="${h}" rx="40" fill="#000" opacity="0.22"/>
    <rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="40" fill="url(#mattressP)" stroke="#2c4380" stroke-width="5"/>
    <path d="M${-w / 2 + 30},${-h / 2 + 18} L${w / 2 - 30},${-h / 2 + 18}" stroke="#fff" stroke-width="6" opacity="0.35"/>
    <path d="M${-w / 2 + 20},0 L${w / 2 - 20},0" stroke="#2c4380" stroke-width="2" stroke-dasharray="8 8" opacity="0.6"/></g>`;
}
function door(x, y, s, open = 0) {
  return `<g transform="translate(${f(x)},${f(y)}) scale(${s})">
    <rect x="-150" y="-760" width="300" height="760" fill="#2a1a10"/>
    <g transform="translate(-150,0) scale(${f(1 - open * 0.75)},1) translate(150,0)">
      <rect x="-150" y="-760" width="300" height="760" fill="#8a5a36" stroke="#4a2e1a" stroke-width="6"/>
      <rect x="-110" y="-700" width="220" height="280" fill="none" stroke="#5e3a20" stroke-width="5"/><rect x="-110" y="-370" width="220" height="300" fill="none" stroke="#5e3a20" stroke-width="5"/>
      <circle cx="110" cy="-380" r="12" fill="#e0b44f"/></g>
    <rect x="-170" y="-780" width="340" height="24" fill="#6b4a32"/></g>`;
}
function pizzaTable(x, y, s, bites = 0) {
  let slices = '';
  for (let i = 0; i < 8; i++) {
    if (i < bites) continue;
    const a0 = i * 45, a1 = a0 + 44;
    const p = (a, r) => [Math.cos(a * Math.PI / 180) * r, Math.sin(a * Math.PI / 180) * r * 0.42];
    const [x0, y0] = p(a0, 230), [x1, y1] = p(a1, 230);
    slices += `<path d="M0,0 L${f(x0)},${f(y0)} A230,97 0 0,1 ${f(x1)},${f(y1)} Z" fill="url(#pizzaG)" stroke="#b56a22" stroke-width="3"/>`;
    for (let k = 0; k < 3; k++) { const [px, py] = p(a0 + 10 + k * 12, 90 + k * 40); slices += `<ellipse cx="${f(px)}" cy="${f(py)}" rx="16" ry="8" fill="${k === 1 ? '#3f7a3a' : '#c0392b'}"/>`; }
  }
  return `<g transform="translate(${f(x)},${f(y)}) scale(${s})">
    <rect x="-520" y="0" width="1040" height="500" fill="#5a3a20"/>
    <ellipse cx="0" cy="0" rx="540" ry="120" fill="#e9d9bd" stroke="#8a6a4a" stroke-width="5"/>
    <path d="M-540,0 L-520,40 C-200,90 200,90 520,40 L540,0" fill="#c9b08a"/>
    <ellipse cx="0" cy="0" rx="250" ry="105" fill="#d8d2c6" stroke="#9c9486" stroke-width="3"/>${slices}
    ${[-380, 380].map((cx) => `<rect x="${cx - 26}" y="-60" width="52" height="70" rx="8" fill="#e04a3a" opacity="0.85"/><rect x="${cx - 26}" y="-60" width="52" height="14" fill="#fff" opacity="0.5"/>`).join('')}
  </g>`;
}
function baklavaBox(x, y, s, rot = 0) {
  let p = '';
  for (let a = 0; a < 4; a++) for (let b = 0; b < 2; b++) p += `<path d="M${-60 + a * 40},${-12 + b * 26} l20,-12 l20,12 l-20,12 Z" fill="#d9a04a" stroke="#8a5a1c" stroke-width="1.5"/><circle cx="${-40 + a * 40}" cy="${-12 + b * 26}" r="3" fill="#6b9a3a"/>`;
  return `<g transform="translate(${f(x)},${f(y)}) rotate(${rot}) scale(${s})"><rect x="-90" y="-40" width="180" height="80" rx="8" fill="#fbf1dc" stroke="#b08a50" stroke-width="4"/>${p}</g>`;
}
module.exports = { defs2, bed, mattress, door, pizzaTable, baklavaBox };
