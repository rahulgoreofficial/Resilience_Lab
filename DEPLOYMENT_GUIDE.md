# RESILIENCE LAB — Production Deployment & Operations Guide

**Application:** Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator  
**Version:** 1.0.0 Production Release  
**Target Environments:** Linux Server (Ubuntu 22.04 LTS / RHEL 9), Docker / Kubernetes, Windows Server  

---

## 1. Deployment Architecture Overview

For production deployments serving multiple engineers or educational labs, RESILIENCE LAB is deployed with:
- **FastAPI / Uvicorn ASGI Backend:** Handles REST queries and WebSocket simulation streaming;
- **PostgreSQL 15+ Database:** Provides durable, ACID-compliant relational persistence with connection pooling;
- **Nginx Reverse Proxy:** Serves pre-compiled React 19 static assets, terminates SSL/TLS, and proxies `/api` and `/ws` traffic to Uvicorn;
- **Systemd / Docker:** Manages automatic service lifecycle, auto-restart on failure, and structured log rotation.

```mermaid
flowchart LR
    Client([Web Browser / Client]) -->|HTTPS:443 / WSS| Nginx[Nginx Reverse Proxy]
    Nginx -->|Static Assets| FrontendDist[Vite React Dist Files]
    Nginx -->|Reverse Proxy /api| Backend[FastAPI Uvicorn :8000]
    Nginx -->|WebSocket /ws| Backend
    Backend -->|SQLAlchemy Pool| Postgres[(PostgreSQL 15+ :5432)]
```

---

## 2. Environment Configuration Matrix

Configure the following environment variables in production:

| Variable | Default Value | Production Recommended | Description |
|---|---|---|---|
| `DATABASE_URL` | `sqlite:///infrastructure_resilience.db` | `postgresql://res_user:strong_pass@localhost:5432/resilience_db` | SQLAlchemy database connection URI |
| `BACKEND_PORT` | `8000` | `8000` | Internal port bound by Uvicorn |
| `FRONTEND_PORT` | `5173` | `80` / `443` | External web client port |
| `LOG_LEVEL` | `INFO` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `CORS_ORIGINS` | `http://localhost:5173` | `https://resilience.yourdomain.com` | Allowed CORS client origins |
| `MAX_NODES_PER_NETWORK`| `5000` | `10000` | Maximum node limit per topology |

---

## 3. Containerized Deployment with Docker & Docker Compose

### 3.1 Docker Compose Configuration (`docker-compose.prod.yml`)
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: resilience_db
    restart: always
    environment:
      POSTGRES_DB: resilience_db
      POSTGRES_USER: res_user
      POSTGRES_PASSWORD: SecretProductionPassword123
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U res_user -d resilience_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: resilience_backend
    restart: always
    environment:
      DATABASE_URL: postgresql://res_user:SecretProductionPassword123@db:5432/resilience_db
      PYTHONPATH: /app
      LOG_LEVEL: INFO
      CORS_ORIGINS: "http://localhost,https://yourdomain.com"
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: resilience_frontend
    restart: always
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend

volumes:
  pgdata:
```

### 3.2 Launching Containers
```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml logs -f
```

---

## 4. Bare-Metal Linux Deployment (Ubuntu 22.04 LTS)

### 4.1 Systemd Backend Service
Create `/etc/systemd/system/resilience-backend.service`:
```ini
[Unit]
Description=RESILIENCE LAB - FastAPI Backend Service
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/resilience-lab/backend
Environment="PYTHONPATH=/var/www/resilience-lab/backend"
Environment="DATABASE_URL=postgresql://res_user:password@localhost:5432/resilience_db"
ExecStart=/var/www/resilience-lab/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable resilience-backend
sudo systemctl start resilience-backend
sudo systemctl status resilience-backend
```

### 4.2 Nginx Reverse Proxy Configuration
Create `/etc/nginx/sites-available/resilience-lab`:
```nginx
server {
    listen 80;
    server_name resilience.yourdomain.com;

    # Serve compiled React frontend
    location / {
        root /var/www/resilience-lab/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Proxy REST API requests
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy WebSocket live simulation telemetry
    location /api/v1/ws/ {
        proxy_pass http://127.0.0.1:8000/api/v1/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

Enable site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/resilience-lab /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 5. Security & Maintenance Routines

1. **Database Backups:**
   ```bash
   # Automated daily PostgreSQL backup:
   pg_dump -U res_user resilience_db | gzip > /backups/resilience_db_$(date +%F).sql.gz
   ```
2. **Health Monitoring:**
   - Integrate `http://localhost:8000/api/v1/health` into your Prometheus / UptimeRobot monitoring probe.
   - Monitor `logs/application/backend.log` for validation errors or unexpected exceptions.

