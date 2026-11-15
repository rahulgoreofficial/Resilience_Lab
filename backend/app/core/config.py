"""
Application configuration module.
Provides environment-aware settings using Pydantic Settings.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    
    # PostgreSQL Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "infrastructure_resilience"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        import os
        import sys
        from pathlib import Path

        if self.DATABASE_URL:
            # If a relative SQLite path was passed, canonicalize it against the workspace root
            if self.DATABASE_URL.startswith("sqlite:///"):
                raw_path = self.DATABASE_URL[len("sqlite:///"):]
                p = Path(raw_path)
                if not p.is_absolute() and not (len(raw_path) > 1 and raw_path[1] == ":"):
                    root_dir = Path(__file__).resolve().parents[3]
                    abs_db = (root_dir / raw_path.lstrip("./\\")).resolve()
                    return f"sqlite:///{abs_db.as_posix()}"
            return self.DATABASE_URL

        # If running as packaged standalone desktop application, default to %LOCALAPPDATA%\RESILIENCE LAB\Data
        if getattr(sys, "frozen", False) or os.environ.get("RESILIENCE_LAB_STANDALONE") == "1":
            local_app_data = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
            data_dir = Path(local_app_data) / "RESILIENCE LAB" / "Data"
            try:
                data_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                data_dir = Path(os.environ.get("TEMP", ".")) / "RESILIENCE LAB" / "Data"
                try:
                    data_dir.mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass
            db_path = (data_dir / "resilience_lab.db").resolve().as_posix()
            return f"sqlite:///{db_path}"

        # Default to canonical root SQLite database if no explicit DATABASE_URL is set
        root_dir = Path(__file__).resolve().parents[3]
        canonical_sqlite = (root_dir / "infrastructure_resilience.db").resolve().as_posix()
        return f"sqlite:///{canonical_sqlite}"
    
    # Fallback SQLite URI for local zero-dependency testing if PostgreSQL is unavailable
    FALLBACK_SQLITE_URI: str = "sqlite:///./infrastructure_resilience.db"

    # Security & Resource Limits
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    MAX_NETWORK_NODES: int = 10000
    MAX_NETWORK_EDGES: int = 50000
    MAX_SIMULATION_TRIALS: int = 500
    MAX_CASCADE_ROUNDS: int = 100

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
