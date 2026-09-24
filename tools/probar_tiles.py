#!/usr/bin/env python3
"""Prueba de esquema de mosaicos de panel (API 2022-06-30-preview).

Envia un panel con un mosaico de grafico de lineas y muestra la respuesta del servicio
para descubrir el esquema exacto que acepta.
"""
import json
import os
import pathlib
import urllib.error
import urllib.request

APP = "dcandes1unab"
TOK = os.environ["TOK"]
DASH = "dtmi:homepageView:qifc38ol"
GRUPO = "ZHRtaTp1bmFiOmRjYW5kZXM6ZGNBbmRlc05vZG87MQ"
DEVS = ["DC-RACKA-01", "DC-RACKB-02", "DC-RACKC-03"]


def api(metodo, ruta, cuerpo=None, api_version="2022-06-30-preview"):
    url = f"https://{APP}.azureiotcentral.com{ruta}?api-version={api_version}"
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, method=metodo,
                                 headers={"Authorization": "Bearer " + TOK,
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


candidatos = {
    "A_linea": {"displayName": "Temperaturas de racks", "x": 0, "y": 4, "width": 5, "height": 3,
                "configuration": {"type": "lineChart", "title": "Temperaturas de racks",
                                  "showLegend": True, "deviceGroup": GRUPO, "devices": DEVS,
                                  "telemetry": [{"name": "tempIntake", "aggregation": "avg"},
                                                {"name": "tempExhaust", "aggregation": "avg"}]}},
    "B_kpi": {"displayName": "PM2.5 ultimo", "x": 5, "y": 4, "width": 2, "height": 2,
              "configuration": {"type": "kpi", "title": "PM2.5", "deviceGroup": GRUPO,
                                "devices": ["DC-AIRE-06"],
                                "telemetry": {"name": "pm25", "aggregation": "avg"}}},
    "C_texto": {"displayName": "Marca", "x": 7, "y": 4, "width": 3, "height": 1,
                "configuration": {"type": "markdown", "description": "**DC-ANDES-1** - Cuarto de control"}},
}

for nombre, tile in candidatos.items():
    cuerpo = {"displayName": "Cuarto de Control DC-ANDES-1", "tiles": [tile]}
    c, b = api("PUT", f"/api/dashboards/{DASH}", cuerpo)
    print(f"{nombre}: {c} {b[:220]}")
    if c == 200:
        print("   -> aceptado")
