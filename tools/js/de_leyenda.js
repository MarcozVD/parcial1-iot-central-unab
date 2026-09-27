async (page) => {
  const out = {};
  const fechas = [
    ['24', '24/09/2026 00:00:00.000', '24/09/2026 23:59:59.000'],
    ['25', '25/09/2026 00:00:00.000', '25/09/2026 23:59:59.000'],
    ['26', '26/09/2026 00:00:00.000', '26/09/2026 23:59:59.000'],
    ['27', '27/09/2026 00:00:00.000', '27/09/2026 23:59:59.000'],
  ];
  const leer = () => page.evaluate(() => {
    const res = {};
    for (const g of document.querySelectorAll('.tsi-legend .tsi-seriesLabel')) {
      const cab = g.querySelector('.tsi-seriesLabelText, h4, [class*="seriesLabelText"]');
      const nombre = (cab ? cab.innerText : g.innerText.split(String.fromCharCode(10))[0]).trim();
      const devs = [...g.querySelectorAll('.tsi-splitByLabel .tsi-seriesName')].map(x => x.innerText.trim());
      res[nombre] = [...new Set(devs)].sort();
    }
    return res;
  });
  for (const [tag, ini, fin] of fechas) {
    if ((await page.locator('input.tsi-dateTimeInput:visible').count()) < 2) {
      await page.locator('button.tsi-dateTimeButton').first().click({ force: true });
      await page.waitForTimeout(1500);
    }
    const ins = page.locator('input.tsi-dateTimeInput:visible');
    // orden seguro: si el nuevo inicio es posterior al fin actual, primero el fin
    for (const [k, val] of [[1, fin], [0, ini], [1, fin]]) {
      const el = ins.nth(k);
      await el.click({ force: true }); await el.fill(val); await el.press('Tab');
      await page.waitForTimeout(300);
    }
    await page.locator('div.tsi-dateTimePickerContainer:visible button', { hasText: /^Save$/ }).first().click({ force: true });
    await page.waitForTimeout(10000);
    const rango = await page.locator('button.tsi-dateTimeButton').first().innerText().catch(() => '?');
    out[tag] = { rango, series: await leer() };
  }
  return JSON.stringify(out);
}
