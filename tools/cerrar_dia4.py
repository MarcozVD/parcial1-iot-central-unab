#!/usr/bin/env python3
"""
cerrar_dia4.py - Cierre de la fecha 4: calcula la ventana final del servidor Ubuntu,
la compara contra el minimo exigido y deja listo el texto para pegar en los documentos.

Uso:
    .venv/Scripts/python.exe tools/cerrar_dia4.py

No escribe nada por si solo: imprime lo que hay que pegar en tools/build_informe.py
(seccion 7 y anexo B) y en tools/build_evidencias.py (seccion 4.2), reemplazando los
placeholders "[COMPLETAR AL CIERRE]".
"""
from __future__ import annotations

import csv
import datetime as dt
import pathlib
import subprocess

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MINIMO_HORAS = 4.0


def horas(t1: str, t2: str) -> float:
    a = dt.time.fromisoformat(t1)
    b = dt.time.fromisoformat(t2)
    return ((b.hour * 3600 + b.minute * 60 + b.second) - (a.hour * 3600 + a.minute * 60 + a.second)) / 3600


def main() -> int:
    print("=== Ventana del servidor Ubuntu (27-sep) ===")
    print("Ejecuta esto por SSH y pega la salida aqui, o corre este script DENTRO del servidor.\n")
    print("ssh -i ~/Downloads/iot_key.pem mvale@52.252.133.127 \\")
    print('  "cd ~/Parcial1_IoT_Central && python3 -c \\"')
    print("import csv, pathlib, datetime as dt")
    print("def h(t1,t2):")
    print("    a=dt.time.fromisoformat(t1); b=dt.time.fromisoformat(t2)")
    print("    return ((b.hour*3600+b.minute*60+b.second)-(a.hour*3600+a.minute*60+a.second))/3600")
    print("mx=0; ini=None; fin=None")
    print("for f in sorted(pathlib.Path('datos').glob('DC-*.csv')):")
    print("    filas=[r[0][11:19] for r in csv.reader(f.open(encoding='utf-8')) if r and r[0].startswith('2026-09-27')]")
    print("    if filas:")
    print("        mx=max(mx,h(filas[0],filas[-1]))")
    print("        ini = filas[0] if ini is None or filas[0] < ini else ini")
    print("        fin = filas[-1] if fin is None or filas[-1] > fin else fin")
    print("print(f'ventana: {ini} -> {fin}  ({mx:.2f} h)')")
    print('"\'')
    print()
    print("=== Cuando tengas la duración final, reemplaza en tools/build_informe.py: ===")
    print('  1. La fila "27-sep (dom)" de la sección 7 (tabla de horas por fecha)')
    print('  2. El callout "[PENDIENTE AL CIERRE...]" -> quitarlo o resumir el cierre real')
    print('  3. La fila "27-sep" de la tabla de "Comparativa de los 4 días" en el Anexo B')
    print()
    print("=== Y en tools/build_evidencias.py: ===")
    print('  1. Sección 4.2: añadir una figura con la captura final de cierre (última recepción por nodo)')
    print('  2. Quitar o resolver el callout "[PENDIENTE AL CIERRE]"')
    print()
    print("=== Luego regenerar: ===")
    print("  .venv/Scripts/python.exe tools/build_informe.py")
    print("  .venv/Scripts/python.exe tools/build_evidencias.py")
    print('  powershell -NoProfile -File tools/topdf.ps1 -Docx "...\\Informe_Parcial1_DC-ANDES-1.docx" -Pdf "...\\Informe_Parcial1_DC-ANDES-1.pdf"')
    print('  powershell -NoProfile -File tools/topdf.ps1 -Docx "...\\Evidencias_Parcial1_DC-ANDES-1.docx" -Pdf "...\\Evidencias_Parcial1_DC-ANDES-1.pdf"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
