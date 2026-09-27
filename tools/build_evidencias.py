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
     "15 %", "capturas 01, 02, 06-09, 13 · secciones 4, 5 y 9 del informe · RULES_*.png"],
    ["Datos, Digital Twin y arquitectura: catálogo de 10 dispositivos, datasheets, rangos de industria, diagrama con telecomunicaciones",
     "20 %", "docs/01-catalogo-dispositivos.md · docs/02-datasheets-y-parametros.md · diagrama_arquitectura.png"],
    ["Heterogeneidad de orígenes (incluye Digital Twin, Wokwi, Python, API pública, feed meteorológico); asincronía, desconexión y operación en línea",
     "20 %", "capturas 02-05, 10-12, 14-21 (datos crudos por origen y por fecha) · logs de nodos · sección 6.1 del informe (4 incidentes reales de desconexión/reconexión)"],
    ["Ventana de 4 días y comparativa (máx/mín/promedio/recuento/sumatoria)",
     "15 %", "docs/04-ventana-4-dias.md · sección 7 y anexo B del informe · capturas del Data Explorer · [tabla comparativa final pendiente de cierre de la fecha 4]"],
    ["Control room y documento: panel personalizado, tablas de parámetros, historial de versiones, repo limpio",
     "15 %", "captura 09 (panel) · informe secciones 8 y 11 · README del repositorio"],
    ["Sustentación y dos códigos en vivo", "15 %", "capturas 15-16 y 19-21 (Python en el servidor Ubuntu y Wokwi en el navegador, en vivo el 26 y 27 de septiembre)"],
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

d.page_break()
d.h("3.3 Vistas de operador de la plantilla", 1)
d.p("Además del panel de aplicación (sección 3), la plantilla publica dos vistas de operador propias: "
    "Overview (KPIs y gráficos de todas las telemetrías del gemelo) y About (propiedades editables). "
    "Ambas se generan a partir del modelo publicado y están disponibles para cualquier dispositivo de la flota.")
d.figure(E + "dia4-views-plantilla.png", "Captura 13 — Vistas configuradas en la plantilla Nodo DC-ANDES-1 (Overview, About).")

d.h("4. Días 2 a 4 — migración a servidor remoto y su evidencia", 1)
d.p("A partir del 25 de septiembre los nodos Python se trasladaron a un servidor Ubuntu remoto "
    "(52.252.133.127) para ejecutar, en la sustentación, el segundo de los dos códigos en un equipo "
    "distinto al portátil. Las capturas siguientes documentan el estado de esa infraestructura en las "
    "fechas 3 y 4, ya con el supervisor remoto corregido (incidente 6.1 del informe).")
d.h("4.1 Día 3 (26-sep) — servidor estable, 8/8 nodos", 2)
d.figure(E + "dia3-portal-flota.png", "Captura 14 — Flota completa (10 dispositivos) el 26 de septiembre.")
d.figure(E + "dia3-datos-rackc.png", "Captura 15 — DC-RACKC-03 publicando desde el servidor Ubuntu: Conectado, telemetría cada 30 s.")
d.figure(E + "dia3-wokwi-rackb.png", "Captura 16 — Monitor serie del ESP32 Rack B publicando en vivo (26-sep).")
d.figure(E + "dia3-panel.png", "Captura 17 — Panel Cuarto de Control con datos del 26 de septiembre.")

d.h("4.2 Día 4 (27-sep) — solo servidor remoto + Rack B", 2)
d.p("Para la fecha 4 se detuvo intencionalmente la flota local: toda la telemetría Python proviene "
    "exclusivamente del servidor Ubuntu, aislando esa infraestructura como el segundo código en vivo de la "
    "sustentación (el primero es el ESP32 en el navegador). La ventana cerró en 4 h 32 min (10:28-15:00), "
    "por encima del mínimo de 4 horas.")
d.figure(E + "dia4-portal-flota.png", "Captura 18 — Flota el 27 de septiembre, con los 7 nodos Python publicando solo desde el servidor.")
d.figure(E + "dia4-datos-rackc.png", "Captura 19 — DC-RACKC-03 (servidor Ubuntu), Conectado, 27/9/2026.")
d.figure(E + "dia4-datos-humo.png", "Captura 20 — DC-HUMO-08 (servidor Ubuntu), 27/9/2026.")
d.figure(E + "dia4-wokwi-rackb.png", "Captura 21 — Monitor serie del ESP32 Rack B, 27/9/2026.")
d.figure(E + "dia4-cierre-flota.png", "Captura 22 — Cierre de la fecha 4: flota completa en el portal, 27/9/2026 15:00.")
d.p("El ESP32 del nodo de agua no llegó a simular en esta fecha (Wokwi con los servidores de compilación "
    "saturados, confirmado con un proyecto nuevo desde cero); el Rack B tuvo cortes intermitentes por el "
    "mismo motivo. Es una limitación de la plataforma Wokwi, no del sketch, y no afecta la cobertura "
    "general porque el nodo de agua ya tiene datos completos en las fechas 1 y 3.")

d.h("5. Logs de los nodos (recortes reales)", 1)
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

d.h("6. Estado de la flota en el arranque", 1)
ruta = pathlib.Path("logs/supervisor.log")
if ruta.exists():
    d.code([ln.rstrip("\n") for ln in ruta.open(encoding="utf-8")][:14] + ["…"])
d.p("El supervisor arranca los ocho nodos locales, los reinicia si terminan y deja el estado en "
    "logs/supervisor_estado.json. Un cronjob de Hermes relanza el supervisor si no está corriendo.")

d.save("informe/Evidencias_Parcial1_DC-ANDES-1.docx")
print("anexo generado: informe/Evidencias_Parcial1_DC-ANDES-1.docx")
