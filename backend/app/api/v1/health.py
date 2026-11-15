"""
Health and Diagnostic API Endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter
from app.core.config import settings
from app.database.session import check_db_connection
from app.schemas.graph_schema import HealthResponse, DatabaseHealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def get_health() -> Dict[str, Any]:
    """Returns application health status."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME
    }


@router.get("/version", tags=["Health"])
def get_version() -> Dict[str, str]:
    """Returns API and project version information."""
    return {
        "version": settings.VERSION,
        "project_name": settings.PROJECT_NAME,
        "phase": "Phase 8 (Layered Architecture, PostgreSQL Integration & Dynamic Network Engine)"
    }


@router.get("/database-health", response_model=DatabaseHealthResponse, tags=["Health"])
def get_database_health() -> Dict[str, Any]:
    """Checks database connectivity health non-blockingly."""
    return check_db_connection()

