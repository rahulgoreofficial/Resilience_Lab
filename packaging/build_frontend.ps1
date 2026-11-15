# =====================================================================
# RESILIENCE LAB - Frontend Production Asset Builder
# =====================================================================
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$FrontendDir = Join-Path $RootDir "frontend"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  BUILDING PRODUCTION FRONTEND DISTRIBUTION (Vite + React) " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Set-Location $FrontendDir

Write-Host "[*] Executing: npm run build" -ForegroundColor Yellow
npm run build

$DistIndex = Join-Path $FrontendDir "dist\index.html"
if (-not (Test-Path $DistIndex)) {
    Write-Error "[-] Build failed: dist\index.html not found!"
    exit 1
}

Write-Host "[+] Frontend build verified successfully: $DistIndex" -ForegroundColor Green

