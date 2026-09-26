async (page) => {
  const out = {};
  for (const id of ['DC-RACKC-03', 'DC-HUMO-08', 'DC-ENERGIA-09']) {
    await page.goto('https://dcandes1unab.azureiotcentral.com/devices/details/' + id, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(11000);
    const txt = await page.evaluate(() => document.body.innerText);
    const est = (txt.match(/Conectado|Desconectado/) || ['?'])[0];
    const ult = (txt.match(/Última recepción de datos: [^\n|]+/) || ['?'])[0];
    out[id] = est + ' | ' + ult;
  }
  return JSON.stringify(out);
}
