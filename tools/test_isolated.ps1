$ErrorActionPreference = "Stop"

$src = "C:\DM\CP\dist\RESILIENCE_LAB"
$dst = "C:\Users\Rahul Gore\AppData\Local\Temp\test_isolated_lab"

if (Test-Path $dst) {
    Remove-Item -Recurse -Force $dst
}

Write-Host "Copying packaged distribution to isolated directory: $dst"
Copy-Item -Path $src -Destination $dst -Recurse

Write-Host "Contents of root directory:"
Get-ChildItem -Path $dst | Select-Object Name, Length

Set-Location $dst
Write-Host "Testing --status CLI:"
$p = Start-Process -FilePath ".\RESILIENCE_LAB.exe" -ArgumentList "--status" -Wait -PassThru -NoNewWindow
Write-Host "ExitCode: $($p.ExitCode)"

