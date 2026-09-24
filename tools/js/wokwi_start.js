async (page) => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const vis = (a) => a.filter((x) => x.offsetParent !== null);
  const log = [];
  for (let intento = 1; intento <= 4; intento++) {
    // cerrar dialogos abiertos
    const c = vis(await page.$$('button')).find((x) => /^CLOSE$/.test((x.innerText || '').trim()));
    if (c) { await c.click(); await sleep(500); }
    const btn = await page.$('button[aria-label="Start the simulation"]');
    if (!btn) { log.push('sin boton start (intento ' + intento + ')'); break; }
    await btn.click();
    let estado = null;
    for (let i = 0; i < 40; i++) {
      await sleep(5000);
      const t = await page.evaluate(() => document.body.innerText);
      if (/Build failed/.test(t)) { estado = { fallo: true, frag: t.slice(Math.max(0, t.indexOf('Build failed') - 200), t.indexOf('Build failed') + 900) }; break; }
      if (/too busy|SEE PRICING|taking longer/.test(t)) { estado = { cola: true }; break; }
      if (/\[TX\]/.test(t)) { estado = { ok: true, frag: t.slice(t.indexOf('[WIFI]'), t.indexOf('[TX]') + 400) }; break; }
      if (i === 6 && /\[WIFI\]/.test(t)) { log.push('wifi ok, esperando TX'); }
    }
    if (estado && estado.ok) return JSON.stringify({ intento, ...estado });
    if (estado && estado.fallo) return JSON.stringify({ intento, ...estado });
    log.push('intento ' + intento + ': ' + (estado ? 'cola' : 'timeout'));
    await sleep(9000);
  }
  const t = await page.evaluate(() => document.body.innerText.slice(-1500));
  return JSON.stringify({ log, final: t });
}
