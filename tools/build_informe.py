#!/usr/bin/env python3
"""Genera el informe profesional del Parcial 1 (Word + PDF via topdf.ps1).

Uso:  python tools/build_informe.py
"""
import pathlib
import sys

sys.path.insert(0, "tools")
from docstyle import Doc  # noqa: E402

E = "evidencias/"
d = Doc("Parcial 1 · IoT Central · DC-ANDES-1")

d.cover(
    "Universidad Autónoma de Bucaramanga · IoT + Cloud + Sistemas Distribuidos",
    "Parcial 1 — IoT Central",
    "Escenario 5.2 Centro de datos: flota heterogénea de 10 dispositivos con 10 orígenes de envío",
    [("Estudiante", "Marcos Valera Daza"),
     ("Escenario", "5.2 Centro de datos — DC-ANDES-1 (AndesCloud S.A.S., Bucaramanga)"),
     ("Aplicación IoT Central", "dcandes1unab · https://dcandes1unab.azureiotcentral.com"),
     ("Plantilla (Digital Twin)", "Nodo DC-ANDES-1 · dtmi:unab:dcandes:dcAndesNodo;1 (42 capacidades, publicada)"),
     ("Panel", "Cuarto de Control DC-ANDES-1 (16 mosaicos: identidad, KPIs, 8 gráficos, alertas)"),
     ("Ventana de métricas", "4 días no continuos: 24, 25, 26 y 27 de septiembre de 2026"),
     ("Flota", "10 dispositivos · 10 orígenes distintos · 6 intervalos de muestreo (15 s … 900 s)")],
    [("Resultado: ", {"b": 1}),
     "la flota completa publica en Azure IoT Central desde códigos y feeds distintos; el cuarto de control "
     "concentra estado de flota, KPIs, ocho gráficos y alertas, y la ventana de cuatro días se analiza con "
     "máximo, mínimo, promedio, recuento y sumatoria."])

d.toc()

d.h("Historial de versiones", 1)
d.table(["Fecha", "Autor", "Versión del documento", "Cambio"], [
    ["2026-09-24", "Marcos Valera Daza", "1.0",
     "Despliegue de la aplicación, plantilla (v1), flota de 10 dispositivos, panel y reglas. Fecha 1 de la "
     "ventana: 14:04-20:05 (6 h 01), 7 nodos locales + 2 ESP32 Wokwi desde ~17:00."],
    ["2026-09-25", "Marcos Valera Daza", "1.1",
     "Fecha 2: 15:37-23:59 (8 h 22) con la flota local. Primer intento de trasladar los nodos Python a un "
     "servidor Ubuntu remoto; el supervisor remoto tenía un fallo de diseño (ver sección 6.1) que dejó solo "
     "el nodo de humo publicando desde ese lado durante la tarde."],
    ["2026-09-26", "Marcos Valera Daza", "1.2",
     "Fecha 3: 00:00-18:09 (18 h 09, la más larga). Diagnóstico y corrección del supervisor remoto; los 7 "
     "nodos Python quedaron estables en Ubuntu. Pausa documentada del nodo de humo (hueco + reconexión) y "
     "caída/recuperación del ESP32 del Rack B por rechazo de SAS (rc=5)."],
    ["2026-09-27", "Marcos Valera Daza", "2.0 (final)",
     "Fecha 4, exclusivamente en el servidor remoto (Ubuntu) + el ESP32 del Rack B (4 h 32, 10:28-15:00). "
     "Cierre de la ventana (35 h 38 min acumuladas en las 4 fechas), comparativa completa por variable, "
     "anexo de evidencias y sustentación."],
], widths_mm=[24, 34, 30, 75])
d.table(["Componente", "Versión"], [
    ["Plantilla / Digital Twin", "dtmi:unab:dcandes:dcAndesNodo;1 (42 capacidades) — publicada"],
    ["dc_sdk_mqtt.py (Rack C)", "1.4.0"], ["dc_sdk_ws.py (Pasillo)", "1.2.0"],
    ["dc_paho.py (Humo)", "1.1.0"], ["dc_api_openmeteo.py (Clima)", "1.3.0"],
    ["dc_api_aire.py (Aire)", "1.2.1"], ["dc_csv_replay.py (Energía)", "1.0.3"],
    ["dc_http_bridge.py + dc_acceso_sim.py (Acceso)", "1.1.4"],
    ["wokwi rackb (ESP32 #1)", "1.5.0"], ["wokwi agua (ESP32 #2)", "1.3.0"],
], widths_mm=[95, 68])

