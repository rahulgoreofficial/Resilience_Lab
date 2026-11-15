# Phase 8: Typed SQLAlchemy 2.x Integration & Session Architecture

## 1. Modern Typed Declarative ORM (SQLAlchemy 2.x)

The simulator uses SQLAlchemy 2.0+ typed declarative syntax across all database models. Instead of legacy `Column()` declarations, fields are statically typed with `Mapped[T]` and configured with `mapped_column(...)`.

### 1.1. Example: Declarative Network Model
```python
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
from sqlalchemy import String, Text, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Network(Base):
    __tablename__ = "networks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    network_type: Mapped[str] = mapped_column(String(64), default="COMMUNICATION_NETWORK", nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    nodes: Mapped[List["NodeModel"]] = relationship("NodeModel", back_populates="network", cascade="all, delete-orphan")
    edges: Mapped[List["EdgeModel"]] = relationship("EdgeModel", back_populates="network", cascade="all, delete-orphan")
```

> [!NOTE]
> Notice the column mapping `metadata_json = mapped_column("metadata", JSON)`. In SQLAlchemy 2.x, the attribute name `metadata` on declarative classes is reserved for Table MetaData. Using `"metadata"` as the underlying database column name while exposing `metadata_json` avoids ORM namespace collision.

---

## 2. Engine Configuration & Connection Pooling

The engine is created via `create_app_engine()` in `app/database/session.py`. It is dynamically tailored depending on whether it connects to PostgreSQL or SQLite:

```python
def create_app_engine(database_url: str) -> Engine:
    if database_url.startswith("sqlite"):
        eng = create_engine(database_url, connect_args={"check_same_thread": False}, echo=False)
        @event.listens_for(eng, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        return eng
    else:
        return create_engine(
            database_url,
            pool_pre_ping=True,      # Tests connection liveness before checkout
            pool_size=5,             # Persistent pool size
            max_overflow=10,         # Maximum overflow connections under load
            connect_args={"connect_timeout": 1},
            echo=False
        )
```

### Key Production Pool Parameters:
1. `pool_pre_ping=True`: Prevents stale connection errors (`OperationalError: server closed the connection unexpectedly`) by pinging PostgreSQL with `SELECT 1` before dispatching requests.
2. `pool_size=5` & `max_overflow=10`: Allows the service to comfortably handle up to 15 concurrent request workers without connection exhaustion.
3. `PRAGMA foreign_keys=ON`: In SQLite mode, foreign key enforcement is explicitly enabled at the driver level to match PostgreSQL cascading delete behavior during unit testing.

---

## 3. Session Scopes & Transaction Management

The architecture separates request-bound sessions from background worker sessions:

### 3.1. Request-Scoped Session (`get_db`)
```python
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: 1 session per HTTP request."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```
- Each incoming HTTP request receives its own isolated database transaction.
- If an unhandled exception or validation failure occurs during execution, the session is rolled back automatically.
- Sessions are guaranteed to close in the `finally:` block, preventing connection leaks.

### 3.2. Background Worker Context (`get_db_context`)
```python
@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Isolated context manager for background workers and startup recovery."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```
- Used during startup lifecycle (`lifespan`) and background simulation workers.
- Automatically commits on successful exit or rolls back on exception.

