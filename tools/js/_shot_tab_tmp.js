async (page) => {
  await page.setViewportSize({ width: 1500, height: 940 });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'C:/Users/mvale/Documents/Parcial1_IoT_Central/evidencias/de-check1.png' });
  return page.url();
}
