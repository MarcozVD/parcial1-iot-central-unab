# Bitácora - Día 2 (25 de septiembre de 2026)

## Resumen
- **Fecha:** 25 de septiembre de 2026
- **Duración:** ~4 h 20 min (15:40 → 20:00)
- **Origen de datos:** 8 nodos Python corriendo en **máquina remota Ubuntu** (52.252.133.127), publicando a Azure IoT Central
- **Estado:** ✅ 8/8 nodos vivos al cierre

## Cambios arquitectónicos
1. **Migración a ejecución remota:** Los 8 nodos Python se trasladaron de Windows local a Ubuntu remoto
   - Código: `dispositivos/python/dc_paho.py` sin cambios
   - Credenciales: copiadas via SCP a `~mvale/Parcial1_IoT_Central/.secrets/env/`
   - Dependencias: `paho-mqtt` + `requests` instaladas en venv (`~/venv_parcial`)

2. **Supervisor remoto:** Nuevo script `dc_supervisor_remote.py` (Linux-only, sin PowerShell)
   - Replemplaza al supervisor Windows
   - Usa `pgrep -f` en lugar de PowerShell para detectar procesos muertos
   - Vigilancia cada 30 s; relanza los nodos que caigan
   - Logs por nodo en `logs/DC-*.log` (stdout + stderr)

3. **Despliegue:** Herramientas nuevas de apoyo
   - `tools/deploy_remote.sh` — desplegador de código + creds + dependencias (bash)
   - `tools/remote_ssh.py` — ejecutor de comandos SSH con auto-detección de llaves

## Ventana de datos recogida
Comenzó a las 15:40 (UTC-05:00 = Bogotá):

| Nodo | Intervalo | Observaciones |
|---|---|---|
| DC-RACKC-03 | 30 s | Rack C, temperatura + humedad relativa |
| DC-HUMO-08 | 45 s | Detectores de humo (múltiples) |
| DC-PASILLO-04 | 60 s | Pasillo principal |
| DC-CLIMA-05 | 15 min | Datos climáticos (OpenMeteo) |
| DC-AIRE-06 | 15 min | Calidad del aire (API de tercero) |
| DC-ENERGIA-09 | 2 min | Consumo eléctrico |
| DC-ACCESO-10 | 2 min | Eventos de acceso (simulado) |
| DC-AGUA-07 | 30 s | Detección de fugas + humedad piso |

**Estado al cierre (20:00):** Todos en vivo, publicando normalmente.

## Verificaciones realizadas
- ✅ Conectividad SSH a Ubuntu (usuario `mvale`, llave `iot_key.pem` de Downloads)
- ✅ Imports de Python en remoto (dc_comun, dc_paho, paho-mqtt, requests)
- ✅ Creación de venv y instalación de dependencias
- ✅ DPS enrollment correcto (rc=0 en HUB)
- ✅ Propiedades reportadas correctas (zona, ubicación, modelo, firmware, intervalo)
- ✅ Supervisor lanzando/vigilando todos los nodos (pgrep funciona)
- ✅ Nodos sin caidas en los últimos ~5 min antes del cierre

## Próximas fechas
Fechas ya cubiertas: **24 sep** (~6 h) y **25 sep** (~4.5 h).
Faltan: **2 más de 4 fechas requeridas** (puede ser 26, 27 u otras).

## Notas técnicas
- **Cobertura real de esta fecha (revisada el 26-sep):** la flota **local** publicó los 7 dispositivos de
  15:37 a 23:59 (8 h 22 min, 2 904 filas), así que la fecha está cubierta de sobra. Además, el supervisor
  remoto (que tenía el fallo de diseño descrito abajo) publicó **solo DC-HUMO-08** entre 15:52 y 18:36
  (1 737 filas infladas por el bucle de reconexión). Durante esa franja el nodo de humo tuvo dos
  publicadores simultáneos: sus filas están intercaladas y así queda anotado.
- **Corrección posterior (26-sep):** el supervisor remoto lanzaba los nodos con el dispositivo como
  argumento, cuando en realidad cada script tiene su `DEVICE_ID` fijo y no lee argumentos. Ese fue el
  motivo de que el 25-sep el lado remoto solo alimentara el nodo de humo. Documentado en
  `docs/bitacora-dia-3.md`. El archivo se conserva tal cual para dejar rastro del fallo.
- Windows local mantiene los 2 ESP32 virtuales (Wokwi) y el simulador nativo en Azure
- Ubuntu remoto hostea los 8 nodos Python (los más voluminosos en datos)
- Panel + reglas + plantilla siguen igual en Azure IoT Central
- Copia de seguridad del repo en OneDrive (verificada, sin credenciales)
- Commits: 4 nuevos (supervisor remoto, despliegue, herramientas SSH)
