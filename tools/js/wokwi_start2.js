async (page) => {
  const salida = { pasos: [] };
  await page.evaluate(() => {
    document.querySelectorAll('.MuiBackdrop-root').forEach((e) => { e.style.display = 'none'; });
  });
  const btn = page.locator('button[aria-label="Start the simulation"]').first();
  if (!(await btn.count())) { salida.error = 'sin boton start'; return JSON.stringify(salida); }
  await btn.click();
  salida.pasos.push('start pulsado');
  for (let i = 0; i < 30; i++) {
    await page.waitForTimeout(6000);
    const t = await page.evaluate(() => document.body.innerText);
    if (/Build failed/.test(t)) {
      const i0 = t.indexOf('Build failed');
      salida.build_failed = t.slice(i0, i0 + 700);
      return JSON.stringify(salida);
    }
    if (/\[TX\]/.test(t)) {
      const i0 = t.indexOf('[WIFI]');
      salida.ok = true;
      salida.serial = t.slice(i0 >= 0 ? i0 : t.indexOf('[DPS]'), t.indexOf('[TX]') + 400);
      return JSON.stringify(salida);
    }
    if (/too busy|SEE PRICING|taking longer than expected/i.test(t)) { salida.cola = true; }
  }
  salida.final = await page.evaluate(() => document.body.innerText.slice(-900));
  return JSON.stringify(salida);
}
