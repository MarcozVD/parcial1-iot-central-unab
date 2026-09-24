async (page) => {
  const d = await page.evaluate(() => {
    const cont = document.querySelector('#d9nss6llu0') || document.querySelector('[id^="d9nss6llu0"]');
    const secs = [...document.querySelectorAll('button[aria-label="Telemetría"],button[aria-label="Funcionalidad"]')]
      .map(b => ({ aria: b.getAttribute('aria-label'), exp: b.getAttribute('aria-expanded'), ctrl: b.getAttribute('aria-controls') }));
    const conts = secs.map(s => {
      const c = document.getElementById(s.ctrl);
      return { ctrl: s.ctrl, txt: c ? c.innerText.slice(0, 400) : null,
               checks: c ? [...c.querySelectorAll('input[type=checkbox]')].map(x => ({ lbl: x.getAttribute('aria-label'), v: x.checked })) : [] };
    });
    return { secs, conts };
  });
  return JSON.stringify(d);
}
