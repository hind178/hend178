// Global <defs>: palettes, gradients, filters and fabric patterns for all characters.
// Injected once into the render page; every frame references them by id.

const P = {
  // shared skin tones
  hind: { skin: '#f7d5c3', skinLight: '#fde8dc', skinShade: '#eab49d', skinDeep: '#d89780', skinLine: '#b9735f', blush: '#f29b98' },
  loreen: { skin: '#f4cfb8', skinLight: '#fce4d6', skinShade: '#e5ad94', skinDeep: '#d39079', skinLine: '#b06b56', blush: '#ee9a92' },
  lizette: { skin: '#f6d0b8', skinLight: '#fde5d6', skinShade: '#e8b096', skinDeep: '#d6937a', skinLine: '#b46e58', blush: '#f2988e' },
  // Hind
  hij: '#2f4fb8', hijLight: '#4d6fd3', hijShade: '#223d98', hijDeep: '#16296c', hijLine: '#142460',
  cap: '#f6f1ea', capShade: '#dcd2c5',
  bl: '#f6f1e8', blLight: '#fffdf8', blShade: '#e2d8ca', blDeep: '#c8baa8', blLine: '#a99883',
  navy: '#1c3282', royal: '#2c4fb4', mid: '#4b6fcc', light: '#8ea7e0', pale: '#c3d0ef', cream: '#efe9dc',
  bag: '#a0602f', bagLight: '#c8844c', bagShade: '#7c4321', bagDeep: '#5a2d13',
  shoe: '#6a3c27', shoeLight: '#a06a4c', shoeDeep: '#3a1f13',
  gold: '#d9b35b', goldLight: '#f6e0a0', goldDeep: '#a77d2c',
  bead: '#2b4fc0', beadDeep: '#132a78',
  // Loreen
  pink: '#f2a7b3', pinkLight: '#fcd3da', pinkShade: '#dc8797', pinkDeep: '#bd6578', pinkLine: '#9e4d61',
  blk: '#1d1b20', blkLight: '#3a3740', blkShade: '#111014', blkLine: '#050507',
  turbBase: '#f3efe6', turbFlower: '#2c3e8c', turbShade: '#cfc8ba',
  plaidBase: '#dcb48c', silver: '#c9ccd3', silverLight: '#f4f5f8', silverDeep: '#8d929c',
  // Lizette
  hair: '#6b4128', hairLight: '#b07a4b', hairHi: '#d2a06a', hairDeep: '#3f2414',
  dot: '#151418', denim: '#f7f7f5', denimShade: '#d9dbe0', denimDeep: '#b4b8c2',
  sandal: '#d8b98e', sandalDeep: '#a6865c',
};

