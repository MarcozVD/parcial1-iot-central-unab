#!/usr/bin/env bash
# deploy_remote.sh - Desplegar los 8 nodos Python en una máquina remota Ubuntu
# Uso:
#   bash tools/deploy_remote.sh <usuario>@<host> [<puerto_ssh>]
# Ejemplo:
#   bash tools/deploy_remote.sh ubuntu@52.252.133.127
#   bash tools/deploy_remote.sh ubuntu@52.252.133.127 2222

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Uso: $0 <usuario>@<host> [<puerto_ssh>]"
    exit 1
fi

REMOTE="$1"
SSH_PORT="${2:-22}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Desplegando flota DC-ANDES-1 en $REMOTE (puerto $SSH_PORT) ==="
echo

# 1. Crear carpeta remota y copiar código
REMOTE_DIR="/home/$(echo "$REMOTE" | cut -d@ -f1)/Parcial1_IoT_Central"
echo "1. Creando directorio remoto: $REMOTE_DIR"
ssh -p "$SSH_PORT" "$REMOTE" "mkdir -p '$REMOTE_DIR/{dispositivos/python,datos,logs,.secrets/env}'" || true

echo "2. Copiando código de los nodos Python..."
scp -P "$SSH_PORT" -r "$RAIZ/dispositivos/python/dc_*.py" "$REMOTE:$REMOTE_DIR/dispositivos/python/"

echo "3. Copiando credenciales..."
scp -P "$SSH_PORT" -r "$RAIZ/.secrets/env/"*.env "$REMOTE:$REMOTE_DIR/.secrets/env/" 2>/dev/null || {
    echo "   ADVERTENCIA: no hay .env en .secrets/env; usa tools/fetch_creds.py primero"
}

echo "4. Instalando dependencias en Ubuntu..."
ssh -p "$SSH_PORT" "$REMOTE" << 'SCRIPT'
set -euo pipefail
cd ~
python3 --version
if ! python3 -m pip list | grep -q paho-mqtt; then
    echo "   Instalando paho-mqtt..."
    python3 -m pip install --user paho-mqtt >/dev/null 2>&1 || sudo apt-get install -y python3-pip >/dev/null 2>&1 && python3 -m pip install paho-mqtt >/dev/null 2>&1
fi
if ! python3 -m pip list | grep -q requests; then
    echo "   Instalando requests..."
    python3 -m pip install --user requests >/dev/null 2>&1 || python3 -m pip install requests >/dev/null 2>&1
fi
echo "   Dependencias OK"
SCRIPT

echo
echo "5. Probando conectividad a un nodo remoto..."
ssh -p "$SSH_PORT" "$REMOTE" "cd '$REMOTE_DIR' && python3 dispositivos/python/dc_comun.py" 2>&1 | head -3 || echo "   (python3 ejecutado, output arriba)"

echo
echo "✅ Despliegue completado."
echo "   Próximo paso: ssh -p $SSH_PORT $REMOTE 'cd $REMOTE_DIR && nohup python3 dispositivos/python/dc_supervisor.py >/dev/null 2>&1 &'"
