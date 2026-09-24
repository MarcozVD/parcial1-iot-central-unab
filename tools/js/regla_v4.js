async (page) => {
  const out = { pasos: [] };
  const ren = page.locator('button:has-text("Cambiar nombre")').first();
  if (await ren.count()) { await ren.click({ force: true }); out.pasos.push('cambiar nombre'); await page.waitForTimeout(3000); }
  out.inputs = await page.evaluate(() => [...document.querySelectorAll('input')].map((e) => ({ aria: e.getAttribute('aria-label'), val: e.value })));
  out.texto = await page.evaluate(() => document.body.innerText.slice(0, 400));
  // escribir el nombre si aparece el campo
  const r = await page.evaluate(() => {
    const i = document.querySelector('input[aria-label^="Escriba un nombre"], input[aria-label*="nombre para la regla"], [role=dialog] input');
    if (!i) return 'sin campo';
    const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    i.focus();
    s.call(i, 'Alerta temperatura de rack');
    i.dispatchEvent(new Event('input', { bubbles: true }));
    return i.value;
  });
  out.nombre = r;
  await page.waitForTimeout(800);
  return JSON.stringify(out);
}
