# =====================================================================
# RESILIENCE LAB - Standalone Executable Verification Script
# =====================================================================
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$DistDir = Join-Path $RootDir "dist\RESILIENCE_LAB"
$DistExe = Join-Path $DistDir "RESILIENCE_LAB.exe"
$InternalDir = Join-Path $DistDir "_internal"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  VERIFYING STANDALONE EXECUTABLE PAYLOAD                    " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Check main executable
if (-not (Test-Path $DistExe)) {
    Write-Error "[-] Main executable missing: $DistExe"
    exit 1
}
$ExeInfo = Get-Item $DistExe
Write-Host ("[+] Main Executable: {0} ({1:N2} MB)" -f $ExeInfo.FullName, ($ExeInfo.Length / 1MB)) -ForegroundColor Green

# 2. Check _internal directory
if (-not (Test-Path $InternalDir)) {
    Write-Error "[-] Dependency bundle missing: $InternalDir"
    exit 1
}
$FileCount = (Get-ChildItem -Path $InternalDir -Recurse -File).Count
Write-Host ("[+] Dependency Bundle: {0} files packaged in _internal" -f $FileCount) -ForegroundColor Green

# 3. Check bundled frontend assets
$FrontendIndex = Join-Path $InternalDir "frontend_dist\index.html"
if (-not (Test-Path $FrontendIndex)) {
    Write-Error "[-] Bundled frontend index missing: $FrontendIndex"
    exit 1
}
Write-Host "[+] Bundled Frontend: Verified ($FrontendIndex)" -ForegroundColor Green

# 4. Check bundled Alembic migrations
$AlembicIni = Join-Path $InternalDir "alembic.ini"
if (-not (Test-Path $AlembicIni)) {
    Write-Error "[-] Bundled alembic.ini missing: $AlembicIni"
    exit 1
}
Write-Host "[+] Bundled Alembic Config: Verified ($AlembicIni)" -ForegroundColor Green

# 5. Test CLI flags of the compiled executable
Write-Host "[*] Testing execution with --status flag..." -ForegroundColor Yellow
$StatusOutput = & $DistExe --status 2>&1 | Out-String
Write-Host $StatusOutput.Trim()
if ($LASTEXITCODE -ne 0) {
    Write-Error "[-] Execution failed with exit code $LASTEXITCODE"
    exit 1
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  STANDALONE EXECUTABLE VERIFICATION PASSED SUCCESSFULLY!    " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

