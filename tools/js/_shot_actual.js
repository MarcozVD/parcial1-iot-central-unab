async (page) => {
  await page.goto('https://dcandes1unab.azureiotcentral.com/device-templates/wf05iYNAtplrCiCa0BiN1/views', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(15000);
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'C:/Users/mvale/Documents/Parcial1_IoT_Central/evidencias/dia4-views-plantilla.png' });
  return page.url();
}