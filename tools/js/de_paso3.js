async (page) => {
  const out = {};
  const inp = page.locator('input[placeholder="Seleccione una telemetría"]').first();
  await inp.click({ force: true });
  await page.waitForTimeout(1500);
  out.opciones = await page.evaluate(() =>
    [...document.querySelectorAll('[role="option"], [class*="popupMenu"] [class*="list-item"]')]
      .map(o => o.innerText.trim()).filter(Boolean).slice(0, 40)
  );
  return JSON.stringify(out);
}
