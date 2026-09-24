async (page) => {
  const r = await page.evaluate(() => {
    const m = window.monaco.editor.getModels().find((x) => /sketch/.test(x.uri.toString()));
    if (!m) return { err: 'sin modelo sketch' };
    const v = m.getValue();
    const lineas = v.split('\n');
    return {
      len: v.length,
      n_lineas: lineas.length,
      linea_170_178: lineas.slice(169, 178),
      tiene_resp: v.includes('[DPS] resp=%ld'),
      // patron correcto: state=%d + barra-n (2 caracteres) en la MISMA linea
      correcto: /state=%d\\n"/.test(v),
      roto: /state=%d\n"/.test(v)
    };
  });
  return JSON.stringify(r);
}
