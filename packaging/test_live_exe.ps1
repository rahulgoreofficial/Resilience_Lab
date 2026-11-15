# =====================================================================
# Test Live Standalone PyInstaller Executable
# =====================================================================
$ErrorActionPreference = "Stop"

$ExePath = "C:\DM\CP\dist\RESILIENCE_LAB\RESILIENCE_LAB.exe"
Write-Host "[*] Launching standalone executable in background..."
$Proc = Start-Process -FilePath $ExePath -ArgumentList "--no-browser" -PassThru

try {
    # Poll for health up to 15 seconds
    $healthy = $false
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Seconds 1
        try {
            $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -TimeoutSec 2
            if ($resp.status -eq "healthy") {
                $healthy = $true
                Write-Host "[+] Server is healthy!" -ForegroundColor Green
                Write-Host ("Response: " + ($resp | ConvertTo-Json -Compress))
                break
            }
        } catch {
            Write-Host "Waiting for server to become responsive... ($($i + 1)s)"
        }
    }

    if (-not $healthy) {
        Write-Error "Server failed to start or report health within 15 seconds."
    }

    # Test SPA catch-all routing (interactive-guide)
    Write-Host "[*] Testing SPA catch-all routing for /interactive-guide..."
    $htmlResp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/interactive-guide" -TimeoutSec 3
    if ($htmlResp.StatusCode -eq 200 -and $htmlResp.Content -match "RESILIENCE LAB") {
        Write-Host "[+] SPA Catch-all route returned index.html successfully!" -ForegroundColor Green
    } else {
        Write-Warning "[-] SPA Catch-all did not return expected index.html content."
    }

    # Test Scenarios API
    Write-Host "[*] Testing scenarios API..."
    $scenarios = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/resilience/scenarios" -TimeoutSec 3
    Write-Host ("[+] Scenarios returned: " + $scenarios.Count) -ForegroundColor Green

    # Test --status CLI
    Write-Host "[*] Testing --status CLI..."
    & $ExePath --status

} finally {
    Write-Host "[*] Stopping server via --stop CLI..."
    & $ExePath --stop
    Start-Sleep -Seconds 2
    if (-not $Proc.HasExited) {
        Write-Host "[*] Force terminating test process..."
        Stop-Process -Id $Proc.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[+] Test completed."
}

