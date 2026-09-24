async (page) => {
  const out = {};
  out.url = page.url();
  // items de la galeria de objetos visuales
  out.galeria = await page.evaluate(() => {
    const cont = [...document.querySelectorAll('div,section')].find(e => (e.innerText || '').startsWith('Adición de un icono'));
    const items = [...document.querySelectorAll('[class*=tile],[class*=visual],[class*=catalog] li,button')]
      .map(e => (e.innerText || e.getAttribute('aria-label') || '').replace(/\n/g, ' ').trim())
      .filter(t => t && t.length < 50);
    return { cont: cont ? cont.innerText.replace(/\n/g, ' | ').slice(0, 800) : null, items: [...new Set(items)].slice(0, 40) };
  });
  return JSON.stringify(out);
}
