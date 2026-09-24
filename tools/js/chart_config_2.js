async (page) => {
  const out = { pasos: [] };
  const log = (m) => out.pasos.push(m);

  // Grupo de dispositivos
  const g = page.locator('input#combo-input-groupId');
  if (await g.count()) {
    await g.click();
    await g.fill('');
    await g.type('Nodo DC-ANDES-1', { delay: 60 });
    await page.waitForTimeout(2500);
    const ops = await page.evaluate(() => [...document.querySelectorAll('[role=option],[class*=list-item],li')]
      .map(o => o.innerText.trim()).filter(t => t && t.length < 60).slice(0, 10));
    log('opciones: ' + JSON.stringify(ops));
    const op = page.locator('[role=option], li, [class*=list-item]').filter({ hasText: 'Nodo DC-ANDES-1' }).first();
    if (await op.count()) { await op.click(); log('grupo ok'); }
    await page.waitForTimeout(2500);
  } else { log('sin input grupo'); }

  // Dispositivos
  const d = page.locator('input#combo-input-instanceId');
  if (await d.count()) {
    await d.click();
    await page.waitForTimeout(2500);
    const ops = await page.evaluate(() => [...document.querySelectorAll('[role=option],[class*=list-item],li')]
      .map(o => o.innerText.trim()).filter(t => t && t.length < 45).slice(0, 20));
    log('dispositivos: ' + JSON.stringify(ops));
    const todo = page.locator('[role=option],li,[class*=list-item]').filter({ hasText: /Seleccionar todo|Seleccionar todos/ }).first();
    if (await todo.count()) { await todo.click(); log('seleccionar todo'); }
    await page.waitForTimeout(2500);
  } else { log('sin input dispositivos'); }

  const estado = await page.evaluate(() => ({
    grupo: (document.querySelector('input#combo-input-groupId') || {}).value,
    disp: (document.querySelector('input#combo-input-instanceId') || {}).value,
    texto: document.body.innerText.slice(-700)
  }));
  return JSON.stringify({ ...out, estado });
}