d.page_break()
d.h("1. Resumen ejecutivo", 1)
d.p("El proyecto despliega un escenario completo de centro de datos sobre Azure IoT Central. La flota no se "
    "llenó con un solo simulador: cada uno de los diez dispositivos declara un origen de envío distinto "
    "(simulador nativo de la plantilla, dos ESP32 virtuales en Wokwi, tres scripts Python con transportes y "
    "códigos diferentes, un replay de CSV histórico, un puente HTTP/REST y dos feeds de API pública). "
    "Sobre esa flota se configuraron vistas de operador, reglas con alertas y un panel tipo cuarto de control "
    "con identidad visual propia, y se mantiene una ventana de métricas de cuatro días no continuos.")
d.kpis([("10", "dispositivos · 10 orígenes"), ("6", "intervalos de muestreo"), ("42", "capacidades en la plantilla"),
        ("4", "días de métricas")])
d.bullets([
    [("Asincronía real: ", {"b": 1}), "15 s, 30 s, 45 s, 60 s, 120 s y 900 s conviven en la misma flota."],
    [("Desconexión documentada: ", {"b": 1}), "el nodo de humo pausa su script en una ventana programada; el hueco y la reconexión quedan en la serie y en el estado de Central."],
    [("Operación en línea: ", {"b": 1}), "los nodos Python y los ESP32 virtuales publican en vivo mientras el resto de la flota sigue en segundo plano."],
    [("Datos anclados a datasheets: ", {"b": 1}), "cada variable tiene rango de fabricante, rango operativo, unidad, precisión e intervalo (anexo A)."],
])
d.callout("el catálogo del grupo es uno solo: diez filas, diez orígenes distinguibles, sin bloques fijos "
          "(ni 5+5 ni “cinco obligatorios y cinco de relleno”).", kind="key", title="Cumplimiento de la regla base")

d.h("2. Escenario seleccionado y objetivo de operación", 1)
d.p("Escenario 5.2 — Centro de datos urbano. La instalación DC-ANDES-1 opera una sala blanca con tres "
    "armarios (racks A, B y C), contención de pasillo frío, climatización por free-cooling, sala de energía "
    "con PDU por fila y control de acceso. El objetivo del cuarto de control es responder tres preguntas en "
    "un vistazo: ¿el ambiente térmico de los racks está dentro de envolvente?, ¿conviene enfriar con aire "
    "exterior?, y ¿hay eventos de seguridad (agua, humo, acceso) que exijan acción inmediata?")
d.table(["Zona", "Rol operativo", "Nodo(s) del catálogo"], [
    ["Racks A/B/C", "temperatura de intake y exhaust, humedad relativa por armario", "01, 02, 03"],
    ["Pasillo frío / contención", "temperatura, humedad y presión diferencial entre pasillos", "04"],
    ["Cubierta técnica", "clima exterior que habilita o limita el free-cooling", "05"],
    ["Sala blanca", "calidad de aire (PM2.5, PM10, AQI, CO2)", "06"],
    ["Piso técnico", "detección de agua bajo piso", "07"],
    ["Techo de sala", "detección de humo y temperatura de techo", "08"],
    ["Tablero de fila C", "energía de la PDU (kW, corriente, factor de potencia)", "09"],
    ["Acceso principal", "estado de puerta y eventos de acceso", "10"],
], widths_mm=[38, 90, 35])

