@echo off
setlocal
title Stop RESILIENCE LAB

echo =================================================================
echo                 STOPPING RESILIENCE LAB
echo =================================================================

cd /d "%~dp0"

set "PYTHON_EXE=%~dp0backend\venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" "%~dp0tools\stop_launcher.py"

echo.
pause

