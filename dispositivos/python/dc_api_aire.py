#!/usr/bin/env python3
"""
dc_api_aire.py - Nodo DC-AIRE-06: **puente de API publica de calidad del aire**
con INGESTA POR HTTPS/REST (API de dispositivo del IoT Hub, puerto 443).
Consulta el feed abierto Open-Meteo Air Quality (PM2.5, PM10, AQI de la ubicacion del
centro de datos) y estima el CO2 interior con el modelo de ocupacion documentado.

Origen de envio: "API publica de calidad de aire (HTTPS/REST 443)" | Intervalo: 900 s
El SAS se firma con la clave simetrica del dispositivo y viaja en la cabecera
Authorization; el topic logico es /devices/{id}/messages/events.
"""
from __future__ import annotations

import json
import signal
import sys
import time
import urllib.request
from datetime import datetime, timezone

import dc_comun as C

DEVICE_ID = "DC-AIRE-06"
ZONA = "Calidad de aire de sala"
UBIC = "Sala blanca - retorno de CRAC 2"
ORIGEN = "API publica de calidad de aire (HTTPS/REST 443)"
FAB, MODELO, VERSION = "Plantower PMS7003 + Sensirion SCD41 / feed Open-Meteo AQ", "Puente-API-Aire/1.0", "1.2.1"
INTERVALO = 900
LAT, LON = 7.1193, -73.1227
API_VERSION = "2018-06-30"     # API de dispositivo por HTTPS del IoT Hub
URL_AQ = ("https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
          "&current=pm2_5,pm10,us_aqi,european_aqi&timezone=America%2FBogota")

bit = C.Bitacora(DEVICE_ID)
parar = {"v": False}


def consultar_fuente() -> dict:
    with urllib.request.urlopen(URL_AQ.format(lat=LAT, lon=LON), timeout=25) as r:
        cur = json.load(r)["current"]
    pm25 = float(cur["pm2_5"])
    pm10 = float(cur["pm10"])
    aqi = float(cur["us_aqi"])
    # CO2 interior: modelo de ocupacion + filtracion (documentado en docs/datasheets.md)
    hora = C.hora_actual()
    ocupacion = 1.0 if 7.5 <= hora <= 18.5 else 0.25
    co2 = 415.0 + 230.0 * ocupacion + 6.0 * pm25 + 12.0 * (0.5 - abs(0.5 - (hora % 24) / 24.0))
    return {
        "tsFuente": cur["time"] + " (America/Bogota, Open-Meteo AQ)",
        "pm25": round(pm25, 2),
        "pm10": round(pm10, 2),
        "aqi": round(aqi, 1),
        "co2": round(co2, 1),
    }


def enviar_https(hub: str, clave: str, datos: dict) -> int:
    """POST a la API HTTPS del IoT Hub (device -> cloud)."""
    url = f"https://{hub}/devices/{DEVICE_ID}/messages/events/?api-version={API_VERSION}"
    sas = C.generar_sas(f"{hub}/devices/{DEVICE_ID}", clave, ttl=3600)
    req = urllib.request.Request(url, data=json.dumps(datos).encode("utf-8"), method="POST",
                                 headers={"Authorization": sas,
                                          "Content-Type": "application/json",
                                          "Content-Encoding": "utf-8"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.status


def main():
    creds = C.cargar_credenciales(DEVICE_ID)
    if not creds["primary_key"]:
        bit.error("sin credenciales (.secrets/env). Aborto.")
        return 1
    hub = C.hub_de_creds(DEVICE_ID)
    if not hub:
        bit.error("falta el hub (datos/hub_DC-AIRE-06.txt). Ejecute antes un nodo SDK o registre el DPS.")
        return 1
    bit.info(f"ingesta HTTPS/REST hacia {hub} (api-version={API_VERSION}, TLS 443)")
    # Propiedades reportadas por HTTPS (mismo camino REST, $iothub/twin no aplica)
    props_url = f"https://{hub}/twin/devices/{DEVICE_ID}?api-version=2020-09-30"
    props = C.propiedades(DEVICE_ID, ZONA, UBIC, ORIGEN, FAB, MODELO, VERSION, INTERVALO)
    try:
        sas = C.generar_sas(f"{hub}/devices/{DEVICE_ID}", creds["primary_key"], ttl=3600)
        req = urllib.request.Request(props_url, data=json.dumps(props).encode(), method="PUT",
                                     headers={"Authorization": sas, "Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=25)
        bit.info(f"propiedades reportadas por twin REST: {props}")
    except Exception as e:
        bit.info(f"twin REST no disponible ({type(e).__name__}); se reintentara al final del ciclo")

    def _salir(*_):
        parar["v"] = True
    signal.signal(signal.SIGINT, _salir)
    signal.signal(signal.SIGTERM, _salir)

    n = 0
    while not parar["v"]:
        if C.en_pausa(DEVICE_ID):
            bit.info("PAUSA documentada")
            time.sleep(5)
            continue
        n += 1
        try:
            datos = consultar_fuente()
            datos["tsDispositivo"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            codigo = enviar_https(hub, creds["primary_key"], datos)
            bit.telemetria(datos, ORIGEN)
            bit.info(f"HTTP {codigo} aceptado por el hub (mensaje #{n})")
        except Exception as e:
            bit.error(f"fallo de ingesta HTTPS: {type(e).__name__}: {e}")
        time.sleep(INTERVALO)

    return 0


if __name__ == "__main__":
    sys.exit(main())
