async (page) => {
  const out = { pasos: [] };
  const esperar = (ms) => page.waitForTimeout(ms);

  const combo = async (lbl, texto) => {
    const inp = page.locator(`input[aria-label^="${lbl}"]`).first();
    if (!(await inp.count())) { out.pasos.push(lbl + ': sin input'); return false; }
    await inp.click({ force: true });
    await inp.fill('');
    await inp.type(texto, { delay: 55 });
    await esperar(2500);
    const res = await page.evaluate((t) => {
      const ops = [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item]')]
        .filter((e) => (e.innerText || '').trim().startsWith(t));
      if (!ops.length) return false;
      ops[0].click();
      return true;
    }, texto);
    await esperar(1500);
    out.pasos.push(lbl + ': ' + res);
    return res;
  };

  await combo('Plantilla de dispositivo', 'Nodo DC-ANDES-1');
  await combo('Telemetría', 'Temperatura exhaust');
  await page.evaluate(() => { const d = document.querySelector('div[aria-label="Operador"], [role=combobox][aria-label="Operador"]'); if (d) d.click(); });
  await esperar(1800);
  out.operador = await page.evaluate(() => {
    const ops = [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item]')].filter((e) => /es mayor que/i.test((e.innerText || '').trim()));
    if (!ops.length) return false;
    ops[0].click();
    return true;
  });
  await esperar(1200);
  // valor: radio "Escriba un valor" + numero
  await page.evaluate(() => {
    const r = [...document.querySelectorAll('input[type=radio]')][0];
    if (r) r.click();
  });
  await esperar(800);
  out.valor = await page.evaluate(() => {
    const i = document.querySelector('input[aria-label^="Valor"]');
    if (!i) return 'sin valor';
    const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    i.focus(); s.call(i, '35'); i.dispatchEvent(new Event('input', { bubbles: true }));
    return i.value;
  });
  await esperar(800);
  // accion de correo
  await page.evaluate(() => {
    const t = [...document.querySelectorAll('*')].find((e) => e.children.length === 0 && (e.innerText || '').trim() === 'Correo electrónico');
    if (t) (t.closest('div,button,li') || t).click();
  });
  await esperar(3000);
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
  await esperar(1200);
  const listo = page.locator('button:has-text("Listo")').first();
  if (await listo.count()) { await listo.click({ force: true }); out.pasos.push('Listo'); await esperar(3000); }
  // nombre: encabezado editable (placeholder, sin aria-label)
  const nom = page.locator('input[placeholder="Escriba un nombre de regla"]').first();
  if (await nom.count()) {
    await nom.click();
    await page.keyboard.type('Alerta temperatura de rack', { delay: 45 });
    out.nombre = await nom.inputValue();
  } else { out.nombre = 'sin campo'; }
  await esperar(700);
  const g = page.locator('button:has-text("Guardar")').first();
  if (await g.count()) { await g.click(); out.pasos.push('guardar'); } else { out.pasos.push('sin boton guardar'); }
  await esperar(9000);
  out.url = page.url();
  out.modal = await page.evaluate(() => {
    const m = document.querySelector('[class*=modal_interrupt]');
    return m ? m.innerText.slice(0, 150) : null;
  });
  return JSON.stringify(out);
}
