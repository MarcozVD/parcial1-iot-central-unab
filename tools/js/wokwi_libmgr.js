async (page) => {
  const out = { pasos: [] };
  const lm = page.getByText('Library Manager').first();
  if (await lm.count()) { await lm.click(); out.pasos.push('abrir library manager'); }
  await page.waitForTimeout(3500);
  const d = await page.evaluate(() => ({
    inputs: [...document.querySelectorAll('input,textarea')].map((e) => ({ lbl: e.getAttribute('aria-label') || e.placeholder || '', id: e.id, tipo: e.type })).filter((x) => x.lbl || x.id),
    botones: [...document.querySelectorAll('button')].map((b) => (b.getAttribute('aria-label') || b.innerText || '').trim()).filter((t) => t && t.length < 40).slice(0, 25),
    texto: document.body.innerText.slice(-450)
  }));
  return JSON.stringify({ ...out, ...d });
}
