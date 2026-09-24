async (page) => {
  const out = { pasos: [] };
  const libs = ['DHT sensor library for ESPx', 'PubSubClient', 'ArduinoJson'];
  const lm = page.getByText('Library Manager').first();
  if (await lm.count()) { await lm.click(); await page.waitForTimeout(1500); }

  const clickTexto = async (texto) => {
    const box = await page.evaluate((t) => {
      const els = [...document.querySelectorAll('*')].filter(
        (e) => e.children.length === 0 && (e.innerText || '').trim() === t && e.offsetParent !== null);
      if (!els.length) return null;
      const r = els[els.length - 1].getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    }, texto);
    if (!box) return false;
    await page.mouse.click(box.x, box.y);
    return true;
  };

  for (const lib of libs) {
    // abrir el buscador
    const boxAdd = await page.evaluate(() => {
      const b = [...document.querySelectorAll('button')].find((x) => (x.getAttribute('aria-label') || '') === 'Add a new library');
      if (!b) return null;
      const r = b.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    });
    if (boxAdd) { await page.mouse.click(boxAdd.x, boxAdd.y); await page.waitForTimeout(2000); }
    const inp = page.locator('input').first();
    await inp.click();
    await inp.fill('');
    await inp.type(lib, { delay: 55 });
    await page.waitForTimeout(3500);
    const ok = await clickTexto(lib);
    await page.waitForTimeout(3000);
    out.pasos.push(`${lib}: ${ok ? 'click' : 'sin resultado'}`);
  }
  const estado = await page.evaluate(() => document.body.innerText.slice(-350));
  return JSON.stringify({ ...out, estado });
}
