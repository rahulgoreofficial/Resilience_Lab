# RESILIENCE LAB — Windows Uninstallation Guide

**Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator**  
*Release Version 1.0.0 — Standalone Windows Distribution*

---

## 1. Standard Uninstallation Methods

You can uninstall RESILIENCE LAB using any of the following standard Windows methods:

### Method A: Via Windows Settings / Control Panel (Recommended)
1. Open **Windows Settings** (shortcut: `Win + I`).
2. Navigate to **Apps** > **Installed apps** (or *Apps & features* on Windows 10).
3. Search for **RESILIENCE LAB**.
4. Click the three dots (`...`) next to the entry and select **Uninstall**.
5. Follow the prompt to complete uninstallation.

### Method B: Via Windows Start Menu
1. Click the **Start Menu** or press the Windows key.
2. Scroll to the **RESILIENCE LAB** folder.
3. Click **Uninstall RESILIENCE LAB**.

### Method C: Via Direct Uninstaller Executable
Run the uninstaller directly from the installation folder:
```powershell
& "$env:LOCALAPPDATA\Programs\RESILIENCE LAB\unins000.exe"
```

---

## 2. User Data Retention & Privacy Choices

During the uninstallation process, RESILIENCE LAB displays a dedicated dialog asking:

> **"Do you want to delete your saved network databases and simulation history?"**  
> *(Selecting "No" will safely preserve your data under: %LOCALAPPDATA%\RESILIENCE LAB\Data)*

- **If you click "No" (Default & Recommended)**:  
  All program binaries, DLLs, and shortcuts are completely uninstalled, but your custom network topologies, simulation run records, and benchmarks are preserved on disk. If you reinstall RESILIENCE LAB later, your graphs and history will immediately be available.
- **If you click "Yes"**:  
  The uninstaller completely deletes the `%LOCALAPPDATA%\RESILIENCE LAB` folder, including all database files (`resilience_lab.db`) and log files (`application.log`).

---

## 3. Silent / Unattended Uninstallation (For Administrators)

To silently remove RESILIENCE LAB without interactive GUI dialogs:

```powershell
# Silent uninstall retaining user data by default
& "$env:LOCALAPPDATA\Programs\RESILIENCE LAB\unins000.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
```

---

## 4. Manual Post-Uninstall Verification Checklist

To confirm that the application was completely cleaned up:

1. **Verify Binary Directory Removed**:
   ```powershell
   Test-Path "$env:LOCALAPPDATA\Programs\RESILIENCE LAB"
   # Expected output: False
   ```
2. **Verify Desktop Shortcut Removed**:
   ```powershell
   Test-Path "$([Environment]::GetFolderPath('Desktop'))\RESILIENCE LAB.lnk"
   # Expected output: False
   ```
3. **Verify Start Menu Entry Removed**:
   ```powershell
   Test-Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\RESILIENCE LAB"
   # Expected output: False
   ```
4. **Data Directory Status**:
   - If retained: `$env:LOCALAPPDATA\RESILIENCE LAB\Data` will contain `resilience_lab.db`.
   - If removed: `$env:LOCALAPPDATA\RESILIENCE LAB` will not exist.

