#!/usr/bin/env python3
"""Genera el anexo de evidencias del Parcial 1 (Word + PDF).

Uso:  python tools/build_evidencias.py
"""
import pathlib
import sys

sys.path.insert(0, "tools")
from docstyle import Doc  # noqa: E402

E = "evidencias/"
d = Doc("Parcial 1 · Evidencias DC-ANDES-1")

d.cover(
    "Universidad Autónoma de Bucaramanga · IoT + Cloud + Sistemas Distribuidos",
    "Anexo de evidencias",
    "Parcial 1 — Escenario 5.2 Centro de datos: flota heterogénea de 10 dispositivos sobre Azure IoT Central",
    [("Estudiante", "Marcos Valera Daza"),
     ("Aplicación", "dcandes1unab · https://dcandes1unab.azureiotcentral.com"),
     ("Ventana", "24 al 27 de septiembre de 2026 (4 días no continuos)"),
     ("Contenido", "matriz de cumplimiento, capturas del portal, logs de los nodos, tablas de la ventana y comandos")],
    [("Uso: ", {"b": 1}),
     "cada evidencia se numera igual que su sección del informe; las capturas provienen del portal y los "
     "registros de los propios nodos (logs y CSVs en el repositorio)."])

d.toc()

d.h("Matriz de cumplimiento (rúbrica → evidencia)", 1)
d.table(["Indicador de evaluación", "Peso", "Dónde está la evidencia"], [
    ["IoT Template (setup + test): aplicación, plantilla publicada, properties, comandos, Rules, identidad visual",
     "15 %", "capturas 01, 02, 06-09 · secciones 4 y 9 del informe · RULES_*.png"],
    ["Datos, Digital Twin y arquitectura: catálogo de 10 dispositivos, datasheets, rangos de industria, diagrama con telecomunicaciones",
     "20 %", "docs/01-catalogo-dispositivos.md · docs/02-datasheets-y-parametros.md · diagrama_arquitectura.png"],
    ["Heterogeneidad de orígenes (incluye Digital Twin, Wokwi, Python, API pública, feed meteorológico); asincronía, desconexión y operación en línea",
     "20 %", "capturas 02-05 y 10-12 (datos crudos por origen) · logs de nodos · hueco documentado"],
    ["Ventana de 4 días y comparativa (máx/mín/promedio/recuento/sumatoria)",
     "15 %", "docs/04-ventana-4-dias.md · resumen_datos.py · capturas del Data Explorer"],
    ["Control room y documento: panel personalizado, tablas de parámetros, historial de versiones, repo limpio",
     "15 %", "captura 09 (panel) · informe secciones 8 y 11 · README del repositorio"],
    ["Sustentación y dos códigos en vivo", "15 %", "capturas 10-12 (Python en el portátil y Wokwi en el navegador en vivo)"],
], widths_mm=[70, 14, 79])

d.h("1. Flota en Azure IoT Central", 1)
d.p("La lista de dispositivos muestra los diez nodos con la plantilla publicada y el estado de cada uno. "
    "El estado Connected/Disconnected se sigue además por nodo en la vista de dispositivo y en los datos sin procesar.")
d.figure(E + "01-flota-10-dispositivos.png", "Captura 01 — Flota de 10 dispositivos: id, estado, plantilla y organización.")

d.h("2. Datos sin procesar por origen de envío", 1)
d.p("Cada captura prueba que un origen distinto publica en Central: el nodo SDK (MQTT/TLS), el puente de "
    "API pública, el simulador nativo y los nodos Wokwi.")
d.figure(E + "02-datos-crudos-rackc.png", "Captura 02 — DC-RACKC-03 (Python SDK MQTT): telemetría cada 30 s y evento de conexión.")
d.figure(E + "03-datos-crudos-clima.png", "Captura 03 — DC-CLIMA-05 (API pública Open-Meteo): valor real con marca de tiempo de la fuente.")
d.figure(E + "05-datos-crudos-racka-simulado.png", "Captura 04 — DC-RACKA-01 (simulador nativo de la plantilla).")

d.page_break()
d.h("3. Cuarto de control", 1)
d.figure(E + "04-panel-cuarto-de-control.png", "Captura 09 — Panel Cuarto de Control DC-ANDES-1 con identidad, KPIs, gráficos y alertas.")

d.h("3.1 Reglas configuradas", 1)
d.p("Las seis reglas de la aplicación quedaron creadas y habilitadas sobre la plantilla Nodo DC-ANDES-1, "
    "cada una con su condición sobre una telemetría del modelo y una acción de correo al operador. "
    "La captura corresponde al estado de la aplicación el 24 de septiembre de 2026.")
d.figure(E + "06-reglas-6-habilitadas.png", "Captura 06 — Reglas: seis reglas habilitadas (temperatura, humedad de rack, humo, PM2.5, humedad de piso, eventos de acceso).")

d.h("3.2 Flota y estado de aprovisionamiento al cierre del día", 1)
d.figure(E + "07-flota-conexion-24sep.png", "Captura 07 — Lista de dispositivos: los diez nodos aprovisionados con la plantilla Nodo DC-ANDES-1.")

d.h("4. Logs de los nodos (recortes reales)", 1)
d.p("Los expedientes completos están en logs/. Se incluyen recortes de arranque y de publicación de cada "
    "origen para que se vea el protocolo y el intervalo reales.")
for nombre, archivo, texto in [
    ("DC-RACKC-03 · SDK MQTT", "logs/DC-RACKC-03.log", "DPS OK, MQTT/TLS conectado y TX cada 30 s"),
    ("DC-PASILLO-04 · SDK sobre WebSockets", "logs/DC-PASILLO-04.log", "transporte alterno en 443"),
    ("DC-HUMO-08 · paho explícito", "logs/DC-HUMO-08.log", "DPS por MQTT a mano y TX con SAS manual"),
    ("DC-ACCESO-10 · puente HTTP/REST", "logs/DC-ACCESO-10.log", "reenvío del sensor de campo al hub"),
]:
    ruta = pathlib.Path(archivo)
    if not ruta.exists():
        continue
    lineas = [ln.rstrip("\n") for ln in ruta.open(encoding="utf-8")][:6]
    d.h(nombre, 2)
    d.code(lineas + ["…"])
    d.p(texto, size=9.5)

d.h("5. Estado de la flota en el arranque", 1)
ruta = pathlib.Path("logs/supervisor.log")
if ruta.exists():
    d.code([ln.rstrip("\n") for ln in ruta.open(encoding="utf-8")][:14] + ["…"])
d.p("El supervisor arranca los ocho nodos locales, los reinicia si terminan y deja el estado en "
    "logs/supervisor_estado.json. Un cronjob de Hermes relanza el supervisor si no está corriendo.")

d.save("informe/Evidencias_Parcial1_DC-ANDES-1.docx")
print("anexo generado: informe/Evidencias_Parcial1_DC-ANDES-1.docx")
