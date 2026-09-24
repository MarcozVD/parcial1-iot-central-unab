#!/usr/bin/env bash
# Crea la flota de 10 dispositivos del Parcial 1 en IoT Central (app dcandes1unab).
# Uso: bash tools/crear_flota.sh
set -e
export PATH="/c/Program Files/Microsoft SDKs/Azure/CLI2/wbin:$PATH"
APP="dcandes1unab"
TPL="dtmi:unab:dcandes:dcAndesNodo;1"

crear() {  # id | nombre | simulado?
  local id="$1" nombre="$2" sim="$3"
  if [ "$sim" = "sim" ]; then
    az iot central device create --app-id "$APP" -d "$id" --device-name "$nombre" --template "$TPL" --simulated -o none
  else
    az iot central device create --app-id "$APP" -d "$id" --device-name "$nombre" --template "$TPL" -o none
  fi
  echo "  + $id  ($nombre)"
}

crear "DC-RACKA-01"   "Rack A - Nodo ambiental (simulador nativo)"  sim
crear "DC-RACKB-02"   "Rack B - Nodo ambiental (Wokwi ESP32 #1)"   no
crear "DC-RACKC-03"   "Rack C - Nodo ambiental (Python SDK MQTT)"   no
crear "DC-PASILLO-04" "Pasillo frio / contencion (Python SDK AMQP)" no
crear "DC-CLIMA-05"   "Estacion exterior free-cooling (Open-Meteo)" no
crear "DC-AIRE-06"    "Calidad de aire de sala (IDEAM/datos.gov.co)" no
crear "DC-AGUA-07"    "Deteccion de agua bajo piso (Wokwi ESP32 #2)" no
crear "DC-HUMO-08"    "Deteccion de humo / incendio (paho MQTT)"    no
crear "DC-ENERGIA-09" "PDU / energia de fila (replay CSV)"          no
crear "DC-ACCESO-10"  "Puerta / control de acceso (puente HTTP)"    no

echo "--- flota creada ---"
az iot central device list --app-id "$APP" -o json > "$HOME/Documents/Parcial1_IoT_Central/logs/flota.json"
