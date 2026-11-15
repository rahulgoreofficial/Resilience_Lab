"""
Repository: EdgeRepository.
Handles persistence and undirected uniqueness validation for communication links.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.edge import EdgeModel


class EdgeRepository:
    """Data access repository for Edge models."""

    @staticmethod
    def create(db: Session, edge: EdgeModel) -> EdgeModel:
        db.add(edge)
        db.flush()
        return edge

    @staticmethod
    def get_by_edge_id(db: Session, network_id: str, edge_id: str) -> Optional[EdgeModel]:
        stmt = select(EdgeModel).where(
            EdgeModel.network_id == network_id,
            EdgeModel.edge_id == edge_id
        )
        return db.scalar(stmt)

    @staticmethod
    def get_by_endpoints(db: Session, network_id: str, u: str, v: str) -> Optional[EdgeModel]:
        can_u = min(u, v)
        can_v = max(u, v)
        stmt = select(EdgeModel).where(
            EdgeModel.network_id == network_id,
            EdgeModel.canonical_u == can_u,
            EdgeModel.canonical_v == can_v
        )
        return db.scalar(stmt)

    @staticmethod
    def list_by_network(db: Session, network_id: str) -> List[EdgeModel]:
        stmt = (
            select(EdgeModel)
            .where(EdgeModel.network_id == network_id)
            .order_by(EdgeModel.edge_id.asc())
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def update(db: Session, edge: EdgeModel, update_data: dict) -> EdgeModel:
        for key, value in update_data.items():
            if value is not None and hasattr(edge, key):
                setattr(edge, key, value)
        db.flush()
        return edge

    @staticmethod
    def delete(db: Session, edge: EdgeModel) -> None:
        db.delete(edge)
        db.flush()

