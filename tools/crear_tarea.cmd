@echo off
REM Crea (o reemplaza) la tarea que arranca la flota DC-ANDES-1 al iniciar sesion.
schtasks /Create /TN "DC-ANDES-1-Parcial1-IoT" /TR "cmd /c \"C:\Users\mvale\Documents\Parcial1_IoT_Central\tools\start_supervisor.cmd\"" /SC ONLOGON /F
if errorlevel 1 (
  echo FALLO al crear la tarea
  exit /b 1
)
echo tarea creada
schtasks /Run /TN "DC-ANDES-1-Parcial1-IoT"
echo tarea lanzada
