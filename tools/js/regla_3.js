async (page) => {
  const out = { pasos: [] };
  // valor
  const val = page.locator('input[aria-label^="Valor"], input[placeholder*="Escriba un valor"]').first();
  if (await val.count()) { await val.fill('35'); await page.waitForTimeout(800); out.valor = await val.inputValue(); }
  // accion: correo electronico (un solo clic)
  const mail = page.getByText('Correo electrónico').first();
  if (await mail.count()) { await mail.click({ force: true }); out.pasos.push('click correo'); await page.waitForTimeout(3000); }
  const campos = await page.evaluate(() => [...document.querySelectorAll('input,textarea')]
    .map((e) => ({ tag: e.tagName, lbl: (e.getAttribute('aria-label') || e.placeholder || '').trim().slice(0, 60), val: (e.value || '').slice(0, 40) }))
    .filter((x) => x.lbl));
  out.campos = campos.slice(0, 15);
  out.texto = await page.evaluate(() => document.body.innerText.slice(-500));
  return JSON.stringify(out);
}
