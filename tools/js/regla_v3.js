async (page) => {
  const out = { pasos: [] };
  // confirmar la tarjeta de accion con "Listo"
  const listo = page.locator('button:has-text("Listo")').first();
  if (await listo.count()) { await listo.click({ force: true }); out.pasos.push('click Listo'); await page.waitForTimeout(3500); }
  out.inputs = await page.evaluate(() => [...document.querySelectorAll('input,textarea')].map((e) => e.getAttribute('aria-label')).filter(Boolean));
  out.botones = await page.evaluate(() => [...document.querySelectorAll('button')].map((b) => (b.innerText || b.getAttribute('aria-label') || '').trim().slice(0, 26)).filter(Boolean).slice(0, 18));
  // nombre de la regla si existe
  const nom = await page.evaluate(() => {
    const i = document.querySelector('input[aria-label^="Escriba un nombre de regla"]');
    if (!i) return null;
    const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    i.focus();
    s.call(i, 'Alerta temperatura de rack');
    i.dispatchEvent(new Event('input', { bubbles: true }));
    return i.value;
  });
  out.nombre = nom;
  await page.waitForTimeout(700);
  const g = await page.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find((x) => /^Guardar$/.test((x.innerText || '').trim()));
    if (!b) return 'sin boton guardar';
    b.click();
    return 'click';
  });
  out.pasos.push('guardar: ' + g);
  await page.waitForTimeout(9000);
  out.url = page.url();
  out.modal = await page.evaluate(() => {
    const m = document.querySelector('[class*=modal_interrupt]');
    return m ? m.innerText.slice(0, 160) : null;
  });
  return JSON.stringify(out);
}
