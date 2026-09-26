# Bitácora — Día 3 (26 de septiembre de 2026)

## Resumen de la fecha

| Aspecto | Valor |
|---|---|
| Fecha de la ventana | sábado 26 de septiembre de 2026 |
| Cobertura | **00:00 → cierre** (la flota local venía publicando desde medianoche; a las 15:22 pasó a la máquina Ubuntu) |
| Origen de los datos | 7 nodos Python en **Ubuntu 52.252.133.127** + 2 ESP32 virtuales de **Wokwi** (navegador local) + simulador nativo en Azure |
| Estado al cierre de la jornada | 7/7 nodos Python vivos en Ubuntu, 2/2 ESP32 publicando, sin errores en los registros |
| Evidencias | 8 capturas `evidencias/dia3-*.png` |

## Qué pasó en esta fecha (orden real de los hechos)

1. **La flota local seguía viva desde la medianoche.** El vigilante (cronjob de Hermes) relanzó la flota
   local al no encontrar la bandera de pausa: los CSV locales tienen registros de hoy desde `00:00:19`.
   Es decir, la fecha 26 tiene datos continuos desde el inicio del día.
2. **Migración a la máquina Ubuntu.** Se desplegó el código de los nodos Python en
   `~/Parcial1_IoT_Central` de `52.252.133.127` (usuario `mvale`, llave `iot_key.pem`), con las
   credenciales de los 7 dispositivos y una venv (`~/venv_parcial`) con `paho-mqtt` y `requests`.
3. **Ventana de duplicación detectada y corregida.** Entre las **14:55 y las 15:22** los mismos 7
   dispositivos publicaron desde los dos lados (nodos locales + nodos de Ubuntu). Se detuvo la flota
   local con `tools/apagar_flota.ps1` a las 15:22 y se dejó la bandera `logs/PAUSA_FLOTA` explicando el
   motivo, para que el vigilante no la reviva. **A partir de las 15:22 la única fuente de los nodos
   Python es Ubuntu.**
4. **Corrección de origen en el nodo de agua.** `DC-AGUA-07` y `DC-RACKB-02` son dispositivos de los
   ESP32 (Wokwi), no de Python. El supervisor remoto se corrigió para lanzar **7** nodos y no 8: en la
   fecha 2 el nodo de agua se había publicado con el cliente paho, lo que queda anotado como
   inconsistencia de origen de ese día. Desde hoy el agua vuelve a su origen declarado (ESP32).
5. **Reconstrucción de los dos ESP32.** El navegador se reabrió con el perfil persistente
   (`playwright-cli -s=iot --browser msedge --persistent --profile ...`), se reinyectaron los sketches,
   diagramas y librerías, y ambas simulaciones quedaron publicando: Rack B cada 15 s y agua cada 30 s.

## Estado de los 10 orígenes

| Dispositivo | Origen de envío | Dónde corre | Estado |
|---|---|---|---|
| DC-RACKC-03 | Python (SDK MQTT/TLS) | Ubuntu | Conectado, 30 s |
| DC-HUMO-08 | Python (paho, SAS manual) | Ubuntu | Conectado, 45 s |
| DC-PASILLO-04 | Python (WebSocket) | Ubuntu | Conectado, 60 s |
| DC-CLIMA-05 | Python (API pública Open-Meteo) | Ubuntu | Conectado, 900 s |
| DC-AIRE-06 | Python (API pública de calidad del aire) | Ubuntu | Conectado, 900 s |
| DC-ENERGIA-09 | Python (replay de CSV) | Ubuntu | Conectado, 120 s |
| DC-ACCESO-10 | Python (simulador de campo) | Ubuntu | Conectado, 120 s |
| DC-RACKB-02 | ESP32 Wokwi (Arduino + PubSubClient) | Navegador local | Publicando, 15 s |
| DC-AGUA-07 | ESP32 Wokwi (Arduino + PubSubClient) | Navegador local | Publicando, 30 s |
| DC-RACKA-01 | Simulador nativo de la plantilla | Azure | Publicando |

## Verificaciones hechas hoy

- Conectividad SSH a Ubuntu con la llave de la carpeta de descargas (usuario `mvale`).
- Importación del módulo común y de `paho` dentro de la venv remota.
- DPS: `rc=0` y `assigned` en los 7 nodos; sin errores ni excepciones en los registros remotos.
- Supervisor remoto: mensajes `vigilancia OK: 7/7 nodos vivos` cada 30 s.
- Portal: estado **Conectado** y «Última recepción de datos» del 26/9/2026 en los nodos consultados.
- Wokwi: monitor serie con `[WIFI] conectado` → `[DPS] assigned` → `[MQTT] conectado al hub` → `[TX] {…} (ok)`.
- Ausencia de procesos locales tras el corte (0 procesos del proyecto en Windows).

## Evidencias de la fecha (`evidencias/`)

| Archivo | Qué prueba |
|---|---|
| `dia3-portal-flota.png` | los 10 dispositivos en la lista del portal |
| `dia3-datos-rackc.png` | datos sin procesar de un nodo Python que corre en Ubuntu (26/9, cada 30 s) |
| `dia3-datos-rackb.png` | datos sin procesar del ESP32 del Rack B |
| `dia3-datos-agua.png` | datos sin procesar del ESP32 del nodo de agua |
| `dia3-wokwi-rackb.png` | monitor serie del ESP32 del Rack B publicando |
| `dia3-wokwi-agua.png` | monitor serie del ESP32 de agua publicando |
| `dia3-panel.png` | panel «Cuarto de Control DC-ANDES-1» |
| `dia3-reglas.png` | reglas configuradas y su estado |

