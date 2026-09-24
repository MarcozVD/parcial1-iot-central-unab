async (page) => {
  const out = {};
  // 1) cerrar modal de error
  const close = page.locator('button[aria-label="Cerrar"]');
  if (await close.count()) { await close.first().click(); await page.waitForTimeout(1500); }
  out.modal_after = await page.evaluate(() => !!document.querySelector('[class*=modal_interrupt]'));

  // 2) suscripción: elegir la segunda opción
  await page.locator('div[role=combobox][aria-label^="Suscripción"]').first().click();
  await page.waitForTimeout(2000);
  const items = page.locator('.ms-Dropdown-item');
  out.n = await items.count();
  if (out.n > 1) { await items.nth(1).click(); }
  await page.waitForTimeout(1500);
  out.sub_after = await page.evaluate(() => {
    const c = document.querySelector('div[role=combobox][aria-label^="Suscripción"]');
    return c ? c.innerText.trim() : null;
  });

  // 3) crear
  await page.locator('button:has-text("Crear")').last().click();
  await page.waitForTimeout(10000);
  out.after = await page.evaluate(() => {
    const modal = document.querySelector('[class*=modal_interrupt]');
    return {
      url: location.href,
      modal: modal ? modal.innerText.slice(0, 300) : null
    };
  });
  return JSON.stringify(out);
}
