@echo off
REM Protocolo del Parcial 1: el usuario dice "para" -> se detiene la flota y se avisa.
REM Uso: doble clic o  tools\PARAR.cmd
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0apagar_flota.ps1"
echo.
echo YA PUEDES DETENER LA MAQUINA (flota detenida; bandera de pausa activa).
pause
