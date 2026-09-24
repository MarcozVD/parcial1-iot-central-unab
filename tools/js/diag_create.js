async (page) => {
  const d = await page.evaluate(() => {
    const btns = [...document.querySelectorAll('button')].map((b, i) => ({
      i, txt: (b.innerText || '').trim().slice(0, 20),
      dis: b.disabled, aria: b.getAttribute('aria-disabled'),
      cls: (b.className || '').toString().slice(0, 60)
    })).filter(b => b.txt);
    const errs = [...document.querySelectorAll('[class*=error],[role=alert],[class*=Error]')]
      .map(e => (e.innerText || '').trim().slice(0, 120)).filter(Boolean).slice(0, 10);
    return { btns: btns.slice(-8), errs, url: location.href };
  });
  return JSON.stringify(d);
}
