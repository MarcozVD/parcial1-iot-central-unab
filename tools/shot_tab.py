#!/usr/bin/env python3
"""Captura la pestaña ACTUAL sin navegar (para proyectos Wokwi anónimos).

Uso:  python tools/shot_tab.py <salida.png> [--tab N] [espera_ms]

A diferencia de tools/shot.py, este NO hace page.goto: navegar una pestaña de Wokwi
destruye el proyecto anónimo (el contenido solo vive en esa pestaña).
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

SESION = "iot"
TMP = pathlib.Path(__file__).resolve().parent / "js" / "_shot_tab_tmp.js"


def main() -> int:
    args = sys.argv[1:]
    tab = None
    if "--tab" in args:
        i = args.index("--tab")
        tab = args[i + 1]
        del args[i:i + 2]
    if not args:
        print(__doc__)
        return 1
    salida = pathlib.Path(args[0]).resolve()
    espera = int(args[1]) if len(args) > 1 else 1500
    ruta = str(salida).replace("\\", "/")

    TMP.write_text(
        "async (page) => {\n"
        "  await page.setViewportSize({ width: 1500, height: 940 });\n"
        f"  await page.waitForTimeout({espera});\n"
        f"  await page.screenshot({{ path: '{ruta}' }});\n"
        "  return page.url();\n"
        "}\n",
        encoding="utf-8",
    )

    exe = shutil.which("playwright-cli") or "playwright-cli.cmd"
    if tab is not None:
        subprocess.run([exe, f"-s={SESION}", "tab-select", str(tab)], capture_output=True, text=True, timeout=90)
    p = subprocess.run([exe, f"-s={SESION}", "run-code", "--filename", str(TMP)],
                       capture_output=True, text=True, timeout=180)
    out = p.stdout + p.stderr
    print(out[-400:] if len(out) > 400 else out)
    print("existe:", salida.exists(), salida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
