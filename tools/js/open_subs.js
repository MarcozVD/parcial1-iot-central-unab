async (page) => {
  // Click REAL sobre el combobox de suscripción; luego volcar opciones
  await page.locator('div[role=combobox][aria-label^="Suscripción"]').first().click();
  await page.waitForTimeout(2500);
  const dump = await page.evaluate(() => {
    const items = [...document.querySelectorAll('[class*=popupMenu] [class*=list-item], [role=option]')]
      .map(e => e.innerText.trim()).filter(Boolean);
    const menus = [...document.querySelectorAll('[class*=popupMenu],[role=listbox]')]
      .map(e => (e.className || '').toString().slice(0, 60) + ' :: ' + (e.innerText || '').replace(/\n/g, ' | ').slice(0, 300));
    return { items, menus, n: document.querySelectorAll('[class*=popupMenu]').length };
  });
  return JSON.stringify(dump);
}
