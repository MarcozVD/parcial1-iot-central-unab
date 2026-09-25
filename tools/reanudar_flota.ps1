# Reanuda la flota DC-ANDES-1 tras apagar o suspender la maquina.
# Uso:  powershell -NoProfile -File tools\reanudar_flota.ps1
$raiz = "C:\Users\mvale\Documents\Parcial1_IoT_Central"
$py = "$raiz\.venv\Scripts\python.exe"

# quitar la bandera de pausa: a partir de aqui los watchdogs vuelven a vigilar
$pausa = "$raiz\logs\PAUSA_FLOTA"
if (Test-Path $pausa) {
    Remove-Item $pausa -Force
    Write-Host "pausa levantada (logs\PAUSA_FLOTA eliminado)."
}

# --- supervisor (8 nodos locales) ---
$sup = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like "*dc_supervisor*" }
if ($sup) {
    Write-Host "Supervisor ya en ejecucion (pid $($sup.ProcessId)). Nada que arrancar."
} else {
    Start-Process -FilePath $py -ArgumentList "$raiz\dispositivos\python\dc_supervisor.py" `
        -WorkingDirectory "$raiz\dispositivos\python" -WindowStyle Hidden
    Write-Host "Supervisor arrancado (8 nodos en ~20 s)."
}

# --- watchdog independiente ---
$wd = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like "*watchdog_win*" }
if ($wd) {
    Write-Host "Watchdog ya en ejecucion (pid $($wd.ProcessId))."
} else {
    Start-Process -FilePath $py -ArgumentList "$raiz\tools\watchdog_win.py" `
        -WorkingDirectory $raiz -WindowStyle Hidden
    Write-Host "Watchdog arrancado (revisa cada 10 min)."
}

Start-Sleep -Seconds 6
Write-Host ""
Write-Host "Estado de los nodos locales:"
& $py "$raiz\tools\watchdog_win.py" --una-vez
Write-Host ""
Write-Host "Si el navegador se cerro, reconstruye los dos ESP32 virtuales: docs\05-operacion.md"
