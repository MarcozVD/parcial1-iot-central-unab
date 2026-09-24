async (page) => {
  const out = { pasos: [] };
  await page.goto('https://dcandes1unab.azureiotcentral.com/rules/create', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(8000);
  out.inputs0 = await page.evaluate(() => [...document.querySelectorAll('input')].map((e) => e.getAttribute('aria-label')).filter(Boolean));

  // --- 1) plantilla
  const combo = async (lbl, texto) => {
    const r1 = await page.evaluate((l) => {
      const i = document.querySelector(`input[aria-label^="${l}"]`);
      if (!i) return 'sin input';
      i.focus();
      i.click();
      return 'click';
    }, lbl);
    out.pasos.push(lbl + ' ' + r1);
    await page.waitForTimeout(1200);
    const inp = page.locator(`input[aria-label^="${lbl}"]`).first();
    await inp.type(texto, { delay: 60 });
    await page.waitForTimeout(2500);
    const res = await page.evaluate((t) => {
      const ops = [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item]')]
        .filter((e) => (e.innerText || '').trim().startsWith(t));
      if (!ops.length) return 'sin opciones';
      ops[0].click();
      return 'ok:' + (ops[0].innerText || '').trim().slice(0, 40);
    }, texto);
    out.pasos.push(lbl + ' -> ' + res);
    await page.waitForTimeout(1500);
    return res;
  };
  await combo('Plantilla de dispositivo', 'Nodo DC-ANDES-1');
  await combo('Telemetría', 'Temperatura exhaust');

  // --- 2) operador
  const op = await page.evaluate(() => {
    const d = document.querySelector('div[aria-label="Operador"], [role=combobox][aria-label="Operador"]');
    if (!d) return 'sin operador';
    d.click();
    return 'abierto';
  });
  out.pasos.push('operador ' + op);
  await page.waitForTimeout(1800);
  const opc = await page.evaluate(() => {
    const ops = [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item]')]
      .filter((e) => /es mayor que/i.test((e.innerText || '').trim()));
    if (!ops.length) return 'sin opcion';
    ops[0].click();
    return 'ok';
  });
  out.pasos.push('operador -> ' + opc);
  await page.waitForTimeout(1200);

  // --- 3) valor
  const val = await page.evaluate(() => {
    const i = document.querySelector('input[aria-label^="Valor"]');
    if (!i) return 'sin valor';
    const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    i.focus();
    s.call(i, '35');
    i.dispatchEvent(new Event('input', { bubbles: true }));
    return i.value;
  });
  out.pasos.push('valor ' + val);

  // --- 4) accion correo
  const mail = await page.evaluate(() => {
    const t = [...document.querySelectorAll('*')].find((e) => e.children.length === 0 && (e.innerText || '').trim() === 'Correo electrónico');
    if (!t) return 'sin texto';
    (t.closest('div,button,li') || t).click();
    return 'click';
  });
  out.pasos.push('correo ' + mail);
  await page.waitForTimeout(3000);
  const mailset = await page.evaluate(() => {
    const set = (sel, v) => {
      const el = document.querySelector(sel);
      if (!el) return 'sin ' + sel;
      const proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
      const s = Object.getOwnPropertyDescriptor(proto, 'value').set;
      el.focus();
      s.call(el, v);
      el.dispatchEvent(new Event('input', { bubbles: true }));
      return 'ok';
    };
    return {
      display: set('input[aria-label^="Nombre para mostrar"]', 'Alerta rack temperatura'),
      para: set('input[aria-label^="Para"]', 'mvalera@o365.unab.edu.co'),
      nota: set('textarea[aria-label^="Nota"]', 'Temperatura de exhaust por encima de 35 C en DC-ANDES-1.')
    };
  });
  out.pasos.push(JSON.stringify(mailset));

  // --- 5) NOMBRE de la regla (al final) + guardar
  const nombre = await page.evaluate(() => {
    const i = document.querySelector('input[aria-label^="Escriba un nombre de regla"]');
    if (!i) return 'sin input nombre';
    const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    i.focus();
    s.call(i, 'Alerta temperatura de rack');
    i.dispatchEvent(new Event('input', { bubbles: true }));
    return i.value;
  });
  out.pasos.push('nombre: ' + nombre);
  await page.waitForTimeout(600);
  const g = await page.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find((x) => (x.innerText || '').trim() === 'Guardar');
    if (!b) return 'sin boton';
    b.click();
    return 'click';
  });
  out.pasos.push('guardar: ' + g);
  await page.waitForTimeout(9000);
  out.url = page.url();
  out.modal = await page.evaluate(() => {
    const m = document.querySelector('[class*=modal_interrupt]');
    return m ? m.innerText.slice(0, 180) : null;
  });
  return JSON.stringify(out);
}
