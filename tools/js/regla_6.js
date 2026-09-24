async (page) => {
  const out = { pasos: [] };
  // cerrar modal de error
  const cerrar = page.locator('[class*=modal_interrupt] button[aria-label="Cerrar"], button[aria-label="Cerrar"]').first();
  if (await cerrar.count()) { await cerrar.click({ force: true }); await page.waitForTimeout(1800); }
  out.modal = await page.evaluate(() => !!(document.querySelector('[class*=modal_interrupt]')));

  // el nombre se escribe AL FINAL: el formulario lo reinicia al re-renderizar otros campos
  const nom = page.locator('input[aria-label^="Escriba un nombre de regla"]').first();
  await nom.click();
  await page.keyboard.press('Control+a');
  await page.keyboard.type('Alerta temperatura de rack (exhaust)', { delay: 40 });
  await page.waitForTimeout(800);
  out.nombre = await nom.inputValue();
  out.estado = await page.evaluate(() => ({
    valor: (document.querySelector('input[aria-label^="Valor"]') || {}).value,
    para: (document.querySelector('input[aria-label^="Para"]') || {}).value,
    plantilla: (document.querySelector('input[aria-label^="Plantilla de dispositivo"]') || {}).value,
    telemetria: (document.querySelector('input[aria-label^="Telemetría"]') || {}).value
  }));
  const guardar = page.locator('button:has-text("Guardar")').first();
  await guardar.click();
  await page.waitForTimeout(9000);
  out.url = page.url();
  out.modal2 = await page.evaluate(() => {
    const m = document.querySelector('[class*=modal_interrupt]');
    return m ? m.innerText.slice(0, 200) : null;
  });
  return JSON.stringify(out);
}
