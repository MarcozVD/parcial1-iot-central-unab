#!/usr/bin/env python3
"""Descubre el esquema de queryRange/telemetry de los mosaicos de panel."""
import json
import os
import urllib.error
import urllib.request

APP = "dcandes1unab"
TOK = os.environ["TOK"]
DASH = "dtmi:homepageView:qifc38ol"
GRUPO = "ZHRtaTp1bmFiOmRjYW5kZXM6ZGNBbmRlc05vZG87MQ"


def put(tiles):
    url = f"https://{APP}.azureiotcentral.com/api/dashboards/{DASH}?api-version=2022-06-30-preview"
    req = urllib.request.Request(url, data=json.dumps({"displayName": "Cuarto de Control DC-ANDES-1", "tiles": tiles}).encode(),
                                 method="PUT", headers={"Authorization": "Bearer " + TOK, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


base = {"displayName": "Temperaturas de racks", "x": 0, "y": 4, "width": 5, "height": 3}
rangos = [
    {"type": "hours", "value": 24},
    {"type": "relative", "value": 24, "unit": "hours"},
    {"type": "lastHours", "value": 24},
    "24h",
    {"type": "day", "value": 1},
]
for qr in rangos:
    cfg = {"type": "lineChart", "title": "Temperaturas de racks", "group": GRUPO,
           "devices": ["DC-RACKA-01", "DC-RACKB-02", "DC-RACKC-03"],
           "telemetry": [{"name": "tempIntake", "aggregation": "avg"}],
           "queryRange": qr}
    c, b = put([{**base, "configuration": cfg}])
    print(f"queryRange={json.dumps(qr)}: {c} {b[:260]}")
    if c == 200:
        print("ACEPTADO:", json.dumps(json.loads(b)["tiles"][0]["configuration"])[:400])
        break
