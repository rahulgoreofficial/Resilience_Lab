"""
Unit and Integration Tests for Phase 5: Failure Simulation Engine.
Verifies dynamic failure simulation, snapshot isolation, combinatorial counting,
alternative route detection, and event tracking.
"""

import pytest
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_model import Node, Edge
from app.graph_engine.graph_validation import NodeNotFoundError, EdgeNotFoundError
from app.simulation import (
    simulate_node_failure,
    simulate_edge_failure,
    simulate_multiple_failures,
    simulation_manager,
    SimulationStatus,
    SimulationType,
    calculate_combination_count
)


@pytest.fixture
def linear_p4():
    """Returns linear path graph P4: A - B - C - D."""
    g = NetworkGraph.create("Linear_P4")
    for nid in ["A", "B", "C", "D"]:
        g.add_node(Node(node_id=nid, node_type="router"))
    g.add_edge(Edge(edge_id="e1", source="A", target="B", weight=2.0))
    g.add_edge(Edge(edge_id="e2", source="B", target="C", weight=3.0))
    g.add_edge(Edge(edge_id="e3", source="C", target="D", weight=1.0))
    return g


@pytest.fixture
def cycle_c4():
    """Returns 4-node cycle C4: A - B - C - D - A."""
    g = NetworkGraph.create("Cycle_C4")
    for nid in ["A", "B", "C", "D"]:
        g.add_node(Node(node_id=nid, node_type="switch"))
    g.add_edge(Edge(edge_id="e1", source="A", target="B", weight=1.0))
    g.add_edge(Edge(edge_id="e2", source="B", target="C", weight=1.0))
    g.add_edge(Edge(edge_id="e3", source="C", target="D", weight=1.0))
    g.add_edge(Edge(edge_id="e4", source="D", target="A", weight=1.0))
    return g


# --- Node Failure Tests ---

def test_node_failure_single_and_immutability(linear_p4):
    """Removing internal node B from P4 splits into 2 components; baseline is unmodified."""
    baseline_v = linear_p4.node_count
    baseline_e = linear_p4.edge_count

    result = simulate_node_failure(linear_p4, failed_node_ids=["B"])

    # Verify simulation result
    assert result.status == SimulationStatus.COMPLETED
    assert result.failed_nodes == ["B"]
    assert "B" not in [n for comp in result.connected_components for n in comp]
    assert result.connected_component_count == 2  # {A} and {C, D}
    assert result.active_node_count == 3
    assert result.active_edge_count == 1  # only e3 (C-D) remains

    # CRITICAL INVARIANT: Original network must remain intact
    assert linear_p4.node_count == baseline_v
    assert linear_p4.edge_count == baseline_e
    assert linear_p4.has_node("B")
    assert linear_p4.has_edge("A", "B")


def test_node_failure_invalid_node_rejected(linear_p4):
    """Attempting to fail a nonexistent node raises NodeNotFoundError."""
    with pytest.raises(NodeNotFoundError):
        simulate_node_failure(linear_p4, failed_node_ids=["NONEXISTENT_NODE"])


def test_node_failure_deduplication(linear_p4):
    """Duplicate node failure requests are safely deduplicated."""
    result = simulate_node_failure(linear_p4, failed_node_ids=["A", "A", "A"])
    assert result.failed_nodes == ["A"]
    assert result.active_node_count == 3


def test_node_failure_with_entry_points_and_services(linear_p4):
    """Evaluates service reachability from ingress entry points."""
    result = simulate_node_failure(
        graph=linear_p4,
        failed_node_ids=["B"],
        entry_points=["A"],
        critical_services=["D"]
    )
    # Since B failed, D in component {C, D} is unreachable from entry point A
    assert "D" in result.unreachable_nodes
    assert "D" in result.affected_critical_services
    assert result.reachable_critical_services == []


