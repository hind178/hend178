const { openPage, snapshot } = require('../src/engine');
const C = { hind: require('../src/characters/hind'), loreen: require('../src/characters/loreen'), lizette: require('../src/characters/lizette') };
(async () => {
  const { browser, page } = await openPage(1);
  const extra = JSON.parse(process.argv[3] || '{}');
  let inner = '<rect width="1080" height="1920" fill="#efe6de"/>';
  ['lizette', 'hind', 'loreen'].forEach((k, i) => {
    inner += `<clipPath id="row${i}"><rect x="0" y="${i * 640}" width="1080" height="640"/></clipPath>
      <g clip-path="url(#row${i})"><g transform="translate(540,${i * 640 + 360}) scale(1.25) translate(-500,-350)">${C[k].draw({ x: 500, y: 1850, s: 1, smile: 0.5, ...extra })}</g></g>`;
  });
  await snapshot(page, inner, process.argv[2]);
  await browser.close();
})();
