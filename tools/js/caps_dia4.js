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
    const est = (txt.match(/Conectado|Desconectado/) || ['?'])[0];
    const m = txt.match(/Última recepción de datos: [^\n|]+/);
    if (m) { out.pasos.push(etiqueta + ' -> ' + est + ' | ' + m[0]); }
  }

  // dia 4: nodos del servidor Ubuntu
  await verDatos('https://dcandes1unab.azureiotcentral.com/devices/details/DC-RACKC-03', E + 'dia4-datos-rackc.png', 'DC-RACKC-03 (Ubuntu)');
  await verDatos('https://dcandes1unab.azureiotcentral.com/devices/details/DC-HUMO-08', E + 'dia4-datos-humo.png', 'DC-HUMO-08 (Ubuntu)');
  await verDatos('https://dcandes1unab.azureiotcentral.com/devices/details/DC-RACKB-02', E + 'dia4-datos-rackb.png', 'DC-RACKB-02 (Wokwi)');

  // flota completa
  await page.goto('https://dcandes1unab.azureiotcentral.com/devices', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(18000);
  await page.screenshot({ path: E + 'dia4-portal-flota.png' });
  out.pasos.push('flota: captura');

  return JSON.stringify(out);
}
