# RESILIENCE LAB — Troubleshooting & Diagnostic Guide

**Software Title:** Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator  
**Version:** 1.0.0 Production Release  

---

## 1. Installation & Environment Issues

### Issue 1.1: "Python is not recognized as an internal or external command"
- **Symptom:** Running `Install_Resilience_Lab.bat` or `python` yields a command not found error in Command Prompt.
- **Root Cause:** Python was installed without checking "Add Python to PATH" in the Windows installer.
- **Resolution:**
  1. Re-run Python installer from [python.org](https://www.python.org/).
  2. Select **Modify**, check **Add Python to environment variables**, and complete setup.
  3. Restart Command Prompt or PowerShell.

### Issue 1.2: "Execution of scripts is disabled on this system"
- **Symptom:** PowerShell blocks `install_windows.ps1` with a `PSSecurityException`.
- **Root Cause:** Default Windows client execution policy restricts unsigned PowerShell scripts.
- **Resolution:**
  `Install_Resilience_Lab.bat` automatically invokes PowerShell with `-ExecutionPolicy Bypass`. If running PowerShell manually, run:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\tools\install_windows.ps1
  ```

### Issue 1.3: "npm install fails with EPERM / operation not permitted"
- **Symptom:** Frontend dependency installation aborts with `EPERM: operation not permitted, mkdir...`
- **Root Cause:** Windows file indexing, active antivirus scanners, or background file locks in `frontend/node_modules`.
- **Resolution:**
  1. Close any running IDEs or editors editing `frontend/`.
  2. Delete `frontend/node_modules` and `frontend/package-lock.json`.
  3. Re-run:
     ```powershell
     cd frontend
     npm cache clean --force
     npm install
     ```

---

## 2. Application Launch & Port Conflicts

### Issue 2.1: "Port 8000 or Port 5173 is already in use"
- **Symptom:** Launcher terminates reporting that port 8000 (Backend) or port 5173 (Frontend) is occupied.
- **Root Cause:** A previous session of Uvicorn, Vite, or another web server is still holding the TCP port.
- **Resolution:**
  1. Double-click `Stop_Resilience_Lab.bat`.
  2. If the port remains locked, identify and terminate the orphan process in PowerShell:
     ```powershell
     # Find PID on port 8000:
     Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
     Stop-Process -Id <PID> -Force
     
     # Find PID on port 5173:
     Get-NetTCPConnection -LocalPort 5173 | Select-Object OwningProcess
     Stop-Process -Id <PID> -Force
     ```

### Issue 2.2: "Backend health check timed out"
- **Symptom:** `launcher.py` displays `[-] Error: Backend health check timed out.`
- **Root Cause:** The backend process failed to boot due to an invalid configuration or database error.
- **Resolution:**
  Inspect `logs/application/backend.log` for the exact stack trace.
  - If a database driver error is present, ensure `DATABASE_URL` is set to `sqlite:///infrastructure_resilience.db` or PostgreSQL is active.

---

## 3. Database & Persistence Troubleshooting

### Issue 3.1: "OperationalError: connection to server at 'localhost' (5432) failed"
- **Symptom:** Backend fails to start, complaining of PostgreSQL connection refusal.
- **Root Cause:** `DATABASE_URL` points to PostgreSQL, but the PostgreSQL service is stopped.
- **Resolution:**
  - For local development, unset `DATABASE_URL` or set:
    ```powershell
    $env:DATABASE_URL = "sqlite:///infrastructure_resilience.db"
    ```
    The backend will automatically create and use local SQLite.
  - If PostgreSQL is desired, verify the service is running:
    ```bash
    sudo systemctl status postgresql # On Linux
    Get-Service -Name postgresql*    # On Windows
    ```

### Issue 3.2: "sqlite3.OperationalError: database is locked"
- **Symptom:** Concurrent simulation runs experience SQLite database lock timeouts.
- **Root Cause:** Default SQLite concurrency handles one write transaction at a time.
- **Resolution:**
  1. The platform configures SQLite with `timeout=30.0` and WAL (Write-Ahead Logging) mode.
  2. For high-concurrency multi-user environments, switch to PostgreSQL as detailed in `DEPLOYMENT_GUIDE.md`.

---

## 4. Algorithmic & Simulation Diagnostics

### Issue 4.1: "RecursionError: maximum recursion depth exceeded"
- **Symptom:** Analyzing extremely large or linear graphs ($|V| \ge 2,500$) crashes during Tarjan's DFS.
- **Root Cause:** Python interpreter recursion depth defaults to 1,000 frames.
- **Resolution:**
  `backend/app/algorithms/articulation_points.py` and `bridges.py` automatically elevate the recursion limit to 100,000 via:
  ```python
  if sys.getrecursionlimit() < 100000:
      sys.setrecursionlimit(100000)
  ```
  Ensure you are using the latest release files.

### Issue 4.2: Simulation Metrics Not Updating on Canvas
- **Symptom:** Executing a failure simulation updates the sidebar metrics, but the visual canvas shows old topology.
- **Resolution:**
  1. Click **Reset View / Fit to Screen** in the top-right canvas control bar.
  2. Verify WebSocket connection status in your browser's Developer Tools (F12 $\to$ Network $\to$ WS). If closed, reload the page.

