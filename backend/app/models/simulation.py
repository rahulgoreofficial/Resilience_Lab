"""
SQLAlchemy ORM Model: SimulationModel.
Persists execution parameters, statuses, and final results for resilience simulations.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class SimulationModel(Base):
    """Stores full simulation lifecycle, configuration, and computed results."""
    __tablename__ = "simulations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    network_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("networks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    snapshot_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("network_snapshots.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    simulation_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False, index=True)
    configuration: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    random_seed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    network: Mapped["Network"] = relationship("Network", back_populates="simulations")
    snapshot: Mapped[Optional["NetworkSnapshot"]] = relationship("NetworkSnapshot", back_populates="simulations")
    events: Mapped[list["SimulationEventModel"]] = relationship(
        "SimulationEventModel",
        back_populates="simulation",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="SimulationEventModel.sequence_number"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "network_id": self.network_id,
            "snapshot_id": self.snapshot_id,
            "simulation_type": self.simulation_type,
            "status": self.status,
            "configuration": self.configuration,
            "random_seed": self.random_seed,
            "results": self.results,
            "error_summary": self.error_summary,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