d.h("3. Arquitectura de referencia con telecomunicaciones", 1)
d.p("La arquitectura se documenta en cuatro capas: dispositivo, red, plataforma y operación. El sitio es "
    "urbano, por lo que la salida a Internet es por fibra con NAT saliente: ningún puerto de entrada queda "
    "abierto y todo el tráfico lo inician los dispositivos.")
d.table(["Capa", "Elementos", "Detalle verificado"], [
    ["Dispositivo", "10 nodos con 10 códigos/feeds", "simulador nativo, 2 ESP32 Wokwi, 3 scripts Python, replay CSV, puente HTTP, 2 puentes de API"],
    ["Red", "Wi-Fi/LAN del sitio + salida a Internet", "MQTT/TLS 8883, MQTT sobre WebSockets 443, HTTPS 443 (REST de dispositivo y feeds)"],
    ["Plataforma", "DPS + IoT Hub gestionado + Digital Twin", "inscripción por clave simétrica; plantilla publicada con gemelo, comandos y propiedades"],
    ["Operación", "vistas, reglas, panel y comandos", "Overview/About por dispositivo, 6 reglas, panel de 16 mosaicos, comandos remotos"],
], widths_mm=[28, 55, 80])
d.figure(E + "diagrama_arquitectura.png", "Arquitectura de referencia: dispositivos, telecomunicaciones, plataforma y operación.")

d.h("4. Catálogo de 10 dispositivos (un solo inventario)", 1)
d.p("Cada fila declara su origen de envío, su protocolo de ingesta, su intervalo y el datasheet que ancla "
    "sus variables. El detalle completo, con la justificación de por qué cada origen es distinto, está en "
    "docs/01-catalogo-dispositivos.md del repositorio.")
d.table(["#", "ID en Central", "Zona", "Origen de envío", "Protocolo", "Int.", "Variables"], [
    ["01", "DC-RACKA-01", "Rack A", "Digital Twin / simulador nativo", "plataforma", "60 s", "tempIntake, tempExhaust, humedadRack"],
    ["02", "DC-RACKB-02", "Rack B", "Wokwi ESP32 #1 (Arduino)", "MQTT/TLS 8883 + DPS", "15 s", "tempIntake, tempExhaust, humedadRack"],
    ["03", "DC-RACKC-03", "Rack C", "Python SDK azure-iot-device", "MQTT/TLS 8883 + DPS", "30 s", "tempIntake, tempExhaust, humedadRack"],
    ["04", "DC-PASILLO-04", "Pasillo frío", "Python SDK (transporte alterno)", "MQTT sobre WebSockets 443", "60 s", "tempPasillo, humedadPasillo, deltaPresionPa"],
    ["05", "DC-CLIMA-05", "Clima exterior", "API pública meteorológica", "HTTPS + MQTT/TLS", "900 s", "tempExterior, humedadExterior, lluviaMm, vientoKmh, radiacionSolar"],
    ["06", "DC-AIRE-06", "Calidad de aire", "API pública (dominio distinto)", "HTTPS + REST 443", "900 s", "pm25, pm10, aqi, co2"],
    ["07", "DC-AGUA-07", "Agua bajo piso", "Wokwi ESP32 #2 (sketch propio)", "MQTT/TLS 8883 + DPS", "30 s", "fugaAgua, humedadPiso"],
    ["08", "DC-HUMO-08", "Humo / incendio", "Cliente MQTT explícito (paho)", "MQTT/TLS 8883 (SAS manual)", "45 s", "humo, tempTecho"],
    ["09", "DC-ENERGIA-09", "PDU / energía", "Replay de CSV histórico", "MQTT/TLS 8883", "120 s", "potenciaKw, corrienteA, factorPotencia"],
    ["10", "DC-ACCESO-10", "Puerta / acceso", "Puente HTTP/REST + sensor de campo", "HTTP local + MQTT/TLS", "120 s", "puertaAbierta, eventosAcceso, tempPuerta"],
], widths_mm=[8, 25, 22, 44, 32, 12, 44])

