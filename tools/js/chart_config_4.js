async (page) => {
  const out = { pasos: [] };
  const log = (m) => out.pasos.push(m);

  // 1) asegurar que el flyout de configuracion esta abierto
  let abierto = await page.evaluate(() => !!document.querySelector('input#combo-input-groupId'));
  if (!abierto) {
    const box = await page.evaluate(() => {
      const t = [...document.querySelectorAll('div')].filter(e => /Gráfico de líneas/.test(e.innerText || '') && e.children.length < 6).pop();
      if (!t) return null;
      const r = t.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + Math.min(40, r.height / 2) };
    });
    if (box) {
      await page.mouse.move(box.x, box.y);
      await page.waitForTimeout(2000);
      const ed = page.locator('button[aria-label="Editar"]:visible').last();
      if (await ed.count()) { await ed.click({ force: true }); log('abrir editar'); await page.waitForTimeout(4000); }
    }
  } else { log('flyout ya abierto'); }

  // 2) grupo de dispositivos
  const g = page.locator('input#combo-input-groupId');
  if (await g.count()) {
    await g.click();
    await page.waitForTimeout(1500);
    await g.fill('');
    await g.type('Nodo DC-ANDES', { delay: 80 });
    await page.waitForTimeout(2500);
    const op = page.locator('[role=option],li,[class*=list-item]').filter({ hasText: 'Nodo DC-ANDES-1' }).first();
    if (await op.count()) { await op.click(); log('grupo elegido'); }
    await page.waitForTimeout(3000);
  }

  // 3) dispositivos -> seleccionar todo
  const d = page.locator('input#combo-input-instanceId');
  if (await d.count()) {
    await d.click();
    await page.waitForTimeout(2500);
    const todo = page.locator('[role=option],li,[class*=list-item]').filter({ hasText: 'Seleccionar todo' }).first();
    if (await todo.count()) { await todo.click(); log('seleccionar todo'); }
    await page.waitForTimeout(3000);
  }

  // 4) telegrama: cuantos checkboxes hay ahora en el flyout
  const chks = await page.evaluate(() => {
    const cont = document.querySelector('input#combo-input-groupId')?.closest('form,div[class]');
    const todos = [...document.querySelectorAll('input[type=checkbox],[role=checkbox]')]
      .map(c => ({ tag: c.tagName, role: c.getAttribute('role'), lbl: (c.getAttribute('aria-label') || c.innerText || '').trim().slice(0, 40), checked: c.checked || c.getAttribute('aria-checked') }));
    return todos.slice(0, 25);
  });
  out.checkboxes = chks;
  out.texto = await page.evaluate(() => document.body.innerText.slice(-700));
  return JSON.stringify(out);
}
