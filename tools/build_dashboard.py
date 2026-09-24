#!/usr/bin/env python3
"""Construye el panel "Cuarto de Control DC-ANDES-1" via la API de IoT Central.

Esquema verificado contra el OpenAPI 2022-06-30-preview
(specification/iotcentral/data-plane/IoTCentral/preview/2022-06-30-preview/iotcentral.json):
  queryRange = {"type":"time","duration":"P1D","resolution":"PT5M"}
  mosaico    = {"displayName","configuration":{...},"x","y","width","height"}
"""
from __future__ import annotations

import base64
import json
import os
import pathlib
import urllib.error
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[1]
APP = "dcandes1unab"
DASH = "dtmi:homepageView:qifc38ol"
GRUPO = "ZHRtaTp1bmFiOmRjYW5kZXM6ZGNBbmRlc05vZG87MQ"
TOK = os.environ["TOK"]

RACKS = ["DC-RACKB-02", "DC-RACKC-03"]   # sensores modelados (Rack A es el simulador nativo)
TODOS = ["DC-RACKA-01", "DC-RACKB-02", "DC-RACKC-03", "DC-PASILLO-04", "DC-CLIMA-05",
         "DC-AIRE-06", "DC-AGUA-07", "DC-HUMO-08", "DC-ENERGIA-09", "DC-ACCESO-10"]

RANGO_DIA = {"type": "time", "duration": "P1D", "resolution": "PT5M"}
RANGO_SEM = {"type": "time", "duration": "P1W", "resolution": "PT30M"}


def cap(nombre, agregado="avg"):
    return {"capability": nombre, "aggregateFunction": agregado}


def lineChart(titulo, devices, caps, x, y, w=5, h=3, rango=None):
    cfg = {"type": "lineChart", "group": GRUPO, "devices": devices,
           "capabilities": caps, "queryRange": rango or RANGO_DIA,
           "format": {"legendEnabled": True, "xAxisEnabled": True, "yAxisEnabled": True}}
    return {"displayName": titulo, "configuration": cfg, "x": x, "y": y, "width": w, "height": h}


def kpi(titulo, devices, caps, x, y, w=2, h=1):
    cfg = {"type": "kpi", "group": GRUPO, "devices": devices, "capabilities": caps,
           "queryRange": RANGO_DIA}
    return {"displayName": titulo, "configuration": cfg, "x": x, "y": y, "width": w, "height": h}


def lkv(titulo, devices, caps, x, y, w=2, h=1):
    cfg = {"type": "lkv", "group": GRUPO, "devices": devices, "capabilities": caps,
           "showTrend": True}
    return {"displayName": titulo, "configuration": cfg, "x": x, "y": y, "width": w, "height": h}


def markdown(titulo, texto, x, y, w, h, imagen=None):
    cfg = {"type": "markdown", "description": texto}
    if imagen:
        cfg["image"] = imagen
    return {"displayName": titulo, "configuration": cfg, "x": x, "y": y, "width": w, "height": h}


def label(texto, x, y, w, h, tam=22):
    cfg = {"type": "label", "text": texto, "textSize": tam, "textSizeUnit": "pt", "wordWrap": True}
    return {"displayName": texto[:40], "configuration": cfg, "x": x, "y": y, "width": w, "height": h}


def main():
    logo = (RAIZ / "assets" / "logo_andescloud_dcandes1.png").read_bytes()
    logo_b64 = "data:image/png;base64," + base64.b64encode(logo).decode()

    tiles = [
        label("DC-ANDES-1 · Cuarto de Control (AndesCloud S.A.S.)", 0, 0, 6, 1, 24),
        markdown("Identidad del escenario",
                 "**DC-ANDES-1** — centro de datos urbano (Bucaramanga)\n\n"
                 "Flota heterogénea de **10 dispositivos** con **10 orígenes de envío** distintos.",
                 6, 0, 4, 2, logo_b64),
        {"displayName": "Dispositivos en el grupo", "x": 0, "y": 1, "width": 2, "height": 1,
         "configuration": {"type": "deviceCount", "group": GRUPO}},
        kpi("Temp. exhaust máx. racks (últ. 24 h)", RACKS, [cap("tempExhaust", "max")], 2, 1),
        kpi("PM2.5 sala (prom. 24 h)", ["DC-AIRE-06"], [cap("pm25", "avg")], 4, 1),
        lkv("PDU fila C — potencia", ["DC-ENERGIA-09"], [cap("potenciaKw", "avg")], 6, 2),
        lkv("Humo techo sala", ["DC-HUMO-08"], [cap("humo", "max")], 8, 2),

        lineChart("Temperaturas de racks B y C (intake / exhaust)", RACKS,
                  [cap("tempIntake", "avg"), cap("tempExhaust", "avg")], 0, 3),
        lineChart("Rack A — simulador nativo de IoT Central (valores aleatorios 0-100)", ["DC-RACKA-01"],
                  [cap("tempIntake", "avg"), cap("tempExhaust", "avg"), cap("humedadRack", "avg")], 5, 3),
        lineChart("Clima exterior — free-cooling", ["DC-CLIMA-05"],
                  [cap("tempExterior", "avg"), cap("radiacionSolar", "avg"), cap("humedadExterior", "avg")], 0, 6, rango=RANGO_SEM),
        lineChart("Calidad de aire de sala", ["DC-AIRE-06"],
                  [cap("pm25", "avg"), cap("pm10", "avg"), cap("co2", "avg")], 5, 6, rango=RANGO_SEM),
        lineChart("Energía de fila (PDU)", ["DC-ENERGIA-09"],
                  [cap("potenciaKw", "avg"), cap("corrienteA", "avg")], 0, 9),
        lineChart("Contención: humedad y presión diferencial", ["DC-PASILLO-04"],
                  [cap("humedadPasillo", "avg"), cap("deltaPresionPa", "avg")], 5, 9),
        lineChart("Detección de humo y temperatura de techo", ["DC-HUMO-08"],
                  [cap("humo", "avg"), cap("tempTecho", "avg")], 0, 12),
        lineChart("Humedad y agua bajo piso", ["DC-AGUA-07"],
                  [cap("humedadPiso", "avg"), cap("fugaAgua", "count")], 5, 12),
        markdown("Alertas configuradas",
                 "**Reglas activas:** temperatura de rack > 27 °C · humedad relativa > 60 % · "
                 "PM2.5 > 35 µg/m³ · fuga de agua = detectada · humo > 0,08 %obs/m · puerta abierta fuera de horario.\n\n"
                 "Las alarmas se acusan con el comando **acuseAlarma** desde la vista del dispositivo.",
                 0, 15, 10, 2),
    ]

    cuerpo = {"displayName": "Cuarto de Control DC-ANDES-1", "tiles": tiles, "personal": False}
    url = f"https://{APP}.azureiotcentral.com/api/dashboards/{DASH}?api-version=2022-06-30-preview"
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode(), method="PUT",
                                 headers={"Authorization": "Bearer " + TOK,
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read().decode())
            print("panel guardado:", r.status, "| mosaicos:", len(d.get("tiles", [])))
    except urllib.error.HTTPError as e:
        print("ERR", e.code, e.read().decode()[:400])


if __name__ == "__main__":
    main()
