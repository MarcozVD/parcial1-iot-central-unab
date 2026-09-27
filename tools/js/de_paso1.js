async (page) => {
  const out = { pasos: [] };
  const r = await page.evaluate(() => {
    const nativeSet = (el, val) => {
      const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      setter.call(el, val);
      el.dispatchEvent(new Event('input', { bubbles: true }));
    };
    const grupoInput = document.querySelector('input[aria-label="Grupo de dispositivos "]');
    if (!grupoInput) return { error: 'no encontrado input de grupo' };
    grupoInput.focus();
    nativeSet(grupoInput, 'Nodo DC-ANDES-1');
    return { ok: true };
  });
  out.paso1 = r;
  await page.waitForTimeout(1800);
  const opciones = await page.evaluate(() =>
    [...document.querySelectorAll('[role="option"], [class*="popupMenu"] [class*="list-item"]')]
      .map(o => o.innerText.trim()).filter(Boolean).slice(0, 10)
  );
  out.opcionesGrupo = opciones;
  return JSON.stringify(out);
}
