#!/usr/bin/env python3
"""Genera el JS de carga del proyecto Wokwi (sketch + diagram + libraries) en base64.

Uso:  python tools/wokwi_payload.py rackb
Salida: tools/js/wokwi_<proyecto>_payload.js
"""
from __future__ import annotations

import base64
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def b64(ruta: pathlib.Path) -> str:
    return base64.b64encode(ruta.read_bytes()).decode()


def inlinear_secrets(sketch: str, secrets: pathlib.Path) -> str:
    """Wokwi no permite archivos extra sin cuenta: se insertan defines en el sketch."""
    defines = []
    for linea in secrets.read_text(encoding="utf-8").splitlines():
        s = linea.strip()
        if s.startswith("#define"):
            defines.append(s)
    cabecera = ("// ---- credenciales (inline; el archivo real no viaja al repo) ----\n"
                + "\n".join(defines) + "\n")
    return sketch.replace('#include "secrets.h"', cabecera)


def main():
    proyecto = sys.argv[1] if len(sys.argv) > 1 else "rackb"
    dirp = RAIZ / "dispositivos" / "wokwi" / proyecto
    sketch = inlinear_secrets((dirp / "sketch.ino").read_text(encoding="utf-8"),
                              dirp / "secrets.h")
    diag = (dirp / "diagram.json").read_text(encoding="utf-8")
    libs = (dirp / "libraries.txt").read_text(encoding="utf-8")
    js = f"""async (page) => {{
  const S = "{base64.b64encode(sketch.encode()).decode()}";
  const D = "{base64.b64encode(diag.encode()).decode()}";
  const L = "{base64.b64encode(libs.encode()).decode()}";
  const r = await page.evaluate(({{ s, d, l }}) => {{
    const dec = (b) => new TextDecoder().decode(Uint8Array.from(atob(b), (c) => c.charCodeAt(0)));
    const modelos = window.monaco ? window.monaco.editor.getModels() : [];
    const buscar = (re) => modelos.find((x) => re.test(x.uri.toString()));
    const out = {{ n: modelos.length, uris: modelos.map((x) => x.uri.toString()).slice(0, 12) }};
    const ms = buscar(/sketch/);
    if (ms) {{ ms.setValue(dec(s)); out.sketch = ms.getValue().length; }}
    const md = buscar(/diagram\\.json/);
    if (md) {{ md.setValue(dec(d)); out.diagram = md.getValue().length; }}
    const ml = buscar(/libraries\\.txt/);
    if (ml) {{ ml.setValue(dec(l)); out.libraries = ml.getValue().length; }}
    return out;
  }}, {{ s: S, d: D, l: L }});
  return JSON.stringify(r);
}}"""
    salida = RAIZ / "tools" / "js" / f"wokwi_{proyecto}_payload.js"
    salida.write_text(js, encoding="utf-8")
    print(f"payload: {salida} ({salida.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
