@echo off
REM Protocolo del Parcial 1: el usuario dice "inicia" (maquina ya encendida) -> flota de nuevo en marcha.
REM Uso: doble clic o  tools\INICIAR.cmd
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0reanudar_flota.ps1"
echo.
echo FLOTA EN MARCHA. Si el navegador se cerro, reconstruye los dos ESP32 (docs\05-operacion.md).
pause
