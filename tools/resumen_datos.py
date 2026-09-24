#!/usr/bin/env python3
"""Resumen estadistico de la ventana de 4 dias a partir de las series locales.

Uso:
  python tools/resumen_datos.py                 # tabla markdown por dia y variable
  python tools/resumen_datos.py --json salida.json

Genera, por dispositivo y variable numerica:
  maximo, minimo, promedio, recuento y sumatoria (cuando aporta) por dia local.
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import statistics
from datetime import datetime

RAIZ = pathlib.Path(__file__).resolve().parents[1]
DATOS = RAIZ / "datos"
NO_NUMERICAS = {"ts_local", "ts_utc", "origen", "device_id", "tsDispositivo", "tsFuente"}
# variables cuya sumatoria tiene sentido operativo
SUMABLES = {"eventosAcceso", "lluviaMm", "potenciaKw", "corrienteA"}


def cargar(ruta: pathlib.Path) -> list[dict]:
    with ruta.open(encoding="utf-8") as fh:
        return [f for f in csv.DictReader(fh) if f.get("ts_local")]


def resumen_dia(filas: list[dict], variable: str) -> dict | None:
    valores = []
    for f in filas:
        v = f.get(variable)
        if v in (None, "", "True", "False"):
            continue
        try:
            valores.append(float(v))
        except ValueError:
            continue
    if not valores:
        return None
    d = {
        "recuento": len(valores),
        "max": round(max(valores), 2),
        "min": round(min(valores), 2),
        "promedio": round(statistics.fmean(valores), 2),
    }
    if variable in SUMABLES:
        d["sumatoria"] = round(sum(valores), 2)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None, help="guardar el resumen completo en JSON")
    args = ap.parse_args()

    salida: dict[str, dict] = {}
    for ruta in sorted(DATOS.glob("DC-*.csv")):
        dev = ruta.stem
        filas = cargar(ruta)
        if not filas:
            continue
        por_dia: dict[str, list[dict]] = {}
        for f in filas:
            dia = f["ts_local"][:10]
            por_dia.setdefault(dia, []).append(f)
        variables = [c for c in filas[0].keys() if c not in NO_NUMERICAS]
        salida[dev] = {}
        for dia, fs in sorted(por_dia.items()):
            salida[dev][dia] = {"muestras": len(fs), "variables": {}}
            for v in variables:
                r = resumen_dia(fs, v)
                if r:
                    salida[dev][dia]["variables"][v] = r

    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(salida, indent=1, ensure_ascii=False),
                                           encoding="utf-8")
        print("json:", args.json)

    print("\n# Resumen de la ventana de 4 dias (series locales)\n")
    for dev, dias in salida.items():
        print(f"\n## {dev}\n")
        print("| Fecha | Muestras | Variable | Máx | Mín | Promedio | Recuento | Sumatoria |")
        print("|---|---|---|---|---|---|---|---|")
        for dia, info in dias.items():
            for v, r in info["variables"].items():
                suma = r.get("sumatoria", "—")
                print(f"| {dia} | {info['muestras']} | {v} | {r['max']} | {r['min']} | "
                      f"{r['promedio']} | {r['recuento']} | {suma} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
