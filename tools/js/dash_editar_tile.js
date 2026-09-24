async (page) => {
  const out = {};
  const btn = page.locator('button:has-text("Editar"), [role=button]:has-text("Editar")').last();
  out.n = await page.locator('button:has-text("Editar")').count();
  await btn.click({ force: true });
  await page.waitForTimeout(5000);
  const d = await page.evaluate(() => {
    const campos = [...document.querySelectorAll('input,textarea,[role=combobox]')]
      .map(e => ({ tag: e.tagName, lbl: (e.getAttribute('aria-label') || e.placeholder || '').trim().slice(0, 50), val: (e.value || '').slice(0, 30) }))
      .filter(x => x.lbl);
    const btns = [...document.querySelectorAll('button')].map(b => (b.innerText || b.getAttribute('aria-label') || '').replace(/\n/g, ' ').trim()).filter(t => t && t.length < 45);
    return { campos: campos.slice(0, 30), btns: [...new Set(btns)].slice(0, 45), texto: document.body.innerText.slice(-1000) };
  });
  return JSON.stringify({ ...out, ...d });
}
