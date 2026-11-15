"""
Database Initialization and Startup Recovery Routines.
Provides graceful recovery of in-flight simulations following server restarts.
"""

import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database.base import Base

logger = logging.getLogger(__name__)


def init_db(engine) -> None:
    """Initializes tables for development/testing if needed."""
    import app.models  # Ensure all models are registered with Base.metadata
    Base.metadata.create_all(bind=engine)


def recover_interrupted_simulations(db: Session) -> int:
    """
    Scans for simulations left in 'running' or 'queued' state prior to backend restart,
    and updates them to 'interrupted' to prevent stale running states.
    
    Returns:
        int: Number of simulations recovered.
    """
    try:
        from app.models.simulation import SimulationModel
        interrupted = db.query(SimulationModel).filter(
            SimulationModel.status.in_(["running", "queued"])
        ).all()

        count = len(interrupted)
        for sim in interrupted:
            sim.status = "interrupted"
            sim.error_summary = "Simulation interrupted by backend restart"
            sim.completed_at = datetime.now(timezone.utc)

        if count > 0:
            db.commit()
            logger.info(f"Startup recovery: Marked {count} unfinished simulation(s) as 'interrupted'.")
        return count
    except Exception as exc:
        logger.warning(f"Startup recovery skipped (tables may not exist yet): {exc}")
        db.rollback()
        return 0

