async (page) => {
  const out = {};
  await page.locator('button[aria-label="Editar"]').first().click();
  await page.waitForTimeout(5000);
  out.url = page.url();
  const d = await page.evaluate(() => {
    const tiles = [...document.querySelectorAll('[class*=tile],[class*=Tile]')]
      .map(e => (e.innerText || '').replace(/\n/g, ' | ').trim().slice(0, 80)).filter(Boolean);
    const botones = [...document.querySelectorAll('button')].map(b => (b.innerText || b.getAttribute('aria-label') || '').trim())
      .filter(t => t && t.length < 45);
    return { tiles: [...new Set(tiles)].slice(0, 20), botones: [...new Set(botones)].slice(0, 45),
             texto: document.body.innerText.slice(0, 500) };
  });
  return JSON.stringify(d);
}
