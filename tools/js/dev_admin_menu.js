async (page) => {
  const out = {};
  // abrir menu "Administrar dispositivo"
  const m = page.locator('button:has-text("Administrar dispositivo"), [aria-label*="Administrar dispositivo"]').first();
  if (await m.count()) { await m.click(); out.paso = 'abrir menu'; await page.waitForTimeout(2500); }
  const items = await page.evaluate(() => [...document.querySelectorAll('[role=menuitem],[role=option],button,li')]
    .map(e => (e.innerText || '').trim()).filter(t => t && t.length < 50));
  out.items = [...new Set(items)].slice(0, 30);
  return JSON.stringify(out);
}
