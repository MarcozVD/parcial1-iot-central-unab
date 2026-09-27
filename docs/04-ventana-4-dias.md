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
| 27-sep (dom) | 10:28 → 15:00 | **4 h 32 min** | exclusivamente el servidor Ubuntu (7 nodos Python) — flota local detenida a propósito para esta fecha | 1 621 |
| **Total** | | **35 h 38 min** | | **14 414** |

- Ninguna fecha baja del mínimo de 4 h que pide el taller (la 4ª fecha cerró en 4 h 32 min, verificado con
  los CSV del servidor a las 15:00).
- Salvedades registradas: el 25-sep el nodo de humo tuvo dos publicadores entre 15:52 y 18:36 (filas
  intercaladas, no erróneas); el 26-sep hay un hueco de ~15 min (15:22 → 15:37) al pasar del portátil a
  la máquina Ubuntu y ~10 min del ESP32 del Rack B al reiniciarse la simulación; el 27-sep el ESP32 del
  nodo de agua no llegó a simular (Wokwi con los servidores de compilación saturados) y el Rack B tuvo
  cortes intermitentes por el mismo motivo (rc=-2).
- Los ESP32 de Wokwi y el simulador nativo no escriben CSV local: su cobertura se mide en el portal
  (última recepción de datos por dispositivo) y en el monitor serie.

## Comparativa de las 4 fechas — máximo, mínimo, promedio, recuento y sumatoria por variable

Fuente: `datos/*.csv` para el 24, 25 y 26-sep (nodos locales); `datos/remoto_dia4/*.csv` para el 27-sep
(única fuente válida de esa fecha, el servidor Ubuntu). Generado con `tools/comparativa_4dias.py`.
## 2026-09-24 (fuente: datos)

| Variable | Max | Min | Promedio | Recuento | Sumatoria |
|---|---|---|---|---|---|
| `aqi (DC-AIRE-06)` | 80.00 | 50.00 | 66.24 | 25 | — |
| `co2 (DC-AIRE-06)` | 740.30 | 567.40 | 665.32 | 25 | — |
| `corrienteA (DC-ENERGIA-09)` | 26.57 | 8.13 | 24.90 | 170 | 4232.29 |
| `deltaPresionPa (DC-PASILLO-04)` | 22.30 | 16.40 | 19.35 | 333 | — |
| `eventosAcceso (DC-ACCESO-10)` | 41.00 | 0.00 | 4.16 | 335 | 1393.0 |
| `factorPotencia (DC-ENERGIA-09)` | 0.98 | 0.95 | 0.96 | 170 | — |
| `humedadExterior (DC-CLIMA-05)` | 98.00 | 73.00 | 91.54 | 26 | — |
| `humedadPasillo (DC-PASILLO-04)` | 53.23 | 46.43 | 49.73 | 333 | — |
| `humedadRack (DC-RACKC-03)` | 50.97 | 40.59 | 45.20 | 658 | — |
| `humo (DC-HUMO-08)` | 0.02 | 0.02 | 0.02 | 446 | — |
| `lluviaMm (DC-CLIMA-05)` | 1.50 | 0.10 | 0.84 | 26 | 21.9 |
| `pm10 (DC-AIRE-06)` | 17.50 | 7.80 | 12.34 | 25 | — |
| `pm25 (DC-AIRE-06)` | 17.10 | 7.60 | 12.04 | 25 | — |
| `potenciaKw (DC-ENERGIA-09)` | 5.84 | 5.28 | 5.57 | 170 | 946.54 |
| `radiacionSolar (DC-CLIMA-05)` | 629.00 | 0.00 | 193.12 | 26 | — |
| `tempExhaust (DC-RACKC-03)` | 34.21 | 31.80 | 33.10 | 658 | — |
| `tempExterior (DC-CLIMA-05)` | 26.30 | 21.60 | 23.25 | 26 | — |
| `tempIntake (DC-RACKC-03)` | 22.43 | 21.56 | 22.01 | 658 | — |
| `tempPasillo (DC-PASILLO-04)` | 20.57 | 19.83 | 20.21 | 333 | — |
| `tempPuerta (DC-ACCESO-10)` | 24.38 | 22.47 | 23.61 | 335 | — |
| `tempTecho (DC-HUMO-08)` | 27.36 | 24.71 | 26.37 | 446 | — |
| `vientoKmh (DC-CLIMA-05)` | 7.60 | 0.90 | 4.63 | 26 | — |

