async (page) => {
  const out = {};
  const ids = ['DC-RACKB-02', 'DC-AGUA-07', 'DC-RACKC-03', 'DC-HUMO-08'];
  for (const id of ids) {
    await page.goto('https://dcandes1unab.azureiotcentral.com/devices/' + id, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(9000);
    out[id] = await page.evaluate(() => {
      const t = document.body.innerText;
      const m = t.match(/(Conectado|Sin conexi[oó]n|Conectando|Desconectado)/);
      const last = t.match(/[ÚU]ltima (conexi[oó]n|vez)[^\n]{0,60}/i);
      return { estado: m ? m[1] : 'no encontrado', ultima: last ? last[0] : null };
    });
  }
  return JSON.stringify(out);
}
