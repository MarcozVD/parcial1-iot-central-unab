async (page) => {
  const out = {};
  const tf = page.locator('button', { hasText: 'Last 24 Hours' }).first();
  out.tf = await tf.count();
  if (out.tf) { await tf.click({ force: true }); await page.waitForTimeout(1500); }
  out.texto = await page.evaluate(() => {
    const c = document.querySelector('[class*="Callout"], [role="dialog"], [class*="timePicker"], [class*="dateRange"]');
    return c ? c.innerText.slice(0, 900) : document.body.innerText.slice(-900);
  });
  out.inputs = await page.evaluate(() => [...document.querySelectorAll('input')].filter(i => i.offsetParent)
    .map(i => ({ a: i.getAttribute('aria-label'), p: i.placeholder, v: i.value, t: i.type })).slice(0, 20));
  return JSON.stringify(out);
}
