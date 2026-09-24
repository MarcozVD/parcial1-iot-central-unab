async (page) => {
  const out = { pasos: [] };
  const nom = page.locator('input[aria-label^="Escriba un nombre de regla"]').first();
  if (await nom.count()) { await nom.fill('Alerta temperatura de rack (exhaust)'); out.nombre = await nom.inputValue(); }
  await page.waitForTimeout(1000);
  // estado del formulario
  out.estado = await page.evaluate(() => ({
    plantilla: (document.querySelector('input[aria-label^="Plantilla de dispositivo"]') || {}).value,
    telemetria: (document.querySelector('input[aria-label^="Telemetría"]') || {}).value,
    valor: (document.querySelector('input[aria-label^="Valor"]') || {}).value,
    para: (document.querySelector('input[aria-label^="Para"]') || {}).value,
    errores: [...document.querySelectorAll('[class*=error],[role=alert]')].map((e) => (e.innerText || '').trim()).filter(Boolean).slice(0, 5),
    guardar_disabled: !!document.querySelector('button[disabled]')
  }));
  const guardar = page.locator('button:has-text("Guardar")').first();
  if (await guardar.count()) { await guardar.click(); out.pasos.push('guardar 2'); }
  await page.waitForTimeout(9000);
  out.url = page.url();
  return JSON.stringify(out);
}
