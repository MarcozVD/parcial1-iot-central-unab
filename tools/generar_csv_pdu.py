#!/usr/bin/env python3
"""Genera el historico CSV de la PDU de fila C (dia tipico, 120 s de resolucion).

Modelo documentado (ver docs/datasheets.md):
  carga_it(t) = 0.42 + 0.30*(1+cos((t-15)*pi/12))/2       [perfil IT, valle 03:00, pico 15:00]
  potenciaKw  = 4.1 + 3.4*carga_it + ruido(0.25)
  factorPot = 0.965 + ruido(0.012)  (recortado a [0.90, 0.995])
  corrienteA = potenciaKw*1000 / (230*factorPot)   # PDU monofasica 230 V
"""
import csv
import math
import pathlib
import random
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "datos" / "historico_pdu_fila.csv"
FECHA = "2026-09-20"


def main():
    random.seed(20260920)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with SALIDA.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ts_origen", "carga_it", "potenciaKw", "corrienteA", "factorPotencia"])
        for seg in range(0, 24 * 3600, 120):
            h = seg / 3600.0
            carga = 0.42 + 0.30 * (1 + math.cos((h - 15.0) * math.pi / 12.0)) / 2
            kw = 4.1 + 3.4 * carga + random.uniform(-0.25, 0.25)
            pf = min(0.995, max(0.90, 0.965 + random.uniform(-0.012, 0.012)))
            ia = kw * 1000.0 / (230.0 * pf)
            ts = f"{FECHA}T{int(h):02d}:{int((h % 1) * 60):02d}:00-05:00"
            w.writerow([ts, round(carga, 3), round(kw, 2), round(ia, 2), round(pf, 3)])
    print(f"generado {SALIDA} ({24*3600//120} filas)")


if __name__ == "__main__":
    sys.exit(main())
