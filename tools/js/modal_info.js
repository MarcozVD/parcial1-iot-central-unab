async (page) => {
  const info = await page.evaluate(() => {
    const modal = document.querySelector('[class*=modal_interrupt], [class*=blast-shield]');
    if (!modal) return { modal: false };
    const btns = [...modal.querySelectorAll('button')].map((b, i) => ({ i, txt: (b.innerText || '').trim().slice(0, 40), aria: b.getAttribute('aria-label'), cls: (b.className || '').toString().slice(0, 50) }));
    return { modal: true, txt: modal.innerText.slice(0, 400), btns };
  });
  return JSON.stringify(info);
}
