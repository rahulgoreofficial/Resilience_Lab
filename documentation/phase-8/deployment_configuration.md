# Phase 8: Deployment, Environment & Service Configuration

## 1. Environment Configurations

The application supports multiple deployment environments through Pydantic Settings (`app/core/config.py`). Configuration parameters can be supplied via environment variables or a root `.env` file.

### 1.1. Example Environment File (`.env.example`)
```env
# Application Metadata
PROJECT_NAME="Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator"
VERSION="1.0.0"
LOG_LEVEL="INFO"

# API Routing
API_V1_STR="/api"
API_V1_PREFIX="/api/v1"

# CORS Configuration
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:3000"]

# PostgreSQL Database Configuration
POSTGRES_SERVER="localhost"
POSTGRES_PORT=5432
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres_secure_password"
POSTGRES_DB="infrastructure_resilience"

# Direct Database URL (Optional: Overrides individual parameters if provided)
# DATABASE_URL="postgresql+psycopg2://postgres:postgres_secure_password@localhost:5432/infrastructure_resilience"

# Resource & Security Limits
MAX_UPLOAD_SIZE_BYTES=10485760    # 10 MB
MAX_NETWORK_NODES=10000           # Maximum graph order |V|
MAX_NETWORK_EDGES=50000           # Maximum graph size |E|
MAX_SIMULATION_TRIALS=500         # Maximum Monte Carlo percolation trials
MAX_CASCADE_ROUNDS=100            # Maximum load redistribution rounds
```

---

## 2. Docker Compose Deployment for PostgreSQL

For staging and production deployments, PostgreSQL is provisioned alongside the FastAPI backend using Docker Compose.

### `docker-compose.yml`
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: resilience_postgres
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres_secure_password
      POSTGRES_DB: infrastructure_resilience
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d infrastructure_resilience"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: resilience_backend
    restart: always
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql+psycopg2://postgres:postgres_secure_password@db:5432/infrastructure_resilience
      - POSTGRES_SERVER=db
      - POSTGRES_PORT=5432
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres_secure_password
      - POSTGRES_DB=infrastructure_resilience
    ports:
      - "8000:8000"
    command: >
      sh -c "alembic upgrade head &&
             uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"

volumes:
  postgres_data:
```

---

## 3. Zero-Dependency Local Development (SQLite Fallback)

To enable friction-free development and instant testing in offline, air-gapped, or sandboxed environments without requiring a local PostgreSQL daemon:

1. **Automatic Detection**: If PostgreSQL is unreachable upon startup (`psycopg2.OperationalError`), the application engine automatically switches to `sqlite:///./infrastructure_resilience.db`.
2. **Feature Parity**: SQLite foreign keys are explicitly enforced via `PRAGMA foreign_keys=ON`, guaranteeing identical cascading delete semantics.
3. **Unit Testing**: During automated testing with pytest, `conftest.py` configures `sqlite:///:memory:` with `StaticPool`, executing all 142 tests in under 1 second without any external dependencies.

---

## 4. Production Startup & Health Verification

### 4.1. Step 1: Run Alembic Migrations
```powershell
cd backend
$env:PYTHONPATH='.'
alembic upgrade head
```

### 4.2. Step 2: Start Uvicorn Server
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4.3. Step 3: Verify Health Endpoints
- HTTP Health: `GET http://127.0.0.1:8000/api/v1/health`
- Database Health: `GET http://127.0.0.1:8000/api/v1/health/db`
- Interactive Swagger UI: `http://127.0.0.1:8000/api/docs`
- Interactive ReDoc: `http://127.0.0.1:8000/api/redoc`

