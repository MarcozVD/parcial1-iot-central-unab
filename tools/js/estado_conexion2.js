async (page) => {
  const out = {};
  const ids = ['DC-RACKB-02', 'DC-AGUA-07'];
  for (const id of ids) {
    await page.goto('https://dcandes1unab.azureiotcentral.com/devices/' + id, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(8000);
    out[id] = await page.evaluate(() => {
      const el = document.querySelector('[class*=deviceConnectionStatus]');
      const chips = [...document.querySelectorAll('[role=status],[class*=Status]')].slice(0, 6).map((e) => ({
        cls: (e.className || '').toString().slice(0, 40),
        txt: (e.innerText || '').trim().slice(0, 60),
        title: e.getAttribute('title') || (e.querySelector('[title]') || {}).title || ''
      }));
      return { conexion: el ? (el.innerText || el.getAttribute('aria-label') || el.outerHTML.slice(0, 120)) : null, chips };
    });
  }
  return JSON.stringify(out);
}
