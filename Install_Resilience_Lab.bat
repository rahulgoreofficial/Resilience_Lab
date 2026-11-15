@echo off
setlocal
title RESILIENCE LAB - Installer

echo =================================================================
echo        RESILIENCE LAB - ONE-CLICK INSTALLER FOR WINDOWS
echo =================================================================
echo Launching automated setup via PowerShell...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\install_windows.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Installation failed or encountered critical errors.
    echo Please review the installation log in the logs\installation\ directory.
    pause
    exit /b %ERRORLEVEL%
)

echo.
pause

