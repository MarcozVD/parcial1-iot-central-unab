# Catálogo único de dispositivos — DC-ANDES-1 (AndesCloud S.A.S.)

**Escenario elegido:** 5.2 *Centro de datos* (ubicación urbana, Bucaramanga).
**Aplicación IoT Central:** `dcandes1unab` → https://dcandes1unab.azureiotcentral.com
**Plantilla (Digital Twin):** `Nodo DC-ANDES-1` · `dtmi:unab:dcandes:dcAndesNodo;1` (42 capacidades, publicada)

> regla del parcial: *cada fila del catálogo declara un origen de envío distinto*. No hay bloques fijos
> (ni 5+5 ni “cinco obligatorios y cinco de relleno”): las diez filas cubren diez códigos/feeds distintos
> y la flota se reparte por zona del centro de datos.

| # | ID en Central | Zona / rol | Origen de envío (identificador) | Protocolo / ingesta hacia Central | Intervalo | Variables publicadas | Sensor / datasheet citado |
|---|---|---|---|---|---|---|---|
| 01 | `DC-RACKA-01` | Rack A — nodo ambiental | **Digital Twin / simulador nativo de IoT Central** (`sim-rackA`, sobre la plantilla) | Simulador de la plataforma (activable desde la app) | ~60 s | `tempIntake`, `tempExhaust`, `humedadRack` (+ todas las del modelo) | Sensor de referencia APC **AP9335TH** (−10…60 °C, ±0,5 °C; 0…95 %HR, ±3 %) |
| 02 | `DC-RACKB-02` | Rack B — nodo ambiental | **Wokwi ESP32 #1** — sketch Arduino + PubSubClient (`wokwi-rackb v1.5.0`) | MQTT/TLS **8883** + DPS (SAS simétrica) | **15 s** | `tempIntake`, `tempExhaust`, `humedadRack` | **DHT22** (−40…80 °C, ±0,5 °C; 0…100 %HR, ±2 %) |
| 03 | `DC-RACKC-03` | Rack C — nodo ambiental | **Python — SDK `azure-iot-device`** (`dc_sdk_mqtt.py v1.4.0`) | MQTT/TLS **8883** + DPS (SDK) | **30 s** | `tempIntake`, `tempExhaust`, `humedadRack` | **Sensirion SHT31** (−40…125 °C, ±0,3 °C; ±1,5 %HR) |
| 04 | `DC-PASILLO-04` | Pasillo frío / contención | **Python — SDK con transporte alterno** (`dc_sdk_ws.py v1.2.0`) | **MQTT sobre WebSockets (443)** + DPS | **60 s** | `tempPasillo`, `humedadPasillo`, `deltaPresionPa` | **Sensirion SDP810-500Pa** (±3 % m.v.) + SHT31 |
| 05 | `DC-CLIMA-05` | Clima exterior (free-cooling) | **API pública meteorológica** (`dc_api_openmeteo.py v1.3.0`, Open-Meteo) | HTTPS (consulta) + MQTT/TLS 8883 (reenvío SDK) | **900 s** | `tempExterior`, `humedadExterior`, `lluviaMm`, `vientoKmh`, `radiacionSolar`, `tsFuente` | **Davis Vantage Pro2** (±0,5 °C; ±3 %HR; ±4 % lluvia; ±5 % viento/radiación) |
| 06 | `DC-AIRE-06` | Calidad de aire de sala | **API pública de dominio distinto** (`dc_api_aire.py v1.2.1`, Open-Meteo Air Quality) | HTTPS (consulta) + **HTTPS/REST 443** (API de dispositivo del hub) | **900 s** | `pm25`, `pm10`, `aqi`, `co2`, `tsFuente` | **Plantower PMS7003** (±10 %) + **Sensirion SCD41** (±30 ppm + 5 %) |
| 07 | `DC-AGUA-07` | Detección de agua bajo piso | **Wokwi ESP32 #2** — sketch propio, sonda analógica + pulsador (`wokwi-agua v1.3.0`) | MQTT/TLS **8883** + DPS | **30 s** | `fugaAgua`, `humedadPiso` | Sonda resistiva tipo **RLE LD2100** (detección 0/1) |
| 08 | `DC-HUMO-08` | Detección de humo / incendio | **Cliente MQTT explícito (paho, sin SDK)** (`dc_paho.py v1.1.0`) | MQTT/TLS 8883 con SAS firmado a mano + DPS por MQTT | **45 s** | `humo`, `tempTecho` | **Siemens FDA241** (0,005…20 %obs/m) |
| 09 | `DC-ENERGIA-09` | PDU / energía de fila | **Replay de CSV histórico** (`dc_csv_replay.py v1.0.3` + `datos/historico_pdu_fila.csv`) | MQTT/TLS 8883 (SDK) con feed de archivo | **120 s** | `potenciaKw`, `corrienteA`, `factorPotencia`, `tsFuente` | **Raritan PX3-5488** (0…32 A, ±1 %; hasta 7,4 kW) |
| 10 | `DC-ACCESO-10` | Puerta / control de acceso | **Puente HTTP/REST** (`dc_http_bridge.py v1.1.4` + `dc_acceso_sim.py`, sensor de campo) | HTTP local (sensor) + MQTT/TLS 8883 (puente) | **120 s** | `puertaAbierta`, `eventosAcceso`, `tempPuerta` | **HID iCLASS SE R40** + controladora Mercury LP1502 |

## Asincronía de la flota

Intervalos distintos en uso: **15 s · 30 s · 45 s · 60 s · 120 s · 900 s** (seis valores, el mínimo exigido son tres).
El intervalo declarado por cada nodo viaja además en la propiedad `intervaloMuestreo` del gemelo.

## Desconexión documentada (hueco en la serie)

- `DC-HUMO-08` (paho) tiene programada una **pausa del script** durante la ventana de la prueba de
  mantenimiento: el nodo deja de publicar y queda **Desconectado** en Central; al reanudar, el estado
  vuelve a **Conectado** y la serie continúa (evidencia: `evidencias/` + `informe/`).
- Los nodos Wokwi muestran su propio ciclo Connecting → Connected cada vez que se reabre el simulador,
  y el simulador nativo (Rack A) muestra el ciclo Bloquear/Desbloquear que usa IoT Central.

## Trazabilidad de orígenes (por qué cada fila es distinta)

| Fila | Qué cambia respecto a las demás (código y/o feed y/o transporte) |
|---|---|
| 01 | No hay código propio: lo genera el **simulador de la plataforma** sobre la misma plantilla. |
| 02 | Firmware **Arduino/C++** (PubSubClient, SAS por mbedTLS) corriendo en un **ESP32 virtual**. |
| 03 | **SDK Python** (DPS + MQTT 8883) con gemelo y métodos. |
| 04 | **Mismo SDK, otro transporte**: MQTT sobre WebSockets en **443** (atraviesa proxies). |
| 05 | **Feed externo** Open-Meteo; el script no “inventa” la variable, la **consulta**. |
| 06 | **Segundo feed externo de otro dominio** (calidad de aire) y **otra ingesta**: REST 443 del hub. |
| 07 | **Segundo sketch Wokwi**, con sensor analógico y pulsador (no comparte código con el 02). |
| 08 | **Sin SDK**: paho-mqtt con SAS firmado a mano y registro DPS explícito por MQTT. |
| 09 | **No hay sensor**: reproduce un **histórico CSV** de la PDU (marca de tiempo de origen + de ingesta). |
| 10 | **Puente HTTP/REST**: el sensor de campo solo habla HTTP contra `127.0.0.1:8098`; el puente traduce a MQTT. |
