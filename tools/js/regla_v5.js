async (page) => {
  const out = { pasos: [] };
  // 1) desde la lista de reglas -> Nuevo (es el flujo que expone el campo de nombre)
  await page.goto('https://dcandes1unab.azureiotcentral.com/rules', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(7000);
  const nuevo = page.locator('button:has-text("Nuevo"), a:has-text("Nuevo")').first();
  if (await nuevo.count()) { await nuevo.click(); out.pasos.push('Nuevo'); await page.waitForTimeout(7000); }
  out.inputs = await page.evaluate(() => [...document.querySelectorAll('input')].map((e) => e.getAttribute('aria-label')).filter(Boolean));

  const combo = async (lbl, texto) => {
    await page.evaluate((l) => { const i = document.querySelector(`input[aria-label^="${l}"]`); if (i) { i.focus(); i.click(); } }, lbl);
    await page.waitForTimeout(1200);
    const inp = page.locator(`input[aria-label^="${lbl}"]`).first();
    await inp.type(texto, { delay: 55 });
    await page.waitForTimeout(2500);
    const res = await page.evaluate((t) => {
      const ops = [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item]')].filter((e) => (e.innerText || '').trim().startsWith(t));
      if (!ops.length) return 'sin opciones';
      ops[0].click();
      return 'ok';
    }, texto);
    out.pasos.push(lbl + ': ' + res);
    await page.waitForTimeout(1500);
  };
  await combo('Plantilla de dispositivo', 'Nodo DC-ANDES-1');
  await combo('Telemetría', 'Temperatura exhaust');
  await page.evaluate(() => { const d = document.querySelector('div[aria-label="Operador"], [role=combobox][aria-label="Operador"]'); if (d) d.click(); });
  await page.waitForTimeout(1800);
  await page.evaluate(() => {
    const ops = [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item]')].filter((e) => /es mayor que/i.test((e.innerText || '').trim()));
    if (ops.length) ops[0].click();
  });
  await page.waitForTimeout(1200);
  await page.evaluate(() => {
    const i = document.querySelector('input[aria-label^="Valor"]');
    if (!i) return;
    const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    i.focus(); s.call(i, '35'); i.dispatchEvent(new Event('input', { bubbles: true }));
  });
  out.pasos.push('condiciones listas');
  // 2) accion correo + Listo
  await page.evaluate(() => {
    const t = [...document.querySelectorAll('*')].find((e) => e.children.length === 0 && (e.innerText || '').trim() === 'Correo electrónico');
    if (t) (t.closest('div,button,li') || t).click();
  });
  await page.waitForTimeout(3000);
  await page.evaluate(() => {
    const set = (sel, v) => {
      const el = document.querySelector(sel);
      if (!el) return;
      const proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
      const s = Object.getOwnPropertyDescriptor(proto, 'value').set;
      el.focus(); s.call(el, v); el.dispatchEvent(new Event('input', { bubbles: true }));
    };
    set('input[aria-label^="Nombre para mostrar"]', 'Alerta rack temperatura');
    set('input[aria-label^="Para"]', 'mvalera@o365.unab.edu.co');
    set('textarea[aria-label^="Nota"]', 'Temperatura de exhaust por encima de 35 C en DC-ANDES-1.');
  });
  await page.waitForTimeout(1200);
  const listo = page.locator('button:has-text("Listo")').first();
  if (await listo.count()) { await listo.click({ force: true }); out.pasos.push('Listo'); await page.waitForTimeout(3000); }
  // 3) nombre con teclado real + guardar
  const nom = page.locator('input[aria-label^="Escriba un nombre de regla"]').first();
  if (await nom.count()) {
    await nom.click();
    await page.keyboard.type('Alerta temperatura de rack', { delay: 45 });
    out.nombre = await nom.inputValue();
  } else { out.nombre = 'sin campo'; }
  await page.waitForTimeout(600);
  const g = page.locator('button:has-text("Guardar")').first();
  if (await g.count()) { await g.click(); out.pasos.push('guardar'); }
  await page.waitForTimeout(9000);
  out.url = page.url();
  out.modal = await page.evaluate(() => {
    const m = document.querySelector('[class*=modal_interrupt]');
    return m ? m.innerText.slice(0, 150) : null;
  });
  return JSON.stringify(out);
}