d.h("5. Digital Twin (plantilla) y operación", 1)
d.p("La plantilla Nodo DC-ANDES-1 se construyó sobre la API de datos de IoT Central y se publicó; los diez "
    "dispositivos la comparten, de modo que el panel y las reglas comparan variables entre nodos con la misma "
    "semántica. Cada nodo publica únicamente el subconjunto de telemetría de su zona y reporta sus propiedades "
    "de identidad (zona, ubicación, origen de envío, fabricante, modelo, versión e intervalo).")
d.table(["Grupo de capacidades", "Contenido"], [
    ["Telemetría (27)", "ambientales de rack y pasillo, meteorología exterior, calidad de aire, agua, humo, energía y acceso, más las marcas de tiempo de fuente y de dispositivo"],
    ["Propiedades (11)", "7 reportadas de identidad + 4 escribibles: umbralTemperatura, umbralHumedad, umbralPM25 y modoOperacion"],
    ["Comandos (4)", "reiniciar, setAlerta (baliza), acuseAlarma (ack del operador) y abrirPuerta (control de acceso)"],
    ["Vistas de operador", "Overview y About, publicadas sobre la plantilla; Overview agrupa KPIs y gráficos de todas las telemetrías del gemelo, About expone las propiedades editables (evidencia captura dia4-views-plantilla.png)"],
], widths_mm=[38, 125])

d.h("6. Asincronía, desconexión y operación en línea", 1)
d.p("La flota mezcla seis intervalos de muestreo distintos, lo que produce series de densidad muy diferente "
    "en el mismo panel: los nodos de 15 s dibujan detalle fino y los de 900 s aportan la tendencia. Esa "
    "asincronía es deliberada y visible en los gráficos y en la propiedad intervaloMuestreo de cada gemelo.")
d.table(["Nodo", "Intervalo", "Transporte", "Comportamiento observado"], [
    ["DC-RACKB-02", "15 s", "MQTT/TLS 8883", "serie más densa; responde a comandos y a la propiedad umbralTemperatura"],
    ["DC-RACKC-03 / DC-AGUA-07", "30 s", "MQTT/TLS 8883", "publicación estable; desconexión y reconexión visibles en el estado"],
    ["DC-HUMO-08", "45 s", "MQTT/TLS 8883 (paho)", "pausa documentada programada: hueco + reconexión"],
    ["DC-RACKA-01 / DC-PASILLO-04", "60 s", "plataforma / WebSockets", "ciclo Bloquear/Desbloquear del simulador y reconexión del SDK"],
    ["DC-ENERGIA-09 / DC-ACCESO-10", "120 s", "MQTT/TLS 8883", "series suaves (replay y puente HTTP)"],
    ["DC-CLIMA-05 / DC-AIRE-06", "900 s", "HTTPS + MQTT/REST", "feed externo: valor real con marca de tiempo de la fuente"],
], widths_mm=[40, 20, 40, 63])

d.h("6.1 Incidentes operativos de la ventana (desconexión real, no solo simulada)", 1)
d.p("Además de la pausa programada del nodo de humo, la ventana de cuatro días registró incidentes reales "
    "de operación distribuida que se documentan aquí porque son la evidencia más directa de asincronía y "
    "desconexión en condiciones de producción, no de laboratorio controlado.")
