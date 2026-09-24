async (page) => {
  const out = { pasos: [] };
  const log = (m) => out.pasos.push(m);
  await page.goto('https://dcandes1unab.azureiotcentral.com/rules', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(6000);
  const nuevo = page.locator('button:has-text("Nuevo"), a:has-text("Nuevo")').first();
  if (await nuevo.count()) { await nuevo.click(); log('nuevo'); await page.waitForTimeout(5000); }
  const campos = await page.evaluate(() => [...document.querySelectorAll('input,[role=combobox]')]
    .map((e) => ({ tag: e.tagName, lbl: (e.getAttribute('aria-label') || e.placeholder || '').trim().slice(0, 45) }))
    .filter((x) => x.lbl).slice(0, 20));
  out.campos = campos;
  out.url = page.url();
  out.texto = await page.evaluate(() => document.body.innerText.slice(0, 800));
  return JSON.stringify(out);
}
