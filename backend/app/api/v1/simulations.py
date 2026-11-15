"""
Simulation Execution and History Endpoints.
Integrates failure simulation engines with database persistence, snapshotting, and event streaming.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_database, get_pagination
from app.schemas.common import PaginationParams, PaginatedResponse
from app.schemas.simulation_schema import (
    NodeFailureRequest,
    EdgeFailureRequest,
    MultipleFailureRequest,
    RandomFailureRequest,
    TargetedFailureRequest,
    CascadingFailureRequest
)
from app.schemas.simulation import SimulationRecordResponse, SimulationEventRecordResponse
from app.services.simulation_service import SimulationService
from app.services.network_service import NetworkService
from app.schemas.network import NetworkImportRequest

router = APIRouter(tags=["Simulations"])


def _resolve_network_id(db: Session, graph_payload) -> str:
    """Helper to ensure simulation has a persistent network snapshot."""
    if not graph_payload:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'network_id' query parameter or 'graph' payload must be provided."
        )
    import_req = NetworkImportRequest(
        name=graph_payload.name or "Ad-hoc Simulation Network",
        description="Auto-persisted for simulation reproducibility",
        data=graph_payload.model_dump()
    )
    net = NetworkService.import_network(db, import_req)
    return net.id


@router.post("/simulations/node-failure", status_code=status.HTTP_200_OK)
def simulate_node_failure(
    payload: NodeFailureRequest,
    network_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Simulates dynamic node failure and records execution in database."""
    target_net_id = network_id or _resolve_network_id(db, payload.graph)
    return SimulationService.run_node_failure(
        db=db,
        network_id=target_net_id,
        failed_node_ids=payload.failed_node_ids,
        entry_points=payload.entry_points,
        critical_services=payload.critical_services
    )


