async (page) => {
  const out = { pasos: [] };
  const abrir = async (nombre) => {
    const t = page.locator(`text="${nombre}"`).first();
    if (await t.count()) { await t.click(); await page.waitForTimeout(2500); out.pasos.push('click ' + nombre); }
    else out.pasos.push('no encontrado ' + nombre);
  };
  await abrir('diagram.json');
  await abrir('libraries.txt');
  const r = await page.evaluate(() => ({
    uris: window.monaco ? window.monaco.editor.getModels().map((m) => m.uri.toString()) : 'sin monaco',
    tabs: [...document.querySelectorAll('[role=tab],button')].map((e) => (e.innerText || '').trim()).filter((t) => t && t.length < 30).slice(0, 25)
  }));
  return JSON.stringify({ ...out, ...r });
}