## 2026-09-25 (fuente: datos)

| Variable | Max | Min | Promedio | Recuento | Sumatoria |
|---|---|---|---|---|---|
| `aqi (DC-AIRE-06)` | 71.00 | 63.00 | 68.18 | 34 | — |
| `co2 (DC-AIRE-06)` | 822.50 | 616.50 | 677.37 | 34 | — |
| `corrienteA (DC-ENERGIA-09)` | 26.57 | 23.71 | 25.07 | 245 | 6141.43 |
| `deltaPresionPa (DC-PASILLO-04)` | 22.10 | 15.40 | 18.87 | 488 | — |
| `eventosAcceso (DC-ACCESO-10)` | 15.00 | 0.00 | 3.17 | 487 | 1543.0 |
| `factorPotencia (DC-ENERGIA-09)` | 0.98 | 0.95 | 0.96 | 245 | — |
| `humedadExterior (DC-CLIMA-05)` | 100.00 | 75.00 | 92.65 | 34 | — |
| `humedadPasillo (DC-PASILLO-04)` | 52.19 | 45.06 | 47.83 | 488 | — |
| `humedadRack (DC-RACKC-03)` | 48.37 | 39.81 | 42.94 | 964 | — |
| `humo (DC-HUMO-08)` | 0.03 | 0.02 | 0.02 | 652 | — |
| `lluviaMm (DC-CLIMA-05)` | 0.90 | 0.00 | 0.26 | 34 | 8.9 |
| `pm10 (DC-AIRE-06)` | 31.40 | 8.40 | 25.27 | 34 | — |
| `pm25 (DC-AIRE-06)` | 29.30 | 8.00 | 23.65 | 34 | — |
| `potenciaKw (DC-ENERGIA-09)` | 5.84 | 5.28 | 5.56 | 245 | 1362.38 |
| `radiacionSolar (DC-CLIMA-05)` | 411.00 | 0.00 | 56.88 | 34 | — |
| `tempExhaust (DC-RACKC-03)` | 34.09 | 30.88 | 32.63 | 964 | — |
| `tempExterior (DC-CLIMA-05)` | 25.30 | 20.60 | 22.24 | 34 | — |
| `tempIntake (DC-RACKC-03)` | 22.43 | 21.36 | 21.92 | 964 | — |
| `tempPasillo (DC-PASILLO-04)` | 20.57 | 19.68 | 20.12 | 488 | — |
| `tempPuerta (DC-ACCESO-10)` | 24.33 | 20.91 | 22.78 | 487 | — |
| `tempTecho (DC-HUMO-08)` | 27.31 | 22.39 | 25.11 | 652 | — |
| `vientoKmh (DC-CLIMA-05)` | 5.30 | 0.60 | 2.79 | 34 | — |

## 2026-09-26 (fuente: datos)

