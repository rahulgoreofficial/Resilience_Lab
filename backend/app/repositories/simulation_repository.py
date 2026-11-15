"""
Repository: SimulationRepository.
Handles persistence for network snapshots, simulation execution records, and chronological events.
"""

from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func
from app.models.network_snapshot import NetworkSnapshot
from app.models.simulation import SimulationModel
from app.models.simulation_event import SimulationEventModel


class SimulationRepository:
    """Data access repository for simulation entities."""

    @staticmethod
    def create_snapshot(db: Session, snapshot: NetworkSnapshot) -> NetworkSnapshot:
        db.add(snapshot)
        db.flush()
        return snapshot

    @staticmethod
    def get_snapshot(db: Session, snapshot_id: str) -> Optional[NetworkSnapshot]:
        stmt = select(NetworkSnapshot).where(NetworkSnapshot.id == snapshot_id)
        return db.scalar(stmt)

    @staticmethod
    def create_simulation(db: Session, sim: SimulationModel) -> SimulationModel:
        db.add(sim)
        db.flush()
        return sim

    @staticmethod
    def get_simulation(db: Session, simulation_id: str) -> Optional[SimulationModel]:
        stmt = (
            select(SimulationModel)
            .where(SimulationModel.id == simulation_id)
            .options(selectinload(SimulationModel.events))
        )
        return db.scalar(stmt)

    @staticmethod
    def list_simulations(
        db: Session,
        network_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[SimulationModel], int]:
        total_stmt = select(func.count(SimulationModel.id))
        if network_id:
            total_stmt = total_stmt.where(SimulationModel.network_id == network_id)
        total = db.scalar(total_stmt) or 0

        stmt = select(SimulationModel)
        if network_id:
            stmt = stmt.where(SimulationModel.network_id == network_id)
        stmt = stmt.order_by(SimulationModel.created_at.desc()).offset(skip).limit(limit)

        items = list(db.scalars(stmt).all())
        return items, total

    @staticmethod
    def update_simulation_status(
        db: Session,
        simulation_id: str,
        status: str,
        results: Optional[Dict[str, Any]] = None,
        error_summary: Optional[str] = None
    ) -> Optional[SimulationModel]:
        stmt = select(SimulationModel).where(SimulationModel.id == simulation_id)
        sim = db.scalar(stmt)
        if not sim:
            return None

        sim.status = status
        if status == "running" and not sim.started_at:
            sim.started_at = datetime.now(timezone.utc)
        elif status in ("completed", "failed", "cancelled", "interrupted"):
            sim.completed_at = datetime.now(timezone.utc)

        if results is not None:
            sim.results = results
        if error_summary is not None:
            sim.error_summary = error_summary

        db.flush()
        return sim

    @staticmethod
    def add_event(
        db: Session,
        simulation_id: str,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None
    ) -> SimulationEventModel:
        # Determine next sequence number
        seq_stmt = (
            select(func.coalesce(func.max(SimulationEventModel.sequence_number), 0))
            .where(SimulationEventModel.simulation_id == simulation_id)
        )
        next_seq = (db.scalar(seq_stmt) or 0) + 1

        event_obj = SimulationEventModel(
            simulation_id=simulation_id,
            sequence_number=next_seq,
            event_type=event_type,
            event_data=event_data or {},
            created_at=datetime.now(timezone.utc)
        )
        db.add(event_obj)
        db.flush()
        return event_obj

    @staticmethod
    def get_events(db: Session, simulation_id: str) -> List[SimulationEventModel]:
        stmt = (
            select(SimulationEventModel)
            .where(SimulationEventModel.simulation_id == simulation_id)
            .order_by(SimulationEventModel.sequence_number.asc())
        )
        return list(db.scalars(stmt).all())

