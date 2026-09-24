async (page) => {
  const out = { pasos: [] };
  const r = await page.evaluate(() => {
    const tiles = [...document.querySelectorAll('[class*=tile],[class*=Tile]')];
    const t = tiles.find(e => /Gráfico de líneas/.test(e.innerText || ''));
    if (!t) return { err: 'no tile', n: tiles.length };
    const b = [...t.querySelectorAll('button')].find(x => /Editar/i.test((x.getAttribute('aria-label') || '') + (x.innerText || '')));
    if (!b) return { err: 'no boton editar' };
    b.click();
    return { ok: true };
  });
  out.click = r;
  await page.waitForTimeout(4500);
  const d = await page.evaluate(() => {
    const campos = [...document.querySelectorAll('input,textarea,[role=combobox],[class*=dropdown]')]
      .map(e => ({ tag: e.tagName, lbl: (e.getAttribute('aria-label') || e.placeholder || '').trim().slice(0, 45), role: e.getAttribute('role'), val: (e.value || '').slice(0, 30) }))
      .filter(x => x.lbl);
    const btns = [...document.querySelectorAll('button')].map(b => (b.innerText || b.getAttribute('aria-label') || '').trim()).filter(t => t && t.length < 40);
    return { campos: campos.slice(0, 25), btns: [...new Set(btns)].slice(0, 45), texto: document.body.innerText.slice(-800) };
  });
  return JSON.stringify({ ...out, ...d });
}
