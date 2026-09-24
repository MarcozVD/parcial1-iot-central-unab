async (page) => {
  const log = [];
  await page.goto('https://login.microsoft.com/device', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(3500);
  const code = 'AP4A65KPD';
  // input del código
  const inp = page.locator('input#otc, input[name=otc], input[type=text]').first();
  if (await inp.count()) { await inp.fill(code); log.push('code filled'); }
  await page.waitForTimeout(500);
  const next = page.locator('button[type=submit], #idSIButton9').first();
  if (await next.count()) { await next.click(); log.push('next clicked'); }
  await page.waitForTimeout(4000);

  // posible selector de cuenta
  const tile = page.locator('div[role=button], .tile').filter({ hasText: 'mvalera@o365.unab.edu.co' }).first();
  if (await tile.count()) { await tile.click(); log.push('account picked'); await page.waitForTimeout(3500); }

  // posible botón Continuar
  const cont = page.locator('button:has-text("Continuar"), button:has-text("Continue")').first();
  if (await cont.count()) { await cont.click(); log.push('continue clicked'); await page.waitForTimeout(3000); }

  const state = await page.evaluate(() => ({ url: location.href, txt: document.body.innerText.slice(0, 700) }));
  return JSON.stringify({ log, ...state });
}
