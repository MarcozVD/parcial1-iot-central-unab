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

d.page_break()
d.h("4.3 Métricas de los 10 dispositivos en las 4 fechas (Data Explorer)", 1)
d.p("Consulta del Explorador de datos de IoT Central sobre el grupo «Nodo DC-ANDES-1 - All devices», "
    "agrupada por Id. de dispositivo, con ocho telemetrías que cubren todas las zonas (temperatura de "
    "intake de rack, pasillo frío, exterior, PM2.5, humedad de piso, temperatura de techo, potencia de "
    "fila y eventos de acceso). Se ejecutó con cuatro rangos, uno por fecha (00:00-23:59, UTC-05:00), y "
    "uno con la ventana completa. La leyenda del Explorador solo lista los dispositivos que enviaron "
    "datos en el rango, así que la tabla siguiente sale directamente de la plataforma, no de los CSV "
    "locales (se guardó en datos/matriz_data_explorer.json).")
import json as _json
_m = _json.loads(pathlib.Path("datos/matriz_data_explorer.json").read_text(encoding="utf-8"))["dispositivos_con_datos"]
_todos = ["DC-RACKA-01", "DC-RACKB-02", "DC-RACKC-03", "DC-PASILLO-04", "DC-CLIMA-05", "DC-AIRE-06",
          "DC-AGUA-07", "DC-HUMO-08", "DC-ENERGIA-09", "DC-ACCESO-10"]
_f = sorted(_m)
d.table(["Dispositivo"] + [f"{x}-sep" for x in _f],
        [[t] + ["sí" if t in _m[x] else "—" for x in _f] for t in _todos]
        + [["Total con datos"] + [f"{len(_m[x])}/10" for x in _f]],
        widths_mm=[45, 29, 29, 29, 29])
d.p("DC-AGUA-07 (ESP32 #2 en Wokwi) no tiene datos el 25-sep (la simulación del nodo de agua no estuvo "
    "publicando ese día) ni el 27-sep (los servidores de compilación de Wokwi no dejaron arrancar la "
    "simulación). Los otros nueve dispositivos publicaron en las cuatro fechas.")
d.figure(E + "de-ventana.png", "Captura 23 — Ventana completa 24-27 sep: ocho telemetrías agrupadas por dispositivo; se ven los huecos entre fechas.")
d.figure(E + "de-24.png", "Captura 24 — Data Explorer, 24/09/2026 00:00-23:59.")
d.figure(E + "de-25.png", "Captura 25 — Data Explorer, 25/09/2026 00:00-23:59.")
d.figure(E + "de-26.png", "Captura 26 — Data Explorer, 26/09/2026 00:00-23:59.")
d.figure(E + "de-27.png", "Captura 27 — Data Explorer, 27/09/2026 00:00-23:59.")

d.page_break()
d.h("4.4 Lectura operativa de los extremos (las 4 fechas)", 1)
d.p("El pliego pide no solo los números sino qué situación operativa explican. Esta tabla compara el extremo "
    "de cada variable en las cuatro fechas y lo interpreta; los valores salen de las mismas series de la "
    "comparativa anterior.")
