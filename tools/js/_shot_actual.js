async (page) => {
  await page.goto('https://dcandes1unab.azureiotcentral.com/devices', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(20000);
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'C:/Users/mvale/Documents/Parcial1_IoT_Central/evidencias/07-flota-conexion-24sep.png' });
  return page.url();
}