async (page) => {
  const out = { pasos: [] };
  const esperar = (ms) => page.waitForTimeout(ms);
  // ir a la lista y crear una regla nueva
  await page.goto('https://dcandes1unab.azureiotcentral.com/rules', { waitUntil: 'domcontentloaded' });
  await esperar(6000);
  const nuevo = page.locator('button:has-text("Nuevo"), a:has-text("Nuevo")').first();
  if (await nuevo.count()) { await nuevo.click(); await esperar(6000); }

  const combo = async (lbl, texto) => {
    const inp = page.locator(`input[aria-label^="${lbl}"]`).first();
    if (!(await inp.count())) { out.pasos.push(lbl + ': sin input'); return false; }
    await inp.click({ force: true });
    await inp.fill('');
    await inp.type(texto, { delay: 55 });
    await esperar(2500);
    const r = await page.evaluate((t) => {
      const ops = [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item]')]
        .filter((e) => (e.innerText || '').trim().startsWith(t));
      if (!ops.length) return false;
      ops[0].click();
      return true;
    }, texto);
    await esperar(1500);
    out.pasos.push(lbl + ': ' + r);
    return r;
  };

  await combo('Plantilla de dispositivo', 'Nodo DC-ANDES-1');
  await combo('Telemetría', 'Humedad de piso tecnico');
  await page.evaluate(() => { const d = document.querySelector('div[aria-label="Operador"], [role=combobox][aria-label="Operador"]'); if (d) d.click(); });
  await esperar(1800);
  out.operador = await page.evaluate((op) => {
    const ops = [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item]')]
      .filter((e) => (e.innerText || '').trim().toLowerCase() === op.toLowerCase());
    if (!ops.length) return false;
    ops[0].click();
    return true;
  }, 'Es mayor que');
  await esperar(1500);

  // valor: si es booleano aparece un desplegable "Seleccione un valor"
  const esBool = '70' === 'true' || '70' === 'false';
  if (esBool) {
    await page.evaluate(() => {
      const radios = [...document.querySelectorAll('input[type=radio]')];
      const r = radios.find((x) => /Seleccione un valor/i.test((x.closest('div') || {}).innerText || ''));
      if (r) r.click();
    });
    await esperar(1500);
    await page.evaluate(() => {
      const d = [...document.querySelectorAll('[role=combobox],div[class*=Dropdown]')].pop();
      if (d) d.click();
    });
    await esperar(1800);
    out.valorBool = await page.evaluate((v) => {
      const ops = [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item],[class*=Dropdown-item]')]
        .filter((e) => /verdadero|true|falso|false/i.test((e.innerText || '').trim()));
      const buscado = v === 'true' ? /verdadero|true/i : /falso|false/i;
      const op = ops.find((e) => buscado.test((e.innerText || '').trim()));
      if (!op) return 'sin opcion booleana (' + ops.length + ')';
      op.click();
      return (op.innerText || '').trim();
    }, '70');
    await esperar(1500);
  } else {
    await page.evaluate((v) => {
      const r = [...document.querySelectorAll('input[type=radio]')].find((x) => /escriba un valor/i.test((x.closest('div') || {}).innerText || ''));
      if (r) r.click();
    });
    await esperar(800);
    out.valor = await page.evaluate((v) => {
      const i = document.querySelector('input[aria-label^="Valor"]');
      if (!i) return 'sin valor';
      const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      i.focus(); s.call(i, v); i.dispatchEvent(new Event('input', { bubbles: true }));
      return i.value;
    }, '70');
    await esperar(800);
  }

  // accion: correo
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
    set('input[aria-label^="Nombre para mostrar"]', 'Alerta DC-ANDES-1');
    set('input[aria-label^="Para"]', 'mvalera@o365.unab.edu.co');
    set('textarea[aria-label^="Nota"]', 'Humedad de piso tecnico por encima de 70 %: posible fuga o condensacion.');
  });
  await esperar(1200);
  const listo = page.locator('button:has-text("Listo")').first();
  if (await listo.count()) { await listo.click({ force: true }); await esperar(3000); }

  // nombre de la regla (encabezado editable sin aria-label) y guardar
  const nom = page.locator('input[placeholder="Escriba un nombre de regla"]').first();
  if (await nom.count()) {
    await nom.click();
    await page.keyboard.type('Alerta humedad en piso tecnico', { delay: 40 });
    out.nombre = await nom.inputValue();
  } else { out.nombre = 'sin campo'; }
  await esperar(700);
  const g = page.locator('button:has-text("Guardar")').first();
  if (await g.count()) { await g.click(); out.pasos.push('guardar'); } else { out.pasos.push('sin boton guardar'); }
  await esperar(9000);
  out.url = page.url();
  out.modal = await page.evaluate(() => {
    const m = document.querySelector('[class*=modal_interrupt]');
    return m ? m.innerText.slice(0, 140) : null;
  });
  return JSON.stringify(out);
}