d.table(["Fecha", "Incidente", "Diagnóstico", "Resolución"], [
    ["25-sep", "El supervisor del servidor Ubuntu lanzaba los 7 scripts con el dispositivo como argumento",
     "Cada script tiene su DEVICE_ID fijo en el código y no lee argumentos: los 7 procesos eran en realidad "
     "el mismo script (DC-HUMO-08) peleando por la única conexión del hub",
     "Reescrito el supervisor con una entrada por script (mismo diseño que el supervisor local); verificado "
     "después con 8/8 procesos vivos y un CSV por dispositivo"],
    ["26-sep", "Doble publicación de los mismos 7 dispositivos desde el portátil y desde Ubuntu (14:55-15:22)",
     "El vigilante local relanzó la flota sin que el servidor remoto estuviera aún desactivado",
     "Flota local detenida y bandera de pausa (logs/PAUSA_FLOTA) para que los vigilantes no la revivan "
     "mientras el servidor remoto sea la fuente activa"],
    ["26/27-sep", "El ESP32 del Rack B quedó en bucle de reconexión (rc=5 y luego rc=-2)",
     "rc=5: SAS rechazado por deriva del reloj del simulador tras varias horas corriendo. rc=-2: fallo de "
     "red del simulador de Wokwi",
     "Firmware actualizado con resincronización de hora y reinicio automático a los 6 fallos consecutivos; "
     "en caliente, reiniciar la simulación restablece la publicación en <90 s"],
    ["27-sep", "El ESP32 del nodo de agua no llegó a compilar (\u201cBuild Servers Busy\u201d)",
     "Cola de compilación del plan gratuito de Wokwi saturada al tener dos proyectos ESP32 simulando a la "
     "vez; se descartó que fuera un problema del proyecto probando con un sketch nuevo desde cero",
     "Limitación de plataforma, no del sketch: el nodo de agua ya tiene cobertura completa en las fechas 1 "
     "y 3; en la fecha 4 la flota queda con 9 de 10 orígenes activos"],
], widths_mm=[16, 45, 51, 51])
d.callout("estos cuatro incidentes se dejan documentados a propósito: el taller pide mostrar desconexión y "
          "reconexión reales, y una migración de infraestructura a mitad de la ventana con sus fallos y "
          "correcciones es evidencia más fuerte que una pausa puramente programada.", kind="key",
          title="Por qué se documentan los fallos y no solo el resultado final")

d.h("7. Ventana de 4 días no continuos", 1)
d.p("La ventana comprende el 24, 25, 26 y 27 de septiembre de 2026. Para cada día y variable se calculan "
    "máximo, mínimo, promedio, recuento y sumatoria (esta última cuando aporta: energía, lluvia y eventos de "
    "acceso). La comparativa se genera desde el Data Explorer de IoT Central y desde las series locales que "
    "cada nodo escribe en datos/; el anexo B contiene las tablas completas y la lectura operativa de cada "
    "extremo.")
d.table(["Fecha", "Ventana con datos", "Duración", "Origen de los datos"], [
    ["24-sep (jue)", "14:04 → 20:05", "6 h 01", "7 nodos locales (portátil) + 2 ESP32 Wokwi desde ~17:00"],
    ["25-sep (vie)", "15:37 → 23:59", "8 h 22", "7 nodos locales (portátil); el intento de servidor remoto solo alimentó el nodo de humo (incidente 6.1)"],
    ["26-sep (sáb)", "00:00 → 18:09", "18 h 09", "local hasta 15:22 (continuaba del 25-sep) y después el servidor Ubuntu; ESP32 desde ~15:14"],
    ["27-sep (dom)", "10:28 → 15:00", "4 h 32", "exclusivamente el servidor Ubuntu (7 nodos Python); flota local detenida a propósito para aislar el segundo código en vivo de la sustentación"],
], widths_mm=[24, 40, 30, 90])
d.p("Las cuatro fechas superan el mínimo de 4 horas exigido; el total acumulado es de 35 h 38 min y "
    "14 414 muestras. El detalle completo por variable (máximo, mínimo, promedio, recuento y sumatoria "
    "de cada fecha) está en el anexo B y en docs/04-ventana-4-dias.md.")

d.h("8. Cuarto de control", 1)
d.p("El panel Cuarto de Control DC-ANDES-1 usa la identidad del escenario (logo y nombre propios, no el "
    "nombre genérico de la aplicación), muestra el recuento de dispositivos del grupo, cuatro KPIs numéricos "
    "y ocho gráficos de telemetría alineados a las variables indispensables, además del bloque de alertas.")
