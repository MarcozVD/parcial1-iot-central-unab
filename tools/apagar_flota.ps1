# Detiene limpiamente la flota scriptada del DC-ANDES-1 antes de apagar o suspender la maquina.
# Uso:  powershell -NoProfile -File tools\apagar_flota.ps1
$raiz = "C:\Users\mvale\Documents\Parcial1_IoT_Central"
$detenidos = 0

# bandera de pausa: los watchdogs (Hermes y Windows) no reaniman la flota mientras exista
$pausa = "$raiz\logs\PAUSA_FLOTA"
"pausa manual $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $pausa -Encoding utf8
Write-Host "pausa marcada en logs\PAUSA_FLOTA (los watchdogs no relanzaran la flota)"

# nodos + supervisor + watchdog: se identifican por linea de comandos del proyecto
$procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object {
    $_.CommandLine -like "*Parcial1_IoT_Central*" -and
    ($_.CommandLine -like "*dc_supervisor*" -or $_.CommandLine -like "*watchdog_win*" -or
     $_.CommandLine -like "*dispositivos\python\dc_*" -or $_.CommandLine -like "*dispositivos/python/dc_*")
}
foreach ($p in $procs) {
    try {
        Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop
        Write-Host ("detenido pid {0}  {1}" -f $p.ProcessId, ($p.CommandLine -replace '^.*[\\/]', ''))
        $detenidos++
    } catch {
        Write-Host ("no se pudo detener pid {0}: {1}" -f $p.ProcessId, $_.Exception.Message)
    }
}
Write-Host ""
Write-Host "procesos detenidos: $detenidos"
"FIN     $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  procesos detenidos: $detenidos" |
    Out-File -FilePath "$raiz\logs\flota_sesiones.log" -Append -Encoding utf8
Write-Host "Los datos ya publicados quedan en Azure IoT Central; los ESP32 virtuales se reconstruyen con docs\05-operacion.md"
