async (page) => {
  const out = {};
  // Ubicación -> Este de EE. UU.
  await page.locator('div[role=combobox][aria-label^="Ubicación"]').first().click();
  await page.waitForTimeout(2000);
  const locEl = page.locator('.ms-Dropdown-item', { hasText: 'Este de EE. UU.' }).first();
  out.loc_count = await locEl.count();
  if (await locEl.count()) { await locEl.click(); }
  await page.waitForTimeout(1200);
  out.loc_after = await page.evaluate(() => {
    const c = document.querySelector('div[role=combobox][aria-label^="Ubicación"]');
    return c ? c.innerText.trim() : null;
  });

  // Plan Estándar 2
  const plan = page.locator('input[aria-label="Plan de precios Estándar 2"]').first();
  out.plan_count = await plan.count();
  if (await plan.count()) {
    await plan.click({ force: true });
    await page.waitForTimeout(800);
    out.plan_checked = await plan.isChecked();
  }
  // Estado de todos los campos
  out.state = await page.evaluate(() => ({
    name: (document.querySelector('input[aria-label^="Nombre de la aplicación"]') || {}).value,
    url: (document.querySelector('input[aria-label^="URL"]') || {}).value,
    sub: (document.querySelector('div[role=combobox][aria-label^="Suscripción"]') || {}).innerText,
    loc: (document.querySelector('div[role=combobox][aria-label^="Ubicación"]') || {}).innerText,
    plan: [...document.querySelectorAll('input[type=radio]')].map(r => r.getAttribute('aria-label') + '=' + r.checked)
  }));
  return JSON.stringify(out);
}
