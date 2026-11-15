"""
Unit and Integration Tests for Phase 6: Resilience Analysis Engine.
Verifies LCC ratio, Pairwise Connectivity, Service Resilience Scores,
Criticality Rankings, Alternative Paths, and Scenario Comparisons.
"""

import pytest
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_model import Node, Edge
from app.resilience import (
    calculate_lcc_ratio,
    calculate_pairwise_connectivity,
    calculate_connectivity_loss,
    calculate_service_resilience_score,
    calculate_weighted_service_resilience_score,
    analyze_network_connectivity,
    analyze_node_criticality,
    analyze_edge_criticality,
    analyze_alternative_routes,
    compare_failure_scenarios,
    generate_resilience_report
)


@pytest.fixture
def complete_k5():
    """Complete graph K5: all pairs connected."""
    g = NetworkGraph.create("Complete_K5")
    for i in range(1, 6):
        g.add_node(Node(node_id=f"v{i}", node_type="server"))
    for i in range(1, 6):
        for j in range(i + 1, 6):
            g.add_edge(Edge(edge_id=f"e_{i}_{j}", source=f"v{i}", target=f"v{j}"))
    return g


@pytest.fixture
def linear_p5():
    """Linear graph P5: 1 - 2 - 3 - 4 - 5."""
    g = NetworkGraph.create("Linear_P5")
    for i in range(1, 6):
        g.add_node(Node(node_id=f"v{i}", node_type="router"))
    for i in range(1, 5):
        g.add_edge(Edge(edge_id=f"e{i}", source=f"v{i}", target=f"v{i+1}", weight=1.0))
    return g


@pytest.fixture
def cycle_c4():
    """Cycle C4: 1 - 2 - 3 - 4 - 1."""
    g = NetworkGraph.create("Cycle_C4")
    for i in range(1, 5):
        g.add_node(Node(node_id=f"v{i}", node_type="switch"))
    for i in range(1, 4):
        g.add_edge(Edge(edge_id=f"e{i}", source=f"v{i}", target=f"v{i+1}", weight=1.0))
    g.add_edge(Edge(edge_id="e4", source="v4", target="v1", weight=1.0))
    return g


# --- Resilience Metrics Tests ---

def test_lcc_ratio():
    assert calculate_lcc_ratio(5, 5) == 1.0
    assert calculate_lcc_ratio(3, 6) == 0.5
    assert calculate_lcc_ratio(0, 0) == 0.0


def test_pairwise_connectivity_complete_and_linear(complete_k5, linear_p5):
    # K5 has 5 nodes in 1 component: C(5, 2) / C(5, 2) = 1.0
    res_k5 = analyze_network_connectivity(complete_k5)
    assert res_k5["pairwise_connectivity"] == 1.0
    assert res_k5["connectivity_loss"] == 0.0

    # P5 is also connected: Pairwise connectivity = 1.0
    res_p5 = analyze_network_connectivity(linear_p5)
    assert res_p5["pairwise_connectivity"] == 1.0


def test_pairwise_connectivity_partitioned():
    """Two isolated components of size 3 and 2 in a 5-node graph."""
    # Connected pairs: C(3, 2) + C(2, 2) = 3 + 1 = 4.
    # Total possible pairs: C(5, 2) = 10.
    # Pairwise connectivity = 4 / 10 = 0.4
    pair_conn = calculate_pairwise_connectivity([3, 2], 5)
    assert pair_conn == 0.4
    assert calculate_connectivity_loss(pair_conn) == 0.6


def test_pairwise_connectivity_edge_cases():
    assert calculate_pairwise_connectivity([], 0) == 0.0
    assert calculate_pairwise_connectivity([1], 1) == 1.0
    assert calculate_pairwise_connectivity([1, 1, 1], 3) == 0.0  # 3 completely isolated nodes


def test_service_resilience_score():
    # All services reachable
    assert calculate_service_resilience_score(["s1", "s2"], ["s1", "s2"]) == 1.0
    # Half reachable
    assert calculate_service_resilience_score(["s1"], ["s1", "s2"]) == 0.5
    # None reachable
    assert calculate_service_resilience_score([], ["s1", "s2"]) == 0.0
    # Denominator zero -> None
    assert calculate_service_resilience_score([], []) is None


