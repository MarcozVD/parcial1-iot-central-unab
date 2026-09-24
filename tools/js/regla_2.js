async (page) => {
  const out = { pasos: [] };
  const elegir = async (lbl, texto) => {
    const inp = page.locator(`input[aria-label^="${lbl}"]`).first();
    if (!(await inp.count())) { out.pasos.push(lbl + ': sin input'); return false; }
    await inp.click({ force: true });
    await inp.fill('');
    await inp.type(texto, { delay: 60 });
    await page.waitForTimeout(2500);
    const opciones = await page.evaluate(() => [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item]')]
      .map((e) => (e.innerText || '').trim()).filter((t) => t && t.length < 60).slice(0, 12));
    out.pasos.push(lbl + ' opciones: ' + JSON.stringify(opciones));
    const op = page.locator('[role=option], li, [class*=popupMenu] [class*=list-item]').filter({ hasText: texto }).first();
    if (await op.count()) { await op.click({ force: true }); await page.waitForTimeout(1500); return true; }
    return false;
  };

  // 1) nombre
  const nom = page.locator('input[aria-label^="Escriba un nombre de regla"]').first();
  if (await nom.count()) { await nom.fill('Alerta temperatura de rack'); out.pasos.push('nombre'); }
  // 2) plantilla
  out.plantilla = await elegir('Plantilla de dispositivo', 'Nodo DC-ANDES-1');
  // 3) telemetria
  out.telemetria = await elegir('Telemetría', 'Temperatura exhaust (rack)');
  // 4) operador
  const opDiv = page.locator('div[aria-label="Operador"], [role=combobox][aria-label="Operador"]').first();
  if (await opDiv.count()) {
    await opDiv.click({ force: true });
    await page.waitForTimeout(2000);
    const ops = await page.evaluate(() => [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item]')]
      .map((e) => (e.innerText || '').trim()).filter((t) => t && t.length < 30).slice(0, 12));
    out.pasos.push('operador opciones: ' + JSON.stringify(ops));
    const gt = page.locator('[role=option], li, [class*=popupMenu] [class*=list-item]').filter({ hasText: /^>|mayor/i }).first();
    if (await gt.count()) { await gt.click({ force: true }); out.pasos.push('operador >'); }
    await page.waitForTimeout(1500);
  }
  // 5) valor
  const val = page.locator('input[aria-label^="Valor"]').first();
  if (await val.count()) { await val.fill('35'); out.pasos.push('valor 35'); }
  await page.waitForTimeout(1500);

  out.texto = await page.evaluate(() => document.body.innerText.slice(-900));
  return JSON.stringify(out);
}
