async (page) => {
  const out = { pasos: [] };
  const E = 'C:/Users/mvale/Documents/Parcial1_IoT_Central/evidencias/';

  async function verDatos(url, ruta, etiqueta) {
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(14000);
    const tab = page.getByText('Datos sin procesar', { exact: false }).first();
    if (await tab.count()) {
      await tab.click({ force: true });
      out.pasos.push(etiqueta + ': pestaña Datos sin procesar');
      await page.waitForTimeout(10000);
    }
    await page.setViewportSize({ width: 1500, height: 940 });
    await page.waitForTimeout(700);
    await page.screenshot({ path: ruta });
    out.pasos.push(etiqueta + ': captura');
    const txt = await page.evaluate(() => document.body.innerText);
    const m = txt.match(/Última recepción de datos: [^\n|]+/);
    if (m) { out.pasos.push(etiqueta + ' -> ' + m[0]); }
  }

  // 1) nodo Python corriendo en la máquina Ubuntu
  await verDatos('https://dcandes1unab.azureiotcentral.com/devices/details/DC-RACKC-03', E + 'dia3-datos-rackc.png', 'DC-RACKC-03 (Ubuntu)');
  // 2) nodo ESP32 simulado en Wokwi
  await verDatos('https://dcandes1unab.azureiotcentral.com/devices/details/DC-RACKB-02', E + 'dia3-datos-rackb.png', 'DC-RACKB-02 (Wokwi)');
  // 3) nodo de agua (Wokwi)
  await verDatos('https://dcandes1unab.azureiotcentral.com/devices/details/DC-AGUA-07', E + 'dia3-datos-agua.png', 'DC-AGUA-07 (Wokwi)');

  // 4) panel
  await page.goto('https://dcandes1unab.azureiotcentral.com/dashboards', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(20000);
  await page.screenshot({ path: E + 'dia3-panel.png' });
  out.pasos.push('panel: captura');

  // 5) reglas
  await page.goto('https://dcandes1unab.azureiotcentral.com/rules', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(14000);
  await page.screenshot({ path: E + 'dia3-reglas.png' });
  out.pasos.push('reglas: captura');

  return JSON.stringify(out);
}
