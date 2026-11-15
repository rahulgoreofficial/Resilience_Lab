@echo off
setlocal
title Stop RESILIENCE LAB
echo Stopping any running RESILIENCE LAB instances...
cd /d "%~dp0"
"%~dp0RESILIENCE_LAB.exe" --stop
pause

