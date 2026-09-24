async (page) => {
  const info = await page.evaluate(() => {
    const els = [...document.querySelectorAll('a,button')].filter(e => /Crear aplicaci/i.test(e.innerText || ''));
    const map = els.map((e, i) => i + ':' + e.tagName + ':' + (e.innerText || '').trim().slice(0, 30));
    return map;
  });
  if (info.length === 0) return { ok: false, info };
  // click real sobre el primero (Aplicación personalizada)
  const el = page.locator('a:has-text("Crear aplicación"), button:has-text("Crear aplicación")').first();
  await el.click();
  await page.waitForTimeout(4000);
  return { ok: true, info, url: page.url() };
}
