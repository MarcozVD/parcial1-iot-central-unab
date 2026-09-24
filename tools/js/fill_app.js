async (page) => {
  const out = {};
  const APPNAME = 'DC-ANDES-1 · AndesCloud UNAB';
  const APPURL = 'dcandes1unab';

  await page.locator('input[aria-label^="Nombre de la aplicación"]').first().fill(APPNAME);
  await page.waitForTimeout(500);
  await page.locator('input[aria-label^="URL"]').first().fill(APPURL);
  await page.waitForTimeout(800);
  out.url_field = await page.locator('input[aria-label^="URL"]').first().inputValue();

  // Suscripción: click real, listar opciones, elegir la primera
  await page.locator('div[role=combobox][aria-label^="Suscripción"]').first().click();
  await page.waitForTimeout(2000);
  out.subs = await page.evaluate(() => [...document.querySelectorAll('.ms-Dropdown-item,[class*=list-item]')]
    .map(e => (e.innerText || '').trim().replace(/\n/g, ' ')).filter(Boolean));
  const optSub = page.locator('.ms-Dropdown-item').first();
  if (await optSub.count()) { await optSub.click(); }
  await page.waitForTimeout(1500);
  out.sub_after = await page.evaluate(() => {
    const c = document.querySelector('div[role=combobox][aria-label^="Suscripción"]');
    return c ? c.innerText.trim() : null;
  });

  // Ubicación
  await page.locator('div[role=combobox][aria-label^="Ubicación"]').first().click();
  await page.waitForTimeout(2000);
  out.locs = await page.evaluate(() => [...document.querySelectorAll('.ms-Dropdown-item,[class*=list-item]')]
    .map(e => (e.innerText || '').trim().replace(/\n/g, ' ')).filter(Boolean).slice(0, 40));
  const locEl = page.locator('.ms-Dropdown-item', { hasText: 'East US' }).first();
  if (await locEl.count()) { await locEl.click(); } else { await page.locator('.ms-Dropdown-item').first().click(); }
  await page.waitForTimeout(1500);
  out.loc_after = await page.evaluate(() => {
    const c = document.querySelector('div[role=combobox][aria-label^="Ubicación"]');
    return c ? c.innerText.trim() : null;
  });

  // Plan Estándar 2
  const plan = page.locator('input[aria-label="Plan de precios Estándar 2"]').first();
  if (await plan.count()) { await plan.check().catch(async () => { await plan.click(); }); }
  out.plan_checked = await page.locator('input[aria-label="Plan de precios Estándar 2"]').first().isChecked().catch(() => null);

  out.name = await page.locator('input[aria-label^="Nombre de la aplicación"]').first().inputValue();
  return JSON.stringify(out);
}
