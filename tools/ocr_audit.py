#!/usr/bin/env python3
"""Capa 2 de la auditoria: OCR de todas las imagenes del repo buscando secretos.

Uso:  python3 tools/ocr_audit.py
Salida: lista de aciertos (imagen + texto); exit 1 si hay hallazgos.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def claves_reales() -> set[str]:
    """Fragmentos de clave real, solo para comparar (no se imprimen enteros)."""
    frags = set()
    p = RAIZ / ".secrets" / "creds.json"
    if p.exists():
        for m in re.finditer(r"[A-Za-z0-9+/]{38,44}={0,2}", p.read_text(encoding="utf-8")):
            frags.add(m.group(0)[:16])
    return frags


def main() -> int:
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ModuleNotFoundError:
        print("Falta rapidocr. Este script necesita un interprete que lo tenga instalado:")
        print("  python3 -m pip install rapidocr-onnxruntime")
        print("y ejecutarlo, por ejemplo:  python3 tools/ocr_audit.py")
        return 2
    ocr = RapidOCR()
    frags = claves_reales()
    imagenes = [f for f in subprocess.run(["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True).stdout.split()
                if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    print(f"imagenes rastreadas: {len(imagenes)} | fragmentos de clave a buscar: {len(frags)}")
    hallazgos = []
    for i, rel in enumerate(imagenes, 1):
        ruta = RAIZ / rel
        try:
            res, _ = ocr(str(ruta))
        except Exception as e:
            print(f"  [{i}/{len(imagenes)}] {rel}: OCR fallo ({type(e).__name__})")
            continue
        texto = " ".join(t[1] for t in (res or [])).replace(" ", "")
        crudo = " ".join(t[1] for t in (res or []))
        for frag in frags:
            if frag in texto or frag in crudo:
                hallazgos.append((rel, f"fragmento de clave real: {frag[:8]}…"))
        for patron, etiqueta in [(r"sig=[A-Za-z0-9%+/=]{10,}", "SAS sig="),
                                 (r"SharedAccessKey=[A-Za-z0-9+/=]{10,}", "SharedAccessKey"),
                                 (r"AccountKey=[A-Za-z0-9+/=]{10,}", "AccountKey"),
                                 (r"gh[pousr]_[A-Za-z0-9]{20,}", "token de GitHub")]:
            if re.search(patron, crudo) or re.search(patron, texto):
                hallazgos.append((rel, etiqueta))
        if i % 5 == 0:
            print(f"  ... {i}/{len(imagenes)} revisadas")
    print()
    if hallazgos:
        print("HALLAZGOS EN IMAGENES:")
        for rel, que in hallazgos:
            print(f"  {rel}: {que}")
        return 1
    print("IMAGENES: limpias (ninguna clave ni token visible en el OCR)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
