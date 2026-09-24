async (page) => {
  const salida = { pasos: [] };
  const estado = async () => page.evaluate(() => ({
    stop: !!document.querySelector('button[aria-label="Stop the simulation"]'),
    start: !!document.querySelector('button[aria-label="Start the simulation"]'),
    build: /Building|Compiling/.test(document.body.innerText),
    error: /Error during build|Build failed/.test(document.body.innerText),
    txt: document.body.innerText.slice(-300)
  }));
  salida.inicial = await estado();
  // detener
  if (salida.inicial.stop) {
    await page.locator('button[aria-label="Stop the simulation"]').first().click();
    salida.pasos.push('stop');
    await page.waitForTimeout(4000);
  }
  // arrancar
  const st = await estado();
  if (st.start) {
    await page.locator('button[aria-label="Start the simulation"]').first().click();
    salida.pasos.push('start');
  } else {
    salida.pasos.push('sin boton start: ' + JSON.stringify(st.txt.slice(-160)));
  }
  for (let i = 0; i < 40; i++) {
    await page.waitForTimeout(6000);
    const t = await page.evaluate(() => document.body.innerText);
    if (/Error during build|Build failed/.test(t)) {
      const i0 = Math.max(0, t.lastIndexOf('sketch.ino:', t.indexOf('Error during build')));
      salida.fallo_build = t.slice(i0 - 200, t.indexOf('Error during build') + 60);
      return JSON.stringify(salida);
    }
    if (/\[DPS\] resp=|\[DPS\] asignado|\[TX\]/.test(t)) {
      salida.ok = true;
      salida.serial = t.slice(Math.max(0, t.indexOf('[WIFI]')), t.length);
      return JSON.stringify(salida);
    }
  }
  salida.final = await page.evaluate(() => document.body.innerText.slice(-500));
  return JSON.stringify(salida);
}
