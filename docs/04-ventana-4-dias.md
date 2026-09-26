# Ventana de 4 días no continuos — comparativa y lectura operativa

Generado: 2026-09-24 15:49 · fuente: `datos/*.csv` (series locales de cada nodo) y consultas equivalentes en el Data Explorer de IoT Central.

## Días cubiertos

| Día | Estado | Muestras totales |
|---|---|---|
| 2026-09-24 | en curso | 488 |

## 2026-09-24

| Variable | Máx | Mín | Promedio | Recuento | Sumatoria | Lectura operativa |
|---|---|---|---|---|---|---|
| `eventosAcceso` (Puerta / acceso) | 41.0 | 0.0 | 2.88 | 84 | 242.0 | la sumatoria es el número de aperturas del día: indicador de ocupación del sitio. |
| `tempPuerta` (Puerta / acceso) | 24.38 | 23.4 | 23.96 | 84 | — | el máximo refleja la ganancia térmica del acceso en las horas de mayor tránsito. |
| `pm25` (Calidad de aire) | 8.3 | 7.6 | 7.95 | 6 | — | el promedio diario se compara con el valor guía de la OMS (15 µg/m³ 24 h); el máximo explica eventos puntuales. |
| `pm10` (Calidad de aire) | 8.5 | 7.8 | 8.15 | 6 | — |  |
| `aqi` (Calidad de aire) | 50.0 | 50.0 | 50.0 | 6 | — |  |
| `co2` (Calidad de aire) | 699.6 | 694.7 | 697.15 | 6 | — | el máximo se alcanza con la sala ocupada (mantenimiento); > 1000 ppm activa la alerta de aire. |
| `tempExterior` (Clima exterior) | 26.3 | 24.9 | 25.36 | 7 | — | el máximo determina las horas sin free-cooling; el mínimo, las horas de enfriamiento gratuito pleno. |
| `humedadExterior` (Clima exterior) | 84.0 | 73.0 | 80.14 | 7 | — |  |
| `lluviaMm` (Clima exterior) | 0.4 | 0.1 | 0.23 | 7 | 1.6 | la sumatoria del día es el agua caída acumulada; > 5 mm en una muestra activa la alerta de lluvia. |
| `vientoKmh` (Clima exterior) | 7.6 | 4.7 | 6.17 | 7 | — |  |
| `radiacionSolar` (Clima exterior) | 629.0 | 379.0 | 529.0 | 7 | — | el máximo marca el pico de ganancia térmica por cubierta y la ventana de máxima carga del chiller. |
| `potenciaKw` (PDU / energía) | 5.84 | 5.36 | 5.6 | 43 | 240.6 | el máximo es la carga de fila en hora pico; la sumatoria diaria aproxima la energía de la fila (kWh). |
| `corrienteA` (PDU / energía) | 26.57 | 8.13 | 24.42 | 43 | 1049.97 | el máximo verifica que la PDU no supera su protección (32 A) con la carga actual. |
| `factorPotencia` (PDU / energía) | 0.98 | 0.95 | 0.97 | 43 | — |  |
| `humo` (Humo / incendio) | 0.02 | 0.02 | 0.02 | 109 | — | el máximo corresponde a la prueba funcional programada (10:00); el resto del día se mantiene en línea base. |
| `tempTecho` (Humo / incendio) | 27.36 | 26.58 | 26.98 | 109 | — | el máximo confirma que la estratificación térmica del techo se mantiene por debajo del umbral de incendio. |
| `tempPasillo` (Pasillo frío) | 20.57 | 19.96 | 20.23 | 81 | — | el máximo verifica la contención del pasillo frío; una subida sostenida anticipa problemas de flujo. |
| `humedadPasillo` (Pasillo frío) | 53.23 | 50.25 | 51.8 | 81 | — |  |
| `deltaPresionPa` (Pasillo frío) | 22.3 | 17.4 | 19.92 | 81 | — | el mínimo es el dato crítico: por debajo de 5 Pa la contención se pierde y el aire caliente recircula. |
| `tempIntake` (Rack C) | 22.41 | 21.71 | 22.08 | 158 | — | sigue la temperatura de la sala blanca; su deriva respecto al día anterior es el primer aviso térmico. |
| `tempExhaust` (Rack C) | 34.21 | 32.45 | 33.33 | 158 | — | el máximo aparece en la franja de mayor carga IT (tarde); el mínimo, en el valle nocturno. Un máximo sostenido por encima del umbral es el disparador de la regla de temperatura. |
| `humedadRack` (Rack C) | 50.97 | 46.2 | 48.42 | 158 | — | el máximo se explica por el ciclo de humedad de la sala; valores > 60 %HR activan la regla de humedad. |

## Lectura de conjunto

- La flota mezcla seis intervalos (15 s … 900 s): los recuentos por variable reflejan esa asincronía y son la evidencia directa de que no todos los nodos muestrean igual.
- Los extremos térmicos coinciden con la franja de mayor carga IT; los meteorológicos con la curva diaria real del feed público.
- Los eventos de seguridad (fuga, humo, acceso) aparecen como picos discretos y son los que disparan las reglas configuradas en IoT Central.
## Horas registradas por fecha (corte 26-sep 16:43)

| Fecha | Ventana con datos | Duración | De dónde salieron los datos | Filas |
|---|---|---|---|---|
| 24-sep (jue) | 14:04 → 20:05 | **6 h 01 min** | 7 nodos locales (Windows) + 2 ESP32 de Wokwi desde ~17:00 | 1 993 |
| 25-sep (vie) | 15:37 → 23:59 | **8 h 22 min** | 7 nodos locales; el supervisor remoto duplicó el nodo de humo entre 15:52 y 18:36 | 2 904 (+1 737 remotas de humo) |
| 26-sep (sáb) | 00:00 → 16:43 | **16 h 43 min** | local hasta 15:22 (venía corriendo desde el 25-sep) y después Ubuntu; ESP32 desde ~15:14 | 5 444 + 715 |
| **Total** | | **31 h 06 min** | | **12 793** |

- Ninguna fecha baja del mínimo de 4–6 h que pide el taller.
- Salvedades registradas: el 25-sep el nodo de humo tuvo dos publicadores entre 15:52 y 18:36 (filas
  intercaladas, no erróneas); el 26-sep hay un hueco de ~15 min (15:22 → 15:37) al pasar del portátil a
  la máquina Ubuntu y ~10 min del ESP32 del Rack B al reiniciarse la simulación.
- Los ESP32 de Wokwi y el simulador nativo no escriben CSV local: su cobertura se mide en el portal
  (última recepción de datos por dispositivo) y en el monitor serie.
