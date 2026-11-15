"""
SQLAlchemy ORM Model: NetworkSnapshot.
Preserves an immutable point-in-time topology snapshot used by simulations.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class NetworkSnapshot(Base):
    """Stores frozen graph snapshots to guarantee historical simulation immutability."""
    __tablename__ = "network_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    network_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("networks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    network_version: Mapped[int] = mapped_column(Integer, nullable=False)
    graph_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    network: Mapped["Network"] = relationship("Network", back_populates="snapshots")
    simulations: Mapped[list["SimulationModel"]] = relationship(
        "SimulationModel",
        back_populates="snapshot"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "network_id": self.network_id,
            "network_version": self.network_version,
            "snapshot_hash": self.snapshot_hash,
            "graph_snapshot": self.graph_snapshot,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