def test_weighted_service_resilience_score():
    importance = {"s1": 10.0, "s2": 2.0}
    # s1 lost, only s2 retained: 2.0 / 12.0 = 0.1667
    weighted_r = calculate_weighted_service_resilience_score(["s2"], ["s1", "s2"], importance)
    assert weighted_r == 0.1667


# --- Criticality Analysis Tests ---

def test_node_criticality_ranking(linear_p5):
    """In P5 (1-2-3-4-5), central node v3 has the largest structural impact."""
    rankings = analyze_node_criticality(linear_p5)
    assert len(rankings) == 5
    # Central cut-vertex v3 splits into two components of size 2 (C(2,2)+C(2,2)=2 pairs out of C(4,2)=6 pairs -> conn=0.3333, delta=0.6667)
    # Endpoints v1 and v5 split into size 4 (C(4,2)=6 pairs out of 6 -> conn=1.0, delta=0.0)
    top_node = rankings[0]
    assert top_node["node_id"] == "v3"
    assert top_node["is_articulation_point"] is True
    assert top_node["connectivity_impact"] > 0.6


def test_edge_criticality_ranking_cycle_vs_bridge(linear_p5, cycle_c4):
    """Every edge in P5 is a bridge; in C4 no edge is a bridge."""
    p5_edges = analyze_edge_criticality(linear_p5)
    assert all(e["is_bridge"] for e in p5_edges)
    # Removing e2 (2-3) or e3 (3-4) disconnects graph into components of size 2 and 3
    assert p5_edges[0]["connectivity_impact"] > 0.0

    c4_edges = analyze_edge_criticality(cycle_c4)
    assert all(not e["is_bridge"] for e in c4_edges)
    assert all(e["connectivity_impact"] == 0.0 for e in c4_edges)


# --- Alternative Path Analysis Tests ---

def test_alternative_routes(cycle_c4):
    """Evaluating route between v1 and v2 when e1 (v1-v2) is disabled."""
    routes = analyze_alternative_routes(
        graph=cycle_c4,
        flow_pairs=[("v1", "v2")],
        failed_edge_ids=["e1"]
    )
    assert len(routes) == 1
    r = routes[0]
    assert r["primary_route"] == ["v1", "v2"]
    assert r["primary_cost"] == 1.0
    assert r["impacted_by_failure"] is True
    assert r["alternative_route_available"] is True
    assert r["alternative_route"] == ["v1", "v4", "v3", "v2"]
    assert r["alternative_cost"] == 3.0


# --- Scenario Comparison Tests ---

def test_scenario_comparison(linear_p5):
    """Compare failure of central node v3 vs end node v1."""
    scenarios = [
        {"scenario_id": "scen_center", "name": "Center Failure", "failed_nodes": ["v3"]},
        {"scenario_id": "scen_leaf", "name": "Leaf Failure", "failed_nodes": ["v1"]}
    ]
    res = compare_failure_scenarios(linear_p5, scenarios)
    assert "baseline" in res
    assert len(res["scenarios"]) == 2

    scen_center = next(s for s in res["scenarios"] if s["scenario_id"] == "scen_center")
    scen_leaf = next(s for s in res["scenarios"] if s["scenario_id"] == "scen_leaf")

    # Center failure splits into 2 components; leaf failure leaves 1 component
    assert scen_center["component_count"] == 2
    assert scen_leaf["component_count"] == 1
    assert scen_center["delta_pairwise_connectivity"] > scen_leaf["delta_pairwise_connectivity"]


# --- Resilience Audit Report Tests ---

def test_generate_resilience_report(linear_p5):
    report = generate_resilience_report(linear_p5, top_k=3)
    assert report["network_name"] == "Linear_P5"
    assert report["structural_health_rating"] in ["MODERATE", "VULNERABLE"]
    assert report["single_points_of_failure"]["articulation_points_count"] == 3  # v2, v3, v4
    assert len(report["top_critical_nodes"]) == 3
    assert len(report["recommendations"]) > 0

