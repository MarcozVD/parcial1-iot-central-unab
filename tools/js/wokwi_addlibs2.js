async (page) => {
  const out = { pasos: [] };
  // estado actual del gestor de librerias
  out.estado0 = await page.evaluate(() => document.body.innerText.slice(-300));

  const quitarBackdrops = async () => {
    await page.evaluate(() => {
      document.querySelectorAll('.MuiBackdrop-root,[class*=Backdrop]').forEach((e) => {
        e.style.pointerEvents = 'none';
        e.style.display = 'none';
      });
    });
  };

  const libs = ['DHT sensor library for ESPx', 'PubSubClient', 'ArduinoJson'];
  for (const lib of libs) {
    await quitarBackdrops();
    const boxAdd = await page.evaluate(() => {
      const b = [...document.querySelectorAll('button')].find((x) => (x.getAttribute('aria-label') || '') === 'Add a new library' && x.offsetParent !== null);
      if (!b) return null;
      const r = b.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    });
    if (boxAdd) { await page.mouse.click(boxAdd.x, boxAdd.y); await page.waitForTimeout(2200); }
    await quitarBackdrops();
    const inp = page.locator('input:visible').first();
    if (await inp.count()) {
      await inp.click({ force: true });
      await inp.fill('');
      await inp.type(lib, { delay: 55 });
      await page.waitForTimeout(3500);
    }
    await quitarBackdrops();
    const box = await page.evaluate((t) => {
      const els = [...document.querySelectorAll('*')].filter((e) => e.children.length === 0 && (e.innerText || '').trim() === t);
      if (!els.length) return null;
      const r = els[els.length - 1].getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    }, lib);
    if (box) { await page.mouse.click(box.x, box.y); out.pasos.push(lib + ': click'); }
    else out.pasos.push(lib + ': sin resultado visible');
    await page.waitForTimeout(3000);
  }
  out.estado1 = await page.evaluate(() => document.body.innerText.slice(-400));
  return JSON.stringify(out);
}