def test_node_failure_multiple_nodes(linear_p4):
    """Simultaneous removal of multiple nodes."""
    result = simulate_node_failure(linear_p4, failed_node_ids=["A", "D"])
    assert result.active_node_count == 2
    assert result.connected_components == [["B", "C"]]


# --- Edge Failure Tests ---

def test_edge_failure_bridge_disconnection(linear_p4):
    """Removing bridge e2 (B-C) disconnects P4 into 2 components with no alternative route."""
    result = simulate_edge_failure(linear_p4, failed_edges=["e2"])

    assert result.status == SimulationStatus.COMPLETED
    assert result.failed_edges == ["e2"]
    assert result.connected_component_count == 2
    
    # Check alternative route analysis
    alt_info = result.metrics["alternative_routes"]["e2"]
    assert alt_info["alternative_path_exists"] is False
    assert alt_info["alternative_path"] == []


def test_edge_failure_cycle_alternative_path(cycle_c4):
    """Removing e1 (A-B) in cycle C4 preserves connectivity via alternative route A-D-C-B."""
    result = simulate_edge_failure(cycle_c4, failed_edges=["e1"])

    assert result.connected_component_count == 1
    alt_info = result.metrics["alternative_routes"]["e1"]
    assert alt_info["alternative_path_exists"] is True
    assert alt_info["alternative_path"] == ["A", "D", "C", "B"]
    assert alt_info["alternative_cost"] == 3.0  # 1.0 + 1.0 + 1.0


def test_edge_failure_by_endpoints(cycle_c4):
    """Edge failure can be specified by endpoint dict or tuple."""
    result = simulate_edge_failure(cycle_c4, failed_edges=[{"source": "A", "target": "B"}])
    assert result.failed_edges == ["e1"]


def test_edge_failure_invalid_edge_rejected(cycle_c4):
    """Attempting to fail a nonexistent edge raises EdgeNotFoundError."""
    with pytest.raises(EdgeNotFoundError):
        simulate_edge_failure(cycle_c4, failed_edges=["nonexistent_edge_id"])


# --- Multiple Failures & Combinatorics Tests ---

def test_multiple_failure_cumulative_effect(linear_p4):
    """Combined node and edge failure computes exact cumulative impact."""
    result = simulate_multiple_failures(
        graph=linear_p4,
        failed_node_ids=["A"],
        failed_edges=["e3"]  # link between C and D
    )

    # Active nodes should be B, C, D (3 nodes)
    assert result.active_node_count == 3
    # After removing e3 and node A (and its edge e1), only e2 (B-C) remains active
    assert result.active_edge_count == 1
    # Components: {B, C} and {D}
    assert result.connected_component_count == 2


def test_combinatorial_counting():
    """Verifies binomial coefficient C(n, k) = n! / (k!(n-k)!)."""
    assert calculate_combination_count(10, 0) == 1
    assert calculate_combination_count(10, 1) == 10
    assert calculate_combination_count(10, 2) == 45
    assert calculate_combination_count(10, 3) == 120
    assert calculate_combination_count(5, 5) == 1
    assert calculate_combination_count(5, 6) == 0


def test_chronological_event_log(linear_p4):
    """Verifies that simulation events follow the required chronological order."""
    result = simulate_node_failure(linear_p4, failed_node_ids=["B"])
    event_names = [e["event"] for e in result.events]
    assert event_names[0] == "simulation_started"
    assert "node_failed" in event_names
    assert "connectivity_recalculated" in event_names
    assert event_names[-1] == "simulation_completed"


def test_simulation_manager_orchestration(linear_p4):
    """SimulationManager registers and retrieves simulation results by UUID."""
    res = simulation_manager.run_node_failure(linear_p4, failed_node_ids=["C"])
    retrieved = simulation_manager.get_simulation(res.simulation_id)
    assert retrieved is not None
    assert retrieved.simulation_id == res.simulation_id
    assert retrieved.failed_nodes == ["C"]

