async (page) => {
  const out = { pasos: [] };
  // formulario limpio
  await page.goto('https://dcandes1unab.azureiotcentral.com/rules/create', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(7000);

  const setReact = async (sel, valor) => page.evaluate(([s, v]) => {
    const el = document.querySelector(s);
    if (!el) return 'sin elemento';
    el.focus();
    const proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
    const set = Object.getOwnPropertyDescriptor(proto, 'value').set;
    set.call(el, v);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    return el.value;
  }, [sel, valor]);

  const elegirCombo = async (lbl, texto) => {
    const inp = page.locator(`input[aria-label^="${lbl}"]`).first();
    await inp.click({ force: true });
    await inp.fill('');
    await inp.type(texto, { delay: 55 });
    await page.waitForTimeout(2200);
    const ok = await page.evaluate((t) => {
      const ops = [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item]')]
        .filter((e) => (e.innerText || '').trim() === t);
      if (!ops.length) return false;
      ops[ops.length - 1].click();
      return true;
    }, texto);
    await page.waitForTimeout(1500);
    return ok;
  };

  // 1) plantilla y telemetria
  out.plantilla = await elegirCombo('Plantilla de dispositivo', 'Nodo DC-ANDES-1');
  out.telemetria = await elegirCombo('Telemetría', 'Temperatura exhaust (rack)');
  // 2) operador
  await page.evaluate(() => {
    const d = document.querySelector('div[aria-label="Operador"], [role=combobox][aria-label="Operador"]');
    if (d) d.click();
  });
  await page.waitForTimeout(1800);
  out.operador = await page.evaluate(() => {
    const ops = [...document.querySelectorAll('[role=option],li,[class*=popupMenu] [class*=list-item]')]
      .filter((e) => /mayor que/i.test((e.innerText || '').trim()));
    if (!ops.length) return false;
    ops[0].click();
    return true;
  });
  await page.waitForTimeout(1200);
  // 3) valor
  out.valor = await setReact('input[aria-label^="Valor"]', '35');
  // 4) accion de correo
  await page.evaluate(() => {
    const t = [...document.querySelectorAll('*')].find((e) => e.children.length === 0 && (e.innerText || '').trim() === 'Correo electrónico');
    if (t) { const b = t.closest('div,button,li') || t; b.click(); }
  });
  await page.waitForTimeout(3000);
  out.nombre_display = await setReact('input[aria-label^="Nombre para mostrar"]', 'Alerta rack - temperatura exhaust');
  out.para = await setReact('input[aria-label^="Para"]', 'mvalera@o365.unab.edu.co');
  out.nota = await setReact('textarea[aria-label^="Nota"]', 'Temperatura de exhaust del rack por encima de 35 C. Revisar contencion y free-cooling.');
  await page.waitForTimeout(800);
  // 5) NOMBRE DE LA REGLA al final
  out.nombre = await setReact('input[aria-label^="Escriba un nombre de regla"]', 'Alerta temperatura de rack');
  await page.waitForTimeout(800);
  // 6) guardar
  out.guardar = await page.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find((x) => (x.innerText || '').trim() === 'Guardar');
    if (!b) return false;
    b.click();
    return true;
  });
  await page.waitForTimeout(9000);
  out.url = page.url();
  out.modal = await page.evaluate(() => {
    const m = document.querySelector('[class*=modal_interrupt]');
    return m ? m.innerText.slice(0, 180) : null;
  });
  return JSON.stringify(out);
}
