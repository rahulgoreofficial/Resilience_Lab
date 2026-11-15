"""
SQLAlchemy ORM Model: NodeModel.
Represents an infrastructure component vertex in G = (V, E).
"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class NodeModel(Base):
    """Stores physical/virtual network devices belonging to a network."""
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    network_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("networks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    node_id: Mapped[str] = mapped_column(String(64), nullable=False)
    node_type: Mapped[str] = mapped_column(String(32), nullable=False)
    importance: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    capacity: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    current_load: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    failure_probability: Mapped[float] = mapped_column(Float, default=0.01, nullable=False)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    network: Mapped["Network"] = relationship("Network", back_populates="nodes")

    __table_args__ = (
        UniqueConstraint("network_id", "node_id", name="uq_network_node_id"),
        CheckConstraint("importance >= 0.0", name="chk_node_importance_non_negative"),
        CheckConstraint("capacity > 0.0", name="chk_node_capacity_positive"),
        CheckConstraint("current_load >= 0.0", name="chk_node_load_non_negative"),
        CheckConstraint("failure_probability >= 0.0 AND failure_probability <= 1.0", name="chk_node_fail_prob_range"),
    )

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "importance": self.importance,
            "capacity": self.capacity,
            "current_load": self.current_load,
            "failure_probability": self.failure_probability,
            "is_critical": self.is_critical,
            "metadata": self.metadata_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

