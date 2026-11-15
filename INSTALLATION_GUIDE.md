# RESILIENCE LAB — Windows Installation Guide

**Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator**  
*Release Version 1.0.0 — Standalone Windows Distribution*

---

## 1. System Requirements

### Hardware Requirements
- **Processor**: 64-bit Intel / AMD dual-core processor (x86-64 / AMD64), 2.0 GHz or higher.
- **Memory (RAM)**: Minimum 4 GB RAM (8 GB recommended for complex 1,000+ node simulations).
- **Storage**: Minimum 1 GB available free storage space.
- **Display**: 1366 × 768 minimum resolution (1920 × 1080 Full HD recommended).
- **Graphics**: WebGL-compatible GPU (integrated or discrete) for interactive 3D Three.js rendering.

### Software Requirements
- **Operating System**: Microsoft Windows 10 (64-bit) or Windows 11 (64-bit).
- **Web Browser**: Google Chrome, Microsoft Edge, Mozilla Firefox, or Brave (modern Chromium / Gecko browser with WebGL 2.0 and WebSocket support).
- **Prerequisites**: **None**. RESILIENCE LAB is 100% self-contained. You do **not** need Python, Node.js, npm, Docker, PostgreSQL, or Visual Studio installed.

---

## 2. Installation Walkthrough

### Step 1: Obtain the Installer
Download `RESILIENCE_LAB_Setup.exe` from the official repository release channel.  
Verify the SHA256 integrity checksum against `release/SHA256SUMS.txt`.

### Step 2: Run Setup
Double-click `RESILIENCE_LAB_Setup.exe`.
> **Note**: Administrative elevation (UAC prompt) is **not required**. The installer installs per-user by default, allowing standard users without admin privileges to install and run the software.

### Step 3: Choose Destination Directory
The default installation directory is:
```text
%LOCALAPPDATA%\Programs\RESILIENCE LAB
(e.g., C:\Users\<Username>\AppData\Local\Programs\RESILIENCE LAB)
```
You may accept the default or browse to custom directory where you have write permissions.

### Step 4: Desktop Shortcut
Check the **"Create a desktop shortcut"** option if you wish to launch RESILIENCE LAB directly from your desktop.

### Step 5: Install & Complete
Click **Install**. The setup program will extract and configure all backend engines, frontend assets, database migrations, and shortcuts.  
On the final screen, keep **"Launch RESILIENCE LAB"** checked and click **Finish**.

---

## 3. Directory Layout & Storage

The application separates executable program binaries from persistent user data and log files:

| Component | Default File System Path | Purpose |
| :--- | :--- | :--- |
| **Program Files** | `%LOCALAPPDATA%\Programs\RESILIENCE LAB\` | Executable binaries, Python runtime, frontend assets, libraries. |
| **User Database** | `%LOCALAPPDATA%\RESILIENCE LAB\Data\resilience_lab.db` | Persistent SQLite database containing saved topologies and simulation runs. |
| **Application Logs** | `%LOCALAPPDATA%\RESILIENCE LAB\Logs\application.log` | Rotating operational logs (up to 5 MB per file, 3 backups). |

---

## 4. Installed Shortcuts

The installer creates the following shortcuts in your Windows Start Menu under **RESILIENCE LAB**:

1. **RESILIENCE LAB**  
   Starts the backend background service, binds to the primary loopback port (`8000`), performs database schema checks, and opens your default browser to `http://localhost:8000`. If an instance is already running, it brings the existing instance into view.
2. **Stop RESILIENCE LAB**  
   Gracefully shuts down any running background instance and releases all loopback sockets.
3. **View Application Logs**  
   Opens Windows Explorer directly to the logs folder (`%LOCALAPPDATA%\RESILIENCE LAB\Logs`).
4. **Open Database Storage**  
   Opens Windows Explorer directly to the database folder (`%LOCALAPPDATA%\RESILIENCE LAB\Data`).
5. **Uninstall RESILIENCE LAB**  
   Launches the clean uninstaller.

---

## 5. Silent / Unattended Installation (IT Deployments)

For automated or enterprise IT deployment across multiple workstations:

```powershell
# Silent install for the current user into default directory
RESILIENCE_LAB_Setup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART

# Silent install into custom directory
RESILIENCE_LAB_Setup.exe /VERYSILENT /DIR="D:\Tools\RESILIENCE_LAB"
```

---

## 6. Troubleshooting & Diagnostics

### Port 8000 in Use
If port 8000 is occupied by another application, RESILIENCE LAB automatically scans and binds to the next available loopback port (`8001`, `8002`, etc.) and launches your browser with the correct active port.

### Stopping Background Process
If the browser was closed but the background service is still running:
- Run the **Stop RESILIENCE LAB** shortcut from the Start Menu, or
- Run via PowerShell:
  ```powershell
  & "$env:LOCALAPPDATA\Programs\RESILIENCE LAB\RESILIENCE_LAB.exe" --stop
  ```

### Inspecting Logs
To review errors or debug logs:
```powershell
Get-Content -Tail 50 -Wait "$env:LOCALAPPDATA\RESILIENCE LAB\Logs\application.log"
```
