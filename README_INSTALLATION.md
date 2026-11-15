# RESILIENCE LAB — Windows Installation Quick Start

Welcome to **RESILIENCE LAB** (Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator).

This package provides a standalone Windows executable installer that allows you to install and run the complete RESILIENCE LAB platform on Windows 10 and Windows 11 without configuring any development environment.

---

## Quick Start (3 Steps)

1. **Download**: Locate `release/RESILIENCE_LAB_Setup.exe`.
2. **Install**: Double-click `RESILIENCE_LAB_Setup.exe` to start the setup wizard.
   - Standard user installation (No Administrator UAC prompt needed).
   - Default install path: `%LOCALAPPDATA%\Programs\RESILIENCE LAB`.
   - Optionally choose to create a Desktop shortcut.
3. **Launch**: Click **Finish** with "Launch RESILIENCE LAB" checked.
   - Your default web browser will open automatically to `http://localhost:8000`.

---

## What is Included?

The standalone package embeds all necessary components:
- **FastAPI / Python 3.12 Engine**: High-performance asynchronous backend and graph theory analysis engine.
- **Algorithms Library**: NetworkX, SciPy, and NumPy for computing Betweenness Centrality, Articulation Points, Bridging Centrality, Percolation Thresholds, and Cascading Failure Simulation.
- **React 18 / Three.js Frontend**: Interactive 3D topology visualizer, interactive failure simulations, design canvas, and real-time dashboard.
- **Embedded Database**: Local SQLite storage engine pre-configured for persistent network models and simulation runs.
- **Automatic Migration**: Database tables are automatically managed; no SQL server installation or configuration is required.

---

## Command-Line Usage & Shortcuts

The installer creates the following shortcuts in your Windows Start Menu:
- **RESILIENCE LAB**: Launches the application and opens the web interface.
- **Stop RESILIENCE LAB**: Shuts down any running background server instance.
- **View Application Logs**: Opens `%LOCALAPPDATA%\RESILIENCE LAB\Logs`.
- **Open Database Storage**: Opens `%LOCALAPPDATA%\RESILIENCE LAB\Data`.
- **Uninstall RESILIENCE LAB**: Runs the clean uninstaller.

You can also run the binary from PowerShell:
```powershell
& "$env:LOCALAPPDATA\Programs\RESILIENCE LAB\RESILIENCE_LAB.exe" --status
& "$env:LOCALAPPDATA\Programs\RESILIENCE LAB\RESILIENCE_LAB.exe" --stop
```

---

## Documentation Links

- Detailed Installation Guide: [INSTALLATION_GUIDE.md](file:///C:/DM/CP/INSTALLATION_GUIDE.md)
- Uninstallation Guide: [UNINSTALLATION_GUIDE.md](file:///C:/DM/CP/UNINSTALLATION_GUIDE.md)
- Build From Source Instructions: [BUILD_INSTRUCTIONS.md](file:///C:/DM/CP/BUILD_INSTRUCTIONS.md)
- Build Manifest & Checksums: [BUILD_MANIFEST.md](file:///C:/DM/CP/release/BUILD_MANIFEST.md)