function defs() {
  const lin = (id, stops, x2 = 1, y2 = 0, extra = '') =>
    `<linearGradient id="${id}" x1="0" y1="0" x2="${x2}" y2="${y2}" ${extra}>${stops.map(([o, c, a = 1]) => `<stop offset="${o}" stop-color="${c}" stop-opacity="${a}"/>`).join('')}</linearGradient>`;
  const radi = (id, stops, cx = 0.5, cy = 0.5, r = 0.6) =>
    `<radialGradient id="${id}" cx="${cx}" cy="${cy}" r="${r}">${stops.map(([o, c, a = 1]) => `<stop offset="${o}" stop-color="${c}" stop-opacity="${a}"/>`).join('')}</radialGradient>`;
  const skinSet = (k) => {
    const s = P[k];
    return radi(`${k}Face`, [[0, s.skinLight], [0.55, s.skin], [1, s.skinShade]], 0.45, 0.42, 0.62)
      + lin(`${k}Limb`, [[0, s.skinShade], [0.45, s.skin], [1, s.skinLight]])
      + lin(`${k}LimbV`, [[0, s.skinShade], [0.5, s.skin], [1, s.skinShade]])
      + lin(`${k}Neck`, [[0, s.skinDeep], [0.25, s.skinShade], [0.6, s.skin], [1, s.skinShade]]);
  };
  return `
  <filter id="blur1" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.2"/></filter>
  <filter id="blur2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2"/></filter>
  <filter id="blur4" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>
  <filter id="blur8" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="8"/></filter>
  <filter id="blur14" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="blur30" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="4" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.1 0.9"/>
  </filter>
  ${skinSet('hind')}${skinSet('loreen')}${skinSet('lizette')}
  ${radi('irisBrown', [[0, '#d9a066'], [0.35, '#b9834d'], [0.8, '#5a3017'], [1, '#2e160a']], 0.5, 0.62, 0.6)}
  ${radi('irisHazel', [[0, '#e0aa6a'], [0.35, '#b07843'], [0.8, '#5e3418'], [1, '#2e160a']], 0.5, 0.62, 0.6)}
  ${radi('irisDark', [[0, '#a8713f'], [0.35, '#6b3d1f'], [0.8, '#2e170b'], [1, '#160903']], 0.5, 0.62, 0.6)}
  ${lin('sclera', [[0, '#e9dcd6'], [0.45, '#fbf7f4'], [1, '#f3ebe7']], 0, 1)}
  ${lin('lipHind', [[0, '#bf6a68'], [1, '#d98680']], 0, 1)}
  ${lin('lipLoreen', [[0, '#c26f72'], [1, '#e1928e']], 0, 1)}
  ${lin('lipLizette', [[0, '#c86a5e'], [1, '#e58e7c']], 0, 1)}
  <!-- Hind -->
  ${radi('hijabGrad', [[0, P.hijLight], [0.45, P.hij], [1, P.hijShade]], 0.38, 0.22, 0.85)}
  ${lin('hijabTailGrad', [[0, P.hijShade], [0.4, P.hij], [1, P.hijDeep]])}
  ${lin('capGrad', [[0, P.cap], [1, P.capShade]], 0, 1)}
  ${lin('blouseGrad', [[0, P.blShade], [0.3, P.blLight], [0.6, P.bl], [1, P.blShade]])}
  ${lin('sleeveGrad', [[0, P.blShade], [0.35, P.blLight], [0.75, P.bl], [1, P.blDeep]])}
  ${lin('foldShadow', [[0, '#0b1645', 0], [0.5, '#0b1645', 0.55], [1, '#0b1645', 0]])}
  ${lin('foldLight', [[0, '#ffffff', 0], [0.5, '#ffffff', 0.12], [1, '#ffffff', 0]])}
  ${lin('skirtSide', [[0, '#0b1645', 0.45], [0.18, '#0b1645', 0.05], [0.4, '#ffffff', 0.07], [0.75, '#0b1645', 0.1], [1, '#0b1645', 0.55]])}
  ${lin('bagGrad', [[0, P.bagLight], [0.45, P.bag], [1, P.bagShade]], 1, 1)}
  ${lin('flapGrad', [[0, P.bagLight], [0.6, P.bag], [1, P.bagShade]], 0, 1)}
  ${lin('strapGrad', [[0, P.bagShade], [0.5, P.bagLight], [1, P.bag]])}
  ${lin('goldGrad', [[0, P.goldLight], [0.5, P.gold], [1, P.goldDeep]], 1, 1)}
  ${lin('silverGrad', [[0, P.silverLight], [0.5, P.silver], [1, P.silverDeep]], 1, 1)}
  ${radi('shoeGrad', [[0, P.shoeLight], [0.55, P.shoe], [1, P.shoeDeep]], 0.4, 0.35, 0.75)}
  ${radi('beadGrad', [[0, '#8fa9ff'], [0.35, P.bead], [1, P.beadDeep]], 0.35, 0.3, 0.75)}
  ${radi('watchFace', [[0, '#ffffff'], [1, '#e9e3d6']], 0.4, 0.35, 0.7)}
  <!-- Loreen -->
  ${lin('pinkGrad', [[0, P.pinkShade], [0.3, P.pinkLight], [0.65, P.pink], [1, P.pinkShade]])}
  ${lin('pinkSleeve', [[0, P.pinkShade], [0.35, P.pinkLight], [0.75, P.pink], [1, P.pinkDeep]])}
  ${lin('blackSkirt', [[0, '#0b0a0d'], [0.3, '#2c2a31'], [0.55, '#1d1b20'], [1, '#08070a']])}
  ${lin('blackGrad', [[0, P.blkShade], [0.4, P.blkLight], [1, P.blkShade]])}
  ${radi('turbanShade', [[0, '#ffffff', 0], [0.7, '#9a8f7c', 0.12], [1, '#5a4f40', 0.45]], 0.42, 0.35, 0.65)}
  <!-- Lizette -->
  ${lin('hairGrad', [[0, P.hairDeep], [0.35, P.hair], [0.7, P.hairLight], [1, P.hair]], 0, 1)}
  ${lin('hairSide', [[0, P.hairDeep], [0.5, P.hair], [1, P.hairDeep]])}
  ${lin('denimGrad', [[0, P.denimShade], [0.35, '#ffffff'], [0.7, P.denim], [1, P.denimDeep]])}
  ${radi('capCrown', [[0, '#4a4852'], [0.5, '#232129'], [1, '#0c0b0f']], 0.4, 0.3, 0.8)}
  ${lin('packGrad', [[0, '#2d2b31'], [0.5, '#1a191d'], [1, '#0b0a0d']], 1, 1)}
  ${patterns()}
  `;
}

