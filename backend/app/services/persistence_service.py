"""
Service: PersistenceService.
Handles dataset seeding, benchmark initialization, and database maintenance.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.network import Network
from app.repositories.network_repository import NetworkRepository
from app.schemas.network import NetworkImportRequest
from app.services.network_service import NetworkService
from app.core.logging import logger


class PersistenceService:
    """Service managing database seeding and persistence initialization."""

    @staticmethod
    def _find_dataset_path(filename: str) -> Optional[Path]:
        candidates = [
            Path(f"datasets/{filename}"),
            Path(f"c:/DM/CP/datasets/{filename}"),
            Path(__file__).resolve().parent.parent.parent.parent / "datasets" / filename
        ]
        for c in candidates:
            if c.exists():
                return c
        return None

    @staticmethod
    def seed_sample_network(db: Session, sample_path: Optional[str] = None) -> Optional[Network]:
        """
        Loads and imports datasets/sample_network.json into SQLite/PostgreSQL if no networks exist.
        """
        existing, total = NetworkRepository.list_all(db, limit=1)
        if total > 0:
            return existing[0]

        path = Path(sample_path) if sample_path else PersistenceService._find_dataset_path("sample_network.json")
        if not path or not path.exists():
            logger.warning(f"Sample network dataset not found at {path}")
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            import_req = NetworkImportRequest(
                name="Calibrated 18-Node Benchmark Network",
                description="Default second-year discrete mathematics benchmark infrastructure topology.",
                network_type="ENTERPRISE_DATACENTER",
                data=data
            )
            network = NetworkService.import_network(db, import_req)
            logger.info(f"Database successfully seeded with benchmark network '{network.name}' (ID: {network.id}).")
            return network
        except Exception as exc:
            logger.error(f"Failed to seed benchmark dataset: {exc}", exc_info=True)
            db.rollback()
            return None

    @staticmethod
    def seed_campus_network(db: Session, force_new: bool = False) -> Optional[Network]:
        """
        Seeds or retrieves the 12-node Campus Network demonstration scenario.
        """
        if not force_new:
            # Check if already present by name
            networks, total = NetworkRepository.list_all(db, limit=100)
            for net in networks:
                if "Campus IT Infrastructure" in net.name or "Campus_IT_Infrastructure" in net.name:
                    return net

        path = PersistenceService._find_dataset_path("campus_network.json")
        if not path or not path.exists():
            logger.warning("Campus demonstration dataset not found at datasets/campus_network.json")
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            import_req = NetworkImportRequest(
                name="Campus IT Infrastructure Demonstration",
                description="Official 12-node campus IT infrastructure demonstration topology for resilience modeling and bridge vulnerability analysis.",
                network_type="CAMPUS_ENTERPRISE",
                data=data
            )
            network = NetworkService.import_network(db, import_req)
            logger.info(f"Successfully loaded campus demonstration network (ID: {network.id}).")
            return network
        except Exception as exc:
            logger.error(f"Failed to seed campus demonstration dataset: {exc}", exc_info=True)
            db.rollback()
            return None

    @staticmethod
    def seed_cascading_network(db: Session, force_new: bool = False) -> Optional[Network]:
        """
        Seeds or retrieves the 5-node Controlled Cascading Failure scenario.
        """
        if not force_new:
            networks, total = NetworkRepository.list_all(db, limit=100)
            for net in networks:
                if "Cascading Failure Demonstration" in net.name or "Cascading_Failure" in net.name:
                    return net

        path = PersistenceService._find_dataset_path("cascading_demo_network.json")
        if not path or not path.exists():
            logger.warning("Cascading failure dataset not found at datasets/cascading_demo_network.json")
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            import_req = NetworkImportRequest(
                name="Cascading Failure Demonstration Topology",
                description="Controlled 5-node cascading failure topology illustrating dynamic load shifts, router overload, and cascade propagation.",
                network_type="WAN_CORE",
                data=data
            )
            network = NetworkService.import_network(db, import_req)
            logger.info(f"Successfully loaded cascading demonstration network (ID: {network.id}).")
            return network
        except Exception as exc:
            logger.error(f"Failed to seed cascading demonstration dataset: {exc}", exc_info=True)
            db.rollback()
            return None

    @staticmethod
    def seed_all_demonstrations(db: Session) -> Dict[str, Any]:
        """
        Ensures both demonstration scenarios and benchmark networks exist in the database.
        """
        sample = PersistenceService.seed_sample_network(db)
        campus = PersistenceService.seed_campus_network(db)
        cascading = PersistenceService.seed_cascading_network(db)
        return {
            "sample_network_id": sample.id if sample else None,
            "campus_network_id": campus.id if campus else None,
            "cascading_network_id": cascading.id if cascading else None,
        }
