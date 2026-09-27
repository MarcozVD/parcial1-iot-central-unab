async (page) => {
  return JSON.stringify(await page.evaluate(() => {
    const devs = [...document.querySelectorAll('*')].filter(e => !e.children.length && /^DC-[A-Z]+-\d\d$/.test((e.innerText || '').trim()));
    const e = devs[0];
    const chain = [];
    let n = e;
    for (let i = 0; i < 6 && n; i++) { chain.push(n.tagName + '.' + (n.className && n.className.baseVal !== undefined ? n.className.baseVal : n.className)); n = n.parentElement; }
    return { total: devs.length, chain, sample: devs.slice(0, 5).map(x => x.innerText) };
  }));
}
