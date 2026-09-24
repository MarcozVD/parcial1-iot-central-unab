# Registra (y arranca) la tarea programada que mantiene viva la flota DC-ANDES-1
# durante la ventana de 4 dias del Parcial 1.
$ErrorActionPreference = 'Stop'
$accion = New-ScheduledTaskAction -Execute 'C:\Users\mvale\Documents\Parcial1_IoT_Central\tools\start_supervisor.cmd'
$disparo = New-ScheduledTaskTrigger -AtLogOn
$conf = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Days 0)
Register-ScheduledTask -TaskName 'DC-ANDES-1-Parcial1-IoT' -Action $accion -Trigger $disparo -Settings $conf -Description 'Flota IoT del Parcial 1 (DC-ANDES-1) - supervisor de nodos Python' -Force | Out-Null
Write-Output "tarea registrada"
Get-ScheduledTask -TaskName 'DC-ANDES-1-Parcial1-IoT' | Select-Object TaskName, State | Format-Table
Start-ScheduledTask -TaskName 'DC-ANDES-1-Parcial1-IoT'
Start-Sleep -Seconds 20
Get-ScheduledTask -TaskName 'DC-ANDES-1-Parcial1-IoT' | Select-Object TaskName, State | Format-Table
