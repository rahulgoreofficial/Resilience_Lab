=====================================================================
RESILIENCE LAB - Standalone Desktop Distribution v1.0.0
Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator
=====================================================================

HOW TO RUN:
1. Double-click "RESILIENCE_LAB.exe" or "Run_Resilience_Lab.bat"
2. The standalone background server will initialize SQLite database
3. Your default web browser will open automatically to:
   http://localhost:8000
4. Keep the console window open while using the application.
5. To stop, close the console window, press Ctrl+C, or run "Stop_Resilience_Lab.bat".

FILE DIRECTORY:
- RESILIENCE_LAB.exe       : Main application executable (requires no Python/Node)
- Run_Resilience_Lab.bat   : Windows batch launcher
- Stop_Resilience_Lab.bat  : Gracefully terminates active background servers
- main.py                  : Python main entry point
- _internal/               : Packaged Python runtime, algorithms, and frontend assets
- INSTALLATION_GUIDE.pdf   : Complete installation manual
- USER_MANUAL.pdf          : Complete user manual and mathematical analysis guide

PERSISTENT USER DATA:
- Database : %LOCALAPPDATA%\RESILIENCE LAB\Data\resilience_lab.db
- Logs     : %LOCALAPPDATA%\RESILIENCE LAB\Logs\application.log
(Your saved topologies and simulation history are preserved across restarts and uninstalls)
=====================================================================

