#!/usr/bin/env python3
"""Dibuja el diagrama de arquitectura del DC-ANDES-1 (4 capas) como PNG con PIL."""
from __future__ import annotations

import pathlib

from PIL import Image, ImageDraw, ImageFont

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "evidencias" / "diagrama_arquitectura.png"

AZUL = (11, 42, 74)
AZUL2 = (23, 68, 120)
CIAN = (0, 194, 224)
VERDE = (16, 122, 87)
NARANJA = (176, 96, 0)
GRIS = (108, 122, 137)
CLARO = (244, 247, 250)
BLANCO = (255, 255, 255)


def fuente(tam: int, negrita: bool = False):
    nom = "segoeuib.ttf" if negrita else "segoeui.ttf"
    for base in (r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu"):
        p = pathlib.Path(base) / nom
        if p.exists():
            try:
                return ImageFont.truetype(str(p), tam)
            except Exception:
                pass
    return ImageFont.load_default()


def main():
    W, H = 1750, 1150
    img = Image.new("RGB", (W, H), BLANCO)
    d = ImageDraw.Draw(img)
    f_tit = fuente(34, True)
    f_sub = fuente(22, True)
    f = fuente(19)
    f_p = fuente(17)
    f_pb = fuente(17, True)

    d.rectangle([0, 0, W, 78], fill=AZUL)
    d.rectangle([0, 74, W, 78], fill=CIAN)
    d.text((34, 20), "DC-ANDES-1 · Arquitectura de referencia (Parcial 1 · IoT Central)", font=f_tit, fill=BLANCO)

    capas = [
        ("CAPA DE DISPOSITIVO", 0, [
            ("01 Simulador nativo (plantilla)", "temp·HR rack A"),
            ("02 Wokwi ESP32 #1 (DHT22+pot+LED)", "temp intake/exhaust·HR"),
            ("03 Python SDK MQTT 8883 (Rack C)", "temp·HR rack C"),
            ("04 Python SDK WebSocket 443 (pasillo)", "temp·HR·dP"),
            ("05/06 Puentes de API pública", "meteo · aire"),
            ("07 Wokwi ESP32 #2 (sonda+pulsador)", "fuga · HR piso"),
            ("08 paho MQTT explícito (humo)", "humo · temp techo"),
            ("09 Replay CSV histórico (PDU)", "kW · A · FP"),
            ("10 Puente HTTP + sensor (acceso)", "puerta · eventos"),
        ]),
        ("CAPA DE RED / TELECOMUNICACIONES", 1, [
            ("MQTT/TLS 1.2 · 8883", "ESP32 Wokwi, SDK, paho"),
            ("MQTT sobre WebSockets · 443", "transporte alterno del SDK"),
            ("HTTPS · 443", "REST de dispositivo y feeds"),
            ("HTTP local 127.0.0.1:8098", "sensor de campo del acceso"),
            ("Salida a Internet del sitio", "fibra urbana · NAT saliente"),
        ]),
        ("CAPA DE PLATAFORMA (Azure IoT Central)", 2, [
            ("DPS · inscripción por clave simétrica", "global.azure-devices-provisioning.net"),
            ("IoT Hub gestionado", "telemetría · gemelo · comandos"),
            ("Digital Twin / plantilla", "dtmi:unab:dcandes:dcAndesNodo;1"),
            ("Grupo de dispositivos", "$template = dcAndesNodo"),
            ("Data Explorer", "consultas y exportación"),
        ]),
        ("CAPA DE OPERACIÓN (cuarto de control)", 3, [
            ("Panel Cuarto de Control DC-ANDES-1", "16 mosaicos · KPIs · 8 gráficos"),
            ("Vistas por dispositivo", "Overview · About · Comandos"),
            ("Reglas y alertas", "6 reglas · correo + webhook"),
            ("Comandos y propiedades", "setAlerta · acuseAlarma · umbrales"),
            ("Sustentación en vivo", "Python + Wokwi en dos equipos"),
        ]),
    ]

    y = 112
    for titulo, idx, items in capas:
        col = [AZUL2, VERDE, AZUL, NARANJA][idx]
        d.rounded_rectangle([30, y, 210, y + 176], radius=12, fill=col)
        # titulo vertical (por palabras)
        palabras = titulo.split()
        yy = y + 14
        for palabra in palabras:
            d.text((44, yy), palabra, font=f_sub, fill=BLANCO)
            yy += 26
        x = 236
        # el ancho se calcula para que TODAS las cajas quepan en el lienzo (antes se cortaban desde la 08)
        margen_dcho, hueco = 24, 12
        ancho = int((W - x - margen_dcho - hueco * (len(items) - 1)) / len(items))
        ancho = max(140, min(300, ancho))
        for nombre, detalle in items:
            d.rounded_rectangle([x, y, x + ancho, y + 176], radius=10, fill=CLARO, outline=col, width=2)
            # envolver el nombre
            linea, lineas = "", []
            for p in nombre.split():
                if d.textlength((linea + " " + p).strip(), font=f) < ancho - 22:
                    linea = (linea + " " + p).strip()
                else:
                    lineas.append(linea)
                    linea = p
            lineas.append(linea)
            ty = y + 18
            for l in lineas[:4]:
                d.text((x + 12, ty), l, font=f, fill=AZUL)
                ty += 24
            ty += 6
            for l in detalle.split(" · "):
                d.text((x + 12, ty), "· " + l, font=f_p, fill=GRIS)
                ty += 22
            x += ancho + hueco
        y += 206

    # flechas verticales entre capas
    for yy in (112 + 176 + 6, 112 + 206 + 176 + 6, 112 + 412 + 176 + 6):
        for x in (420, 900, 1400):
            d.line([x, yy - 14, x, yy + 14], fill=CIAN, width=4)

    d.text((32, H - 54), "Los diez nodos comparten la plantilla publicada y publican cada uno su subconjunto de "
                         "telemetría; el cuarto de control se alimenta del mismo grupo de dispositivos.",
           font=f_p, fill=GRIS)
    img.save(SALIDA)
    print("diagrama:", SALIDA, img.size)


if __name__ == "__main__":
    main()