function patterns() {
  return `
  <pattern id="pNavyFloral" width="26" height="26" patternUnits="userSpaceOnUse">
    <rect width="26" height="26" fill="${P.navy}"/>
    <g fill="${P.cream}" transform="translate(13,13)"><ellipse rx="2" ry="4.6"/><ellipse rx="4.6" ry="2"/><circle r="1.6" fill="${P.mid}"/></g>
    <g fill="${P.light}"><circle r="1.6"/><circle cx="26" r="1.6"/><circle cy="26" r="1.6"/><circle cx="26" cy="26" r="1.6"/></g>
  </pattern>
  <pattern id="pCreamIkat" width="34" height="34" patternUnits="userSpaceOnUse">
    <rect width="34" height="34" fill="${P.cream}"/><path d="M17,3 L29,17 L17,31 L5,17 Z" fill="${P.royal}"/>
    <path d="M17,9 L24,17 L17,25 L10,17 Z" fill="${P.cream}"/><circle cx="17" cy="17" r="2.6" fill="${P.navy}"/>
    <g fill="${P.mid}"><circle r="2"/><circle cx="34" r="2"/><circle cy="34" r="2"/><circle cx="34" cy="34" r="2"/></g>
  </pattern>
  <pattern id="pRoyalLattice" width="22" height="22" patternUnits="userSpaceOnUse">
    <rect width="22" height="22" fill="${P.royal}"/><path d="M0,0 L22,22 M22,0 L0,22" stroke="${P.light}" stroke-width="1.4"/>
    <circle cx="11" cy="11" r="2.2" fill="${P.cream}"/>
    <g fill="${P.cream}"><circle r="1.5"/><circle cx="22" r="1.5"/><circle cy="22" r="1.5"/><circle cx="22" cy="22" r="1.5"/></g>
  </pattern>
  <pattern id="pLightCross" width="28" height="28" patternUnits="userSpaceOnUse">
    <rect width="28" height="28" fill="${P.mid}"/><path d="M14,6 L16,12 L22,14 L16,16 L14,22 L12,16 L6,14 L12,12 Z" fill="${P.navy}"/>
    <circle cx="14" cy="14" r="2" fill="${P.cream}"/>
  </pattern>
  <pattern id="pMedallion" width="42" height="42" patternUnits="userSpaceOnUse">
    <rect width="42" height="42" fill="#172a6e"/>
    <path d="M21,5 L25,15 L36,13 L28,21 L36,29 L25,27 L21,37 L17,27 L6,29 L14,21 L6,13 L17,15 Z" fill="${P.cream}"/>
    <path d="M21,12 L26,21 L21,30 L16,21 Z" fill="${P.royal}"/><circle cx="21" cy="21" r="2.2" fill="${P.cream}"/>
  </pattern>
  <pattern id="pCreamDots" width="18" height="18" patternUnits="userSpaceOnUse">
    <rect width="18" height="18" fill="${P.pale}"/><rect x="6" y="6" width="6" height="6" fill="${P.royal}" transform="rotate(45 9 9)"/>
    <g fill="${P.navy}"><circle r="1.5"/><circle cx="18" r="1.5"/><circle cy="18" r="1.5"/><circle cx="18" cy="18" r="1.5"/></g>
  </pattern>
  <pattern id="pBand" width="16" height="16" patternUnits="userSpaceOnUse">
    <rect width="16" height="16" fill="${P.cream}"/><path d="M0,11 L4,5 L8,11 L12,5 L16,11" fill="none" stroke="${P.royal}" stroke-width="2"/>
    <circle cx="4" cy="13" r="1.2" fill="${P.navy}"/><circle cx="12" cy="13" r="1.2" fill="${P.navy}"/>
  </pattern>
  <pattern id="pSpeckle" width="12" height="12" patternUnits="userSpaceOnUse">
    <rect width="12" height="12" fill="#2442a0"/><circle cx="3" cy="3" r="1.1" fill="${P.light}"/><circle cx="9" cy="9" r="1.1" fill="${P.pale}"/>
  </pattern>
  <!-- Loreen: cream turban with navy blossoms -->
  <pattern id="pTurban" width="46" height="46" patternUnits="userSpaceOnUse" patternTransform="rotate(-12)">
    <rect width="46" height="46" fill="${P.turbBase}"/>
    <g fill="${P.turbFlower}">
      <g transform="translate(12,12)"><ellipse rx="3.6" ry="6.5"/><ellipse rx="3.6" ry="6.5" transform="rotate(72)"/><ellipse rx="3.6" ry="6.5" transform="rotate(144)"/><ellipse rx="3.6" ry="6.5" transform="rotate(216)"/><ellipse rx="3.6" ry="6.5" transform="rotate(288)"/><circle r="2.2" fill="#e8c770"/></g>
      <g transform="translate(35,33) rotate(30) scale(0.75)"><ellipse rx="3.6" ry="6.5"/><ellipse rx="3.6" ry="6.5" transform="rotate(72)"/><ellipse rx="3.6" ry="6.5" transform="rotate(144)"/><ellipse rx="3.6" ry="6.5" transform="rotate(216)"/><ellipse rx="3.6" ry="6.5" transform="rotate(288)"/><circle r="2.2" fill="#e8c770"/></g>
      <path d="M30,8 C33,10 34,14 32,17 C30,14 29,11 30,8 Z" fill="#5d73c4"/>
      <path d="M6,34 C9,35 11,39 10,42 C7,40 6,37 6,34 Z" fill="#5d73c4"/>
      <circle cx="24" cy="24" r="1.6" fill="#7d8fd3"/><circle cx="42" cy="12" r="1.4" fill="#7d8fd3"/>
    </g>
  </pattern>
  <!-- Loreen: plaid handbag -->
  <pattern id="pPlaid" width="40" height="40" patternUnits="userSpaceOnUse">
    <rect width="40" height="40" fill="${P.plaidBase}"/>
    <rect x="0" y="14" width="40" height="7" fill="#1c1a1d" opacity="0.85"/><rect x="14" y="0" width="7" height="40" fill="#1c1a1d" opacity="0.6"/>
    <rect x="0" y="31" width="40" height="2" fill="#ffffff" opacity="0.8"/><rect x="31" y="0" width="2" height="40" fill="#ffffff" opacity="0.8"/>
    <rect x="0" y="7" width="40" height="1.2" fill="#c8402f"/><rect x="7" y="0" width="1.2" height="40" fill="#c8402f"/>
  </pattern>
  <!-- Lizette: black with white polka dots -->
  <pattern id="pPolka" width="22" height="22" patternUnits="userSpaceOnUse">
    <rect width="22" height="22" fill="${P.dot}"/><circle cx="5.5" cy="5.5" r="2.4" fill="#f4f1ec"/><circle cx="16.5" cy="16.5" r="2.4" fill="#f4f1ec"/>
  </pattern>
  <!-- Lizette: hair strands -->
  <pattern id="pHairStrands" width="14" height="60" patternUnits="userSpaceOnUse">
    <path d="M3,0 C5,20 1,40 3,60" stroke="${P.hairHi}" stroke-width="1.6" fill="none" opacity="0.55"/>
    <path d="M10,0 C8,22 12,38 10,60" stroke="${P.hairDeep}" stroke-width="1.4" fill="none" opacity="0.5"/>
  </pattern>`;
}

module.exports = { P, defs };
