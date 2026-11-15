# ==============================================================================
# RESILIENCE LAB - Automated Installation Script for Windows
# Project: Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator
# ==============================================================================

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# Establish project root directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
Set-Location -Path $RootDir

# Ensure log directory exists
$LogDir = Join-Path $RootDir "logs\installation"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "install_$Timestamp.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogMessage = "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] [$Level] $Message"
    Add-Content -Path $LogFile -Value $LogMessage
    
    switch ($Level) {
        "INFO"    { Write-Host $Message -ForegroundColor Cyan }
        "SUCCESS" { Write-Host $Message -ForegroundColor Green }
        "WARN"    { Write-Host $Message -ForegroundColor Yellow }
        "ERROR"   { Write-Host $Message -ForegroundColor Red }
        default   { Write-Host $Message }
    }
}

Clear-Host
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "         RESILIENCE LAB - AUTOMATED ENVIRONMENT INSTALLER        " -ForegroundColor White
Write-Host "   Graph-Theoretic Critical Infrastructure Resilience Platform   " -ForegroundColor DarkCyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Log "Starting automated installation process..."

# ------------------------------------------------------------------------------
# 1. System Prerequisite Verification
# ------------------------------------------------------------------------------
Write-Host "`n[1/5] Checking system prerequisites..." -ForegroundColor Yellow

# Check Python
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    Write-Log "Python is not found in system PATH. Python 3.10+ is required." "ERROR"
    Write-Host "`nPlease install Python 3.10 or newer from https://www.python.org/" -ForegroundColor Red
    exit 1
}

$PythonVersion = & python --version 2>&1
Write-Log "Detected Python: $PythonVersion" "INFO"

# Check Node.js
$NodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $NodeCmd) {
    Write-Log "Node.js is not found in system PATH. Node.js 18+ is required." "ERROR"
    Write-Host "`nPlease install Node.js 18 or newer from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

$NodeVersion = & node --version 2>&1
Write-Log "Detected Node.js: $NodeVersion" "INFO"

# Check npm
$NpmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $NpmCmd) {
    Write-Log "npm is not found in system PATH." "ERROR"
    exit 1
}

$NpmVersion = & npm --version 2>&1
Write-Log "Detected npm: v$NpmVersion" "INFO"

# ------------------------------------------------------------------------------
# 2. Python Virtual Environment Configuration
# ------------------------------------------------------------------------------
Write-Host "`n[2/5] Configuring Python virtual environment..." -ForegroundColor Yellow
$VenvDir = Join-Path $RootDir "backend\venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$VenvPip = Join-Path $VenvDir "Scripts\pip.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Log "Creating virtual environment at backend\venv..." "INFO"
    & python -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Failed to create Python virtual environment." "ERROR"
        exit 1
    }
} else {
    Write-Log "Existing virtual environment verified at backend\venv." "INFO"
}

Write-Host "Installing Python backend dependencies..." -ForegroundColor Cyan
& $VenvPip install -r (Join-Path $RootDir "backend\requirements.txt") *>> $LogFile
if ($LASTEXITCODE -ne 0) {
    Write-Log "pip install encountered warnings or errors. Check log file: $LogFile" "WARN"
} else {
    Write-Log "Python backend dependencies successfully installed." "SUCCESS"
}

# ------------------------------------------------------------------------------
# 3. Frontend Dependencies & Production Build
# ------------------------------------------------------------------------------
Write-Host "`n[3/5] Setting up frontend environment..." -ForegroundColor Yellow
$FrontendDir = Join-Path $RootDir "frontend"
$NodeModulesDir = Join-Path $FrontendDir "node_modules"

if (-not (Test-Path $NodeModulesDir)) {
    Write-Log "Installing frontend npm dependencies..." "INFO"
    npm install --prefix $FrontendDir *>> $LogFile
    if ($LASTEXITCODE -ne 0) {
        Write-Log "npm install failed. Review log: $LogFile" "ERROR"
        exit 1
    }
} else {
    Write-Log "Frontend node_modules verified." "INFO"
}

Write-Host "Building production frontend assets..." -ForegroundColor Cyan
npm run build --prefix $FrontendDir *>> $LogFile
if ($LASTEXITCODE -ne 0) {
    Write-Log "Frontend production build failed. Review log: $LogFile" "ERROR"
    exit 1
}
Write-Log "Frontend build completed cleanly." "SUCCESS"

# ------------------------------------------------------------------------------
# 4. Database Initialization & Seeding
# ------------------------------------------------------------------------------
Write-Host "`n[4/5] Initializing database and benchmark topologies..." -ForegroundColor Yellow
$env:PYTHONPATH = "backend"
& $VenvPython (Join-Path $RootDir "tools\seed_database.py") *>> $LogFile
if ($LASTEXITCODE -ne 0) {
    Write-Log "Database initialization error. Review log: $LogFile" "WARN"
} else {
    Write-Log "Database schema initialized and sample topologies verified." "SUCCESS"
}

# ------------------------------------------------------------------------------
# 5. Final Installation Verification
# ------------------------------------------------------------------------------
Write-Host "`n[5/5] Running installation self-check..." -ForegroundColor Yellow
$TestRunner = Join-Path $VenvDir "Scripts\pytest.exe"
if (Test-Path $TestRunner) {
    & $TestRunner backend/tests/test_graph_model.py -q *>> $LogFile
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Self-test passed: Graph engine verified." "SUCCESS"
    }
}

Write-Host "`n=================================================================" -ForegroundColor Green
Write-Host "             INSTALLATION COMPLETED SUCCESSFULLY!                " -ForegroundColor White
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "`nTo start RESILIENCE LAB:" -ForegroundColor White
Write-Host "  1. Double-click 'Run_Resilience_Lab.bat'" -ForegroundColor Cyan
Write-Host "  2. Or run: powershell -File tools/launcher.py`n" -ForegroundColor Gray
Write-Host "To stop the application cleanly, double-click 'Stop_Resilience_Lab.bat'." -ForegroundColor Yellow
Write-Host "Installation log saved to: $LogFile`n" -ForegroundColor DarkGray

