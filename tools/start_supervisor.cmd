@echo off
REM Arranca el supervisor de la flota DC-ANDES-1 (Parcial 1 IoT, UNAB).
REM Se registra como tarea programada "DC-ANDES-1 Parcial1 IoT" (al iniciar sesion).
cd /d "C:\Users\mvale\Documents\Parcial1_IoT_Central\dispositivos\python"
"C:\Users\mvale\Documents\Parcial1_IoT_Central\.venv\Scripts\python.exe" "dc_supervisor.py" >> "C:\Users\mvale\Documents\Parcial1_IoT_Central\logs\supervisor.out" 2>&1
