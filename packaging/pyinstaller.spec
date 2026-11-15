# -*- mode: python ; coding: utf-8 -*-
"""
RESILIENCE LAB - PyInstaller Specification File
Target: Windows 10/11 x64 Standalone Onedir Distribution
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

SPEC_DIR = Path(SPECPATH).resolve() if "SPECPATH" in globals() else Path("packaging").resolve()
ROOT_DIR = SPEC_DIR.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"
ALEMBIC_DIR = BACKEND_DIR / "alembic"
DATASETS_DIR = ROOT_DIR / "datasets"
ICON_PATH = ROOT_DIR / "installer" / "assets" / "app_icon.ico"

# Collect hidden imports for dynamic modules
hiddenimports = [
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "fastapi",
    "fastapi.staticfiles",
    "fastapi.responses",
    "starlette",
    "starlette.routing",
    "starlette.middleware",
    "starlette.middleware.cors",
    "starlette.staticfiles",
    "starlette.responses",
    "sqlalchemy",
    "sqlalchemy.dialects.sqlite",
    "alembic",
    "alembic.config",
    "alembic.script",
    "networkx",
    "numpy",
    "pandas",
    "pydantic",
    "pydantic_settings",
    "websockets",
    "sqlite3",
]

# Collect all project internal submodules
hiddenimports += collect_submodules("app")

# Collect data files
datas = []

# Include compiled React frontend
if FRONTEND_DIST.exists():
    datas.append((str(FRONTEND_DIST), "frontend_dist"))

# Include Alembic migration files
if ALEMBIC_DIR.exists():
    datas.append((str(ALEMBIC_DIR), "alembic"))
if (BACKEND_DIR / "alembic.ini").exists():
    datas.append((str(BACKEND_DIR / "alembic.ini"), "."))

# Include sample datasets if present
if DATASETS_DIR.exists():
    datas.append((str(DATASETS_DIR), "datasets"))

# Include application icon
if ICON_PATH.exists():
    datas.append((str(ICON_PATH), "."))

# Include app package data
datas += collect_data_files("app")

block_cipher = None

a = Analysis(
    [str(SPEC_DIR / "launcher.py")],
    pathex=[str(BACKEND_DIR), str(ROOT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "pytest",
        "unittest",
        "IPython",
        "notebook",
        "sphinx"
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="RESILIENCE_LAB",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON_PATH) if ICON_PATH.exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="RESILIENCE_LAB",
)
