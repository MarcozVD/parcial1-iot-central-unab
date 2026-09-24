async (page) => {
  const out = { pasos: [] };
  // localizar el mosaico sin configurar
  const box = await page.evaluate(() => {
    const tiles = [...document.querySelectorAll('div')].filter(e => /No hay ninguna capacidad seleccionada/.test(e.innerText || '') && e.children.length < 6);
    const t = tiles[tiles.length - 1];
    if (!t) return null;
    const r = t.getBoundingClientRect();
    return { x: r.x + r.width / 2, y: r.y + Math.min(40, r.height / 2), w: r.width, h: r.height };
  });
  out.box = box;
  if (box) {
    await page.mouse.move(box.x, box.y);
    await page.waitForTimeout(2500);
    const btns = await page.evaluate(() => [...document.querySelectorAll('button')].map(b => (b.getAttribute('aria-label') || b.innerText || '').replace(/\n/g, ' ').trim()).filter(Boolean).slice(0, 40));
    out.btns_tras_hover = [...new Set(btns)];
    // click en Editar (el que este visible ahora)
    const ed = page.locator('button[aria-label="Editar"]:visible, button:has-text("Editar"):visible').last();
    if (await ed.count()) { await ed.click({ force: true }); out.pasos.push('click editar'); }
    await page.waitForTimeout(5000);
  }
  const d = await page.evaluate(() => ({
    campos: [...document.querySelectorAll('input,textarea,[role=combobox]')]
      .map(e => ({ lbl: (e.getAttribute('aria-label') || e.placeholder || '').trim().slice(0, 50), val: (e.value || '').slice(0, 30) }))
      .filter(x => x.lbl).slice(0, 30),
    texto: document.body.innerText.slice(-1100)
  }));
  return JSON.stringify({ ...out, ...d });
}
