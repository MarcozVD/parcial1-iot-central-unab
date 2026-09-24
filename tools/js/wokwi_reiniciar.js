async (page) => {
  const salida = { pasos: [] };
  // detener la simulacion si esta corriendo (para recompilar con el codigo nuevo)
  const stop = page.locator('button[aria-label="Stop the simulation"]').first();
  if (await stop.count()) { await stop.click(); salida.pasos.push('stop'); await page.waitForTimeout(2500); }
  const start = page.locator('button[aria-label="Start the simulation"]').first();
  if (await start.count()) { await start.click(); salida.pasos.push('start'); }
  else salida.pasos.push('sin boton start');
  for (let i = 0; i < 35; i++) {
    await page.waitForTimeout(6000);
    const t = await page.evaluate(() => document.body.innerText);
    if (/Build failed/.test(t)) { salida.fail = t.slice(t.indexOf('Build failed'), t.indexOf('Build failed') + 600); return JSON.stringify(salida); }
    if (/\[DPS\] resp=|\[DPS\] asignado|\[TX\]/.test(t)) {
      salida.ok = true;
      const i0 = Math.max(0, t.indexOf('[WIFI]'));
      salida.serial = t.slice(i0, t.length);
      return JSON.stringify(salida);
    }
  }
  salida.final = await page.evaluate(() => document.body.innerText.slice(-800));
  return JSON.stringify(salida);
}
