// Render every environment backdrop once to PNG (cached; reused by all frames & future episodes).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const B = require('./environments/backgrounds');
const E = require('./environments/ep2_backgrounds');
const OUT = path.join(__dirname, '..', 'assets', 'backgrounds');
const list = {
  hotel_corridor: E.hotelCorridor, room_day: () => E.hotelRoom(false), room_night: () => E.hotelRoom(true), restaurant: E.restaurant, sweets: E.sweetsShop, night_street: E.nightStreet, park: E.amusementPark,
  uni_bus: () => B.university({ bus: true }), uni_plain: () => B.university({}), uni_gate: () => B.university({ gate: true }),
  study: B.studyRoom, corridor: B.corridor, bedroom: B.bedroom, classroom: B.classroom, bus_interior: B.busInterior,
  mountain_road: B.mountainRoad, hotel_ext: B.hotelExterior, lobby: B.lobby,
  bokeh_warm: () => B.bokeh(['#f6d8b0', '#cfdcea'], 3), bokeh_bus: () => B.bokeh(['#e9eef2', '#bcd2e4'], 8), bokeh_lobby: () => B.bokeh(['#f3dcb6', '#e8c896'], 13),
};
(async () => {
  const only = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: B.BW, height: B.BH } });
  for (const [k, fn] of Object.entries(list)) {
    if (only.length && !only.includes(k)) continue;
    await page.setContent(`<html><body style="margin:0">${fn()}</body></html>`);
    await page.screenshot({ path: path.join(OUT, k + '.jpg'), type: 'jpeg', quality: 92 });
    process.stdout.write(k + ' ');
  }
  await browser.close(); console.log('done');
})();
