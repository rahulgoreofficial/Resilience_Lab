# Phase 2: Execution & Verification Commands
## Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator

---

### 1. Backend Commands

#### 1.1 Activate Virtual Environment
```powershell
# From workspace root (Windows PowerShell)
backend\venv\Scripts\Activate.ps1
```

#### 1.2 Run Backend Unit Tests (Pytest)
```powershell
# Run the complete test suite (67 tests)
cd c:\DM\CP\backend
& "c:\DM\CP\backend\venv\Scripts\pytest.exe" -v

# Run with short test summary
& "c:\DM\CP\backend\venv\Scripts\pytest.exe" -q
```

#### 1.3 Start Backend Development Server (FastAPI + Uvicorn)
```powershell
cd c:\DM\CP\backend
& "c:\DM\CP\backend\venv\Scripts\uvicorn.exe" app.main:app --host 0.0.0.0 --port 8000 --reload
```
Once started:
- API Root: `http://localhost:8000/api`
- Interactive Swagger UI: `http://localhost:8000/api/docs`
- Health Check: `http://localhost:8000/api/health`
- Database Health Check: `http://localhost:8000/api/database-health`

---

### 2. Frontend Commands

#### 2.1 Install Frontend Dependencies
```bash
cd c:\DM\CP\frontend
npm install
```

#### 2.2 Start Frontend Development Server
```bash
cd c:\DM\CP\frontend
npm run dev
```
Access in browser: `http://localhost:5173`

#### 2.3 Run Production Build & Type-Check
```bash
cd c:\DM\CP\frontend
npm run build
```
Build output artifacts are placed in `frontend/dist/`.

---

### 3. Optional Containerized Execution (Docker Compose)

When Docker Desktop is installed and running on the host system:
```bash
# Start PostgreSQL database and FastAPI backend
docker compose up -d

# Check service logs
docker compose logs -f

# Shut down services and preserve database volume
docker compose down
```
*(Note: As specified in Phase 2, the application operates normally without Docker or PostgreSQL).*

