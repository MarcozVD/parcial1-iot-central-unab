# Tablas de parámetros y datasheets — DC-ANDES-1

Cada variable de telemetría está anclada a un sensor o feed real. La columna
**“valor en el código”** documenta el modelo/offset con el que el nodo genera el dato
(código en `dispositivos/`), y **“umbral de Rule”** el valor configurado en IoT Central.

## 1. Variables de racks y pasillo (nodos 01, 02, 03, 04)

| Variable | Sensor / datasheet | Rango fabricante | Rango operativo del escenario | Unidad | Precisión | Intervalo usado | Valor usado en el código | Umbral de Rule |
|---|---|---|---|---|---|---|---|---|
| `tempIntake` | DHT22 (Wokwi) / SHT31 (Rack C) / APC AP9335TH (ref.) | −40 … 80 | 18 … 26 | °C | ±0,5 | 15 / 30 / 60 s | `21,0 + 1,5·carga + ruido(±0,35)` | — (alimenta KPI) |
| `tempExhaust` | APC AP9335TH / derivado térmico | −10 … 60 | 26 … 38 | °C | ±0,5 | 15 / 30 s | `intake + 8,0 + 4,5·carga` (Wokwi: potenciómetro = carga) | **> 35 °C** |
| `humedadRack` | DHT22 / SHT31 | 0 … 100 | 38 … 62 | %HR | ±2 … ±3 | 15 / 30 / 60 s | `47 + 6·sen((h−4)π/12) + ruido(±1,2)` | **> 60 %HR** |
| `tempPasillo` | SHT31 | −40 … 125 | 18 … 22 | °C | ±0,3 | 60 s | `19,4 + 1,2·carga + ruido(±0,3)` | **> 26 °C** |
| `humedadPasillo` | SHT31 | 0 … 100 | 40 … 58 | %HR | ±1,5 | 60 s | `50 + 4·sen((h−5)π/12) + ruido(±1,0)` | — |
| `deltaPresionPa` | Sensirion SDP810-500Pa | −500 … +500 | 3 … 30 (positivo = contención) | Pa | ±3 % m.v. | 60 s | `14 + 8·carga + ruido(±2,5)` | **< 5 Pa** (pérdida de contención) |

## 2. Meteorología exterior (nodo 05 — feed Open-Meteo)

| Variable | Fuente / datasheet | Rango fabricante | Rango operativo | Unidad | Precisión | Intervalo | Valor en el código | Umbral de Rule |
|---|---|---|---|---|---|---|---|---|
| `tempExterior` | Open-Meteo (ref. Davis Vantage Pro2) | −40 … 65 | 15 … 30 | °C | ±0,5 | 900 s | dato **real** del feed | **> 28 °C** → free-cooling limitado |
| `humedadExterior` | Open-Meteo | 0 … 100 | 40 … 95 | %HR | ±3 | 900 s | dato real | — |
| `radiacionSolar` | Open-Meteo (shortwave) | 0 … 1500 | 0 … 1000 | W/m² | ±5 % | 900 s | dato real | **> 700 W/m²** |
| `vientoKmh` | Open-Meteo | 0 … 150 | 0 … 40 | km/h | ±5 % | 900 s | dato real | — |
| `lluviaMm` | Open-Meteo (precipitation) | 0 … 100 | 0 … 20 | mm | ±4 % | 900 s | dato real | **> 5 mm** |
| `tsFuente` | marca de tiempo de la API | — | — | ISO 8601 | — | 900 s | `current.time` del feed | — |

## 3. Calidad de aire (nodo 06)

| Variable | Fuente / datasheet | Rango fabricante | Rango operativo | Unidad | Precisión | Intervalo | Valor en el código | Umbral de Rule |
|---|---|---|---|---|---|---|---|---|
| `pm25` | Open-Meteo AQ (ref. Plantower PMS7003) | 0 … 1000 | 0 … 60 | µg/m³ | ±10 | 900 s | dato **real** del feed | **> 35 µg/m³** (OMS 24 h) |
| `pm10` | Open-Meteo AQ | 0 … 1000 | 0 … 100 | µg/m³ | ±10 | 900 s | dato real | **> 50 µg/m³** |
| `aqi` | índice US EPA | 0 … 500 | 0 … 150 | índice | — | 900 s | dato real (`us_aqi`) | **> 100** |
| `co2` | Sensirion SCD41 (estimación de ocupación) | 400 … 4000 | 400 … 1200 | ppm | ±(30 + 5 % m.v.) | 900 s | `415 + 230·ocupación + 6·pm25 + 12·(0,5−\|0,5−h/24\|)` | **> 1000 ppm** |

