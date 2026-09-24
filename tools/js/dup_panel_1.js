async (page) => {
  const log = [];
  // 1) Copiar el panel por defecto
  await page.locator('button[aria-label="Copiar"]').first().click();
  await page.waitForTimeout(3000);
  const campos = await page.evaluate(() => [...document.querySelectorAll('input,textarea')]
    .map(e => ({ lbl: e.getAttribute('aria-label') || e.placeholder || '', val: e.value || '' })));
  log.push({ paso: 'dialogo copiar', campos });
  // 2) Nombre del panel
  const nombre = page.locator('input[aria-label^="Nombre"], input[aria-label*="ombre"]').first();
  if (await nombre.count()) { await nombre.fill('Cuarto de Control DC-ANDES-1'); }
  await page.waitForTimeout(500);
  const botones = await page.evaluate(() => [...document.querySelectorAll('button')]
    .map(b => (b.innerText || '').trim()).filter(Boolean));
  log.push({ botones });
  return JSON.stringify(log);
}
