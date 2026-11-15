"""
Repository: NetworkRepository.
Handles database queries and optimistic concurrency version management for Network entities.
"""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func
from app.models.network import Network
from app.core.exceptions import NetworkVersionConflictError


class NetworkRepository:
    """Data access repository for Network models."""

    @staticmethod
    def create(db: Session, network: Network) -> Network:
        db.add(network)
        db.flush()
        return network

    @staticmethod
    def get_by_id(db: Session, network_id: str) -> Optional[Network]:
        stmt = select(Network).where(Network.id == network_id)
        return db.scalar(stmt)

    @staticmethod
    def get_by_id_with_elements(db: Session, network_id: str) -> Optional[Network]:
        """Eagerly loads related nodes and edges in a single query."""
        stmt = (
            select(Network)
            .where(Network.id == network_id)
            .options(selectinload(Network.nodes), selectinload(Network.edges))
        )
        return db.scalar(stmt)

    @staticmethod
    def list_all(db: Session, skip: int = 0, limit: int = 50) -> Tuple[List[Network], int]:
        total_stmt = select(func.count(Network.id))
        total = db.scalar(total_stmt) or 0

        stmt = (
            select(Network)
            .order_by(Network.created_at.desc())
            .offset(skip)
            .limit(limit)
            .options(selectinload(Network.nodes), selectinload(Network.edges))
        )
        items = list(db.scalars(stmt).all())
        return items, total

    @staticmethod
    def update(
        db: Session,
        network: Network,
        update_data: dict,
        expected_version: Optional[int] = None
    ) -> Network:
        if expected_version is not None and network.version != expected_version:
            raise NetworkVersionConflictError(
                message=f"Network version conflict: expected {expected_version}, but current version is {network.version}."
            )

        for key, value in update_data.items():
            if value is not None and hasattr(network, key):
                setattr(network, key, value)

        network.version += 1
        db.flush()
        return network

    @staticmethod
    def increment_version(db: Session, network: Network) -> int:
        network.version += 1
        db.flush()
        return network.version

    @staticmethod
    def delete(db: Session, network: Network) -> None:
        db.delete(network)
        db.flush()

