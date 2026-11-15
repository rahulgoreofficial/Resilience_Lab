# Phase 8: Database Migrations with Alembic

## 1. Migration Environment Setup

Database schema changes are governed strictly through **Alembic**, ensuring repeatable and version-controlled database migrations across development, staging, and production PostgreSQL databases.

### 1.1. Directory Structure
```text
backend/
├── alembic.ini                   # Alembic configuration file
└── alembic/
    ├── env.py                    # Migration execution environment
    ├── script.py.mako            # Migration template
    └── versions/
        └── 001_initial_normalized_schema.py  # Initial revision
```

### 1.2. Configuration in `alembic/env.py`
The migration runner dynamically hooks into the application's Declarative `Base.metadata`:

```python
from app.database.base import Base
import app.models  # Registers all 6 declarative models

target_metadata = Base.metadata
```

If the environment variable `DATABASE_URL` is set, Alembic overrides the static URL in `alembic.ini`:
```python
db_url = os.environ.get("DATABASE_URL") or settings.SQLALCHEMY_DATABASE_URI
config.set_main_option("sqlalchemy.url", db_url)
```

---

## 2. Migration Revisions

### 2.1. Revision `001_initial_normalized_schema.py`
- **Revision ID**: `001`
- **Revises**: `None`
- **Creates Tables**:
  - `networks`
  - `nodes`
  - `edges`
  - `network_snapshots`
  - `simulations`
  - `simulation_events`
- **Enforces Constraints**:
  - Unique: `uq_network_node_id`, `uq_network_edge_id`, `uq_network_undirected_edge`, `uq_simulation_event_sequence`.
  - Checks: `chk_node_capacity_positive`, `chk_node_fail_prob_range`, `chk_edge_no_self_loops`, `chk_edge_reliability_range`.
  - Foreign Keys: `networks.id` cascading to all dependent tables, `simulations.snapshot_id` with `SET NULL`.

---

## 3. Migration Operational Commands

All commands should be executed from the `backend/` directory with virtual environment activated:

### 3.1. Apply All Pending Migrations (Upgrade to Head)
```powershell
$env:PYTHONPATH='.'
alembic upgrade head
```

### 3.2. Downgrade Migration (Roll Back 1 Revision)
```powershell
$env:PYTHONPATH='.'
alembic downgrade -1
```

### 3.3. Check Current Migration Status
```powershell
$env:PYTHONPATH='.'
alembic current
```

### 3.4. Generate New Migration Script (Autogenerate)
```powershell
$env:PYTHONPATH='.'
alembic revision --autogenerate -m "add_column_name"
```

---

## 4. Verification & Idempotency Testing

The initial migration was verified using both upgrade and downgrade cycles against clean database targets:

```text
INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial_normalized_schema
INFO  [alembic.runtime.migration] Running downgrade 001 -> , initial_normalized_schema
INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial_normalized_schema
```
- Both forward application (`upgrade head`) and rollback (`downgrade -1`) execute cleanly with zero database artifacts left behind.

