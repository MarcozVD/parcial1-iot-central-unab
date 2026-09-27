async (page) => {
  const out = { pasos: [] };
  const cancel = page.locator('button', { hasText: /^Cancel$/ }).first();
  if (await cancel.count()) { await cancel.click({ force: true }); await page.waitForTimeout(800); }

  const tels = ['Temperatura pasillo frio', 'Temperatura exterior (free-cooling)', 'PM2.5 en sala (ug/m3)',
    'Humedad de piso tecnico', 'Temperatura de techo', 'Potencia de fila', 'Eventos de acceso acumulados'];
  for (const t of tels) {
    await page.locator('button', { hasText: /^Agregar$/ }).first().click({ force: true });
    await page.waitForTimeout(1000);
    // el nuevo searchbox vacio de telemetria es el ultimo sin valor
    const idx = await page.evaluate(() => {
      const ins = [...document.querySelectorAll('input[type="search"]')].filter(i => i.offsetParent);
      const cands = ins.filter(i => !i.getAttribute('aria-label') && !i.value);
      return cands.length ? ins.indexOf(cands[cands.length - 1]) : -1;
    });
    if (idx < 0) { out.pasos.push(t + ': sin input'); continue; }
    const inp = page.locator('input[type="search"]:visible').nth(idx);
    await inp.click({ force: true });
    await page.waitForTimeout(700);
    await inp.fill(t.slice(0, 12));
    await page.waitForTimeout(1200);
    const opt = page.locator('[role="option"], [class*="popupMenu"] [class*="list-item"]', { hasText: t }).first();
    if (await opt.count()) { await opt.click({ force: true }); out.pasos.push(t + ': ok'); }
    else out.pasos.push(t + ': sin opcion');
    await page.waitForTimeout(900);
  }
  // agrupar por dispositivo
  const g = page.locator('input[aria-label="Agrupar por "]').first();
  await g.click({ force: true });
  await page.waitForTimeout(1200);
  out.opcionesAgrupar = await page.evaluate(() =>
    [...document.querySelectorAll('[role="option"], [class*="popupMenu"] [class*="list-item"]')].map(o => o.innerText.trim()).filter(Boolean));
  return JSON.stringify(out);
}
