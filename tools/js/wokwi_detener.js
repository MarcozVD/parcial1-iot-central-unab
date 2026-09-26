async (page) => {
  const out = { pasos: [] };
  // botón de detener de la simulación de Wokwi (cuadrado): probar varios selectores
  const cands = [
    'button[aria-label="Stop the simulation" i]',
    'button[aria-label*="stop" i]',
    'button[title*="stop" i]',
  ];
  for (const sel of cands) {
    const b = page.locator(sel).first();
    if (await b.count()) {
      await b.click({ force: true });
      out.pasos.push('detenida con ' + sel);
      await page.waitForTimeout(2500);
      out.pantalla = await page.evaluate(() => document.body.innerText.slice(-160));
      return JSON.stringify(out);
    }
  }
  // alternativa: el control de simulación expone un botón por texto
  for (const t of ['Stop', 'Detener']) {
    const b = page.getByRole('button', { name: t }).first();
    if (await b.count()) { await b.click({ force: true }); out.pasos.push('detenida por texto ' + t); await page.waitForTimeout(2500); return JSON.stringify(out); }
  }
  // último recurso: leer los atributos aria de los botones de la barra
  out.botones = await page.evaluate(() => [...document.querySelectorAll('button')].map((b) => b.getAttribute('aria-label') || b.title || b.innerText.trim()).filter(Boolean).slice(0, 25));
  return JSON.stringify(out);
}
