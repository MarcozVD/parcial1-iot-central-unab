async (page) => {
  const found = await page.evaluate(() => [...document.querySelectorAll('button,input[type=submit]')]
    .map(e => (e.innerText || e.value || '').trim()).filter(Boolean));
  const btn = page.locator('button:has-text("Continuar"), input[value="Continuar"], #idSIButton9, button[type=submit]').first();
  let clicked = false;
  if (await btn.count()) { await btn.click(); clicked = true; }
  await page.waitForTimeout(5000);
  const st = await page.evaluate(() => ({ url: location.href.slice(0, 120), txt: document.body.innerText.slice(0, 400) }));
  return JSON.stringify({ found, clicked, ...st });
}
