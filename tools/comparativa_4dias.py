#!/usr/bin/env python3
"""Comparativa completa de las 4 fechas: max/min/promedio/recuento/sumatoria por variable.

Combina las fuentes correctas de cada fecha:
- 24, 25, 26-sep: datos/*.csv (portatil), recortado por fecha
- 27-sep: datos/remoto_dia4/*.csv (servidor Ubuntu, unica fuente valida de esa fecha)

Imprime una tabla markdown lista para pegar en docs/04-ventana-4-dias.md.
"""
import csv
import pathlib
import statistics as st

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FECHAS = ["2026-09-24", "2026-09-25", "2026-09-26", "2026-09-27"]

# variable -> (etiqueta para el informe, si tiene sentido sumar)
VARS_SUMABLES = {"eventosAcceso", "potenciaKw", "corrienteA", "lluviaMm"}


def leer_variables(carpeta: pathlib.Path, fecha: str) -> dict:
    """dispositivo/variable -> lista de valores numericos de esa fecha."""
    datos: dict[str, list[float]] = {}
    for f in sorted(carpeta.glob("DC-*.csv")):
        if "campo" in f.stem:
            continue
        with f.open(encoding="utf-8") as fh:
            r = csv.DictReader(fh)
            cols = [c for c in r.fieldnames or [] if c not in
                    ("ts_local", "ts_utc", "origen", "device_id", "tsFuente", "tsDispositivo")]
            for row in r:
                if not row["ts_local"].startswith(fecha):
                    continue
                for c in cols:
                    v = row.get(c, "")
                    try:
                        fv = float(v)
                    except (ValueError, TypeError):
                        continue
                    clave = f"{c} ({f.stem})"
                    datos.setdefault(clave, []).append(fv)
    return datos


def main() -> None:
    fuentes = {
        "2026-09-24": RAIZ / "datos",
        "2026-09-25": RAIZ / "datos",
        "2026-09-26": RAIZ / "datos",
        "2026-09-27": RAIZ / "datos" / "remoto_dia4",
    }
    for fecha in FECHAS:
        carpeta = fuentes[fecha]
        datos = leer_variables(carpeta, fecha)
        print(f"\n## {fecha} (fuente: {carpeta.relative_to(RAIZ)})\n")
        print("| Variable | Max | Min | Promedio | Recuento | Sumatoria |")
        print("|---|---|---|---|---|---|")
        for clave in sorted(datos):
            vals = datos[clave]
            var = clave.split(" (")[0]
            suma = round(sum(vals), 2) if var in VARS_SUMABLES else "—"
            print(f"| `{clave}` | {max(vals):.2f} | {min(vals):.2f} | {st.mean(vals):.2f} | {len(vals)} | {suma} |")


if __name__ == "__main__":
    main()
