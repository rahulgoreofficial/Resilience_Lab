# RESILIENCE LAB — Windows Installer Build & Packaging Instructions

This document provides instructions for compiling and packaging the **RESILIENCE LAB** standalone Windows installer (`release/RESILIENCE_LAB_Setup.exe`) from source.

---

## 1. Build Environment Prerequisites

To reproduce the build from source on Windows:

1. **Operating System**: Microsoft Windows 10 or 11 (64-bit).
2. **Python**: Python 3.12+ (64-bit) with `pip` and virtual environment support.
3. **Node.js**: Node.js 18+ or 20+ (LTS) with `npm`.
4. **Inno Setup**: Inno Setup 6.3+ or 7.1+ (installed in `tools/inno_setup` or default Program Files directory).
5. **PowerShell**: Windows PowerShell 5.1 or PowerShell Core 7+.

---

## 2. Directory Layout of Packaging Infrastructure

```text
CP/
├── frontend/                     # React + Vite + Three.js application
│   ├── dist/                     # Production build artifacts (compiled by Vite)
│   └── package.json
├── backend/                      # FastAPI + SQLAlchemy + NetworkX backend
│   ├── app/                      # Application routes, models, algorithms
│   ├── alembic/                  # Database migration scripts
│   └── requirements.txt
├── packaging/                    # Standalone packaging configurations
│   ├── launcher.py               # Standalone desktop process controller & single-instance manager
│   ├── pyinstaller.spec          # PyInstaller onedir build specification
│   ├── build_frontend.ps1        # Automates Vite production compilation
│   ├── build_backend.ps1         # Runs pytest and builds PyInstaller dist
│   ├── verify_package.ps1        # Validates payload integrity and CLI flags
│   └── assets/app_icon.ico       # Multi-resolution application icon
├── installer/                    # Inno Setup installer infrastructure
│   ├── RESILIENCE_LAB.iss        # Inno Setup 7 Pascal script & wizard configuration
│   ├── build_installer.ps1       # Compiles Setup.exe, generates SHA256 & manifest
│   └── assets/app_icon.ico       # Installer wizard icon
├── tools/
│   └── inno_setup/ISCC.exe       # Inno Setup command-line compiler
└── release/                      # Final release distribution deliverables
    ├── RESILIENCE_LAB_Setup.exe  # Standalone Windows installer
    ├── BUILD_MANIFEST.md         # Detailed build provenance & metadata
    └── SHA256SUMS.txt            # Cryptographic checksums
```

---

## 3. Step-by-Step Build Pipeline

### Step 1: Build Production Frontend Assets
Compiles the React, TailwindCSS, and Three.js application into static distribution assets:
```powershell
powershell -ExecutionPolicy Bypass -File packaging/build_frontend.ps1
```
*Output*: Generates optimized static bundle in `frontend/dist/` (HTML, JS, CSS, assets).

### Step 2: Build Standalone Backend with PyInstaller
Executes all backend unit and regression tests, then invokes PyInstaller using `packaging/pyinstaller.spec`:
```powershell
powershell -ExecutionPolicy Bypass -File packaging/build_backend.ps1
```
*Output*: Generates standalone folder in `dist/RESILIENCE_LAB/` containing:
- `RESILIENCE_LAB.exe` (launcher binary)
- `_internal/` (Python runtime, compiled C-extensions, dependencies, alembic scripts, frontend static files)

### Step 3: Verify the Standalone Payload
Verifies that all binaries, DLLs, Alembic configs, and static assets exist and tests the executable CLI:
```powershell
powershell -ExecutionPolicy Bypass -File packaging/verify_package.ps1
```

### Step 4: Compile Inno Setup Windows Installer
Compiles `installer/RESILIENCE_LAB.iss` with LZMA2/Ultra64 solid compression, computes SHA256 checksums, and records the build manifest:
```powershell
powershell -ExecutionPolicy Bypass -File installer/build_installer.ps1
```
*Output*: Creates `release/RESILIENCE_LAB_Setup.exe`, `release/SHA256SUMS.txt`, and `release/BUILD_MANIFEST.md`.

---

## 4. One-Click Complete Build Pipeline

To execute all build steps in sequence:

```powershell
# Run complete end-to-end build
powershell -ExecutionPolicy Bypass -File packaging/build_frontend.ps1
powershell -ExecutionPolicy Bypass -File packaging/build_backend.ps1
powershell -ExecutionPolicy Bypass -File packaging/verify_package.ps1
powershell -ExecutionPolicy Bypass -File installer/build_installer.ps1
```

---

## 5. Clean / Rebuild Commands

To perform a clean rebuild from scratch:
```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build, dist, release
```
Then rerun the steps above.

