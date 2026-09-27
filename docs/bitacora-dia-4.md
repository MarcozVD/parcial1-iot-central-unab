# Bitácora — Día 4 (27 de septiembre de 2026)

## Resumen

| Aspecto | Valor |
|---|---|
| Fecha | domingo 27 de septiembre de 2026 (cuarta y última fecha de la ventana) |
| Inicio | 10:28 (hora de Bogotá) |
| Origen | 7 nodos Python en el **servidor Ubuntu** (52.252.133.127) + 1 ESP32 Wokwi (Rack B) |
| Pendiente | El ESP32 de agua no llegó a simular por saturación de los servidores de compilación de Wokwi |

## Arranque

- El servidor ya estaba con `0 procesos` (apagado limpiamente el 26-sep). Se relanzó el supervisor:
  `dc_supervisor_remote.py` → 8/8 procesos vivos a los 20 s, con CSV frescos por dispositivo.
- El navegador de la sesión anterior se había cerrado (esperable, nuevo día): se reabrió con el perfil
  persistente de Edge (cookies de IoT Central conservadas; los proyectos Wokwi no, son anónimos).
- Se reconstruyó el ESP32 del **Rack B**: sketch + diagrama + librerías + arranque. Publicando con
  normalidad a los pocos minutos (`[TX] {...} (ok)` cada 15 s).

## Incidencia: ESP32 de agua no pudo simular

El proyecto del nodo de agua quedó bloqueado en **"Build Servers Busy"** de Wokwi durante más de
20 minutos, con varios reintentos (cerrar diálogo + reiniciar simulación) espaciados en el tiempo.
No es un fallo del sketch ni del proyecto: es la cola de compilación del plan gratuito de Wokwi,
saturada por tener dos proyectos ESP32 abiertos a la vez en la misma sesión. Es una limitación conocida
del plan gratuito (ver nota en `docs/05-operacion.md`, sección "Wokwi free-plan constraints").

**Cobertura de la fecha sin el nodo de agua:** 9 de 10 orígenes activos (7 Python en servidor + Rack B
ESP32 + simulador nativo). El nodo de agua ya tiene cobertura de sobra en las fechas 1 y 3
(24-sep y 26-sep), así que la ventana comparativa no queda con huecos totales para ese dispositivo.

## Estado verificado (11:21, ~53 min de ventana)

| Origen | Estado | Última recepción |
|---|---|---|
| DC-RACKC-03 (Ubuntu) | Conectado | 27/9/2026, 11:13:54 |
| DC-HUMO-08 (Ubuntu) | vivo (supervisor) | en curso |
| DC-PASILLO-04, DC-ACCESO-10, DC-ENERGIA-09, DC-CLIMA-05, DC-AIRE-06 (Ubuntu) | vivos (supervisor 8/8) | en curso |
| DC-RACKB-02 (Wokwi) | publicando | monitor serie con TX (ok) |
| DC-AGUA-07 (Wokwi) | **no arrancó** | Build Servers Busy (Wokwi) |
| DC-RACKA-01 | simulador nativo, sin cambios | Azure |

## Evidencias (`evidencias/dia4-*.png`)

| Archivo | Qué prueba |
|---|---|
| `dia4-portal-flota.png` | los 10 dispositivos en el portal |
| `dia4-datos-rackc.png` | datos sin procesar de DC-RACKC-03 (Ubuntu), Conectado, 27/9 11:13:54 |
| `dia4-datos-humo.png` | datos sin procesar de DC-HUMO-08 (Ubuntu) |
| `dia4-datos-rackb.png` | datos sin procesar de DC-RACKB-02 (ESP32) |
| `dia4-wokwi-rackb.png` | monitor serie del ESP32 del Rack B publicando en vivo |
EOF
