# Arquitectura de referencia — DC-ANDES-1 (con capa de telecomunicaciones)

```
 CAPA DE DISPOSITIVO                CAPA DE RED                    CAPA DE PLATAFORMA                 CAPA DE OPERACIÓN
 ────────────────────               ───────────────                ────────────────────               ──────────────────
 ┌───────────────────────────┐      ┌──────────────────┐           ┌───────────────────────┐          ┌──────────────────┐
 │ 01 Simulador nativo       │      │  Wi-Fi / LAN      │          │  DPS (SAS simétrica)  │          │  Vistas por       │
 │    (Device Template)      │─────▶│  del sitio        │          │  global.azure-        │          │  dispositivo      │
 ├───────────────────────────┤      │  (sala blanca)    │          │  devices-             │          │  (Overview/About) │
 │ 02/07 ESP32 virtual       │      ├──────────────────┤          │  provisioning.net     │          ├──────────────────┤
 │    (Wokwi, DHT22 / sonda) │─────▶│  MQTT/TLS 8883    │          │  :8883                │          │  Reglas y alertas │
 ├───────────────────────────┤      │  + DPS MQTT       │─────────▶├───────────────────────┤          │  (correo/webhook) │
 │ 03/08/09 Scripts Python   │─────▶│  TLS 1.2+,        │          │  Azure IoT Central    │          ├──────────────────┤
 │    (SDK, paho, CSV)       │      │  puerto 8883      │          │  (IoT Hub gestionado) │          │  Panel “Cuarto de │
 ├───────────────────────────┤      ├──────────────────┤          │  · gemelo digital     │          │  Control” con KPIs│
 │ 04 Script Python (Rack C, │─────▶│  MQTT sobre       │          │  · comandos           │          │  y 8 gráficos     │
 │    pasillo) SDK/WebSocket │      │  WebSockets 443   │          │  · propiedades        │          ├──────────────────┤
 ├───────────────────────────┤      ├──────────────────┤          │  · telemetría         │          │  Comandos remotos │
 │ 10 Puente HTTP/REST +     │─────▶│  HTTPS 443        │          ├───────────────────────┤          │  (setAlerta,      │
 │    sensor de campo        │      │  (REST de         │          │  Data Explorer        │          │  abrirPuerta,     │
 ├───────────────────────────┤      │  dispositivo)     │          │  (consultas y         │          │  acuseAlarma)     │
 │ 05/06 Puentes de API      │─────▶│                   │          │  exportación)         │          └──────────────────┘
 │    pública (HTTPS/443)    │      │  Salida a Internet│          └───────────────────────┘                   ▲
 └───────────────────────────┘      │  del predio       │                                                     │
                                    │  (fibra urbana;   │                    ingenieros de operación ─────────┘
                                    │  sin NAT entrante)│
                                    └──────────────────┘
```

## Capa de dispositivo

Diez nodos, diez códigos/feeds distintos (ver `docs/01-catalogo-dispositivos.md`):
simulador nativo de la plantilla, dos ESP32 virtuales en Wokwi (firmware Arduino/C++ con
PubSubClient), tres scripts Python (SDK MQTT, SDK sobre WebSockets, paho explícito), un
replay de CSV histórico, un puente HTTP/REST con su sensor de campo y dos puentes de API
pública (meteorología y calidad de aire). Las variables de cada nodo están ancladas a
datasheets reales en `docs/02-datasheets-y-parametros.md`.

## Capa de red y telecomunicaciones

