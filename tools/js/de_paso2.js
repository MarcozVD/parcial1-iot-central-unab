async (page) => {
  const out = {};
  const opt = page.locator('[role="option"], [class*="popupMenu"] [class*="list-item"]', { hasText: 'All devices' }).first();
  await opt.click({ force: true });
  await page.waitForTimeout(1500);
  out.grupoSeleccionado = await page.evaluate(() =>
    document.querySelector('input[aria-label="Grupo de dispositivos "]')?.value || null
  );
  return JSON.stringify(out);
}
