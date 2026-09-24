async (page) => {
  await page.goto('https://dcandes1unab.azureiotcentral.com/device-templates/wf05iYNAtplrCiCa0BiN1', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(7000);
  const info = await page.evaluate(() => {
    const tabs = [...document.querySelectorAll('[role=tab],button,a')].map(e => (e.innerText || '').trim())
      .filter(t => t && t.length < 40);
    const uniq = [...new Set(tabs)];
    return { url: location.href, texto: document.body.innerText.slice(0, 1400), tabs: uniq.slice(0, 40) };
  });
  return JSON.stringify(info);
}
