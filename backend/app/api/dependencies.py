"""
API Route Dependencies.
Provides database sessions, pagination query parameters, and entity extractors.
"""

from typing import Generator
from fastapi import Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.common import PaginationParams


def get_database(db: Session = Depends(get_db)) -> Generator[Session, None, None]:
    """Provides a transactional database session for the request."""
    return db


def get_pagination(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Page limit")
) -> PaginationParams:
    """Extracts pagination parameters from query string."""
    return PaginationParams(skip=skip, limit=limit)

