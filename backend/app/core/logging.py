"""
Structured Logging Configuration.
Configures formatting, log levels, console, and persistent file logging.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """Initializes structured logging for the application with console and file handlers."""
    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    handlers = [logging.StreamHandler(sys.stdout)]

    # Determine persistent log file location
    log_file_path = os.environ.get("RESILIENCE_LAB_LOG_FILE")
    if not log_file_path and (getattr(sys, "frozen", False) or os.environ.get("RESILIENCE_LAB_STANDALONE") == "1"):
        local_app_data = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
        logs_dir = Path(local_app_data) / "RESILIENCE LAB" / "Logs"
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            logs_dir = Path(os.environ.get("TEMP", ".")) / "RESILIENCE LAB" / "Logs"
            try:
                logs_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
        log_file_path = str(logs_dir / "application.log")

    if log_file_path:
        try:
            p = Path(log_file_path).resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                str(p),
                maxBytes=5 * 1024 * 1024,  # 5 MB
                backupCount=3,
                encoding="utf-8"
            )
            file_handler.setFormatter(logging.Formatter(log_format))
            handlers.append(file_handler)
        except Exception as exc:
            print(f"[!] Warning: Unable to initialize file logger at {log_file_path}: {exc}", file=sys.stderr)

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        handlers=handlers,
        force=True
    )
    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


logger = logging.getLogger("resilience_simulator")