d.table(["Bloque del panel", "Contenido"], [
    ["Identidad", "rótulo del escenario y mosaico con el logo de AndesCloud DC-ANDES-1"],
    ["Estado de flota", "mosaico de recuento de dispositivos del grupo + estados en la lista de dispositivos"],
    ["KPIs", "temperatura de exhaust máxima de racks (24 h), PM2.5 promedio, potencia de PDU y humo de techo"],
    ["Gráficos", "racks B/C, simulador nativo del Rack A, clima exterior, calidad de aire, energía, contención, humo y agua"],
    ["Alertas", "bloque con las reglas activas y su umbral, más el historial de comandos y alarmas"],
], widths_mm=[35, 128])

d.h("9. Reglas y alertas", 1)
d.p("La aplicación tiene seis reglas creadas sobre la plantilla Nodo DC-ANDES-1 y habilitadas en la "
    "plataforma (evidencia E6). Cada regla evalúa una telemetría del modelo contra un umbral operativo y "
    "dispara una acción de correo electrónico a la cuenta del operador; los umbrales coinciden con los del "
    "anexo A y con los que publican los nodos.")
d.table(["#", "Regla (nombre en Central)", "Condición", "Acción", "Id"], [
    ["1", "Alerta temperatura de rack", "tempExhaust > 35 °C", "correo", "067173ba…"],
    ["2", "Alerta humedad de rack", "humedadRack > 60 %HR", "correo", "7ac863ed…"],
    ["3", "Humo detectado en sala", "humo > 0,08 %obs/m", "correo", "6a579d61…"],
    ["4", "Calidad de aire degradada", "pm25 > 35 µg/m³", "correo", "—"],
    ["5", "Alerta humedad en piso tecnico", "humedadPiso > 70 %", "correo", "5374af4b…"],
    ["6", "Exceso de eventos de acceso", "eventosAcceso > 20", "correo", "562cc3a3…"],
], widths_mm=[8, 52, 45, 20, 38])
d.bullets([
    [("Destinatario: ", {"b": 1}), "todas las acciones notifican a mvalera@o365.unab.edu.co (cuenta del operador)."],
    [("Criterio de diseño: ", {"b": 1}), "las condiciones se definieron sobre telemetrías numéricas para que el umbral sea explicable y trazable al datasheet; los estados booleanos (fuga, puerta) se cubren con los indicadores numéricos asociados (humedad de piso, eventos de acceso)."],
    [("Verificación: ", {"b": 1}), "la lista de reglas muestra las seis en estado Habilitado (evidencias/06-reglas-6-habilitadas.png)."],
])
d.figure(E + "06-reglas-6-habilitadas.png", "Evidencia E6 — las seis reglas de la aplicación, habilitadas.")

d.h("10. Limitaciones percibidas de IoT Central", 1)
d.bullets([
    [("El simulador nativo no se puede parametrizar: ", {"b": 1}), "produce valores aleatorios 0-100 en todas las telemetrías del modelo; por eso las comparativas térmicas usan los racks con sensor modelado y el Rack A se muestra aparte y etiquetado."],
    [("Reglas y paneles no tienen API pública estable: ", {"b": 1}), "la plantilla, los dispositivos, los grupos y el panel sí se pueden automatizar por API/CLI, pero las reglas solo existen en la interfaz (la API de reglas responde 404 en GA y preview)."],
    [("Sesiones de portal cortas: ", {"b": 1}), "la consola de IoT Central cierra la sesión cada pocos minutos, lo que obliga a trabajar por ráfagas y a guardar cada avance."],
    [("Cuotas de mensajes: ", {"b": 1}), "los planes estándar incluyen 2 dispositivos y una bolsa de mensajes; una flota de 10 nodos con intervalos cortos consume la bolsa y obliga a vigilar el costo."],
    [("Formato de mosaicos poco documentado: ", {"b": 1}), "el esquema de los mosaicos hubo que reconstruirlo desde el OpenAPI preview (queryRange con duración ISO-8601 y capabilities con función de agregación)."],
])