## 4. Seguridad física: agua, humo, energía y acceso (nodos 07-10)

| Variable | Sensor / datasheet | Rango fabricante | Rango operativo | Unidad | Precisión | Intervalo | Valor en el código | Umbral de Rule |
|---|---|---|---|---|---|---|---|---|
| `fugaAgua` | RLE LD2100 + sonda resistiva | 0 / 1 (detección) | 0 / 1 | booleano | — | 30 s | `true` solo durante la prueba funcional (pulsador) o la ventana programada 15:00 | **= true** (alarma inmediata) |
| `humedadPiso` | sonda resistiva (potenciómetro en Wokwi) | 0 … 100 | 30 … 90 | % | ±5 | 30 s | `map(pot,0,1023,30,90) + 8 si fuga` | **> 70 %** |
| `humo` | Siemens FDA241 (índice de oscurecimiento) | 0,005 … 20 | 0,01 … 0,10 | %obs/m | ±0,005 | 45 s | `0,021 + 0,004·sen + \|ruido\|`; prueba programada 10:00 → `0,09` | **> 0,08 %obs/m** |
| `tempTecho` | APC AP9335TH | −10 … 60 | 22 … 30 | °C | ±0,5 | 45 s | `24,5 + 2,5·cos((h−15)π/12) + ruido(±0,4)` | **> 40 °C** (incendio) |
| `potenciaKw` | Raritan PX3-5488 | 0 … 7,4 | 4,1 … 7,5 | kW | ±1 % | 120 s | `4,1 + 3,4·carga` (CSV histórico) | **> 7,0 kW** |
| `corrienteA` | Raritan PX3-5488 (monofásica 230 V) | 0 … 32 | 18 … 33 | A | ±1 % | 120 s | `P·1000 / (230·FP)` | **> 30 A** |
| `factorPotencia` | Raritan PX3-5488 | 0 … 1 | 0,90 … 0,995 | — | ±0,01 | 120 s | `0,965 + ruido(±0,012)` | **< 0,90** |
| `puertaAbierta` | HID iCLASS SE R40 + Mercury LP1502 | 0 / 1 | 0 / 1 | booleano | — | 120 s | `true` 12 % de las muestras en horario 07:30–18:30, o por comando `abrirPuerta` | **= true fuera de horario** |
| `eventosAcceso` | contador del controlador | 0 … 65535 | creciente | eventos | — | 120 s | acumulado por cada apertura | — (KPI/sumatoria) |
| `tempPuerta` | termistor del lector | −20 … 60 | 21 … 25 | °C | ±0,5 | 120 s | `22,4 + 1,6·cos((h−15)π/12) + ruido(±0,4)` | — |

## 5. Propiedades y comandos de la plantilla

| Tipo | Nombre | Uso |
|---|---|---|
| Propiedad (reportada) | `zona`, `ubicacion`, `origenEnvio`, `fabricante`, `modelo`, `versionFirmware`, `intervaloMuestreo` | identidad del nodo; `origenEnvio` documenta el origen del catálogo dentro del propio gemelo |
| Propiedad **escribible** | `umbralTemperatura` (27 °C), `umbralHumedad` (60 %), `umbralPM25` (35 µg/m³), `modoOperacion` (Normal/Mantenimiento/Emergencia) | la nube ajusta el comportamiento del nodo en caliente (twin desired → el script reevalúa sin reiniciar) |
| Comando | `reiniciar`, `setAlerta`, `acuseAlarma`, `abrirPuerta` | operación desde el cuarto de control; responden con JSON y quedan en el historial de comandos |

## 6. Reglas (Rules) y acciones

| Regla | Condición | Acción | Evidencia |
|---|---|---|---|
| Alerta temperatura de rack | `tempExhaust > 35` | correo + webhook | `evidencias/` |
| Alerta humedad de rack | `humedadRack > 60` | correo | `evidencias/` |
| Fuga de agua detectada | `fugaAgua = true` | correo + webhook | `evidencias/` |
| Humo detectado | `humo > 0,08` | correo + webhook | `evidencias/` |
| Calidad de aire degradada | `pm25 > 35` | correo | `evidencias/` |
| Acceso fuera de horario | `puertaAbierta = true` | correo | `evidencias/` |
