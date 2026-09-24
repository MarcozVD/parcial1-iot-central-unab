async (page) => {
  const out = { pasos: [] };
  const set = async (lbl, valor) => {
    const el = page.locator(`input[aria-label^="${lbl}"], textarea[aria-label^="${lbl}"]`).first();
    if (await el.count()) { await el.fill(valor); out.pasos.push(lbl + '=' + valor); return true; }
    out.pasos.push(lbl + ': no encontrado');
    return false;
  };
  await set('Nombre para mostrar', 'Alerta rack - temperatura exhaust');
  await set('Para', 'mvalera@o365.unab.edu.co');
  await set('Nota', 'Temperatura de exhaust del rack por encima de 35 C (DC-ANDES-1, sala blanca). Revisar contencion y free-cooling.');
  await page.waitForTimeout(1200);
  const guardar = page.locator('button:has-text("Guardar")').first();
  if (await guardar.count()) { await guardar.click(); out.pasos.push('guardar'); }
  await page.waitForTimeout(7000);
  out.url = page.url();
  out.texto = await page.evaluate(() => document.body.innerText.slice(0, 700));
  return JSON.stringify(out);
}
