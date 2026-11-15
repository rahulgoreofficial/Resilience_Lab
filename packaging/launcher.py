"""
RESILIENCE LAB — Desktop Application Launcher & Process Controller
Project: Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator
Target: Windows 10 & 11 Standalone Desktop Package
"""

import os
import sys
import io
import time
import socket
import logging
import argparse
import threading
import webbrowser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

# Windows GUI / PyInstaller safety: Ensure stdout and stderr are never None
if sys.stdout is None:
    try:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    except Exception:
        sys.stdout = io.StringIO()
if sys.stderr is None:
    try:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
    except Exception:
        sys.stderr = io.StringIO()

# Configure standalone environment variables before application imports
os.environ["RESILIENCE_LAB_STANDALONE"] = "1"

# Resolve user data and log directories under %LOCALAPPDATA%\RESILIENCE LAB
LOCAL_APP_DATA = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
APP_DATA_ROOT = Path(LOCAL_APP_DATA) / "RESILIENCE LAB"
DATA_DIR = APP_DATA_ROOT / "Data"
LOGS_DIR = APP_DATA_ROOT / "Logs"

try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError):
    # Fallback to TEMP if AppData directory creation is restricted (e.g. test sandbox)
    fallback_root = Path(os.environ.get("TEMP", ".")) / "RESILIENCE LAB"
    DATA_DIR = fallback_root / "Data"
    LOGS_DIR = fallback_root / "Logs"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = (DATA_DIR / "resilience_lab.db").resolve().as_posix()
LOG_PATH = (LOGS_DIR / "application.log").resolve().as_posix()

os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["RESILIENCE_LAB_LOG_FILE"] = LOG_PATH

# PyInstaller runtime path adjustment
if getattr(sys, "frozen", False):
    bundle_dir = Path(getattr(sys, "_MEIPASS", sys.executable)).resolve()
    if not bundle_dir.is_dir():
        bundle_dir = bundle_dir.parent
    sys.path.insert(0, str(bundle_dir))
    # Point FRONTEND_DIST to packaged static directory
    for candidate in [bundle_dir / "frontend_dist", bundle_dir / "static", bundle_dir / "frontend" / "dist"]:
        if candidate.is_dir() and (candidate / "index.html").is_file():
            os.environ["FRONTEND_DIST"] = str(candidate)
            break
else:
    # Running from source tree
    repo_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo_root / "backend"))
    dev_frontend = repo_root / "frontend" / "dist"
    if dev_frontend.is_dir():
        os.environ["FRONTEND_DIST"] = str(dev_frontend)

# Setup initial logging
handlers = [logging.FileHandler(LOG_PATH, encoding="utf-8", mode="a")]
if sys.stdout and hasattr(sys.stdout, "write"):
    handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Launcher] %(message)s",
    handlers=handlers
)
logger = logging.getLogger("Launcher")


