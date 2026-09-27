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

El proyecto del nodo de agua quedó bloqueado en **"Build Servers Busy"** de Wokwi. Se probó:

1. Cerrar el diálogo y reiniciar la simulación (3 intentos espaciados ~3-5 min).
2. **Abrir un proyecto completamente nuevo** (pestaña limpia, sin historial) e inyectar el sketch desde
   cero: mismo resultado.

Con el mismo bloqueo en un proyecto recién creado, se descarta que sea un problema del proyecto o de la
sesión: es la cola de compilación del plan gratuito de Wokwi, saturada por tener el Rack B simulando en
paralelo. Es una limitación conocida del plan gratuito (ver nota en `docs/05-operacion.md`, sección
"Wokwi free-plan constraints"). Se dejó de insistir tras ~30 min de intentos.

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
| `dia4-views-plantilla.png` | Views de operador de la plantilla (Overview, About) — requisito de la sección 4 del taller |

## Actualización de los documentos entregables (13:25, mientras la fecha 4 termina de acumular horas)

Se detectó que `Informe_Parcial1_DC-ANDES-1.docx/pdf` y `Evidencias_Parcial1_DC-ANDES-1.docx/pdf` estaban
congelados en el estado del 24-sep (generados a las 17:03/17:08 de ese día) y no reflejaban nada de los
días 2, 3 y 4: la migración a Ubuntu, los incidentes y su corrección, ni las evidencias nuevas. Se
actualizaron ambos generadores (`tools/build_informe.py`, `tools/build_evidencias.py`) y se regeneraron:

- **Historial de versiones** con el resumen real de cada fecha (horas, origen de los datos, qué cambió).
- **Sección 6.1 nueva** — "Incidentes operativos de la ventana": los 4 fallos reales (supervisor remoto
  mal diseñado, doble publicación, SAS del Rack B, Wokwi saturado) con diagnóstico y resolución. Es
  evidencia más fuerte de desconexión/reconexión real que la pausa puramente programada.
- **Sección 5** — Views de operador documentadas (Overview, About), con su captura.
- **Sección 7 y Anexo B** — tabla de horas por fecha (24: 6h01, 25: 8h22, 26: 18h09) con una fila y un
  callout explícitos de **"[COMPLETAR AL CIERRE]"** para la fecha 4, y una tabla de incidencias por fecha.
- **Anexo de evidencias** — nuevas secciones 3.3 (Views) y 4 (días 2-4: capturas dia3-* y dia4-*), con un
  callout de cierre pendiente para cuando termine la ventana de hoy.
- Matriz de cumplimiento actualizada para citar las capturas y secciones nuevas.

Ambos documentos se regeneraron a PDF sin errores: informe 13 páginas (antes 11), anexo 14 páginas
(antes 9). Verificado con extracción de texto que el contenido nuevo (historial, incidentes, placeholder
de cierre) está presente en el PDF, no solo en el .docx.

**Lo que falta cuando la fecha 4 complete las horas mínimas:**
1. Reemplazar la fila `[COMPLETAR AL CIERRE]` de la sección 7 y del Anexo B con la ventana final real.
2. Añadir la tabla comparativa completa de las 4 fechas (máx/mín/promedio/recuento/sumatoria) al Anexo B,
   siguiendo el mismo procedimiento que ya se aplicó a la fecha 1 en `docs/04-ventana-4-dias.md`.
3. Capturar la evidencia de cierre (última recepción de datos de cada nodo) y, si el nodo de agua logra
   simular antes del cierre, su evidencia correspondiente.
4. Regenerar ambos documentos con `tools/build_informe.py` + `tools/build_evidencias.py` y volver a
   convertir a PDF con `tools/topdf.ps1`.

## Cierre de la fecha 4 (15:00) — ventana completada

La fecha 4 superó el mínimo de 4 horas: **10:28 → 15:00 (4 h 32 min)**, verificado con los CSV del
servidor Ubuntu (`datos/remoto_dia4/`, copiados al cierre). 1 621 muestras en total.

| Nodo | Ventana | Duración | Muestras |
|---|---|---|---|
| DC-RACKC-03 | 10:28:14 → 15:00:43 | 4.54 h | 540 |
| DC-HUMO-08 | 10:28:15 → 15:00:32 | 4.54 h | 364 |
| DC-PASILLO-04 | 10:28:16 → 14:59:45 | 4.52 h | 272 |
| DC-ACCESO-10 | 10:28:25 → 14:58:49 | 4.51 h | 271 |
| DC-ENERGIA-09 | 10:28:23 → 14:59:38 | 4.52 h | 136 |
| DC-CLIMA-05 / DC-AIRE-06 | 10:28:20 → 14:58:3x | 4.50 h | 19 c/u |

El ESP32 del Rack B tuvo cortes intermitentes (`rc=-2`) durante la ventana pero se recuperó varias veces;
el nodo de agua no llegó a simular en toda la fecha (ver incidencia arriba).

### Documentos actualizados con el cierre real

Se completó lo que quedó pendiente en la actualización de las 13:25:

1. **Tabla de horas por fecha** (sección 7 del informe y `docs/04-ventana-4-dias.md`): la fila del 27-sep
   pasó de `[COMPLETAR AL CIERRE]` a **4 h 32 min**, con el total de la ventana en **35 h 38 min** y
   **14 414 muestras** en las 4 fechas.
2. **Comparativa completa por variable** (`tools/comparativa_4dias.py`, nuevo): máximo, mínimo, promedio,
   recuento y sumatoria de cada variable en cada una de las 4 fechas, calculada desde las series reales
   (portátil para 24/25/26-sep, servidor Ubuntu para 27-sep). Insertada en el Anexo B del informe y en
   `docs/04-ventana-4-dias.md` — más de 80 filas de datos reales, no estimados.
3. **Evidencia de cierre**: captura `dia4-cierre-flota.png` (flota completa en el portal a las 15:00) y
   estados individuales de 5 dispositivos, todos "Conectado" con marca de tiempo de cierre.
4. Los tres callouts `[PENDIENTE]` / `[COMPLETAR AL CIERRE]` / `EN CURSO` se retiraron; verificado con
   extracción de texto de los PDF finales que ninguno de esos marcadores permanece.

**Documentos finales:** informe 17 páginas (era 11 al inicio del día), anexo 15 páginas (era 9). Ambos
verificados con `pymupdf`: contienen "4 h 32", "35 h 38" y la captura de cierre; no contienen ningún
marcador de pendiente.

**Ventana completa de las 4 fechas:**

| Fecha | Duración |
|---|---|
| 24-sep | 6 h 01 |
| 25-sep | 8 h 22 |
| 26-sep | 18 h 09 |
| 27-sep | 4 h 32 |
| **Total** | **35 h 38** |

Las 4 fechas superan el mínimo de 4 horas que exige el taller.
