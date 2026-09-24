async (page) => {
  await page.goto('https://dcandes1unab.azureiotcentral.com/devices/details/DC-RACKA-01', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(7000);
  const d = await page.evaluate(() => {
    const botones = [...document.querySelectorAll('button,[role=button],a')]
      .map(e => ({ t: (e.innerText || '').trim().slice(0, 40), aria: e.getAttribute('aria-label') }))
      .filter(x => (x.t || x.aria) && (x.t || x.aria).length < 45);
    return { url: location.href, botones: [...new Set(botones.map(b => b.aria || b.t))].slice(0, 40), texto: document.body.innerText.slice(0, 600) };
  });
  return JSON.stringify(d);
}