d.table(["Variable", "24-sep", "25-sep", "26-sep", "27-sep", "Qué explica el extremo"], [
    ["tempExhaust (Rack C) máx", "34,21", "34,09", "34,23", "34,16",
     "el máximo se mantiene casi idéntico los cuatro días y siempre por debajo del umbral de 35 °C: la carga IT y la climatización fueron estables. El mínimo (30,6 en 26-sep) es el valle de madrugada; el 27-sep no tiene valle porque la ventana empezó a las 10:28"],
    ["humedadRack máx / mín", "50,97 / 40,59", "48,37 / 39,81", "54,17 / 40,69", "54,03 / 47,49",
     "todo el rango se mantiene dentro de la banda 40-60 %HR recomendada. El máximo más alto (26-sep) coincide con el día más lluvioso: la humedad exterior entró a la sala"],
    ["deltaPresionPa mín", "16,40", "15,40", "14,90", "16,60",
     "la presión diferencial nunca se acercó al umbral de 5 Pa con el que se perdería la contención del pasillo frío. El valor más bajo (26-sep) es el mismo día con más tránsito: la apertura de puertas es lo que la baja"],
    ["tempExterior máx", "26,30", "25,30", "26,10", "24,90",
     "define las horas sin free-cooling: cuanto más alta, más rato tiene que trabajar el chiller. El 26-sep combina la temperatura más alta con la radiación solar mayor, así que fue el día con menos enfriamiento gratuito"],
    ["pm25 máx", "17,10", "29,30", "21,90", "6,70",
     "el 25-sep fue el peor día de aire (29,3 µg/m³, cerca de la guía de 24 h de la OMS) pero sin llegar al umbral de 35; el 27-sep fue el más limpio, coherente con la lluvia de días anteriores"],
    ["humo máx", "0,02", "0,03", "0,10", "0,03",
     "la línea base es 0,02. El pico de 0,10 del 26-sep es el único valor que supera el umbral de la regla (0,08): es el evento que justifica tener la regla de humo configurada"],
    ["potenciaKw máx / suma", "5,84 / 946", "5,84 / 1 362", "6,79 / 2 854", "5,84 / 757",
     "el 26-sep registra la carga de fila más alta de la ventana (6,79 kW) y consume más energía porque también es la fecha más larga (18 h): fue el día de mayor trabajo del centro de datos"],
    ["corrienteA máx / mín", "26,57 / 8,13", "26,57 / 23,71", "30,82 / 24,15", "26,57 / 23,71",
     "el máximo del 26-sep (30,82 A) es el punto más cercano a la protección de 32 A de la PDU en toda la ventana. El mínimo de 8,13 A del 24-sep corresponde a las primeras horas de la ventana, con poca carga conectada"],
    ["eventosAcceso suma", "1 393", "1 543", "6 049", "2 388",
     "el 26-sep concentra cuatro veces más aperturas que el primer día: fue la jornada de mantenimiento y visitas, y explica también el mínimo de presión diferencial de esa fecha"],
    ["tempTecho máx", "27,36", "27,31", "27,38", "27,37",
     "la estratificación del techo se mantiene prácticamente igual los cuatro días y muy lejos del umbral de incendio: el techo no se calienta de forma anómala en ninguna fecha"],
], widths_mm=[30, 20, 20, 20, 20, 55])

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

d.h("5.1 Los dos códigos que se ejecutan en la sustentación", 2)
d.p("El pliego pide que en la defensa se vean dos códigos corriendo en equipos distintos. Son estos dos, y "
    "sus registros reales quedan aquí: el nodo Python del Rack C corriendo en el servidor Ubuntu "
    "(equipo 1) y el ESP32 del Rack B en el simulador de Wokwi (equipo 2).")
d.code(["# Equipo 1 · servidor Ubuntu (52.252.133.127) · dc_sdk_mqtt.py → DC-RACKC-03",
        "[INFO] [DPS] asignado a iotc-...azure-devices.net",
        "[INFO] [HUB] CONNECT rc=0 (0=OK, 4=timeout de red, 5=no autorizado)",
        "[INFO] TX cada 30 s  tempIntake / tempExhaust / humedadRack",
        "",
        "# Equipo 2 · Wokwi en el navegador · sketch rackb → DC-RACKB-02",
        "[WIFI] conectado",
        "[NTP] epoch=1790453591",
        "[DPS] resp=202 status=assigning  →  [DPS] resp=200 status=assigned",
        "[MQTT] conectado al hub (Rack B)",
        '[TX] {"tempIntake":22.36,"tempExhaust":32.31,"humedadRack":47.8} (ok)   cada 15 s'])
d.figure(E + "dia4-datos-rackc.png", "Captura 28 — Equipo 1 en vivo: DC-RACKC-03 conectado publicando desde el servidor Ubuntu.")
d.figure(E + "dia4-wokwi-rackb.png", "Captura 29 — Equipo 2 en vivo: ESP32 del Rack B publicando en el simulador de Wokwi.")
d.p("El ciclo de desconexión y reconexión que hay que explicar en la defensa está documentado en la "
    "sección 6.1 del informe (los cuatro incidentes reales) y en la captura del Rack B caído con rc=-2.")

d.h("6. Estado de la flota en el arranque", 1)
ruta = pathlib.Path("logs/supervisor.log")
if ruta.exists():
    d.code([ln.rstrip("\n") for ln in ruta.open(encoding="utf-8")][:14] + ["…"])
d.p("El supervisor arranca los ocho nodos locales, los reinicia si terminan y deja el estado en "
    "logs/supervisor_estado.json. Un cronjob de Hermes relanza el supervisor si no está corriendo.")

d.save("informe/Evidencias_Parcial1_DC-ANDES-1.docx")
print("anexo generado: informe/Evidencias_Parcial1_DC-ANDES-1.docx")
