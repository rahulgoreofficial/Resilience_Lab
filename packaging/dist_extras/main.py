"""
RESILIENCE LAB - Main Application Entry Point
Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator
"""

import sys
import subprocess
from pathlib import Path

cur_dir = Path(__file__).resolve().parent
exe_path = cur_dir / "RESILIENCE_LAB.exe"

if exe_path.exists():
    sys.exit(subprocess.call([str(exe_path)] + sys.argv[1:]))
else:
    # Source fallback
    sys.path.insert(0, str(cur_dir / "backend"))
    from packaging.launcher import run_launcher
    run_launcher()

