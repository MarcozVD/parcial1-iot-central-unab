async (page) => {
  const out = {};
  const nombre = page.locator('input[aria-label^="Nombre"]').first();
  if (await nombre.count()) { await nombre.fill('Cuarto de Control DC-ANDES-1'); await page.waitForTimeout(500); }
  out.nombre = await nombre.inputValue().catch(() => null);
  await page.locator('button:has-text("Copiar")').last().click();
  await page.waitForTimeout(8000);
  out.url1 = page.url();
  // entrar en modo edicion del panel nuevo
  const ed = page.locator('button[aria-label="Editar"]').first();
  if (await ed.count()) { await ed.click(); await page.waitForTimeout(6000); }
  out.url2 = page.url();
  const info = await page.evaluate(() => {
    const galeria = [...document.querySelectorAll('button,[role=button],div[class*=tile],[class*=gallery]')]
      .map(e => (e.getAttribute('aria-label') || e.innerText || '').trim())
      .filter(t => t && t.length < 60);
    return [...new Set(galeria)].slice(0, 60);
  });
  out.galeria = info;
  out.texto = (await page.evaluate(() => document.body.innerText.slice(0, 700)));
  return JSON.stringify(out);
}
