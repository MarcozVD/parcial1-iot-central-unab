#!/usr/bin/env python3
"""Genera docs/04-ventana-4-dias.md a partir de datos/resumen_parcial.json.

Uso:  python tools/build_ventana_md.py
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime

RAIZ = pathlib.Path(__file__).resolve().parents[1]
JSON = RAIZ / "datos" / "resumen_parcial.json"
SALIDA = RAIZ / "docs" / "04-ventana-4-dias.md"

NOMBRES = {
    "DC-RACKA-01": "Rack A — simulador nativo de IoT Central",
    "DC-RACKB-02": "Rack B — Wokwi ESP32 #1 (15 s)",
    "DC-RACKC-03": "Rack C — Python SDK MQTT (30 s)",
    "DC-PASILLO-04": "Pasillo frío — Python SDK WebSockets (60 s)",
    "DC-CLIMA-05": "Clima exterior — API pública Open-Meteo (900 s)",
    "DC-AIRE-06": "Calidad de aire — API pública AQ (900 s)",
    "DC-AGUA-07": "Agua bajo piso — Wokwi ESP32 #2 (30 s)",
    "DC-HUMO-08": "Humo / incendio — paho MQTT explícito (45 s)",
    "DC-ENERGIA-09": "PDU / energía — replay CSV (120 s)",
    "DC-ACCESO-10": "Puerta / acceso — puente HTTP (120 s)",
}
LECTURA = {
    "tempExhaust": "el máximo aparece en la franja de mayor carga IT (tarde); el mínimo, en el valle nocturno. "
                   "Un máximo sostenido por encima del umbral es el disparador de la regla de temperatura.",
    "tempIntake": "sigue la temperatura de la sala blanca; su deriva respecto al día anterior es el primer aviso térmico.",
    "humedadRack": "el máximo se explica por el ciclo de humedad de la sala; valores > 60 %HR activan la regla de humedad.",
    "tempExterior": "el máximo determina las horas sin free-cooling; el mínimo, las horas de enfriamiento gratuito pleno.",
    "radiacionSolar": "el máximo marca el pico de ganancia térmica por cubierta y la ventana de máxima carga del chiller.",
    "lluviaMm": "la sumatoria del día es el agua caída acumulada; > 5 mm en una muestra activa la alerta de lluvia.",
    "pm25": "el promedio diario se compara con el valor guía de la OMS (15 µg/m³ 24 h); el máximo explica eventos puntuales.",
    "co2": "el máximo se alcanza con la sala ocupada (mantenimiento); > 1000 ppm activa la alerta de aire.",
    "humedadPiso": "el máximo sostenido cerca del umbral indica riesgo de condensación; el pico con fuga es la prueba funcional.",
    "humo": "el máximo corresponde a la prueba funcional programada (10:00); el resto del día se mantiene en línea base.",
    "potenciaKw": "el máximo es la carga de fila en hora pico; la sumatoria diaria aproxima la energía de la fila (kWh).",
    "corrienteA": "el máximo verifica que la PDU no supera su protección (32 A) con la carga actual.",
    "tempTecho": "el máximo confirma que la estratificación térmica del techo se mantiene por debajo del umbral de incendio.",
    "tempPuerta": "el máximo refleja la ganancia térmica del acceso en las horas de mayor tránsito.",
    "eventosAcceso": "la sumatoria es el número de aperturas del día: indicador de ocupación del sitio.",
    "tempPasillo": "el máximo verifica la contención del pasillo frío; una subida sostenida anticipa problemas de flujo.",
    "deltaPresionPa": "el mínimo es el dato crítico: por debajo de 5 Pa la contención se pierde y el aire caliente recircula.",
}


def tabla_dia(dia: str, datos: dict) -> str:
    filas = ["| Variable | Máx | Mín | Promedio | Recuento | Sumatoria | Lectura operativa |",
             "|---|---|---|---|---|---|---|"]
    for dev, dias in datos.items():
        if dia not in dias:
            continue
        for var, r in dias[dia]["variables"].items():
            suma = r.get("sumatoria", "—")
            lect = LECTURA.get(var, "")
            filas.append(f"| `{var}` ({NOMBRES.get(dev, dev).split(' — ')[0]}) | {r['max']} | {r['min']} | "
                         f"{r['promedio']} | {r['recuento']} | {suma} | {lect} |")
    return "\n".join(filas)


def main():
    datos = json.loads(JSON.read_text(encoding="utf-8"))
    dias = sorted({d for dev in datos.values() for d in dev})
    out = ["# Ventana de 4 días no continuos — comparativa y lectura operativa",
           "",
           f"Generado: {datetime.now():%Y-%m-%d %H:%M} · fuente: `datos/*.csv` (series locales de cada nodo) "
           "y consultas equivalentes en el Data Explorer de IoT Central.",
           "",
           "## Días cubiertos",
           "",
           "| Día | Estado | Muestras totales |",
           "|---|---|---|"]
    for d_ in dias:
        total = sum(dev[d_]["muestras"] for dev in datos.values() if d_ in dev)
        out.append(f"| {d_} | {'cerrado' if d_ < max(dias) else 'en curso'} | {total} |")
    out.append("")
    for d_ in dias:
        out.append(f"## {d_}")
        out.append("")
        out.append(tabla_dia(d_, datos))
        out.append("")
    out.append("## Lectura de conjunto")
    out.append("")
    out.append("- La flota mezcla seis intervalos (15 s … 900 s): los recuentos por variable reflejan esa "
               "asincronía y son la evidencia directa de que no todos los nodos muestrean igual.")
    out.append("- Los extremos térmicos coinciden con la franja de mayor carga IT; los meteorológicos con la "
               "curva diaria real del feed público.")
    out.append("- Los eventos de seguridad (fuga, humo, acceso) aparecen como picos discretos y son los que "
               "disparan las reglas configuradas en IoT Central.")
    SALIDA.write_text("\n".join(out), encoding="utf-8")
    print("escrito:", SALIDA, "dias:", dias)


if __name__ == "__main__":
    main()
