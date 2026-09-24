async (page) => {
  await page.goto('https://dcandes1unab.azureiotcentral.com/devices/details/DC-RACKA-01/rawdata', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(10000);
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'C:/Users/mvale/Documents/Parcial1_IoT_Central/evidencias/05-datos-crudos-racka-simulado.png' });
  return page.url();
}