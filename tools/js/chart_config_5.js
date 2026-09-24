async (page) => {
  const out = {};
  const upd = page.locator('button:has-text("Actualizar")').first();
  out.hay = await upd.count();
  if (out.hay) { await upd.click(); out.pasos = ['click actualizar']; }
  await page.waitForTimeout(6000);
  out.texto = await page.evaluate(() => document.body.innerText.slice(-500));
  // guardar el panel
  const guardar = page.locator('button:has-text("Guardar")').first();
  if (await guardar.count()) { await guardar.click(); out.pasos.push('click guardar'); }
  await page.waitForTimeout(6000);
  out.url = page.url();
  out.texto2 = await page.evaluate(() => document.body.innerText.slice(-400));
  return JSON.stringify(out);
}
