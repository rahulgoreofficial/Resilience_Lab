"""
Repository: NodeRepository.
Handles persistence and lifecycle for network nodes.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.models.node import NodeModel
from app.models.edge import EdgeModel


class NodeRepository:
    """Data access repository for Node models."""

    @staticmethod
    def create(db: Session, node: NodeModel) -> NodeModel:
        db.add(node)
        db.flush()
        return node

    @staticmethod
    def get_by_node_id(db: Session, network_id: str, node_id: str) -> Optional[NodeModel]:
        stmt = select(NodeModel).where(
            NodeModel.network_id == network_id,
            NodeModel.node_id == node_id
        )
        return db.scalar(stmt)

    @staticmethod
    def list_by_network(db: Session, network_id: str) -> List[NodeModel]:
        stmt = (
            select(NodeModel)
            .where(NodeModel.network_id == network_id)
            .order_by(NodeModel.node_id.asc())
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def update(db: Session, node: NodeModel, update_data: dict) -> NodeModel:
        for key, value in update_data.items():
            if value is not None and hasattr(node, key):
                setattr(node, key, value)
        db.flush()
        return node

    @staticmethod
    def delete(db: Session, node: NodeModel) -> None:
        # Cascade delete incident edges in the same network
        incident_stmt = select(EdgeModel).where(
            EdgeModel.network_id == node.network_id,
            or_(
                EdgeModel.source_node_id == node.node_id,
                EdgeModel.target_node_id == node.node_id
            )
        )
        incident_edges = db.scalars(incident_stmt).all()
        for edge in incident_edges:
            db.delete(edge)

        db.delete(node)
        db.flush()

