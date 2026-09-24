async (page) => {
  const out = {};
  // el campo Valor del caso booleano: el desplegable que muestra "Seleccione un valor"
  const d = page.locator('div:has-text("Valor *")').last();
  const abierto = await page.evaluate(() => {
    // buscar el combobox del bloque Valor
    const labels = [...document.querySelectorAll('*')].filter((e) => e.children.length === 0 && /^Valor \*$/.test((e.innerText || '').trim()));
    if (!labels.length) return 'sin label Valor';
    const cont = labels[0].closest('div[class*=field],div[class*=Field],div');
    const combo = cont ? cont.querySelector('[role=combobox],[class*=Dropdown],button') : null;
    if (combo) { combo.click(); return 'click:' + (combo.className || '').toString().slice(0, 40); }
    // fallback: el ultimo combobox visible
    const cbs = [...document.querySelectorAll('[role=combobox]')].filter((e) => e.offsetParent !== null);
    if (cbs.length) { cbs[cbs.length - 1].click(); return 'fallback'; }
    return 'sin combo';
  });
  out.abierto = abierto;
  await page.waitForTimeout(2200);
  out.opciones = await page.evaluate(() => [...document.querySelectorAll('[role=option],li,[class*=list-item],[class*=Dropdown-item],[role=listbox] *')].map((e) => (e.innerText || '').trim()).filter(Boolean).slice(0, 12));
  out.html = await page.evaluate(() => {
    const pops = [...document.querySelectorAll('[class*=Callout],[class*=callout],[role=listbox],[class*=popup]')];
    return pops.map((p) => (p.innerText || '').trim().slice(0, 120)).filter(Boolean).slice(0, 4);
  });
  return JSON.stringify(out);
}
