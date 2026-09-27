async (page) => {
  const out = {};
  const btn = page.locator('button', { hasText: 'Analizar' }).last();
  await btn.click({ force: true });
  await page.waitForTimeout(6000);
  out.url = page.url();
  out.texto = await page.evaluate(() => document.body.innerText.slice(0, 500));
  return JSON.stringify(out);
}
