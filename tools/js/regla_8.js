async (page) => {
  const out = { pasos: [] };
  const rn = page.locator('button:has-text("Cambiar nombre")').first();
  if (await rn.count()) { await rn.click({ force: true }); out.pasos.push('click cambiar nombre'); await page.waitForTimeout(2500); }
  out.inputs = await page.evaluate(() => [...document.querySelectorAll('input,textarea')]
    .map((e) => ({ aria: e.getAttribute('aria-label'), val: (e.value || '').slice(0, 30) })).filter((x) => x.aria));
  out.texto = await page.evaluate(() => document.body.innerText.slice(-450));
  return JSON.stringify(out);
}
