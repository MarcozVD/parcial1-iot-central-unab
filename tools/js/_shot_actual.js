async (page) => {
  await page.goto('https://dcandes1unab.azureiotcentral.com/devices', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(18000);
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'C:/Users/mvale/Documents/Parcial1_IoT_Central/evidencias/dia3-portal-flota.png' });
  return page.url();
}