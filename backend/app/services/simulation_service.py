"""
Service: SimulationService.
Coordinates execution of failure simulations with persistent network snapshots,
database tracking of execution state, event recording, and live WebSocket broadcasts.
"""

import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from app.models.simulation import SimulationModel
from app.repositories.simulation_repository import SimulationRepository
from app.services.network_service import NetworkService
from app.graph_engine.graph_builder import NetworkGraph
from app.simulation import (
    simulate_node_failure,
    simulate_edge_failure,
    simulate_multiple_failures,
    simulate_random_failure,
    simulate_targeted_failure,
    simulate_cascading_failure,
    ws_manager
)
from app.core.exceptions import SimulationNotFoundError, BadRequestError
from app.core.logging import logger


class SimulationService:
    """Service layer orchestrating simulation execution and database persistence."""

    @staticmethod
    def _execute_and_persist(
        db: Session,
        sim_id: str,
        network_id: str,
        snapshot_id: Optional[str],
        sim_type: str,
        config: Dict[str, Any],
        engine_runner
    ) -> Dict[str, Any]:
        """
        Executes a simulation engine function, records lifecycle transitions,
        persists events, updates final results, and notifies WebSocket subscribers.
        """
        sim_model = SimulationModel(
            id=sim_id,
            network_id=network_id,
            snapshot_id=snapshot_id,
            simulation_type=sim_type,
            status="running",
            configuration=config,
            random_seed=config.get("random_seed"),
            started_at=datetime.now(timezone.utc)
        )
        SimulationRepository.create_simulation(db, sim_model)
        db.commit()

        # Emit simulation_started event
        start_event_data = {"simulation_id": sim_id, "type": sim_type, "status": "running"}
        SimulationRepository.add_event(db, sim_id, "simulation_started", start_event_data)
        db.commit()

        try:
            # Execute mathematical simulation engine
            raw_result = engine_runner()

            result_dict = raw_result.to_dict() if hasattr(raw_result, "to_dict") else raw_result

            # Persist individual execution events into simulation_events table
            events_list = result_dict.get("events", [])
            for ev in events_list:
                ev_name = ev.get("event", "event")
                SimulationRepository.add_event(db, sim_id, ev_name, ev)

            # Mark completed
            SimulationRepository.update_simulation_status(
                db=db,
                simulation_id=sim_id,
                status="completed",
                results=result_dict
            )
            db.commit()

            # Schedule live notification
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(ws_manager.broadcast_event(sim_id, {
                    "event": "simulation_completed",
                    "simulation_id": sim_id,
                    "status": "completed"
                }))
            except (RuntimeError, Exception):
                pass

            return result_dict

        except Exception as exc:
            logger.error(f"Simulation '{sim_id}' failed: {exc}", exc_info=True)
            SimulationRepository.add_event(db, sim_id, "simulation_failed", {"error": str(exc)})
            SimulationRepository.update_simulation_status(
                db=db,
                simulation_id=sim_id,
                status="failed",
                error_summary=str(exc)
            )
            db.commit()
            raise

    @staticmethod
    def run_node_failure(
        db: Session,
        network_id: str,
        failed_node_ids: List[str],
        entry_points: Optional[List[str]] = None,
        critical_services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        snapshot = NetworkService.create_snapshot(db, network_id)
        graph_engine = NetworkGraph.from_dict(snapshot.graph_snapshot)
        sim_id = str(uuid.uuid4())

        config = {
            "failed_node_ids": failed_node_ids,
            "entry_points": entry_points or [],
            "critical_services": critical_services or []
        }

        return SimulationService._execute_and_persist(
            db=db,
            sim_id=sim_id,
            network_id=network_id,
            snapshot_id=snapshot.id,
            sim_type="node_failure",
            config=config,
            engine_runner=lambda: simulate_node_failure(
                graph=graph_engine,
                failed_node_ids=failed_node_ids,
                entry_points=entry_points,
                critical_services=critical_services,
                simulation_id=sim_id
            )
        )

    @staticmethod
    def run_edge_failure(
        db: Session,
        network_id: str,
        failed_edges: List[Any],
        entry_points: Optional[List[str]] = None,
        critical_services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        snapshot = NetworkService.create_snapshot(db, network_id)
        graph_engine = NetworkGraph.from_dict(snapshot.graph_snapshot)
        sim_id = str(uuid.uuid4())

        config = {
            "failed_edges": failed_edges,
            "entry_points": entry_points or [],
            "critical_services": critical_services or []
        }

        return SimulationService._execute_and_persist(
            db=db,
            sim_id=sim_id,
            network_id=network_id,
            snapshot_id=snapshot.id,
            sim_type="edge_failure",
            config=config,
            engine_runner=lambda: simulate_edge_failure(
                graph=graph_engine,
                failed_edges=failed_edges,
                entry_points=entry_points,
                critical_services=critical_services,
                simulation_id=sim_id
            )
        )

    @staticmethod
    def run_multiple_failures(
        db: Session,
        network_id: str,
        failed_node_ids: Optional[List[str]] = None,
        failed_edges: Optional[List[Any]] = None,
        entry_points: Optional[List[str]] = None,
        critical_services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        snapshot = NetworkService.create_snapshot(db, network_id)
        graph_engine = NetworkGraph.from_dict(snapshot.graph_snapshot)
        sim_id = str(uuid.uuid4())

        config = {
            "failed_node_ids": failed_node_ids or [],
            "failed_edges": failed_edges or [],
            "entry_points": entry_points or [],
            "critical_services": critical_services or []
        }

        return SimulationService._execute_and_persist(
            db=db,
            sim_id=sim_id,
            network_id=network_id,
            snapshot_id=snapshot.id,
            sim_type="multiple_failure",
            config=config,
            engine_runner=lambda: simulate_multiple_failures(
                graph=graph_engine,
                failed_node_ids=failed_node_ids,
                failed_edges=failed_edges,
                entry_points=entry_points,
                critical_services=critical_services,
                simulation_id=sim_id
            )
        )

    @staticmethod
    def run_random_failure(
        db: Session,
        network_id: str,
        failure_target: str = "NODES",
        failure_count: Optional[int] = None,
        failure_percentage: Optional[float] = None,
        num_trials: int = 10,
        random_seed: Optional[int] = 42,
        selection_method: str = "UNIFORM",
        entry_points: Optional[List[str]] = None,
        critical_services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        snapshot = NetworkService.create_snapshot(db, network_id)
        graph_engine = NetworkGraph.from_dict(snapshot.graph_snapshot)
        sim_id = str(uuid.uuid4())

        config = {
            "failure_target": failure_target,
            "failure_count": failure_count,
            "failure_percentage": failure_percentage,
            "num_trials": num_trials,
            "random_seed": random_seed,
            "selection_method": selection_method
        }

        return SimulationService._execute_and_persist(
            db=db,
            sim_id=sim_id,
            network_id=network_id,
            snapshot_id=snapshot.id,
            sim_type="random_failure",
            config=config,
            engine_runner=lambda: simulate_random_failure(
                graph=graph_engine,
                failure_target=failure_target,
                failure_count=failure_count,
                failure_percentage=failure_percentage,
                num_trials=num_trials,
                random_seed=random_seed,
                selection_method=selection_method,
                entry_points=entry_points,
                critical_services=critical_services,
                simulation_id=sim_id
            )
        )

    @staticmethod
    def run_targeted_failure(
        db: Session,
        network_id: str,
        strategy: str = "DEGREE",
        failure_count: Optional[int] = None,
        failure_percentage: Optional[float] = None,
        adaptive: bool = True,
        entry_points: Optional[List[str]] = None,
        critical_services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        snapshot = NetworkService.create_snapshot(db, network_id)
        graph_engine = NetworkGraph.from_dict(snapshot.graph_snapshot)
        sim_id = str(uuid.uuid4())

        config = {
            "strategy": strategy,
            "failure_count": failure_count,
            "failure_percentage": failure_percentage,
            "adaptive": adaptive
        }

        return SimulationService._execute_and_persist(
            db=db,
            sim_id=sim_id,
            network_id=network_id,
            snapshot_id=snapshot.id,
            sim_type="targeted_failure",
            config=config,
            engine_runner=lambda: simulate_targeted_failure(
                graph=graph_engine,
                strategy=strategy,
                failure_count=failure_count,
                failure_percentage=failure_percentage,
                adaptive=adaptive,
                entry_points=entry_points,
                critical_services=critical_services,
                simulation_id=sim_id
            )
        )

    @staticmethod
    def run_cascading_failure(
        db: Session,
        network_id: str,
        initial_failed_nodes: Optional[List[str]] = None,
        initial_failed_edges: Optional[List[Any]] = None,
        traffic_demands: Optional[List[Dict[str, Any]]] = None,
        overload_threshold: float = 1.0,
        max_simulation_rounds: int = 10,
        entry_points: Optional[List[str]] = None,
        critical_services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        snapshot = NetworkService.create_snapshot(db, network_id)
        graph_engine = NetworkGraph.from_dict(snapshot.graph_snapshot)
        sim_id = str(uuid.uuid4())

        config = {
            "initial_failed_nodes": initial_failed_nodes or [],
            "initial_failed_edges": initial_failed_edges or [],
            "traffic_demands": traffic_demands or [],
            "overload_threshold": overload_threshold,
            "max_rounds": max_simulation_rounds
        }

        return SimulationService._execute_and_persist(
            db=db,
            sim_id=sim_id,
            network_id=network_id,
            snapshot_id=snapshot.id,
            sim_type="cascading_failure",
            config=config,
            engine_runner=lambda: simulate_cascading_failure(
                graph=graph_engine,
                initial_failed_nodes=initial_failed_nodes,
                initial_failed_edges=initial_failed_edges,
                traffic_demands=traffic_demands,
                overload_threshold=overload_threshold,
                max_simulation_rounds=max_simulation_rounds,
                entry_points=entry_points,
                critical_services=critical_services,
                simulation_id=sim_id
            )
        )

    @staticmethod
    def get_simulation(db: Session, simulation_id: str) -> SimulationModel:
        sim = SimulationRepository.get_simulation(db, simulation_id)
        if not sim:
            raise SimulationNotFoundError(message=f"Simulation '{simulation_id}' not found.")
        return sim

    @staticmethod
    def list_simulations(
        db: Session,
        network_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[SimulationModel], int]:
        return SimulationRepository.list_simulations(db, network_id=network_id, skip=skip, limit=limit)

    @staticmethod
    def get_simulation_events(db: Session, simulation_id: str) -> List[dict]:
        sim = SimulationService.get_simulation(db, simulation_id)
        events = SimulationRepository.get_events(db, simulation_id)
        return [e.to_dict() for e in events]

