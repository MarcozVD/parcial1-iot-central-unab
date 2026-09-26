async (page) => {
  await page.setViewportSize({ width: 1500, height: 940 });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: 'C:/Users/mvale/Documents/Parcial1_IoT_Central/evidencias/dia3-wokwi-agua.png' });
  return page.url();
}
