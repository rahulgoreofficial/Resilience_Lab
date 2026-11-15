$ErrorActionPreference = "Stop"

$exe = "C:\DM\CP\dist\RESILIENCE_LAB\RESILIENCE_LAB.exe"
Write-Host "Starting process: $exe"
$p = Start-Process -FilePath $exe -ArgumentList "--no-browser" -PassThru
Start-Sleep -Seconds 3

Write-Host "Process ID: $($p.Id)"
Write-Host "HasExited: $($p.HasExited)"
if ($p.HasExited) {
    Write-Host "ExitCode: $($p.ExitCode)"
} else {
    Write-Host "Process is RUNNING!"
    Stop-Process -Id $p.Id -Force
    Write-Host "Stopped process."
}

Write-Host "Recent application log entries:"
Get-Content -Tail 15 "$env:TEMP\RESILIENCE LAB\Logs\application.log"

