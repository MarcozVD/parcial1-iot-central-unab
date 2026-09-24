async (page) => {
  const out = { pasos: [] };
  // cerrar dialogos y abrir Library Manager
  await page.evaluate(() => document.querySelectorAll('.MuiBackdrop-root').forEach((e) => { e.style.display = 'none'; }));
  const lm = page.getByText('Library Manager').first();
  if (await lm.count()) { await lm.click(); await page.waitForTimeout(2500); }
  const txt = await page.evaluate(() => document.body.innerText.slice(-420));
  out.txt = txt;
  const libs = ['DHT sensor library for ESPx', 'PubSubClient', 'ArduinoJson'];
  for (const lib of libs) {
    if (txt.includes(lib)) { out.pasos.push(lib + ': ya instalada'); continue; }
    await page.evaluate(() => document.querySelectorAll('.MuiBackdrop-root').forEach((e) => { e.style.display = 'none'; }));
    const add = page.locator('button[aria-label="Add a new library"]').first();
    if (await add.count()) { await add.click({ force: true }); await page.waitForTimeout(2200); }
    await page.evaluate(() => document.querySelectorAll('.MuiBackdrop-root').forEach((e) => { e.style.display = 'none'; }));
    const inp = page.locator('input:visible').first();
    if (await inp.count()) {
      await inp.click({ force: true });
      await inp.fill('');
      await inp.type(lib, { delay: 55 });
      await page.waitForTimeout(3500);
    }
    await page.evaluate(() => document.querySelectorAll('.MuiBackdrop-root').forEach((e) => { e.style.display = 'none'; }));
    const box = await page.evaluate((t) => {
      const els = [...document.querySelectorAll('*')].filter((e) => e.children.length === 0 && (e.innerText || '').trim() === t);
      if (!els.length) return null;
      const r = els[els.length - 1].getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    }, lib);
    if (box) { await page.mouse.click(box.x, box.y); out.pasos.push(lib + ': click'); }
    else out.pasos.push(lib + ': sin resultado');
    await page.waitForTimeout(3000);
  }
  out.txt_final = await page.evaluate(() => document.body.innerText.slice(-380));
  return JSON.stringify(out);
}
