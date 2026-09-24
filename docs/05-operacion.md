# Operación de la ventana de 4 días (24–27 sep 2026)

## Rutina diaria

```bash
cd ~/Documents/Parcial1_IoT_Central

# 1) ¿sigue viva la flota scriptada?
.venv/Scripts/python.exe tools/estado_diario.py

# 2) refrescar el análisis de la ventana (CSV locales -> JSON + markdown)
.venv/Scripts/python.exe tools/resumen_datos.py --json datos/resumen_parcial.json
.venv/Scripts/python.exe tools/build_ventana_md.py

# 3) revisar el portal (flota, datos sin procesar, panel, reglas) y capturar evidencias
python tools/shot.py "https://dcandes1unab.azureiotcentral.com/devices" evidencias/01-flota-10-dispositivos.png
```

Si el supervisor no está corriendo: `tools/start_supervisor.cmd` (o el cronjob de Hermes lo relanza solo,
cada 10 minutos, con `tools/watchdog_flota.py`).

## Nodos ESP32 virtuales (Wokwi)

Los dos ESP32 virtuales son pestañas del navegador con un proyecto **anónimo**: el contenido vive solo en
esa pestaña. Si el navegador o la sesión de automatización se cierran, la pestaña se restaura con el
sketch de ejemplo y hay que reconstruirla (≈5 minutos). Los fuentes autoritativos están en el repositorio
(`dispositivos/wokwi/rackb/`, `dispositivos/wokwi/agua/`), así que la reconstrucción es mecánica:

```bash
# 1) abrir una pestaña nueva de proyecto ESP32
playwright-cli -s=iot tab-new "https://wokwi.com/projects/new/esp32"

# 2) inyectar sketch (genera el JS con el sketch + secrets.h inline en base64)
.venv/Scripts/python.exe tools/wokwi_payload.py rackb     # o "agua"
python tools/pw.py js tools/js/wokwi_rackb_payload.js

# 3) abrir la pestaña diagram.json y volver a inyectar (sketch + diagrama)
python tools/pw.py js tools/js/wokwi_tabs.js
python tools/pw.py js tools/js/wokwi_rackb_payload.js

# 4) instalar librerías (DHT sensor library for ESPx, PubSubClient, ArduinoJson)
python tools/pw.py js tools/js/wokwi_libs_agua.js

# 5) arrancar la simulación y comprobar el monitor serie
python tools/pw.py js tools/js/wokwi_reiniciar3.js
```

Señales correctas en el monitor serie: `[WIFI] conectado` → `[NTP] epoch=…` → `[DPS] resp=202 status=assigning`
→ `[DPS] resp=200 status=assigned` → `[MQTT] conectado al hub` → `[TX] {…} (ok)` cada 15 s (Rack B) o 30 s (agua).

Detalles que ya costaron tiempo (documentados también en la skill `wokwi-esp32-simulation`):

- El DPS responde **202 (assigning)** antes del 200 (assigned): el sketch debe sondear con el `operationId`.
- El SAS del hub dura 1 h: el sketch reconecta al detectar `!mqtt.connected()`; el nodo paho renueva el token.
- Las pestañas de fondo **siguen simulando** (verificado): dos simulaciones conviven.
- El gestor de librerías de Wokwi necesita que se desactive el `MuiBackdrop` y clics por coordenadas.

## Pausa documentada (hueco en la serie)

`datos/pausa_DC-HUMO-08.json` define la ventana en la que el nodo de humo deja de publicar
(sáb 26 sep 02:00–02:20, mantenimiento programado). El script lo respeta, loguea `PAUSA documentada`
y al terminar la ventana vuelve a publicar sin intervención: eso produce el hueco y la reconexión que
pide el parcial. Para la sustentación se puede provocar el mismo efecto en vivo apagando el nodo.

## Costo y cuotas

- App en plan **Estándar 2** (2 dispositivos gratuitos + bolsa de 30 000 mensajes/mes).
- Consumo estimado de la flota: ≈18 000 mensajes/día con los intervalos actuales (15 s … 900 s).
  Si se necesita recortar, subir el intervalo del nodo de humo (45 s → 120 s) y del Rack B (15 s → 30 s).
- Revisar el costo en el portal de Azure (Cost Management) al cierre del día 4.
