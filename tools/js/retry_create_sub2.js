async (page) => {
  const out = {};
  // abrir dropdown de suscripción y listar opciones
  await page.locator('div[role=combobox][aria-label^="Suscripción"]').first().click();
  await page.waitForTimeout(2000);
  const items = page.locator('.ms-Dropdown-item');
  out.n = await items.count();
  out.labels = [];
  for (let i = 0; i < out.n; i++) {
    const el = items.nth(i);
    out.labels.push({ i, txt: (await el.innerText()).replace(/\n/g, ' '), title: await el.getAttribute('title') });
  }
  // elegir la SEGUNDA opción
  if (out.n > 1) { await items.nth(1).click(); }
  await page.waitForTimeout(1500);
  out.sub_after = await page.evaluate(() => {
    const c = document.querySelector('div[role=combobox][aria-label^="Suscripción"]');
    return { txt: c ? c.innerText.trim() : null, title: c ? c.getAttribute('title') : null };
  });
  // crear
  const btn = page.locator('button:has-text("Crear")').last();
  await btn.click();
  await page.waitForTimeout(9000);
  out.after = await page.evaluate(() => ({
    url: location.href,
    errs: [...document.querySelectorAll('[class*=error],[role=alert],[class*=Error]')].map(e => (e.innerText || '').trim().slice(0, 140)).filter(Boolean).slice(0, 6),
    head: document.body.innerText.slice(0, 400)
  }));
  return JSON.stringify(out);
}
