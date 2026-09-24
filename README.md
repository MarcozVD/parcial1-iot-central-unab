# Parcial 1 — IoT Central con flota heterogénea de 10 dispositivos

**Escenario 5.2 — Centro de datos** · *DC-ANDES-1* (AndesCloud S.A.S., Bucaramanga, Colombia)
Universidad Autónoma de Bucaramanga · IoT + Cloud + Sistemas Distribuidos · 2026-II

| | |
|---|---|
| **Aplicación IoT Central** | `dcandes1unab` → https://dcandes1unab.azureiotcentral.com |
| **Plantilla (Digital Twin)** | `Nodo DC-ANDES-1` · `dtmi:unab:dcandes:dcAndesNodo;1` (42 capacidades, publicada) |
| **Panel / cuarto de control** | *Cuarto de Control DC-ANDES-1* (16 mosaicos: identidad, KPIs, 8 gráficos, alertas) |
| **Ventana de métricas** | 4 días no continuos: 24, 25, 26 y 27 de septiembre de 2026 |
| **Flota** | 10 dispositivos · 10 orígenes de envío distintos · 6 intervalos de muestreo |

## Arranque rápido

```bash
# 1) entorno
uv venv --python 3.11 .venv
uv pip install --python .venv/Scripts/python.exe azure-iot-device paho-mqtt requests pandas matplotlib python-docx openpyxl

# 2) credenciales (NUNCA al repositorio: .secrets/env/<device>.env)
python tools/fetch_creds.py          # lee ID Scope y claves de IoT Central (az CLI logueado)

# 3) flota completa en segundo plano (8 nodos + supervisor)
python dispositivos/python/dc_supervisor.py --estado
tools/start_supervisor.cmd           # en Windows: arranca el supervisor desprendido

# 4) comprobacion
python tools/estado_flota.py         # resumen de la ultima muestra de cada nodo local
```

## Estructura

```
docs/            01-catalogo-dispositivos.md     catalogo unico de las 10 filas (origen por fila)
                 02-datasheets-y-parametros.md   tablas por variable: datasheet, rango, precision, umbral
                 03-arquitectura.md              diagrama por capas (dispositivo/red/plataforma/operacion)
                 04-ventana-4-dias.md            analisis de los 4 dias no continuos (max/min/prom/cuenta/suma)
dispositivos/
  python/        dc_comun.py            utilidades comunes (SAS, bitacora CSV, modelos por zona)
                 dc_sdk_mqtt.py         nodo Rack C      (SDK azure-iot-device, MQTT/TLS 8883)
                 dc_sdk_ws.py           nodo Pasillo     (SDK, MQTT sobre WebSockets 443)
                 dc_paho.py             nodo Humo        (MQTT explicito paho, SAS a mano, sin SDK)
                 dc_api_openmeteo.py    nodo Clima       (API publica Open-Meteo)
                 dc_api_aire.py         nodo Aire        (API publica + ingesta HTTPS/REST 443)
                 dc_csv_replay.py       nodo Energia     (replay de CSV historico)
                 dc_http_bridge.py      nodo Acceso      (puente HTTP -> MQTT)
                 dc_acceso_sim.py       sensor de campo del acceso (habla solo HTTP local)
                 dc_supervisor.py       mantiene viva la flota y reinicia nodos caidos
  wokwi/rackb/   sketch.ino, diagram.json, libraries.txt, secrets.h.example
  wokwi/agua/    sketch.ino, diagram.json, libraries.txt, secrets.h.example
tools/           generar_csv_pdu.py  build_dashboard.py  shot.py  resumen_datos.py
                 fetch_creds.py  resolver_hub.py  watchdog_flota.py  reparar_csv.py  build_informe.py
assets/          logo_andescloud_dcandes1.png (identidad del escenario)
datos/           series locales por dispositivo (*.csv) e historico de la PDU
logs/            bitacoras por dispositivo y salidas del supervisor
evidencias/      capturas del portal, logs y graficas
informe/         informe y anexo de evidencias (.docx / .pdf)
```

## Decisiones de diseño (resumen)

1. **Un solo catálogo de 10 filas con 10 orígenes distintos.** Cada fila cambia código,
   feed o transporte (ver la tabla de trazabilidad en `docs/01-catalogo-dispositivos.md`).
   No hay “dispositivos de relleno”: el simulador nativo cubre una fila y los Wokwi dos.
2. **Una sola plantilla** (`Nodo DC-ANDES-1`) para los diez dispositivos: permite que el
   panel compare variables entre nodos y que las reglas sean homogéneas. Cada nodo publica
   únicamente el subconjunto de telemetría de su zona.
3. **Asincronía real**: 15 s, 30 s, 45 s, 60 s, 120 s y 900 s conviven en la misma flota; el
   intervalo declarado viaja en la propiedad `intervaloMuestreo`.
4. **Desconexión documentada**: `datos/pausa_<device>.json` programa una pausa del nodo de
   humo; el hueco queda en la serie y en el estado *Desconectado* de Central.
5. **Todo lo que se puede ejecutar, se ejecuta**: el portal se usa para lo que solo existe
   en la interfaz (vistas, reglas, panel, personalización) y la API/CLI para lo repetible
   (plantilla, dispositivos, credenciales, panel).
6. **Sin secretos en el repositorio**: `.secrets/`, `secrets.h`, `.env` y `*.pem` están en
   `.gitignore`; los scripts leen las credenciales de variables de entorno o de archivos
   locales fuera de control de versiones.

## Operación de los 4 días

| Día | Fecha | Qué ocurre |
|---|---|---|
| 1 | jue 24 sep | despliegue completo de la flota y arranque de la ventana de métricas |
| 2 | vie 25 sep | publicación continua; primera consulta del Data Explorer |
| 3 | sáb 26 sep | pausa documentada del nodo de humo (hueco + reconexión) |
| 4 | dom 27 sep | cierre de la ventana, comparativa de los 4 días y sustentación |

El detalle día a día (incluidos los valores máximo/mínimo/promedio/recuento/sumatoria y la
lectura operativa de cada extremo) está en `docs/04-ventana-4-dias.md`.

## Modelos y supuestos documentados

- Las variables **reales** provienen de los feeds públicos (Open-Meteo y Open-Meteo Air
  Quality) y de los CSV históricos de la PDU.
- Las variables sin fuente pública (temperaturas de racks, presión diferencial, humo,
  acceso) se generan con **modelos físicos simples** documentados por variable en
  `docs/02-datasheets-y-parametros.md` (valor base, amplitud, offset, ruido), de modo que
  todo extremo tiene una explicación operativa.
- El **simulador nativo** de IoT Central no permite fijar rangos por variable: produce
  valores aleatorios 0-100. Por eso las comparativas térmicas usan los racks B y C
  (sensores modelados) y el Rack A se muestra aparte, etiquetado como simulador nativo.
