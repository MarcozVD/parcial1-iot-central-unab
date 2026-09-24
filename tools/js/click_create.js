async (page) => {
  const btn = page.locator('button:has-text("Crear")').last();
  const n = await page.locator('button:has-text("Crear")').count();
  await btn.click();
  await page.waitForTimeout(8000);
  const res = await page.evaluate(() => ({ url: location.href, txt: document.body.innerText.slice(0, 900) }));
  return JSON.stringify({ n, ...res });
}
