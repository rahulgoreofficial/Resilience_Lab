@echo off
setlocal
title RESILIENCE LAB

echo =================================================================
echo                      RESILIENCE LAB
echo   Graph-Theoretic Critical Infrastructure Resilience Platform
echo =================================================================
echo Starting RESILIENCE LAB standalone server...
echo.

cd /d "%~dp0"
if exist "%~dp0RESILIENCE_LAB.exe" (
    "%~dp0RESILIENCE_LAB.exe" %*
) else (
    echo [ERROR] Main executable RESILIENCE_LAB.exe not found!
    pause
)

