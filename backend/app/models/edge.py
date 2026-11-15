"""
SQLAlchemy ORM Model: EdgeModel.
Represents an undirected communication link between vertices in G = (V, E).
"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, JSON, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class EdgeModel(Base):
    """Stores communication links with canonical endpoint ordering to enforce undirected uniqueness."""
    __tablename__ = "edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    network_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("networks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    edge_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_node_id: Mapped[str] = mapped_column(String(64), nullable=False)
    target_node_id: Mapped[str] = mapped_column(String(64), nullable=False)
    canonical_u: Mapped[str] = mapped_column(String(64), nullable=False)
    canonical_v: Mapped[str] = mapped_column(String(64), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    latency: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    capacity: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    reliability: Mapped[float] = mapped_column(Float, default=0.99, nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    network: Mapped["Network"] = relationship("Network", back_populates="edges")

    __table_args__ = (
        UniqueConstraint("network_id", "edge_id", name="uq_network_edge_id"),
        UniqueConstraint("network_id", "canonical_u", "canonical_v", name="uq_network_undirected_edge"),
        CheckConstraint("canonical_u != canonical_v", name="chk_edge_no_self_loops"),
        CheckConstraint("weight >= 0.0", name="chk_edge_weight_non_negative"),
        CheckConstraint("latency >= 0.0", name="chk_edge_latency_non_negative"),
        CheckConstraint("capacity > 0.0", name="chk_edge_capacity_positive"),
        CheckConstraint("reliability >= 0.0 AND reliability <= 1.0", name="chk_edge_reliability_range"),
    )

    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "source": self.source_node_id,
            "target": self.target_node_id,
            "weight": self.weight,
            "latency": self.latency,
            "capacity": self.capacity,
            "reliability": self.reliability,
            "metadata": self.metadata_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