d.h("11. Repositorio y manejo de secretos", 1)
d.p("El repositorio incluye el código de los diez orígenes, los dos proyectos Wokwi, las herramientas de "
    "despliegue y generación de documentos, y las evidencias. Las credenciales nunca viajan en el código: los "
    "scripts leen ID Scope y claves desde variables de entorno o desde .secrets/env/<device>.env, y los "
    "archivos .secrets/, secrets.h y *.pem están excluidos por .gitignore.")
d.code(["# variables de entorno usadas por todos los nodos",
        "export ID_SCOPE=\"0ne00XXXXXX\"",
        "export DEVICE_ID=\"DC-RACKC-03\"",
        "export PRIMARY_KEY=\"<clave base64 del dispositivo>\"   # jamas en el repositorio",
        "",
        "# SAS (HMAC-SHA256 sobre el recurso percent-encoded, igual que el SDK)",
        "sr = quote(f\"{hub}/devices/{device_id}\", safe=\"\")",
        "sig = b64(HMAC_SHA256(b64decode(key), sr + \"\\n\" + expiry))"])

d.page_break()
d.h("Anexo A — Datasheets y tablas de parámetros", 1)
d.p("El detalle por variable (rango del fabricante, rango operativo del escenario, unidad, precisión, "
    "intervalo usado, valor empleado en el código y umbral de la regla) está en "
    "docs/02-datasheets-y-parametros.md y se resume en la siguiente tabla para las variables indispensables.")
d.table(["Variable", "Sensor / datasheet", "Rango fabricante", "Rango operativo", "Precisión", "Int."], [
    ["tempIntake / tempExhaust", "DHT22 (Wokwi) · SHT31 (Rack C) · APC AP9335TH (ref.)", "−40 … 80 °C", "18 … 38 °C", "±0,5 °C", "15-60 s"],
    ["humedadRack", "DHT22 / SHT31", "0 … 100 %HR", "38 … 62 %HR", "±2 … ±3 %HR", "15-60 s"],
    ["deltaPresionPa", "Sensirion SDP810-500Pa", "−500 … 500 Pa", "3 … 30 Pa", "±3 % m.v.", "60 s"],
    ["tempExterior / radiacionSolar", "Open-Meteo (ref. Davis Vantage Pro2)", "−40 … 65 °C / 0 … 1500 W/m²", "15 … 30 °C / 0 … 1000 W/m²", "±0,5 °C / ±5 %", "900 s"],
    ["pm25 / pm10 / co2", "Open-Meteo AQ (PMS7003) · SCD41", "0 … 1000 µg/m³ · 400 … 4000 ppm", "0 … 60 µg/m³ · 400 … 1200 ppm", "±10 % · ±(30+5 %) ppm", "900 s"],
    ["fugaAgua / humedadPiso", "RLE LD2100 + sonda resistiva", "0/1 · 0 … 100 %", "0/1 · 30 … 90 %", "— · ±5 %", "30 s"],
    ["humo / tempTecho", "Siemens FDA241 · APC AP9335TH", "0,005 … 20 %obs/m · −10 … 60 °C", "0,01 … 0,10 %obs/m · 22 … 30 °C", "±0,005 · ±0,5 °C", "45 s"],
    ["potenciaKw / corrienteA / FP", "Raritan PX3-5488", "0 … 7,4 kW · 0 … 32 A · 0 … 1", "4,1 … 7,5 kW · 18 … 33 A · 0,90 … 0,995", "±1 % · ±1 % · ±0,01", "120 s"],
    ["puertaAbierta / eventosAcceso", "HID iCLASS SE R40 + Mercury LP1502", "0/1 · 0 … 65535", "0/1 · creciente", "—", "120 s"],
], widths_mm=[36, 44, 34, 34, 22, 14])

d.h("Anexo B — Evidencias y comparativa de los 4 días", 1)
d.p("Las capturas del portal (flota, datos sin procesar de cada origen, panel, reglas, estados "
    "Connected/Disconnected), los logs de los dos códigos que se ejecutan en vivo y las tablas de la "
    "comparativa de cuatro días se adjuntan en el anexo de evidencias (informe/Evidencias_Parcial1.docx).")
