#!/usr/bin/env python3
"""Genera el guion de sustentacion en Word/PDF a partir de docs/06-sustentacion.md.

Uso:  .venv/Scripts/python.exe tools/build_sustentacion.py

Convierte un subconjunto de markdown (titulos, tablas, listas, bloques de codigo,
citas y negritas) al estilo del proyecto (tools/docstyle.py).
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, "tools")
from docstyle import Doc  # noqa: E402

FUENTE = pathlib.Path("docs/06-sustentacion.md")
SALIDA = "informe/Guion_Sustentacion_Parcial1.docx"


def inline(texto: str):
    """Convierte **negritas** y `codigo` en partes para docstyle."""
    partes = []
    for trozo in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", texto):
        if not trozo:
            continue
        if trozo.startswith("**") and trozo.endswith("**"):
            partes.append((trozo[2:-2], {"b": 1}))
        elif trozo.startswith("`") and trozo.endswith("`"):
            partes.append((trozo[1:-1], {"code": 1}))
        else:
            partes.append(trozo)
    return partes


def main() -> int:
    lineas = FUENTE.read_text(encoding="utf-8").splitlines()
    d = Doc("Parcial 1 · Sustentación DC-ANDES-1")
    d.cover(
        "Universidad Autónoma de Bucaramanga · IoT + Cloud + Sistemas Distribuidos",
        "Guion de sustentación",
        "Parcial 1 — Escenario 5.2 Centro de datos: flota heterogénea de 10 dispositivos sobre Azure IoT Central",
        [("Estudiante", "Marcos Valera Daza"),
         ("Aplicación", "dcandes1unab · https://dcandes1unab.azureiotcentral.com"),
         ("Repositorio", "https://github.com/MarcozVD/parcial1-iot-central-unab"),
         ("Duración de la demo", "12–15 min + preguntas")],
        [("Cómo usar este guion: ", {"b": 1}),
         "sigue el orden de la sección 1 para la demo en vivo; la sección 3 tiene las respuestas listas "
         "para las preguntas del ingeniero y la 4 indica qué enseñar según cada indicador de evaluación."])

    i = 0
    while i < len(lineas):
        ln = lineas[i].rstrip()
        if ln.startswith("# ") or ln.strip() in ("", "---"):
            i += 1
            continue
        if ln.startswith("### "):
            d.h(ln[4:].strip(), 2); i += 1; continue
        if ln.startswith("## "):
            d.h(ln[3:].strip(), 1); i += 1; continue
        if ln.startswith("```"):
            j = i + 1
            bloque = []
            while j < len(lineas) and not lineas[j].startswith("```"):
                bloque.append(lineas[j].rstrip()); j += 1
            d.code(bloque); i = j + 1; continue
        if ln.startswith("|"):
            cabecera, filas = None, []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                celdas = [c.strip() for c in lineas[i].strip().strip("|").split("|")]
                if set("".join(celdas)) <= set("-: "):
                    i += 1; continue
                if cabecera is None:
                    cabecera = celdas
                else:
                    filas.append(celdas)
                i += 1
            if cabecera:
                ancho = max(len(f) for f in filas) if filas else len(cabecera)
                filas = [f + [""] * (ancho - len(f)) for f in filas]
                d.table(cabecera, filas)
            continue
        if ln.startswith(">"):
            cita = []
            while i < len(lineas) and lineas[i].startswith(">"):
                cita.append(lineas[i].lstrip("> ").rstrip()); i += 1
            d.callout(" ".join(cita).replace("**", ""), kind="info"); continue
        if re.match(r"^\s*[-*] |^\d+\. ", ln):
            items = []
            while i < len(lineas) and re.match(r"^\s*[-*] |^\d+\. ", lineas[i]):
                texto = re.sub(r"^\s*(?:[-*]|\d+\.)\s*", "", lineas[i]).rstrip()
                items.append([*inline(texto)]); i += 1
            d.bullets(items); continue
        parrafo = []
        while i < len(lineas) and lineas[i].strip() and not re.match(r"^(#|\||>|```|\s*[-*] |\d+\. )", lineas[i]):
            parrafo.append(lineas[i].strip()); i += 1
        if parrafo:
            d.p(*inline(" ".join(parrafo)))
        else:
            i += 1

    d.save(SALIDA)
    print("guion generado:", SALIDA)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
