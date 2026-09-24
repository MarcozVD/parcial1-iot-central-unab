#!/usr/bin/env python3
"""Genera el logo del escenario DC-ANDES-1 (AndesCloud S.A.S.) en PNG.

Salida: assets/logo_andescloud_dcandes1.png (usado en el panel, la personalizacion de
la aplicacion y el informe).
"""
from __future__ import annotations

import pathlib

from PIL import Image, ImageDraw, ImageFont

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "assets" / "logo_andescloud_dcandes1.png"
AZUL = (17, 45, 78)
AZUL2 = (23, 68, 120)
BLANCO = (245, 248, 252)
CIAN = (0, 194, 224)
GRIS = (150, 170, 190)


def fuente(tam: int):
    for nombre in ("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        for base in (r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu"):
            p = pathlib.Path(base) / nombre
            if p.exists():
                try:
                    return ImageFont.truetype(str(p), tam)
                except Exception:
                    pass
    return ImageFont.load_default()


def main():
    W, H = 900, 300
    img = Image.new("RGB", (W, H), AZUL)
    d = ImageDraw.Draw(img)
    # degradado suave
    for y in range(H):
        f = y / H
        d.line([(0, y), (W, y)], fill=(int(AZUL[0] + (AZUL2[0] - AZUL[0]) * f),
                                       int(AZUL[1] + (AZUL2[1] - AZUL[1]) * f),
                                       int(AZUL[2] + (AZUL2[2] - AZUL[2]) * f)))
    # barra cian inferior
    d.rectangle([0, H - 14, W, H], fill=CIAN)
    # rack estilizado (3 unidades + LED cian)
    x0, y0, w, h = 48, 42, 132, 42
    for i in range(4):
        y = y0 + i * (h + 12)
        d.rounded_rectangle([x0, y, x0 + w, y + h], radius=8, fill=BLANCO)
        d.rounded_rectangle([x0 + 12, y + 9, x0 + w - 60, y + h - 9], radius=4, fill=AZUL)
        d.ellipse([x0 + w - 42, y + 13, x0 + w - 22, y + h - 13], fill=CIAN)
    # textos
    d.text((212, 52), "DC-ANDES-1", font=fuente(62), fill=BLANCO)
    d.text((216, 130), "Centro de datos urbano · Bucaramanga", font=fuente(26), fill=GRIS)
    d.text((216, 168), "AndesCloud S.A.S.", font=fuente(30), fill=CIAN)
    d.text((216, 210), "Cuarto de control · Parcial 1 IoT+Cloud (UNAB)", font=fuente(20), fill=GRIS)
    img.save(SALIDA)
    print("logo:", SALIDA, img.size)


if __name__ == "__main__":
    main()
