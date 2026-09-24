# Bitácora · Día 1 — jueves 24 de septiembre de 2026

Registro de lo ejecutado en el día de despliegue del Parcial 1 (escenario 5.2 Centro de datos,
DC-ANDES-1). Cada punto se verificó contra la plataforma o contra el propio código en ejecución.

## 1. Plataforma

| Elemento | Resultado | Verificación |
|---|---|---|
| Grupo de recursos | `rg-parcial1-dc` (centralus) | `az group show` |
| Aplicación IoT Central | `dcandes1unab` · «DC-ANDES-1 · AndesCloud UNAB» · SKU ST2 | portal + `az iot central app show` |
| Plantilla (Digital Twin) | «Nodo DC-ANDES-1» · `dtmi:unab:dcandes:nodoDCAndes;1` · 42 capacidades · **publicada** | portal (id interno `wf05iYNAtplrCiCa0BiN1`) |
| Dispositivos | 10 creados con clave simétrica (DPS) | portal (lista «Aprovisionado») |
| Panel | «Cuarto de Control DC-ANDES-1» · 16 mosaicos | portal + REST 200 |
| Reglas | 6 creadas y **habilitadas** | `evidencias/06-reglas-6-habilitadas.png` |
| Identidad visual | logo del escenario (`assets/logo_andescloud_dcandes1.png`) | mosaico del panel |

## 2. Flota: diez dispositivos, diez orígenes de envío

| # | Id | Origen | Transporte / código | Intervalo |
|---|---|---|---|---|
| 01 | DC-RACKA-01 | Simulador nativo de la plantilla | plataforma | 60 s |
| 02 | DC-RACKB-02 | ESP32 virtual (Wokwi #1) | MQTT/TLS 8883 + DPS, sketch propio | 15 s |
| 03 | DC-RACKC-03 | SDK `azure-iot-device` (Python) | MQTT/TLS 8883 + DPS | 30 s |
| 04 | DC-PASILLO-04 | SDK Python con transporte alterno | MQTT sobre WebSockets 443 | 60 s |
| 05 | DC-CLIMA-05 | API pública Open-Meteo | HTTPS + MQTT/TLS | 900 s |
| 06 | DC-AIRE-06 | API pública de calidad del aire | HTTPS/REST 443 + MQTT/TLS | 900 s |
| 07 | DC-AGUA-07 | ESP32 virtual (Wokwi #2) | MQTT/TLS 8883 + DPS, sketch propio | 30 s |
| 08 | DC-HUMO-08 | Cliente MQTT explícito (paho, sin SDK) | MQTT/TLS 8883 con SAS manual | 45 s |
| 09 | DC-ENERGIA-09 | Replay de CSV histórico de la PDU | MQTT/TLS 8883 | 120 s |
| 10 | DC-ACCESO-10 | Puente HTTP/REST + sensor de campo | HTTP local → MQTT/TLS | 120 s |

Estado al cierre del día (17:13): **los diez publican**. Los ocho nodos locales con CSV escritos
hacía menos de 2 minutos (los dos de 900 s, en su turno), los dos ESP32 con `[TX] … (ok)` en el
monitor serie y el simulador nativo activo en la plataforma.

## 3. Datos y documentación generada

- `docs/01-catalogo-dispositivos.md` — catálogo único de las 10 filas con su justificación de origen.
- `docs/02-datasheets-y-parametros.md` — por variable: datasheet de referencia, rango de fabricante,
  rango operativo, precisión, intervalo y umbral de regla.
- `docs/03-arquitectura.md` + `evidencias/diagrama_arquitectura.png` — cuatro capas con
  telecomunicaciones (puertos 8883, 443 y REST).
- `docs/04-ventana-4-dias.md` — ventana 24–27 sep: máximo, mínimo, promedio, recuento y sumatoria.
- `docs/05-operacion.md` — rutina diaria, reconstrucción de los ESP32 virtuales, pausa documentada y costo.
- `datos/historico_pdu_fila.csv` — serie de la PDU (fila C, día típico, 120 s).
- `informe/Informe_Parcial1_DC-ANDES-1.docx|.pdf` — **11 páginas**, secciones 1–11 y anexos A/B.
- `informe/Evidencias_Parcial1_DC-ANDES-1.docx|.pdf` — **9 páginas**, matriz de cumplimiento,
  capturas del portal, logs de los nodos y estado del supervisor.

## 4. Evidencias capturadas

| Archivo | Contenido |
|---|---|
| `01-flota-10-dispositivos.png` | lista de los diez dispositivos en la plataforma |
| `02-datos-crudos-rackc.png` | datos sin procesar del nodo Python SDK (30 s) |
| `03-datos-crudos-clima.png` | datos sin procesar del feed público (valor con marca de la fuente) |
| `04-panel-cuarto-de-control.png` | panel con identidad, KPIs, gráficos y alertas |
| `05-datos-crudos-racka-simulado.png` | datos del simulador nativo de la plantilla |
| `06-reglas-6-habilitadas.png` | las seis reglas en estado Habilitado |
| `07-flota-conexion-24sep.png` | lista de dispositivos al cierre del día |
| `logs/wokwi_rackb_serie.txt`, `logs/wokwi_agua_serie.txt` | monitor serie crudo de los dos ESP32, con reconexiones |

## 5. Incidencias resueltas durante el día

1. **DPS respondía 202 («assigning») y los sketches lo descartaban.** Se corrigió el firmware para
   sondear con el `operationId` hasta `assigned`; ambos ESP32 se registran ahora solos.
2. **Firma SAS mal codificada** en el cliente paho (percent-encoding asimétrico) → nodo de humo
   reconectando correctamente con token renovado.
3. **La sesión del navegador murió** y con ella el contenido de los dos proyectos Wokwi (viven solo
   en la pestaña). Se reconstruyeron desde los fuentes del repositorio y se automatizó el
   procedimiento (`docs/05-operacion.md`).
4. **Un script del portal navegó la pestaña del simulador** y destruyó el proyecto de agua. Se blindó
   la herramienta de automatización con pestaña fija (`pw.py --tab N`, `shot.py --tab N`).
5. **Formulario de reglas de la interfaz**: el nombre de la regla es un encabezado editable sin
   `aria-label`, y las acciones deben confirmarse con «Listo». Documentado para las próximas tandas.
6. **La tarea programada de Windows** (`schtasks`) está bloqueada por permisos en este equipo; el
   arranque y la vigilancia de la flota se hacen con procesos desprendidos (supervisor + watchdog).

## 6. Continuidad para los días 2 a 4

- **Supervisor** (8 nodos locales, reinicio automático) y **watchdog independiente** de Hermes
  (`tools/watchdog_win.py`, cada 10 min) corriendo desprendidos: la flota sigue publicando aunque se
  cierre la aplicación.
- **Dependencias de la máquina**: los nodos y los ESP32 virtuales corren en este equipo. Apagarlo o
  suspenderlo detiene 9 de los 10 orígenes (solo sobrevive el simulador nativo de la plataforma).
- **Pausa documentada** del nodo de humo: sábado 26 sep, 02:00–02:20 (hueco + reconexión).
- **Cierre previsto**: domingo 27 sep, comparativa de los cuatro días, evidencias finales y
  sustentación con los dos códigos en vivo.
