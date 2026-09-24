async (page) => {
  const out = { pasos: [] };
  const log = (m) => out.pasos.push(m);

  // 1) Titulo
  const titulo = page.locator('input[aria-label^="Título"]').first();
  if (await titulo.count()) { await titulo.fill('Temperaturas de racks (intake / exhaust)'); log('titulo'); }

  // 2) Grupo de dispositivos (combobox Fluent con input oculto)
  const combo = page.locator('[role=combobox][aria-label^="Grupo de dispositivos"]').first();
  if (await combo.count()) {
    await combo.click();
    await page.waitForTimeout(2000);
    const set = await page.evaluate(() => {
      const inp = [...document.querySelectorAll('input')].find(e => (e.getAttribute('aria-label') || '').startsWith('Grupo de dispositivos'));
      if (!inp) return 'sin input';
      inp.focus();
      const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      s.call(inp, 'Nodo DC-ANDES-1');
      inp.dispatchEvent(new Event('input', { bubbles: true }));
      return 'ok';
    });
    log('grupo filtro: ' + set);
    await page.waitForTimeout(2500);
    const opciones = await page.evaluate(() => [...document.querySelectorAll('[role=option],[class*=list-item]')].map(o => o.innerText.trim()).slice(0, 8));
    log('opciones grupo: ' + JSON.stringify(opciones));
    const op = page.locator('[role=option], [class*=list-item]').filter({ hasText: 'Nodo DC-ANDES-1' }).first();
    if (await op.count()) { await op.click(); log('grupo elegido'); }
    await page.waitForTimeout(2000);
  }

  // 3) Dispositivos
  const comboD = page.locator('[role=combobox][aria-label^="Dispositivos"]').first();
  if (await comboD.count()) {
    await comboD.click();
    await page.waitForTimeout(2500);
    const ops = await page.evaluate(() => [...document.querySelectorAll('[role=option],[class*=list-item]')].map(o => o.innerText.trim()).slice(0, 15));
    log('opciones dispositivos: ' + JSON.stringify(ops));
  }
  const estado = await page.evaluate(() => ({
    titulo: (document.querySelector('input[aria-label^="Título"]') || {}).value,
    grupo: (document.querySelector('[role=combobox][aria-label^="Grupo de dispositivos"]') || {}).innerText,
    disp: (document.querySelector('[role=combobox][aria-label^="Dispositivos"]') || {}).innerText,
    texto: document.body.innerText.slice(-600)
  }));
  return JSON.stringify({ ...out, estado });
}
