async (page) => {
  await page.goto('https://dcandes1unab.azureiotcentral.com/dashboards', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(7000);
  const info = await page.evaluate(() => {
    const botones = [...document.querySelectorAll('button,a,[role=button]')]
      .map(e => ({ t: (e.innerText || '').trim().slice(0, 40), aria: e.getAttribute('aria-label') }))
      .filter(x => x.t || x.aria);
    return { url: location.href, texto: document.body.innerText.slice(0, 900), botones: botones.slice(0, 30) };
  });
  return JSON.stringify(info);
}