| Variable | Max | Min | Promedio | Recuento | Sumatoria |
|---|---|---|---|---|---|
| `aqi (DC-AIRE-06)` | 73.00 | 68.00 | 71.46 | 61 | — |
| `co2 (DC-AIRE-06)` | 740.20 | 553.10 | 646.81 | 61 | — |
| `corrienteA (DC-ENERGIA-09)` | 30.82 | 24.15 | 27.96 | 460 | 12862.66 |
| `deltaPresionPa (DC-PASILLO-04)` | 22.20 | 14.90 | 18.39 | 917 | — |
| `eventosAcceso (DC-ACCESO-10)` | 27.00 | 0.00 | 6.58 | 919 | 6049.0 |
| `factorPotencia (DC-ENERGIA-09)` | 0.98 | 0.95 | 0.96 | 460 | — |
| `humedadExterior (DC-CLIMA-05)` | 99.00 | 66.00 | 86.54 | 61 | — |
| `humedadPasillo (DC-PASILLO-04)` | 54.99 | 45.18 | 51.16 | 917 | — |
| `humedadRack (DC-RACKC-03)` | 54.17 | 40.69 | 49.20 | 1826 | — |
| `humo (DC-HUMO-08)` | 0.10 | 0.02 | 0.02 | 1200 | — |
| `lluviaMm (DC-CLIMA-05)` | 0.50 | 0.00 | 0.14 | 61 | 8.4 |
| `pm10 (DC-AIRE-06)` | 22.90 | 8.10 | 14.42 | 61 | — |
| `pm25 (DC-AIRE-06)` | 21.90 | 8.00 | 13.86 | 61 | — |
| `potenciaKw (DC-ENERGIA-09)` | 6.79 | 5.37 | 6.20 | 460 | 2853.89 |
| `radiacionSolar (DC-CLIMA-05)` | 781.00 | 0.00 | 311.10 | 61 | — |
| `tempExhaust (DC-RACKC-03)` | 34.23 | 30.61 | 32.28 | 1826 | — |
| `tempExterior (DC-CLIMA-05)` | 26.10 | 20.10 | 22.51 | 61 | — |
| `tempIntake (DC-RACKC-03)` | 22.44 | 21.26 | 21.82 | 1826 | — |
| `tempPasillo (DC-PASILLO-04)` | 20.58 | 19.60 | 20.05 | 917 | — |
| `tempPuerta (DC-ACCESO-10)` | 24.35 | 20.42 | 22.16 | 919 | — |
| `tempTecho (DC-HUMO-08)` | 27.38 | 21.62 | 24.16 | 1200 | — |
| `vientoKmh (DC-CLIMA-05)` | 8.10 | 0.80 | 4.11 | 61 | — |

## 2026-09-27 (fuente: datos\remoto_dia4)

| Variable | Max | Min | Promedio | Recuento | Sumatoria |
|---|---|---|---|---|---|
| `aqi (DC-AIRE-06)` | 48.00 | 44.00 | 45.89 | 19 | — |
| `co2 (DC-AIRE-06)` | 690.10 | 678.20 | 683.64 | 19 | — |
| `corrienteA (DC-ENERGIA-09)` | 26.57 | 23.71 | 25.08 | 136 | 3410.59 |
| `deltaPresionPa (DC-PASILLO-04)` | 22.20 | 16.60 | 19.45 | 273 | — |
| `eventosAcceso (DC-ACCESO-10)` | 20.00 | 0.00 | 8.75 | 273 | 2388.0 |
| `factorPotencia (DC-ENERGIA-09)` | 0.98 | 0.95 | 0.96 | 136 | — |
| `humedadExterior (DC-CLIMA-05)` | 89.00 | 73.00 | 78.95 | 19 | — |
| `humedadPasillo (DC-PASILLO-04)` | 54.93 | 51.11 | 53.38 | 273 | — |
| `humedadRack (DC-RACKC-03)` | 54.03 | 47.49 | 51.26 | 541 | — |
| `humo (DC-HUMO-08)` | 0.03 | 0.02 | 0.02 | 365 | — |
| `lluviaMm (DC-CLIMA-05)` | 0.30 | 0.20 | 0.23 | 19 | 4.3 |
| `pm10 (DC-AIRE-06)` | 6.80 | 4.70 | 5.71 | 19 | — |
| `pm25 (DC-AIRE-06)` | 6.70 | 4.60 | 5.55 | 19 | — |
| `potenciaKw (DC-ENERGIA-09)` | 5.84 | 5.28 | 5.56 | 136 | 756.62 |
| `radiacionSolar (DC-CLIMA-05)` | 770.00 | 462.00 | 660.00 | 19 | — |
| `tempExhaust (DC-RACKC-03)` | 34.16 | 32.02 | 33.13 | 541 | — |
| `tempExterior (DC-CLIMA-05)` | 24.90 | 23.00 | 24.05 | 19 | — |
| `tempIntake (DC-RACKC-03)` | 22.41 | 21.63 | 22.03 | 541 | — |
| `tempPasillo (DC-PASILLO-04)` | 20.56 | 19.90 | 20.24 | 273 | — |
| `tempPuerta (DC-ACCESO-10)` | 24.40 | 22.74 | 23.67 | 273 | — |
| `tempTecho (DC-HUMO-08)` | 27.37 | 25.10 | 26.48 | 365 | — |
| `vientoKmh (DC-CLIMA-05)` | 8.60 | 1.90 | 6.52 | 19 | — |
