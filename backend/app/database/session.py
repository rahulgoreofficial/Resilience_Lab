"""
Database Session and Connection Management.
Implements connection pooling, health checks, transaction scopes, and isolated worker sessions.
"""

import logging
from typing import Dict, Any, Generator
from contextlib import contextmanager
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from app.core.config import settings

logger = logging.getLogger(__name__)


def create_app_engine(database_url: str) -> Engine:
    """Creates a configured SQLAlchemy engine."""
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        eng = create_engine(
            database_url,
            connect_args=connect_args,
            echo=False
        )
        # Enable foreign key constraint enforcement in SQLite
        @event.listens_for(eng, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        return eng
    else:
        return create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={"connect_timeout": 2},
            echo=False
        )


# Default Engine & SessionFactory
engine = create_app_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def set_engine_and_session(new_engine: Engine) -> None:
    """Allows test fixtures to dynamically swap engine and session factory."""
    global engine, SessionLocal
    engine = new_engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def check_db_connection() -> Dict[str, Any]:
    """
    Non-blocking database health check.
    Returns status 'healthy' or 'unavailable' without raising unhandled exceptions.
    """
    if engine is None:
        return {
            "status": "unavailable",
            "database": settings.POSTGRES_DB,
            "error": "Engine not initialized"
        }
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": settings.POSTGRES_DB,
            "host": settings.POSTGRES_SERVER,
            "port": settings.POSTGRES_PORT,
            "dialect": engine.dialect.name
        }
    except Exception as exc:
        return {
            "status": "unavailable",
            "database": settings.POSTGRES_DB,
            "host": settings.POSTGRES_SERVER,
            "port": settings.POSTGRES_PORT,
            "dialect": engine.dialect.name if engine else "unknown",
            "error": str(exc)
        }


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a separate, transactional database session per request.
    Automatically rolls back uncommitted changes on exception and always closes the session.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager providing an isolated session for background workers and services.
    Ensures sessions are never shared across concurrent threads or workers.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
