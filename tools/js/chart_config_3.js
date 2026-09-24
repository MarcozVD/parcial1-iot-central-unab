async (page) => {
  const out = { pasos: [] };
  const log = (m) => out.pasos.push(m);

  // expandir la seccion "Telemetria" (header colapsado)
  const r = await page.evaluate(() => {
    const h = [...document.querySelectorAll('div,span,button,h3')].find(e => /^Telemetría$/.test((e.innerText || '').trim()));
    if (!h) return 'no header';
    let cont = h.closest('[class*=section],[class*=Section],div');
    const trig = cont ? cont.querySelector('[class*=ActionTrigger],button') : null;
    if (trig) { trig.click(); return 'click trigger'; }
    h.click(); return 'click header';
  });
  log('telemetria: ' + r);
  await page.waitForTimeout(3000);

  const chks = await page.evaluate(() => [...document.querySelectorAll('input[type=checkbox]')]
    .map((c, i) => ({ i, lbl: (c.getAttribute('aria-label') || (c.closest('label') ? c.closest('label').innerText : '') || '').trim().slice(0, 40), checked: c.checked })));
  log('checkboxes: ' + JSON.stringify(chks.slice(0, 12)));

  // marcar tempIntake y tempExhaust
  for (const nombre of ['Temperatura intake (rack)', 'Temperatura exhaust (rack)']) {
    const c = page.locator(`input[type=checkbox][aria-label*="${nombre}"]`).first();
    if (await c.count()) { await c.check({ force: true }); log('marcado ' + nombre); }
  }
  await page.waitForTimeout(1500);
  const upd = page.locator('button:has-text("Actualizar")').first();
  if (await upd.count()) { await upd.click(); log('actualizar'); }
  await page.waitForTimeout(5000);
  return JSON.stringify({ ...out, texto: await page.evaluate(() => document.body.innerText.slice(-400)) });
}
