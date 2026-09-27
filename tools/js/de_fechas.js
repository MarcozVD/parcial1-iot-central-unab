async (page) => {
  const out = { pasos: [] };
  const E = 'C:/Users/mvale/Documents/Parcial1_IoT_Central/evidencias/';
  await page.setViewportSize({ width: 1600, height: 1000 });
  const dlg = page.locator('div.tsi-dateTimePickerContainer');
  const fechas = [
    ['26', '26/09/2026 00:00:00.000', '26/09/2026 23:59:59.000'],
    ['27', '27/09/2026 00:00:00.000', '27/09/2026 23:59:59.000'],
  ];
  for (const [tag, ini, fin] of fechas) {
    if ((await page.locator('input.tsi-dateTimeInput:visible').count()) < 2) {
      await page.locator('button.tsi-dateTimeButton').first().click({ force: true });
      await page.waitForTimeout(1500);
    }
    const ins = page.locator('input.tsi-dateTimeInput:visible');
    const n = await ins.count();
    if (n < 2) { out.pasos.push(tag + ': inputs=' + n); continue; }
    for (const [k, val] of [[1, fin], [0, ini]]) {
      const el = ins.nth(k);
      await el.click({ force: true }); await el.fill('');
      await el.fill(val); await el.press('Tab'); await page.waitForTimeout(300); if ((await el.inputValue()) !== val) { await el.fill(val); await el.press('Tab'); }
      await page.waitForTimeout(400);
    }
    await page.locator('div.tsi-dateTimePickerContainer:visible button', { hasText: /^Save$/ }).first().click({ force: true });
    await page.waitForTimeout(10000);
    const rango = await page.locator('button.tsi-dateTimeButton').first().innerText().catch(() => '?');
    await page.screenshot({ path: E + `de-${tag}.png` });
    out.pasos.push(`${tag}: ${rango}`);
  }
  return JSON.stringify(out);
}
