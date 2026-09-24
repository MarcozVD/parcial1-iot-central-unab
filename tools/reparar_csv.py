#!/usr/bin/env python3
"""Repara los CSV de telemetria local: pone la cabecera correcta con los nombres de
variable de cada dispositivo (los archivos escritos antes del arreglo quedaron con una
cabecera de 4 columnas y filas de 8).

Uso: python tools/reparar_csv.py
"""
from __future__ import annotations

import csv
import pathlib

DATOS = pathlib.Path(__file__).resolve().parents[1] / "datos"

VARS = {
    "DC-RACKA-01": ["tempIntake", "tempExhaust", "humedadRack", "tsDispositivo"],
    "DC-RACKB-02": ["tempIntake", "tempExhaust", "humedadRack", "tsDispositivo"],
    "DC-RACKC-03": ["tempIntake", "tempExhaust", "humedadRack", "tsDispositivo"],
    "DC-PASILLO-04": ["tempPasillo", "humedadPasillo", "deltaPresionPa", "tsDispositivo"],
    "DC-CLIMA-05": ["tsFuente", "tempExterior", "humedadExterior", "lluviaMm", "vientoKmh",
                    "radiacionSolar", "tsDispositivo"],
    "DC-AIRE-06": ["tsFuente", "pm25", "pm10", "aqi", "co2", "tsDispositivo"],
    "DC-AGUA-07": ["fugaAgua", "humedadPiso", "tsDispositivo"],
    "DC-HUMO-08": ["humo", "tempTecho", "tsDispositivo"],
    "DC-ENERGIA-09": ["tsFuente", "potenciaKw", "corrienteA", "factorPotencia", "tsDispositivo"],
    "DC-ACCESO-10": ["puertaAbierta", "eventosAcceso", "tempPuerta", "tsDispositivo"],
    "DC-ACCESO-10-campo": ["puertaAbierta", "eventosAcceso", "tempPuerta"],
}
BASE = ["ts_local", "ts_utc", "origen", "device_id"]


def reparar(ruta: pathlib.Path) -> str:
    dev = ruta.stem
    filas = list(csv.reader(ruta.open(encoding="utf-8")))
    if not filas:
        return f"{dev}: vacio"
    vars_ = VARS.get(dev)
    if vars_ is None:
        return f"{dev}: sin mapa de variables (se deja igual)"
    esperado = len(BASE) + len(vars_)
    buenas = [f for f in filas[1:] if len(f) == esperado]
    malas = len(filas) - 1 - len(buenas)
    with ruta.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(BASE + vars_)
        w.writerows(buenas)
    return f"{dev}: {len(buenas)} filas normalizadas, {malas} descartadas"


def main():
    for ruta in sorted(DATOS.glob("*.csv")):
        if ruta.name.startswith("historico"):
            continue
        print(" ", reparar(ruta))


if __name__ == "__main__":
    main()
