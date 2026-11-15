"""
SQLAlchemy ORM Model: SimulationEventModel.
Chronological events emitted during simulation execution.
"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class SimulationEventModel(Base):
    """Stores sequential simulation progress events with deterministic ordering."""
    __tablename__ = "simulation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    simulation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("simulations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    simulation: Mapped["SimulationModel"] = relationship("SimulationModel", back_populates="events")

    __table_args__ = (
        UniqueConstraint("simulation_id", "sequence_number", name="uq_simulation_event_sequence"),
    )

    def to_dict(self) -> dict:
        return {
            "sequence_number": self.sequence_number,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

