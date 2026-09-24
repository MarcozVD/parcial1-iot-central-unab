#!/usr/bin/env python3
"""Captura de pantalla web (solo pagina) con playwright-cli, sesion persistente 'iot'.

Uso:  python tools/shot.py <url> <salida.png> [espera_ms]
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import shutil

SESION = "iot"
TMP = pathlib.Path(r"C:\Users\mvale\Documents\Parcial1_IoT_Central\tools\js\_shot_actual.js")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    url, salida = sys.argv[1], sys.argv[2]
    espera = int(sys.argv[3]) if len(sys.argv) > 3 else 6000
    ruta = str(pathlib.Path(salida).resolve()).replace("\\", "/")
    TMP.write_text(f"""async (page) => {{
  await page.goto('{url}', {{ waitUntil: 'domcontentloaded' }});
  await page.waitForTimeout({espera});
  await page.setViewportSize({{ width: 1600, height: 1000 }});
  await page.waitForTimeout(800);
  await page.screenshot({{ path: '{ruta}' }});
  return page.url();
}}""", encoding="utf-8")
    exe = shutil.which("playwright-cli") or "playwright-cli.cmd"
    cmd = f'"{exe}" -s={SESION} run-code --filename "{TMP}"'
    p = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=240)
    out = (p.stdout or "") + (p.stderr or "")
    print(out[-400:])
    print("PNG:", ruta, "existe:", pathlib.Path(salida).exists())
    return 0


if __name__ == "__main__":
    sys.exit(main())
