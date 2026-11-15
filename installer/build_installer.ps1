# =====================================================================
# RESILIENCE LAB - Inno Setup 7 Windows Installer Compiler
# =====================================================================
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$InstallerDir = $ScriptDir
$IssFile = Join-Path $InstallerDir "RESILIENCE_LAB.iss"
$ReleaseDir = Join-Path $RootDir "release"
$SetupExe = Join-Path $ReleaseDir "RESILIENCE_LAB_Setup.exe"

# Search for ISCC.exe
$IsccCandidates = @(
    (Join-Path $RootDir "tools\inno_setup\ISCC.exe"),
    "${env:ProgramFiles(x86)}\Inno Setup 7\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 7\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)

$IsccPath = $null
foreach ($candidate in $IsccCandidates) {
    if (Test-Path $candidate) {
        $IsccPath = $candidate
        break
    }
}

if (-not $IsccPath) {
    $Command = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
    if ($Command) {
        $IsccPath = $Command.Source
    }
}

if (-not $IsccPath) {
    Write-Error "[-] Inno Setup Compiler (ISCC.exe) not found!"
    exit 1
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  COMPILING RESILIENCE LAB STANDALONE INSTALLER             " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "[+] Using Inno Setup Compiler: $IsccPath" -ForegroundColor Green

if (-not (Test-Path $ReleaseDir)) {
    New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
}

# Compile with Inno Setup
Write-Host "[*] Compiling installer script: $IssFile" -ForegroundColor Yellow
& $IsccPath $IssFile
if ($LASTEXITCODE -ne 0) {
    Write-Error "[-] Inno Setup compilation failed with exit code $LASTEXITCODE"
    exit 1
}

if (-not (Test-Path $SetupExe)) {
    Write-Error "[-] Setup executable not generated at: $SetupExe"
    exit 1
}

$SetupItem = Get-Item $SetupExe
$SetupSizeMB = [math]::Round(($SetupItem.Length / 1MB), 2)
Write-Host ("[+] Installer generated successfully: {0} ({1:N2} MB)" -f $SetupExe, $SetupSizeMB) -ForegroundColor Green

# Compute SHA256 checksums for release directory using Python helper
$PyExe = Join-Path $RootDir "backend\venv\Scripts\python.exe"
if (Test-Path $PyExe) {
    Write-Host "[*] Updating SHA256 checksums and build manifest..." -ForegroundColor Yellow
    & $PyExe -c "
import hashlib
from pathlib import Path
from datetime import datetime

release_dir = Path('release')
entries = []
setup_size_mb = 0
setup_hash = ''
setup_bytes = 0

for p in sorted(release_dir.iterdir()):
    if p.is_file() and p.name != 'SHA256SUMS.txt':
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        entries.append(f'{h}  {p.name}')
        if p.name == 'RESILIENCE_LAB_Setup.exe':
            setup_hash = h
            setup_bytes = p.stat().st_size
            setup_size_mb = round(setup_bytes / (1024 * 1024), 2)

(release_dir / 'SHA256SUMS.txt').write_text('\n'.join(entries) + '\n', encoding='utf-8')

manifest_text = f'''# RESILIENCE LAB — Windows Installer Build Manifest

- **Application Name**: RESILIENCE LAB
- **Product Title**: Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator
- **Version**: 1.0.0
- **Installer Executable**: `RESILIENCE_LAB_Setup.exe`
- **Output Directory**: `release/`
- **File Size**: {setup_size_mb} MB ({setup_bytes} bytes)
- **SHA256 Checksum**: `{setup_hash}`
- **Build Timestamp**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
- **Target OS**: Microsoft Windows 10 / Windows 11 (64-bit x64)
- **Packaging Engine**: PyInstaller 6.22.3 (onedir, console enabled)
- **Setup Compiler**: Inno Setup 7.1.1
- **Compression**: LZMA2 / Ultra64 Solid Compression
- **Frontend Stack**: React 18, Vite, Three.js / React Three Fiber, TailwindCSS
- **Backend Stack**: FastAPI, Uvicorn, SQLAlchemy, Alembic, SQLite, NetworkX, NumPy, SciPy
- **Database Engine**: Embedded SQLite (%LOCALAPPDATA%\\RESILIENCE LAB\\Data\\resilience_lab.db)
- **Included Root Files**: RESILIENCE_LAB.exe, Run_Resilience_Lab.bat, Stop_Resilience_Lab.bat, main.py, README.txt, manuals
'''
(release_dir / 'BUILD_MANIFEST.md').write_text(manifest_text, encoding='utf-8')
print('[+] Manifest and SHA256SUMS.txt successfully updated.')
print(f'    SHA256: {setup_hash}')
"
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  INSTALLER BUILD COMPLETED SUCCESSFULLY!                   " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