| Camino | Transporte | Puerto | Por qué |
|---|---|---|---|
| ESP32 (Wokwi #1 y #2) | MQTT sobre TLS 1.2 | **8883** | transporte nativo de IoT Hub; en Wokwi la termina el gateway del simulador (SSID `Wokwi-GUEST`) |
| Python SDK (Rack C, PDU, clima) | MQTT sobre TLS 1.2 | **8883** | camino estándar del SDK (`azure-iot-device`) |
| Python SDK (pasillo) | **MQTT sobre WebSockets** | **443** | atraviesa proxies/firewalls corporativos que bloquean 8883; mismo protocolo, distinto canal |
| Puente de calidad de aire | **HTTPS** (REST de dispositivo) | **443** | ingesta sin MQTT: `POST /devices/{id}/messages/events` con SAS |
| Puentes de API pública | **HTTPS saliente** (443) hacia api.open-meteo.com / air-quality-api.open-meteo.com | 443 | los feeds externos se consultan, no se reciben |
| Sensor de campo del acceso | HTTP en `127.0.0.1:8098` | — | el sensor real no conoce Azure: el puente traduce a MQTT |

Elección del sitio: **urbano**, por lo que no se requiere 4G/LTE ni enlace satelital; el
predio sale por fibra con **NAT saliente** (no hay puertos de entrada abiertos: todo el
tráfico es iniciado por los dispositivos). Autenticación **SAS simétrica del dispositivo**
firmada con HMAC-SHA256 contra DPS; el registro se hace una vez y el hub asignado se
reutiliza (`datos/hub_<device>.txt`).

**Detalle fino del protocolo** (validado en los laboratorios previos y reutilizado aquí):
el recurso que se firma se **percent-encoda antes de firmar** (igual que
`azure-iot-device/sastoken.py`); DPS acepta `api-version=2021-06-01`, pero el endpoint MQTT
del hub **rechaza versiones ≥ 2020**, por lo que el nodo usa `2019-10-01` en la conexión al
hub (un `api-version` alto devuelve CONNACK `rc=5` con un token perfectamente válido).

## Capa de plataforma (Azure IoT Central)

- **DPS** (Device Provisioning Service) con inscripción por **clave simétrica**: la app
  aprovisiona los diez dispositivos contra el hub asignado.
- **IoT Hub gestionado** de IoT Central: telemetría, gemelo digital (propiedades reportadas
  y *desired*), comandos sincrónicos y archivos.
- **Digital Twin / plantilla** `Nodo DC-ANDES-1` (`dtmi:unab:dcandes:dcAndesNodo;1`) con 27
  capacidades de telemetría, 11 propiedades (4 escribibles) y 4 comandos; publicada y usada
  por los diez dispositivos.
- **Grupo de dispositivos** `Nodo DC-ANDES-1 - All devices` (`SELECT * FROM devices WHERE
  $template = "dtmi:unab:dcandes:dcAndesNodo;1"`), base de los mosaicos del panel.
- **Data Explorer** para consultas sobre la ventana de cuatro días y exportación de series.
- **Reglas** con acciones de correo y webhook (ver `docs/02-datasheets-y-parametros.md §6`).

## Capa de operación

- Vistas por dispositivo autogeneradas (Overview con KPIs y gráficos, About con propiedades).
- **Panel personalizado “Cuarto de Control DC-ANDES-1”**: identidad visual del escenario
  (logo y nombre propios, no el genérico de Azure), recuento de dispositivos del grupo,
  KPIs (temperatura de exhaust máxima de racks, PM2.5 promedio, potencia y humo del último
  valor), seis gráficos de líneas y un bloque de alertas.
- Comandos remotos desde el cuarto de control (`setAlerta`, `acuseAlarma`, `reiniciar`,
  `abrirPuerta`) y propiedades escribibles para ajustar umbrales en caliente.
- Sustentación: dos nodos vivos en dos equipos distintos (Python en el portátil + Wokwi en
  el navegador) mientras el resto de la flota sigue publicando en segundo plano.

## Resiliencia y operación continua

- `dc_supervisor.py` mantiene los ocho procesos locales y los reinicia si terminan; un
  **cronjob de Hermes** (cada 10 min) relanza el supervisor si no está corriendo.
- Cada nodo escribe su bitácora (`logs/<device>.log`), su serie local (`datos/<device>.csv`)
  y su salida (`logs/<node>.out`); los CSV locales permiten el análisis de los cuatro días
  aunque el portal se consulte más tarde.
- `datos/pausa_<device>.json` permite programar la **pausa documentada** de un nodo
  (hueco controlado) sin tocar el código.
