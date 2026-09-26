# Operación de la ventana de 4 días (24–27 sep 2026)

## Protocolo con el asistente (dos palabras)

El usuario avisa con **una palabra** y el asistente ejecuta el resto:

| Palabra | Qué hace el asistente | Respuesta esperada |
|---|---|---|
| **«para»** | `tools/apagar_flota.ps1`: detiene nodos, supervisor y vigilantes, y deja la bandera `logs/PAUSA_FLOTA` | *«Ya puedes detener la máquina»* + resumen de lo detenido y ventana de datos del día |
| **«inicia»** | (la máquina ya está encendida) `tools/reanudar_flota.ps1`: levanta supervisor y vigilante, reconstruye los ESP32 virtuales si el navegador se cerró y **registra el arranque** (fecha/hora, nodos vivos, primeras muestras) | *«Flota en marcha»* + estado por nodo y primeras lecturas |

Equivalentes para hacerlo sin el asistente: `tools\PARAR.cmd` y `tools\INICIAR.cmd` (doble clic).

## Apagar y reanudar la máquina

El parcial pide **cuatro fechas distintas (no tienen que ser consecutivas)** con gráficos; no exige
una máquina encendida 4 días seguidos. La condición real es que **cada una de las cuatro fechas
elegidas tenga unas horas de datos** para poder calcular máximo, mínimo, promedio, recuento y
sumatoria. Con 4–6 h por fecha los gráficos ya son representativos.

Al parar, `apagar_flota.ps1` deja la bandera `logs/PAUSA_FLOTA`: mientras exista, **ninguno** de los
dos vigilantes (el cronjob de Hermes y `tools/watchdog_win.py`) relanza nada, así que la flota no se
"resucita" sola mientras la máquina sigue encendida. `reanudar_flota.ps1` borra la bandera y arranca
supervisor y vigilante (sin duplicar si ya estaban corriendo).

> Ojo al contar procesos: en una venv creada con `uv` cada proceso Python aparece como **dos**
> procesos del sistema (lanzador + intérprete, con la misma línea de comandos y PIDs consecutivos).
> Un supervisor y sus ocho nodos son **18** entradas en `Get-CimInstance`, no un síntoma de duplicado.
> El supervisor lleva además testigo propio (`logs/supervisor.pid`) y, si dos lanzadores coinciden,
> **gana el de pid más bajo** y el otro sale sin arrancar nodos.

Antes de apagar o suspender (opcional, ordena el corte):

```powershell
powershell -NoProfile -File tools\apagar_flota.ps1
```

Al volver a encender, un solo comando devuelve todo a su sitio:

```powershell
powershell -NoProfile -File tools\reanudar_flota.ps1
```

El script arranca el supervisor y el watchdog (y no duplica nada si ya estaban corriendo), muestra el
estado de los ocho nodos y recuerda lo único manual: **si el navegador se cerró, hay que reconstruir
los dos ESP32 virtuales** (sección anterior, ≈5 minutos). El simulador nativo de la plantilla
(`DC-RACKA-01`) vive en Azure y sigue publicando aunque la máquina esté apagada, por lo que la
ventana nunca queda vacía — pero un solo nodo no sustenta las comparativas.

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

# 4) copia de seguridad del repositorio y los entregables (ZIP en OneDrive, sin credenciales)
.venv/Scripts/python.exe tools/backup.py
```

El repositorio **no tiene remoto**: solo vive en esta máquina. Por eso la rutina diaria termina con
`tools/backup.py`, que empaqueta el proyecto (código, docs, informes, evidencias, datos y el propio
histórico de git) en `~/OneDrive/Parcial1_IoT_Central_backup/` excluyendo `.venv` y `.secrets`. El
ZIP se verifica solo: imprime cuántos archivos lleva y confirma que no haya credenciales dentro. Las
credenciales del dispositivo no se respaldan a propósito: se vuelven a obtener con
`tools/fetch_creds.py` (az CLI) cuando haga falta.

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

## Modo remoto (Ubuntu) — desde el 26-sep

Los 7 nodos Python **no** corren en el portátil: corren en la máquina Ubuntu `52.252.133.127`.

```bash
# arrancar (con la máquina encendida): supervisor + 7 nodos
ssh -i ~/Downloads/iot_key.pem mvale@52.252.133.127 \
  "cd ~/Parcial1_IoT_Central && setsid nohup ~/venv_parcial/bin/python3 \
   dispositivos/python/dc_supervisor_remote.py > logs/supervisor.log 2>&1 < /dev/null &"

# estado
ssh -i ~/Downloads/iot_key.pem mvale@52.252.133.127 \
  "tail -3 ~/Parcial1_IoT_Central/logs/supervisor.log"

# parar (antes de apagar la máquina remota)
ssh -i ~/Downloads/iot_key.pem mvale@52.252.133.127 \
  "pkill -9 -f '[v]env_parcial'"
```

Reglas del modo remoto:

- **Los 7 nodos Python van en Ubuntu; los 2 ESP32 van en Wokwi (navegador del portátil).**
  `DC-RACKB-02` y `DC-AGUA-07` **nunca** se lanzan desde el supervisor: pertenecen a los sketches.
- **La flota local queda en pausa** (`logs/PAUSA_FLOTA`): si se relanzara, los mismos dispositivos
  publicarían desde dos sitios a la vez (ya ocurrió el 26-sep entre 14:55 y 15:22).
- En el patrón de `pkill` se usa `'[v]env_parcial'` (truco del corchete): escribir el nombre tal cual
  haría que el propio comando de parada coincida con el patrón y se mate a sí mismo.
- `setsid` + `nohup` + `</dev/null` son necesarios para que el arranque sobreviva al cierre de la sesión
  SSH; sin eso el proceso muere al terminar el comando.

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
