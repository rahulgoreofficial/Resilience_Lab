@echo off
setlocal
title RESILIENCE LAB - Infrastructure Resilience Platform

echo =================================================================
echo                      RESILIENCE LAB
echo   Graph-Theoretic Critical Infrastructure Resilience Platform
echo =================================================================

cd /d "%~dp0"

:: 1. Check if standalone compiled executable exists in dist or current folder
if exist "%~dp0RESILIENCE_LAB.exe" (
    echo [INFO] Launching standalone RESILIENCE LAB executable...
    "%~dp0RESILIENCE_LAB.exe" %*
    goto :end
)

if exist "%~dp0dist\RESILIENCE_LAB\RESILIENCE_LAB.exe" (
    echo [INFO] Launching packaged standalone executable from dist...
    "%~dp0dist\RESILIENCE_LAB\RESILIENCE_LAB.exe" %*
    goto :end
)

:: 2. Check if Python virtual environment exists for source execution
set "PYTHON_EXE=%~dp0backend\venv\Scripts\python.exe"
if exist "%PYTHON_EXE%" (
    echo [INFO] Launching via Python development environment...
    "%PYTHON_EXE%" "%~dp0tools\launcher.py" %*
    goto :end
)

:: 3. Check system Python
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Launching via system Python...
    python "%~dp0tools\launcher.py" %*
    goto :end
)

:: 4. If nothing is found, direct user to the standalone installer
echo.
echo [ERROR] No Python runtime or compiled executable detected!
echo.
echo Please run the standalone installer to set up RESILIENCE LAB:
echo release\RESILIENCE_LAB_Setup.exe
echo.
pause

:end
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Process exited with error code %ERRORLEVEL%.
    pause
)
