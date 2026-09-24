#!/usr/bin/env python3
"""Estado de la flota en un vistazo (para las actualizaciones diarias).

Uso:  python tools/estado_diario.py
"""
from __future__ import annotations

import csv
import json
import pathlib
from datetime import datetime

RAIZ = pathlib.Path(__file__).resolve().parents[1]
DATOS = RAIZ / "datos"
LOGS = RAIZ / "logs"


def main():
    print(f"# Estado de la flota DC-ANDES-1 · {datetime.now():%Y-%m-%d %H:%M}\n")
    est = LOGS / "supervisor_estado.json"
    if est.exists():
        d = json.loads(est.read_text(encoding="utf-8"))
        vivos = sum(1 for v in d.values() if v.get("pid"))
        print(f"Nodos gestionados por el supervisor: {len(d)} · con proceso vivo: {vivos}")
        for k, v in d.items():
            print(f"  - {k:14s} pid={v.get('pid')} arranques={v.get('arranques')}")
    print()
    print("| Nodo | Muestras hoy | Última muestra local | Último valor |")
    print("|---|---|---|---|")
    hoy = datetime.now().strftime("%Y-%m-%d")
    for ruta in sorted(DATOS.glob("DC-*.csv")):
        with ruta.open(encoding="utf-8") as fh:
            filas = [f for f in csv.DictReader(fh) if f.get("ts_local", "").startswith(hoy)]
        if not filas:
            print(f"| {ruta.stem} | 0 | — | — |")
            continue
        ult = filas[-1]
        valores = {k: v for k, v in ult.items()
                   if k not in ("ts_local", "ts_utc", "origen", "device_id", "tsDispositivo", "tsFuente")}
        print(f"| {ruta.stem} | {len(filas)} | {ult['ts_local'][11:19]} | "
              f"{json.dumps(valores, ensure_ascii=False)} |")
    print()
    print("## Reglas y alertas (revisar en el portal)")
    print("- Temperatura de rack > 35 °C · Humedad > 60 % · Fuga de agua · Humo > 0,08 · PM2.5 > 35 · Acceso fuera de horario")
    pausa = DATOS / "pausa_DC-HUMO-08.json"
    if pausa.exists():
        print(f"- Pausa programada del nodo de humo: {json.loads(pausa.read_text(encoding='utf-8'))['desde']} → "
              f"{json.loads(pausa.read_text(encoding='utf-8'))['hasta']}")


if __name__ == "__main__":
    main()
