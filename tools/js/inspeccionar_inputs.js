async (page) => {
  const info = await page.evaluate(() => {
    return [...document.querySelectorAll('input')].map((e, i) => {
      const cont = e.closest('div');
      return {
        i,
        aria: e.getAttribute('aria-label'),
        type: e.type,
        placeholder: e.placeholder,
        valor: e.value,
        visible: e.offsetParent !== null,
        contexto: cont ? (cont.innerText || '').replace(/\n/g, ' | ').slice(0, 80) : '',
        clases: (e.className || '').toString().slice(0, 60)
      };
    });
  });
  return JSON.stringify(info);
}
