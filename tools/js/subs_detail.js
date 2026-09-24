async (page) => {
  // Detalle de las opciones del dropdown de suscripción (id, texto, estado)
  const dump = await page.evaluate(() => {
    const items = [...document.querySelectorAll('.ms-Dropdown-item, [class*=list-item]')].map(e => ({
      txt: (e.innerText || '').trim().replace(/\n/g, ' '),
      cls: (e.className || '').toString().slice(0, 80),
      title: e.getAttribute('title') || '',
      id: e.id || ''
    }));
    return items;
  });
  return JSON.stringify(dump);
}
