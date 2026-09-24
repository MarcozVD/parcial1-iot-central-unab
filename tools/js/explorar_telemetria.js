async (page) => {
  // vuelve a abrir la configuracion del mosaico (por si se cerro) y explora la seccion Telemetria
  const info = await page.evaluate(() => {
    const h = [...document.querySelectorAll('*')].find(e => e.children.length === 0 && /^Telemetría$/.test((e.innerText || '').trim()));
    if (!h) return { err: 'sin header Telemetria', texto: document.body.innerText.slice(-300) };
    const cadena = [];
    let n = h;
    for (let i = 0; i < 6 && n; i++) {
      cadena.push({ i, tag: n.tagName, cls: (n.className || '').toString().slice(0, 70), role: n.getAttribute('role'), aria: n.getAttribute('aria-expanded'), html: (n.outerHTML || '').slice(0, 160) });
      n = n.parentElement;
    }
    const botones = h.parentElement ? [...h.parentElement.querySelectorAll('button,[class*=ActionTrigger]')].map(b => ({ cls: (b.className || '').toString().slice(0, 60), aria: b.getAttribute('aria-label'), txt: (b.innerText || '').trim().slice(0, 20) })) : [];
    return { cadena, botones };
  });
  return JSON.stringify(info);
}
