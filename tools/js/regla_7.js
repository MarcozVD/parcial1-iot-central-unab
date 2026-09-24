async (page) => {
  const out = { pasos: [] };
  // cerrar modales si hay
  for (let i = 0; i < 3; i++) {
    const hay = await page.evaluate(() => !!document.querySelector('[class*=modal_interrupt]'));
    if (!hay) break;
    await page.evaluate(() => {
      const b = [...document.querySelectorAll('button')].find((x) => (x.getAttribute('aria-label') || '') === 'Cerrar');
      if (b) b.click();
    });
    await page.waitForTimeout(1500);
  }
  // nombre con setter nativo (React) + eventos reales
  const r = await page.evaluate(() => {
    const inp = document.querySelector('input[aria-label^="Escriba un nombre de regla"]');
    if (!inp) return 'sin input';
    inp.focus();
    const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    s.call(inp, 'Alerta temperatura de rack (exhaust)');
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    inp.dispatchEvent(new Event('change', { bubbles: true }));
    return inp.value;
  });
  out.nombre_setter = r;
  await page.waitForTimeout(1200);
  const nom = page.locator('input[aria-label^="Escriba un nombre de regla"]').first();
  out.nombre_leido = await nom.inputValue().catch(() => null);
  // guardar
  const g = await page.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find((x) => (x.innerText || '').trim() === 'Guardar');
    if (!b) return false;
    b.click();
    return true;
  });
  out.click_guardar = g;
  await page.waitForTimeout(9000);
  out.url = page.url();
  out.modal = await page.evaluate(() => {
    const m = document.querySelector('[class*=modal_interrupt]');
    return m ? m.innerText.slice(0, 160) : null;
  });
  return JSON.stringify(out);
}
