async (page) => {
  const out = { pasos: [] };
  const add = page.locator('button[aria-label="Add a new library"]').first();
  if (await add.count()) { await add.click(); out.pasos.push('abrir add library'); }
  await page.waitForTimeout(3000);
  const antes = await page.evaluate(() => ({
    inputs: [...document.querySelectorAll('input')].map((e) => ({ lbl: e.getAttribute('aria-label') || e.placeholder || '', id: e.id })),
    texto: document.body.innerText.slice(-300)
  }));
  // buscar la primera libreria
  const inp = page.locator('input[type=text], input[type=search], input:not([type])').first();
  out.nInputs = await page.locator('input').count();
  if (out.nInputs) {
    await inp.click();
    await inp.fill('');
    await inp.type('DHT sensor library for ESPx', { delay: 60 });
    out.pasos.push('texto escrito');
    await page.waitForTimeout(3500);
  }
  const res = await page.evaluate(() => ({
    items: [...document.querySelectorAll('[role=option],li,div[class*=result],div[class*=item]')]
      .map((e) => (e.innerText || '').replace(/\n/g, ' | ').trim()).filter((t) => t && t.length < 90).slice(0, 15),
    texto: document.body.innerText.slice(-700)
  }));
  return JSON.stringify({ ...out, antes, ...res });
}
