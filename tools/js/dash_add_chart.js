async (page) => {
  const out = { pasos: [] };
  // 1) elegir "Grafico de lineas" en la galeria
  const opt = page.locator('text=Gráfico de líneas').first();
  if (await opt.count()) { await opt.click(); out.pasos.push('clic grafico de lineas'); }
  await page.waitForTimeout(1500);
  // 2) agregar mosaico
  const add = page.locator('button:has-text("Agregar mosaico"), button[aria-label*="Agregar mosaico"]').first();
  if (await add.count()) { await add.click(); out.pasos.push('clic agregar mosaico'); }
  await page.waitForTimeout(5000);
  const d = await page.evaluate(() => {
    const inputs = [...document.querySelectorAll('input,textarea,[role=combobox]')]
      .map(e => ({ lbl: (e.getAttribute('aria-label') || e.placeholder || '').trim().slice(0, 40), val: (e.value || '').slice(0, 40), role: e.getAttribute('role') }))
      .filter(x => x.lbl);
    const btns = [...document.querySelectorAll('button')].map(b => (b.innerText || b.getAttribute('aria-label') || '').trim()).filter(t => t && t.length < 40);
    return { inputs: inputs.slice(0, 25), btns: [...new Set(btns)].slice(0, 40), texto: document.body.innerText.slice(-900) };
  });
  return JSON.stringify({ ...out, ...d });
}