@router.post("/simulations/edge-failure", status_code=status.HTTP_200_OK)
def simulate_edge_failure(
    payload: EdgeFailureRequest,
    network_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Simulates communication link severance and alternative route search."""
    target_net_id = network_id or _resolve_network_id(db, payload.graph)
    return SimulationService.run_edge_failure(
        db=db,
        network_id=target_net_id,
        failed_edges=payload.failed_edges,
        entry_points=payload.entry_points,
        critical_services=payload.critical_services
    )


@router.post("/simulations/multiple-failure", status_code=status.HTTP_200_OK)
def simulate_multiple_failure(
    payload: MultipleFailureRequest,
    network_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Simulates simultaneous combinations of node and edge failures."""
    target_net_id = network_id or _resolve_network_id(db, payload.graph)
    return SimulationService.run_multiple_failures(
        db=db,
        network_id=target_net_id,
        failed_node_ids=payload.failed_node_ids,
        failed_edges=payload.failed_edges,
        entry_points=payload.entry_points,
        critical_services=payload.critical_services
    )


@router.post("/simulations/random", status_code=status.HTTP_200_OK)
def simulate_random(
    payload: RandomFailureRequest,
    network_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Executes stochastic percolation failure trials with reproducibility seed."""
    target_net_id = network_id or _resolve_network_id(db, payload.graph)
    return SimulationService.run_random_failure(
        db=db,
        network_id=target_net_id,
        failure_target=payload.failure_target,
        failure_count=payload.failure_count,
        failure_percentage=payload.failure_percentage,
        num_trials=payload.num_trials,
        random_seed=payload.random_seed,
        selection_method=payload.selection_method,
        entry_points=payload.entry_points,
        critical_services=payload.critical_services
    )


@router.post("/simulations/targeted", status_code=status.HTTP_200_OK)
def simulate_targeted(
    payload: TargetedFailureRequest,
    network_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Executes targeted adversarial attacks (Degree, Articulation Point, or Impact)."""
    target_net_id = network_id or _resolve_network_id(db, payload.graph)
    return SimulationService.run_targeted_failure(
        db=db,
        network_id=target_net_id,
        strategy=payload.strategy,
        failure_count=payload.failure_count,
        failure_percentage=payload.failure_percentage,
        adaptive=payload.adaptive,
        entry_points=payload.entry_points,
        critical_services=payload.critical_services
    )


@router.post("/simulations/cascading", status_code=status.HTTP_200_OK)
def simulate_cascading(
    payload: CascadingFailureRequest,
    network_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Executes capacity-based cascading traffic redistribution."""
    target_net_id = network_id or _resolve_network_id(db, payload.graph)
    return SimulationService.run_cascading_failure(
        db=db,
        network_id=target_net_id,
        initial_failed_nodes=payload.initial_failed_nodes,
        initial_failed_edges=payload.initial_failed_edges,
        traffic_demands=payload.traffic_demands,
        overload_threshold=payload.overload_threshold,
        max_simulation_rounds=payload.max_simulation_rounds,
        entry_points=payload.entry_points,
        critical_services=payload.critical_services
    )


@router.get("/simulations", response_model=PaginatedResponse[SimulationRecordResponse])
def list_simulations(
    network_id: Optional[str] = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_database)
) -> PaginatedResponse[SimulationRecordResponse]:
    """Lists historical simulations, optionally filtered by network_id."""
    sims, total = SimulationService.list_simulations(
        db=db,
        network_id=network_id,
        skip=pagination.skip,
        limit=pagination.limit
    )
    items = [
        SimulationRecordResponse(
            id=s.id,
            network_id=s.network_id,
            snapshot_id=s.snapshot_id,
            simulation_type=s.simulation_type,
            status=s.status,
            configuration=s.configuration,
            random_seed=s.random_seed,
            results=s.results,
            error_summary=s.error_summary,
            started_at=s.started_at.isoformat() if s.started_at else None,
            completed_at=s.completed_at.isoformat() if s.completed_at else None,
            created_at=s.created_at.isoformat()
        )
        for s in sims
    ]
    return PaginatedResponse(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get("/networks/{network_id}/simulations", response_model=PaginatedResponse[SimulationRecordResponse])
def list_network_simulations(
    network_id: str,
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_database)
) -> PaginatedResponse[SimulationRecordResponse]:
    """Lists simulation executions performed on a specific network."""
    return list_simulations(network_id=network_id, pagination=pagination, db=db)


@router.get("/simulations/{simulation_id}", response_model=SimulationRecordResponse)
def get_simulation(
    simulation_id: str,
    db: Session = Depends(get_database)
) -> SimulationRecordResponse:
    """Retrieves full simulation execution record by UUID."""
    sim = SimulationService.get_simulation(db, simulation_id)
    return SimulationRecordResponse(
        id=sim.id,
        network_id=sim.network_id,
        snapshot_id=sim.snapshot_id,
        simulation_type=sim.simulation_type,
        status=sim.status,
        configuration=sim.configuration,
        random_seed=sim.random_seed,
        results=sim.results,
        error_summary=sim.error_summary,
        started_at=sim.started_at.isoformat() if sim.started_at else None,
        completed_at=sim.completed_at.isoformat() if sim.completed_at else None,
        created_at=sim.created_at.isoformat()
    )


@router.get("/simulations/{simulation_id}/results")
def get_simulation_results(
    simulation_id: str,
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Retrieves computed resilience results and metrics for a simulation."""
    sim = SimulationService.get_simulation(db, simulation_id)
    return {
        "simulation_id": sim.id,
        "status": sim.status,
        "results": sim.results,
        "error_summary": sim.error_summary
    }


@router.get("/simulations/{simulation_id}/events", response_model=List[SimulationEventRecordResponse])
def get_simulation_events(
    simulation_id: str,
    db: Session = Depends(get_database)
) -> List[SimulationEventRecordResponse]:
    """Retrieves chronological execution events for a simulation."""
    events = SimulationService.get_simulation_events(db, simulation_id)
    return [
        SimulationEventRecordResponse(
            sequence_number=e["sequence_number"],
            event_type=e["event_type"],
            event_data=e["event_data"],
            created_at=e["created_at"]
        )
        for e in events
    ]

