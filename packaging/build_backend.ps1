# =====================================================================
# RESILIENCE LAB - Backend PyInstaller Packager
# =====================================================================
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $RootDir "backend"
$PythonExe = Join-Path $BackendDir "venv\Scripts\python.exe"
$PyInstallerExe = Join-Path $BackendDir "venv\Scripts\pyinstaller.exe"
$SpecFile = Join-Path $ScriptDir "pyinstaller.spec"
$DistExe = Join-Path $RootDir "dist\RESILIENCE_LAB\RESILIENCE_LAB.exe"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  BUILDING STANDALONE BACKEND WITH PYINSTALLER (onedir)     " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (-not (Test-Path $PythonExe)) {
    Write-Error "[-] Python virtual environment not found at: $PythonExe"
    exit 1
}

# 1. Run Unit Tests to ensure stability
Write-Host "[*] Executing Backend Unit Tests..." -ForegroundColor Yellow
Set-Location $RootDir
& $PythonExe -m pytest backend/tests -v --disable-warnings -q
if ($LASTEXITCODE -ne 0) {
    Write-Error "[-] Backend tests failed! Aborting packaging."
    exit 1
}
Write-Host "[+] All backend unit tests passed." -ForegroundColor Green

# 2. Run PyInstaller
Write-Host "[*] Executing PyInstaller with spec: $SpecFile" -ForegroundColor Yellow
& $PyInstallerExe $SpecFile --noconfirm --clean

if (-not (Test-Path $DistExe)) {
    Write-Error "[-] PyInstaller build failed: $DistExe not found!"
    exit 1
}

$ExeSize = (Get-Item $DistExe).Length / 1MB
Write-Host ("[+] Backend standalone package created successfully: {0} ({1:N2} MB)" -f $DistExe, $ExeSize) -ForegroundColor Green

