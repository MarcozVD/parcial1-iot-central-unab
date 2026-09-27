async (page) => {
  const out = {};
  out.botones = await page.evaluate(() => [...document.querySelectorAll('button')].filter(b => b.offsetParent)
    .map(b => (b.innerText.trim() || b.getAttribute('aria-label') || '').slice(0, 30)).filter(Boolean));
  out.picker = await page.evaluate(() => {
    const i = [...document.querySelectorAll('input')].find(x => /\d\d\/\d\d\/2026/.test(x.value));
    let n = i; for (let k = 0; k < 6 && n; k++) n = n.parentElement;
    return n ? n.innerText.slice(0, 800) : null;
  });
  return JSON.stringify(out);
}