## Incidencias y cómo se resolvieron

- **Doble publicación (14:55–15:22):** los mismos dispositivos publicaban desde Windows y desde Ubuntu.
  Se detuvo la flota local y se dejó bandera de pausa con el motivo escrito.
- **El nodo de agua contado dos veces:** el supervisor remoto incluía `DC-AGUA-07`, que pertenece al
  ESP32. Se corrigió la lista y se anotó la inconsistencia de la fecha 2.
- **Interfaz inventada en el supervisor remoto (el error más caro del día).** La primera versión del
  supervisor remoto lanzaba los nodos como `dc_paho.py <DISPOSITIVO> <intervalo>`, pero **eso no existe**:
  cada script tiene su dispositivo fijo dentro del código (`DEVICE_ID`) y **no lee argumentos**
  (`dc_paho.py` → DC-HUMO-08, `dc_sdk_mqtt.py` → DC-RACKC-03, ...). Consecuencia: los 7 procesos eran en
  realidad el mismo script y el mismo dispositivo (DC-HUMO-08), peleando por la única conexión del hub, y
  en bucle de reconexión. **Síntoma que lo delató:** los registros de los 7 nodos mostraban las mismas
  propiedades reportadas y el portal marcaba "Desconectado" a los demás dispositivos.
  Se reescribió el supervisor con el diseño probado (una entrada por **script**, igual que el supervisor
  del portátil) y se instaló `azure-iot-device` en la venv remota (era el otro motivo de las caídas).
  Verificado después: **8/8 nodos vivos, un CSV por dispositivo y los 7 dispositivos en "Conectado"** con
  marca de tiempo en curso.
- **Alcance de ese error en la fecha 2 (25 sep):** el supervisor remoto publicó **solo DC-HUMO-08**
  (1 737 filas entre 15:52 y 18:36, infladas por el bucle de reconexión). Ese día la cobertura buena la
  dio la flota **local**, que estuvo publicando los 7 dispositivos de 15:37 a 23:59 (8 h 22 min,
  2 904 filas). Entre 15:52 y 18:36 el nodo de humo tuvo dos publicadores a la vez (local + remoto), así
  que sus filas de esa franja están intercaladas: es la única salvedad de la fecha.
- **`pkill` que se mataba a sí mismo:** al filtrar procesos por línea de comandos, el propio comando de
  parada coincidía con el patrón y se suicidaba antes de relanzar. Se separó en dos llamadas
  (parar / arrancar) y se usó el truco del corchete en el patrón.
- **Sketch del Rack B caía con `rc=5` (SAS rechazado)** tras horas de simulación: se añadió al firmware
  la resincronización de hora y el reinicio del nodo cuando el rechazo persiste (commit `c5ca966`).

## Pendiente para el día 4

- Dejar la flota en marcha y cerrar la fecha 4 con capturas nuevas.
- Actualizar el informe y el anexo con la tabla comparativa de las 4 fechas (máx/mín/promedio/recuento/sumatoria).
- Revisar el consumo de mensajes en Cost Management antes del cierre.

## Seguimiento de la tarde (verificación en vivo)

Comprobación hecha a las 16:05 (hora de Bogotá) con la flota en marcha:

| Dispositivo | Intervalo | Último registro | Estado |
|---|---|---|---|
| DC-RACKC-03 | 30 s | 16:04:59 | Conectado |
| DC-HUMO-08 | 45 s | 16:05:10 | Conectado |
| DC-PASILLO-04 | 60 s | 16:04:28 | Conectado |
| DC-ACCESO-10 | 120 s | 16:03:36 | Conectado |
| DC-ENERGIA-09 | 120 s | 16:03:34 | Conectado |
| DC-CLIMA-05 | 900 s | 15:52:30 | Conectado (siguiente muestra ≈16:07) |
| DC-AIRE-06 | 900 s | 15:52:30 | Conectado (siguiente muestra ≈16:07) |
| DC-RACKB-02 (ESP32) | 15 s | — | **cayó en bucle de reconexión** (`[DPS] fallo connect rc=-2`) |
| DC-AGUA-07 (ESP32) | 30 s | 16:05 | Publicando |

- **Incidencia:** el ESP32 del Rack B quedó atrapado en `[DPS] fallo connect rc=-2` (fallo de conexión
  del simulador, no del firmware: el nodo de agua, con el mismo código, seguía publicando). Se resolvió
  **reiniciando la simulación** (wokwi_reiniciar3.js: stop → start); a los ~80 s ya volvía a publicar
  `[TX] {…} (ok)`. Hueco aproximado: **≈10 minutos** del nodo del Rack B (queda registrado aquí).
- Lección operativa: si un ESP32 de Wokwi no sale del ciclo de DPS en ~1 minuto, reiniciar la
  simulación es más rápido que esperar; el proyecto anónimo se conserva siempre que no se navegue la
  pestaña.