d.h("Comparativa de los 4 días — estado por fecha", 2)
d.table(["Fecha", "Duración", "Origen", "Incidencia relevante"], [
    ["24-sep", "6 h 01", "portátil + 2 ESP32 Wokwi", "ninguna; fecha base de referencia"],
    ["25-sep", "8 h 22", "portátil (servidor solo alimentó DC-HUMO-08)", "supervisor remoto mal diseñado (6.1)"],
    ["26-sep", "18 h 09", "portátil hasta 15:22, después servidor Ubuntu", "supervisor corregido; SAS del Rack B rechazado y recuperado"],
    ["27-sep", "4 h 32", "exclusivamente servidor Ubuntu + ESP32 Rack B (intermitente)", "nodo de agua sin datos (Wokwi saturado, 6.1)"],
], widths_mm=[18, 30, 62, 74])

d.h("Comparativa por variable — máximo, mínimo, promedio, recuento y sumatoria", 2)
d.p("Tabla generada con tools/comparativa_4dias.py a partir de las series de cada nodo (datos/*.csv para "
    "el 24, 25 y 26-sep; datos/remoto_dia4/*.csv, la única fuente válida, para el 27-sep). Se muestran las "
    "variables de los nodos con sensor modelado (Rack C, pasillo, humo, acceso, energía, clima exterior y "
    "calidad de aire); el simulador nativo (Rack A) queda fuera por producir valores aleatorios sin anclaje "
    "a datasheet (limitación documentada en la sección 10 del informe).")

import csv as _csv
import statistics as _st

_VARS_SUMABLES = {"eventosAcceso", "potenciaKw", "corrienteA", "lluviaMm"}
_FUENTES = {
    "2026-09-24": pathlib.Path("datos"),
    "2026-09-25": pathlib.Path("datos"),
    "2026-09-26": pathlib.Path("datos"),
    "2026-09-27": pathlib.Path("datos/remoto_dia4"),
}


def _leer_variables(carpeta, fecha):
    datos = {}
    for f in sorted(carpeta.glob("DC-*.csv")):
        if "campo" in f.stem:
            continue
        with f.open(encoding="utf-8") as fh:
            r = _csv.DictReader(fh)
            cols = [c for c in (r.fieldnames or []) if c not in
                    ("ts_local", "ts_utc", "origen", "device_id", "tsFuente", "tsDispositivo")]
            for row in r:
                if not row["ts_local"].startswith(fecha):
                    continue
                for c in cols:
                    try:
                        fv = float(row.get(c, ""))
                    except (ValueError, TypeError):
                        continue
                    datos.setdefault(f"{c} ({f.stem})", []).append(fv)
    return datos


for _fecha, _carpeta in _FUENTES.items():
    _datos = _leer_variables(_carpeta, _fecha)
    d.h(_fecha, 3)
    _filas = []
    for _clave in sorted(_datos):
        _vals = _datos[_clave]
        _var = _clave.split(" (")[0]
        _suma = f"{sum(_vals):.2f}" if _var in _VARS_SUMABLES else "—"
        _filas.append([_clave, f"{max(_vals):.2f}", f"{min(_vals):.2f}", f"{_st.mean(_vals):.2f}",
                       str(len(_vals)), _suma])
    d.table(["Variable (nodo)", "Máx", "Mín", "Promedio", "Recuento", "Sumatoria"], _filas,
             widths_mm=[55, 18, 18, 22, 20, 20])

d.callout("el recuento por variable y fecha es la evidencia directa de la asincronía de la flota: los "
          "nodos de 900 s (clima, aire) acumulan decenas de muestras por día mientras los de 30-60 s "
          "(rack, pasillo, acceso) acumulan cientos o miles. La caída de recuento del 27-sep frente al "
          "26-sep es proporcional a que esa fecha corrió 4 h 32 min contra 18 h 09.", kind="key",
          title="Lectura de la comparativa")

d.save("informe/Informe_Parcial1_DC-ANDES-1.docx")
print("informe generado: informe/Informe_Parcial1_DC-ANDES-1.docx")
