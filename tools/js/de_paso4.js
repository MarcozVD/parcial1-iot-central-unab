async (page) => {
  const out = {};
  const opt = page.locator('[role="option"], [class*="popupMenu"] [class*="list-item"]', { hasText: 'Temperatura intake (rack)' }).first();
  await opt.click({ force: true });
  await page.waitForTimeout(1500);
  out.click1 = 'ok';
  // buscar boton Analizar
  const btn = page.locator('button', { hasText: 'Analizar' }).first();
  out.analizarExiste = await btn.count();
  return JSON.stringify(out);
}
