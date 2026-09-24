async (page) => {
  const salida = { pasos: [] };
  // pulsar "Restart the simulation" si aparece
  const r = page.getByText('Restart the simulation').first();
  if (await r.count()) { await r.click(); salida.pasos.push('restart'); }
  else salida.pasos.push('sin boton restart');
  for (let i = 0; i < 30; i++) {
    await page.waitForTimeout(6000);
    const t = await page.evaluate(() => document.body.innerText);
    if (/Build failed/.test(t)) { salida.fail = t.slice(t.indexOf('Build failed'), t.indexOf('Build failed') + 600); return JSON.stringify(salida); }
    if (/\[TX\]/.test(t)) { salida.ok = true; salida.serial = t.slice(t.indexOf('[DPS]'), t.indexOf('[TX]') + 300); return JSON.stringify(salida); }
  }
  salida.final = await page.evaluate(() => document.body.innerText.slice(-600));
  return JSON.stringify(salida);
}
