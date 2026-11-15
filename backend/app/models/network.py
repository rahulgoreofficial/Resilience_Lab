"""
SQLAlchemy ORM Model: Network.
Represents an infrastructure network with optimistic version tracking.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Network(Base):
    """
    Stores root network infrastructure metadata.
    Enforces optimistic concurrency via the version column.
    """
    __tablename__ = "networks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    network_type: Mapped[str] = mapped_column(String(64), default="COMMUNICATION_NETWORK", nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    nodes: Mapped[list["NodeModel"]] = relationship(
        "NodeModel",
        back_populates="network",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    edges: Mapped[list["EdgeModel"]] = relationship(
        "EdgeModel",
        back_populates="network",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    snapshots: Mapped[list["NetworkSnapshot"]] = relationship(
        "NetworkSnapshot",
        back_populates="network",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    simulations: Mapped[list["SimulationModel"]] = relationship(
        "SimulationModel",
        back_populates="network",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "network_type": self.network_type,
            "metadata": self.metadata_json,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

