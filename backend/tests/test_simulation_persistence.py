"""
Tests for Simulation Persistence, Snapshot Immutability, and Recovery (Phase 8).
Verifies that simulations create frozen snapshots, persist event logs, and recover from crashes.
"""

from datetime import datetime, timezone
import pytest
from sqlalchemy import select

from app.models.network import Network
from app.models.node import NodeModel
from app.models.edge import EdgeModel
from app.models.simulation import SimulationModel
from app.models.network_snapshot import NetworkSnapshot
from app.services.network_service import NetworkService
from app.services.simulation_service import SimulationService
from app.database.init_db import recover_interrupted_simulations
from app.schemas.network import NetworkCreate
from app.schemas.node import NodeCreate
from app.schemas.edge import EdgeCreate


def _setup_triangle_network(db):
    """Helper to create a 3-node connected network: R1 - R2 - S1 - R1."""
    net = NetworkService.create_network(db, NetworkCreate(name="Persistence Test Net"))
    net_id = net.id

    NetworkService.add_node(db, net_id, NodeCreate(node_id="R1", node_type="router"))
    NetworkService.add_node(db, net_id, NodeCreate(node_id="R2", node_type="router"))
    NetworkService.add_node(db, net_id, NodeCreate(node_id="S1", node_type="switch"))

    NetworkService.add_edge(db, net_id, EdgeCreate(edge_id="e1", source_node_id="R1", target_node_id="R2", weight=1.0))
    NetworkService.add_edge(db, net_id, EdgeCreate(edge_id="e2", source_node_id="R2", target_node_id="S1", weight=2.0))
    NetworkService.add_edge(db, net_id, EdgeCreate(edge_id="e3", source_node_id="S1", target_node_id="R1", weight=3.0))

    return net_id


def test_simulation_execution_creates_snapshot_and_persists(db_session):
    """Verify that running a simulation creates an immutable snapshot and persists results."""
    net_id = _setup_triangle_network(db_session)

    # Run node failure simulation
    result = SimulationService.run_node_failure(
        db=db_session,
        network_id=net_id,
        failed_node_ids=["R2"]
    )
    assert result is not None
    assert "simulation_id" in result
    sim_id = result["simulation_id"]

    # Retrieve persisted simulation model
    sim = SimulationService.get_simulation(db_session, sim_id)
    assert sim.id == sim_id
    assert sim.network_id == net_id
    assert sim.status == "completed"
    assert sim.simulation_type == "node_failure"
    assert sim.snapshot_id is not None
    assert sim.started_at is not None
    assert sim.completed_at is not None
    assert sim.results is not None
    assert sim.results["failed_nodes"] == ["R2"]

    # Verify snapshot
    snapshot = db_session.get(NetworkSnapshot, sim.snapshot_id)
    assert snapshot is not None
    assert snapshot.network_id == net_id
    assert snapshot.snapshot_hash is not None
    assert len(snapshot.snapshot_hash) >= 16


def test_snapshot_immutability_on_network_modifications(db_session):
    """
    Verify that subsequent mutations to a network do not mutate or invalidate
    historical snapshots or historical simulation records.
    """
    net_id = _setup_triangle_network(db_session)

    # 1. Run simulation S1 on initial topology
    res1 = SimulationService.run_node_failure(
        db=db_session,
        network_id=net_id,
        failed_node_ids=["R1"]
    )
    sim1_id = res1["simulation_id"]
    sim1 = SimulationService.get_simulation(db_session, sim1_id)
    snap1 = db_session.get(NetworkSnapshot, sim1.snapshot_id)
    orig_hash = snap1.snapshot_hash
    orig_graph = dict(snap1.graph_snapshot)

    # 2. Mutate network: add node, add edge, delete node
    NetworkService.add_node(db_session, net_id, NodeCreate(node_id="N_NEW", node_type="server"))
    NetworkService.add_edge(
        db_session,
        net_id,
        EdgeCreate(edge_id="e_new", source_node_id="R2", target_node_id="N_NEW")
    )
    NetworkService.delete_node(db_session, net_id, "S1")

    # Verify network version increased
    current_net = NetworkService.get_network(db_session, net_id)
    assert current_net.version > snap1.network_version

    # 3. Verify snapshot snap1 remained completely unchanged
    db_session.refresh(snap1)
    assert snap1.snapshot_hash == orig_hash
    assert snap1.graph_snapshot == orig_graph
    assert "N_NEW" not in [n["node_id"] for n in snap1.graph_snapshot["nodes"]]
    assert "S1" in [n["node_id"] for n in snap1.graph_snapshot["nodes"]]


def test_simulation_event_chronological_sequence(db_session):
    """Verify that simulation events are persisted with monotonically increasing sequence numbers."""
    net_id = _setup_triangle_network(db_session)

    res = SimulationService.run_node_failure(
        db=db_session,
        network_id=net_id,
        failed_node_ids=["S1"]
    )
    sim_id = res["simulation_id"]

    events = SimulationService.get_simulation_events(db_session, sim_id)
    assert len(events) >= 1

    # Verify sequence numbers are 1, 2, 3...
    seq_numbers = [e["sequence_number"] for e in events]
    assert seq_numbers == list(range(1, len(events) + 1))
    assert events[0]["event_type"] == "simulation_started"


def test_startup_recovery_interrupted_simulations(db_session):
    """
    Verify that simulations left in 'running' or 'queued' state prior to backend restart
    are updated to 'interrupted' by recover_interrupted_simulations.
    """
    net_id = _setup_triangle_network(db_session)

    # Insert an in-flight simulation manually
    sim_running = SimulationModel(
        network_id=net_id,
        simulation_type="random_failure",
        status="running",
        configuration={"num_trials": 100},
        started_at=datetime.now(timezone.utc)
    )
    sim_queued = SimulationModel(
        network_id=net_id,
        simulation_type="targeted_failure",
        status="queued",
        configuration={"strategy": "degree"}
    )
    sim_completed = SimulationModel(
        network_id=net_id,
        simulation_type="node_failure",
        status="completed"
    )
    db_session.add_all([sim_running, sim_queued, sim_completed])
    db_session.commit()

    # Execute recovery routine
    recovered_count = recover_interrupted_simulations(db_session)
    assert recovered_count == 2

    # Refresh models
    db_session.refresh(sim_running)
    db_session.refresh(sim_queued)
    db_session.refresh(sim_completed)

    assert sim_running.status == "interrupted"
    assert "interrupted by backend restart" in sim_running.error_summary
    assert sim_running.completed_at is not None

    assert sim_queued.status == "interrupted"
    assert sim_completed.status == "completed"  # Unaffected


def test_simulation_history_and_retrieval(db_session):
    """Verify listing and retrieving historical simulations for a network."""
    net_id = _setup_triangle_network(db_session)

    # Run two different simulations
    SimulationService.run_node_failure(db_session, net_id, failed_node_ids=["R1"])
    SimulationService.run_edge_failure(db_session, net_id, failed_edges=[["R1", "R2"]])

    # List simulations for network
    sims, total = SimulationService.list_simulations(db_session, network_id=net_id)
    assert total == 2
    assert len(sims) == 2
    types = {s.simulation_type for s in sims}
    assert types == {"node_failure", "edge_failure"}