def is_port_bound(port: int, host: str = "127.0.0.1") -> bool:
    """Checks whether a TCP port is bound and accepting connections."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex((host, port)) == 0
    except OSError:
        return False


def probe_health(port: int, timeout: float = 1.0) -> bool:
    """Checks whether a healthy RESILIENCE LAB backend is actively responding on the given port."""
    url = f"http://127.0.0.1:{port}/api/v1/health"
    try:
        req = Request(url, headers={"User-Agent": "ResilienceLab-Launcher/1.0"})
        with urlopen(req, timeout=timeout) as response:
            return response.status == 200
    except (URLError, TimeoutError, OSError):
        return False


def send_shutdown_signal(port: int = 8000) -> bool:
    """Requests graceful shutdown of running instance via protected localhost endpoint."""
    url = f"http://127.0.0.1:{port}/api/v1/system/shutdown"
    try:
        req = Request(url, data=b"{}", headers={"Content-Type": "application/json", "User-Agent": "ResilienceLab-Launcher/1.0"})
        with urlopen(req, timeout=3.0) as resp:
            return resp.status == 200
    except Exception as exc:
        logger.debug(f"Shutdown request to port {port} failed: {exc}")
        return False


def initialize_database():
    """Initializes SQLite schema, migrations, and seeds default networks safely."""
    logger.info(f"Target SQLite database: {DB_PATH}")
    try:
        from app.database.init_db import init_db, recover_interrupted_simulations
        from app.database.session import engine, get_db_context
        from app.services.persistence_service import PersistenceService

        init_db(engine)
        logger.info("Database schema verified.")

        with get_db_context() as db:
            recover_interrupted_simulations(db)
            PersistenceService.seed_sample_network(db)
            logger.info("Startup recovery and default campus network verified.")
    except Exception as exc:
        logger.error(f"Database initialization error: {exc}", exc_info=True)


def find_suitable_port(preferred_port: int = 8000) -> int:
    """Selects preferred port or increments to find next available port."""
    if not is_port_bound(preferred_port):
        return preferred_port

    logger.warning(f"Preferred port {preferred_port} is already bound. Searching for next free port...")
    for candidate in range(preferred_port + 1, preferred_port + 50):
        if not is_port_bound(candidate):
            logger.info(f"Using alternate port: {candidate}")
            return candidate

    return preferred_port


def run_launcher():
    parser = argparse.ArgumentParser(
        description="RESILIENCE LAB — Desktop Application Launcher",
        prog="RESILIENCE_LAB"
    )
    parser.add_argument("--stop", action="store_true", help="Gracefully stop any running RESILIENCE LAB background instances")
    parser.add_argument("--status", action="store_true", help="Check status of RESILIENCE LAB service")
    parser.add_argument("--open-logs", action="store_true", help="Open logs directory in File Explorer")
    parser.add_argument("--open-data", action="store_true", help="Open database directory in File Explorer")
    parser.add_argument("--no-browser", action="store_true", help="Start server without launching default browser")
    parser.add_argument("--port", type=int, default=8000, help="Custom listening port (default: 8000)")
    args = parser.parse_args()

    # Handle utility arguments
    if args.open_logs:
        os.startfile(str(LOGS_DIR))
        return

    if args.open_data:
        os.startfile(str(DATA_DIR))
        return

    if args.stop:
        logger.info("Stopping RESILIENCE LAB instances...")
        stopped = False
        for p in range(8000, 8010):
            if probe_health(p):
                if send_shutdown_signal(p):
                    logger.info(f"Successfully stopped instance running on port {p}.")
                    stopped = True
        if not stopped:
            logger.info("No active RESILIENCE LAB instances detected.")
        return

    if args.status:
        is_healthy = probe_health(args.port)
        print(f"RESILIENCE LAB (Port {args.port}): {'HEALTHY (Running)' if is_healthy else 'STOPPED'}")
        return

    # 1. Single-Instance Check: Reuse existing healthy instance if running
    target_port = args.port
    if probe_health(target_port):
        logger.info(f"An existing RESILIENCE LAB instance is already active and healthy on port {target_port}.")
        logger.info("Opening browser window to active instance...")
        webbrowser.open(f"http://127.0.0.1:{target_port}")
        return

    # 2. Select port
    port = find_suitable_port(target_port)

    # 3. Initialize Database
    initialize_database()

    # 4. Import FastAPI & Uvicorn
    try:
        import uvicorn
        from app.main import app
    except Exception as exc:
        logger.exception(f"Fatal error loading application backend: {exc}")
        sys.exit(1)

    app_url = f"http://127.0.0.1:{port}"
    print("============================================================")
    print("                      RESILIENCE LAB                        ")
    print("   Graph-Theoretic Critical Infrastructure Resilience Platform")
    print("============================================================")
    print(f"   [+] Server URL : {app_url}")
    print(f"   [+] Database   : {DB_PATH}")
    print(f"   [+] Log File   : {LOG_PATH}")
    print("============================================================")
    print("   [+] Application is running. Keep this window open.")
    print("   [+] Press Ctrl+C in this window to stop the server.")
    print("============================================================")

    logger.info(f"Operational on {app_url}. Database: {DB_PATH}")

    # 5. Open browser after brief delay to allow socket listener to bind
    if not args.no_browser:
        def open_browser():
            time.sleep(1.2)
            try:
                logger.info(f"Opening browser at: {app_url}")
                webbrowser.open(app_url)
            except Exception as exc:
                logger.warning(f"Could not open system browser automatically: {exc}")

        threading.Thread(target=open_browser, daemon=True).start()

    # 6. Run Uvicorn directly on the main thread with log_config=None (prevents isatty crash)
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="info",
            access_log=False,
            log_config=None
        )
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Shutting down gracefully...")
    except Exception as exc:
        logger.exception(f"Server runtime exception: {exc}")
    finally:
        logger.info("RESILIENCE LAB terminated cleanly.")


if __name__ == "__main__":
    run_launcher()
