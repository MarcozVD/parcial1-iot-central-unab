async (page) => {
  const out = { pasos: [] };
  // 1) cerrar dialogos MUI que bloquean
  for (let i = 0; i < 4; i++) {
    const cerrar = page.locator('.MuiDialog-root button:has-text("CLOSE"), .MuiDialog-root button:has-text("Cerrar"), .MuiDialog-root button[aria-label*="close" i]').first();
    if (await cerrar.count()) { await cerrar.click({ force: true }); out.pasos.push('dialogo cerrado'); await page.waitForTimeout(1500); }
    else {
      await page.keyboard.press('Escape');
      await page.waitForTimeout(1200);
      const hay = await page.locator('.MuiDialog-root').count();
      if (!hay) break;
    }
  }
  out.dialogos = await page.locator('.MuiDialog-root').count();
  const st = await page.evaluate(() => ({
    stop: !!document.querySelector('button[aria-label="Stop the simulation"]'),
    start: !!document.querySelector('button[aria-label="Start the simulation"]'),
    tail: document.body.innerText.slice(-260)
  }));
  out.estado = st;
  if (st.stop) {
    await page.evaluate(() => { const b = document.querySelector('button[aria-label="Stop the simulation"]'); if (b) b.click(); });
    out.pasos.push('stop'); await page.waitForTimeout(4000);
  }
  await page.evaluate(() => { const b = document.querySelector('button[aria-label="Start the simulation"]'); if (b) b.click(); });
  out.pasos.push('start');
  for (let i = 0; i < 45; i++) {
    await page.waitForTimeout(6000);
    const t = await page.evaluate(() => document.body.innerText);
    if (/Error during build|Build failed/.test(t)) {
      out.fallo = t.slice(Math.max(0, t.indexOf('Error during build') - 400), t.indexOf('Error during build') + 60);
      return JSON.stringify(out);
    }
    if (/\[DPS\] resp=|\[DPS\] asignado|\[TX\]/.test(t)) {
      out.ok = true;
      out.serial = t.slice(Math.max(0, t.indexOf('[WIFI]')), Math.min(t.length, t.indexOf('[WIFI]') + 700));
      return JSON.stringify(out);
    }
  }
  out.final = await page.evaluate(() => document.body.innerText.slice(-400));
  return JSON.stringify(out);
}
