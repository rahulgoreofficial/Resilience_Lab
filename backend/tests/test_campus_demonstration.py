"""
Test Suite: Campus IT Infrastructure Demonstration & Network Resilience Hardening.
Validates the 12-node campus network topology, single points of failure (bridges),
C1-L1 disruption, L1-B1 backup redundancy, and candidate-link recommendation.
"""

import json
import pytest
from pathlib import Path
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_model import Node, Edge
from app.algorithms.connected_components import find_connected_components
from app.algorithms.articulation_points import find_articulation_points
from app.algorithms.bridges import find_bridges
from app.algorithms.shortest_path import dijkstra_shortest_path
from app.resilience.connectivity_analysis import analyze_network_connectivity
from app.services.analytics_service import AnalyticsService
from app.services.persistence_service import PersistenceService
from app.simulation.cascading_failure import simulate_cascading_failure


@pytest.fixture
def campus_graph() -> NetworkGraph:
    """Loads the canonical 12-node campus demonstration graph."""
    path = Path("datasets/campus_network.json")
    if not path.exists():
        path = Path("c:/DM/CP/datasets/campus_network.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return NetworkGraph.from_dict(data)


@pytest.fixture
def cascading_graph() -> NetworkGraph:
    """Loads the 5-node controlled cascading failure graph."""
    path = Path("datasets/cascading_demo_network.json")
    if not path.exists():
        path = Path("c:/DM/CP/datasets/cascading_demo_network.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return NetworkGraph.from_dict(data)


def test_campus_baseline_topology(campus_graph):
    """
    Step A Validation:
    - 12 vertices, 11 edges.
    - Exactly 1 connected component.
    - 11 bridges (tree topology).
    - 100% LCC ratio, 100% pairwise connectivity, 100% critical service reachability.
    """
    assert campus_graph.node_count == 12
    assert campus_graph.edge_count == 11

    comp_info = find_connected_components(campus_graph)
    assert comp_info["component_count"] == 1
    assert comp_info["giant_component_size"] == 12

    bridges_res = find_bridges(campus_graph)
    assert len(bridges_res["bridges"]) == 11

    ap_res = find_articulation_points(campus_graph)
    # Internal switch/router nodes are articulation points
    assert set(ap_res["articulation_points"]) == {"R1", "C1", "L1", "B1", "A1", "D1", "LMS"}

    entry_points = ["G1"]
    critical_services = ["LS1", "LS2", "AS1", "LMS"]

    baseline_analysis = analyze_network_connectivity(
        graph=campus_graph,
        entry_points=entry_points,
        critical_services=critical_services
    )

    assert baseline_analysis["lcc_ratio"] == 1.0
    assert baseline_analysis["pairwise_connectivity"] == 1.0
    assert len(baseline_analysis["reachable_critical_services"]) == 4
    assert len(baseline_analysis["unreachable_critical_services"]) == 0


def test_campus_c1_l1_failure_disruption(campus_graph):
    """
    Step C Validation:
    - Remove C1-L1 link on isolated simulation graph.
    - Results in 2 connected components with sizes 10 and 2.
    - Giant component size = 10.
    - LCC ratio = 10/12 = 83.33%.
    - Reachable critical services = 3/4 = 75% (LS1 is isolated).
    - Pairwise connectivity = (10*9 + 2*1) / (12*11) = 92/132 ≈ 69.70%.
    """
    g_sim = campus_graph.clone()
    assert g_sim.has_edge("C1", "L1")

    # Find edge id
    c1_l1_edge = None
    for e in g_sim.get_all_edges():
        if (e.source == "C1" and e.target == "L1") or (e.source == "L1" and e.target == "C1"):
            c1_l1_edge = e
            break
    assert c1_l1_edge is not None

    g_sim.remove_edge(c1_l1_edge.edge_id)

    comp_info = find_connected_components(g_sim)
    assert comp_info["component_count"] == 2

    comp_sizes = sorted([len(c) for c in comp_info["components"]])
    assert comp_sizes == [2, 10]

    # Verify component members
    lab_comp = next(c for c in comp_info["components"] if len(c) == 2)
    assert set(lab_comp) == {"L1", "LS1"}

    entry_points = ["G1"]
    critical_services = ["LS1", "LS2", "AS1", "LMS"]

    failure_analysis = analyze_network_connectivity(
        graph=g_sim,
        entry_points=entry_points,
        critical_services=critical_services,
        baseline_node_ids=campus_graph.get_node_ids()
    )

    # 1. LCC ratio = 10 / 12 = 83.333%
    assert round(failure_analysis["lcc_ratio"], 4) == round(10.0 / 12.0, 4)

    # 2. Pairwise connectivity = 92 / 132 ≈ 0.6970
    expected_pairwise = (10 * 9 + 2 * 1) / (12 * 11)
    assert round(failure_analysis["pairwise_connectivity"], 4) == round(expected_pairwise, 4)

    # 3. Critical services reachability = 3 of 4 = 75%
    reachable_svcs = set(failure_analysis["reachable_critical_services"])
    unreachable_svcs = set(failure_analysis["unreachable_critical_services"])
    assert reachable_svcs == {"LS2", "AS1", "LMS"}
    assert unreachable_svcs == {"LS1"}


def test_campus_network_improvement_l1_b1(campus_graph):
    """
    Step D & E Validation:
    - Add candidate backup edge L1-B1.
    - C1-L1 and C1-B1 become 2-edge connected (part of cycle C1-L1-B1-C1).
    - Re-simulate C1-L1 disruption on improved graph:
      - 1 connected component.
      - 100% LCC ratio.
      - 100% Pairwise connectivity.
      - 4 of 4 critical services reachable (100%).
      - Alternative path exists: G1 -> R1 -> C1 -> B1 -> L1 -> LS1.
    """
    g_improved = campus_graph.clone()
    backup_edge = Edge(
        edge_id="E_L1_B1",
        source="L1",
        target="B1",
        weight=1.0,
        capacity=500.0,
        latency=4.0,
        metadata={"label": "Laboratory-Library Redundant Trunk", "backup": True}
    )
    g_improved.add_edge(backup_edge)

    assert g_improved.edge_count == 12

    # Check bridges: C1-L1 and C1-B1 are no longer bridges
    bridges_res = find_bridges(g_improved)
    bridge_pairs = {tuple(sorted(b)) for b in bridges_res["bridges"]}
    assert tuple(sorted(("C1", "L1"))) not in bridge_pairs
    assert tuple(sorted(("C1", "B1"))) not in bridge_pairs
    assert tuple(sorted(("L1", "B1"))) not in bridge_pairs

    # Now remove C1-L1 on improved graph
    c1_l1_edge = next(
        e for e in g_improved.get_all_edges()
        if (e.source == "C1" and e.target == "L1") or (e.source == "L1" and e.target == "C1")
    )
    g_improved.remove_edge(c1_l1_edge.edge_id)

    comp_info = find_connected_components(g_improved)
    assert comp_info["component_count"] == 1
    assert comp_info["giant_component_size"] == 12

    entry_points = ["G1"]
    critical_services = ["LS1", "LS2", "AS1", "LMS"]

    improved_failure_analysis = analyze_network_connectivity(
        graph=g_improved,
        entry_points=entry_points,
        critical_services=critical_services,
        baseline_node_ids=campus_graph.get_node_ids()
    )

    assert improved_failure_analysis["lcc_ratio"] == 1.0
    assert improved_failure_analysis["pairwise_connectivity"] == 1.0
    assert len(improved_failure_analysis["reachable_critical_services"]) == 4
    assert len(improved_failure_analysis["unreachable_critical_services"]) == 0

    # Verify alternative path to LS1 via B1
    alt_path_res = dijkstra_shortest_path(g_improved, "G1", "LS1", weight_attribute="weight")
    assert alt_path_res["path"] == ["G1", "R1", "C1", "B1", "L1", "LS1"]


def test_candidate_link_evaluation_ranking(campus_graph):
    """
    Validation of automatic candidate-link analysis:
    - Evaluates non-existent edges.
    - Detects L1-B1 as a high-impact candidate against C1-L1 failure.
    - Verifies positive Delta LCC, Delta Pairwise, and bridges eliminated.
    """
    result = AnalyticsService.evaluate_candidate_backup_links(
        graph_data=campus_graph.to_dict(),
        target_bridge_id="E_C1_L1",
        target_failure_nodes=["C1", "L1"],
        entry_points=["G1"],
        critical_services=["LS1", "LS2", "AS1", "LMS"],
        max_recommendations=10
    )

    assert result["total_candidates_evaluated"] > 0
    recommendations = result["recommendations"]
    assert len(recommendations) > 0

    # Top recommendation should connect L1 or LS1 to a switch/router that preserves connectivity
    cand_pairs = [tuple(sorted((c["source"], c["target"]))) for c in recommendations[:5]]
    assert tuple(sorted(("L1", "B1"))) in cand_pairs

    # Verify L1-B1 metrics in recommendations
    l1_b1_cand = next(c for c in recommendations if tuple(sorted((c["source"], c["target"]))) == tuple(sorted(("L1", "B1"))))
    assert l1_b1_cand["delta_lcc_percent"] > 16.0  # +16.67%
    assert l1_b1_cand["delta_pairwise_percent"] > 30.0  # +30.30%
    assert l1_b1_cand["delta_critical_services"] == 1  # Restores LS1
    assert l1_b1_cand["resulting_components"] == 1
    assert "Engineering Deployment Caveat" in l1_b1_cand["engineering_caveat"]


def test_cascading_failure_controlled_scenario(cascading_graph):
    """
    Section 6 Validation:
    - PR1 carries normal traffic with capacity 500.
    - Demand from CL1 to SRV_APP is 300.
    - When PR1 fails, traffic redirects to BR1.
    - BR1 background load (100) + rerouted traffic (300) = 400 > 350 (capacity).
    - In Round 2, BR1 fails from overload.
    - In Round 3, destination service SRV_APP becomes unreachable.
    """
    sim_res = simulate_cascading_failure(
        graph=cascading_graph,
        initial_failed_nodes=["PR1"],
        traffic_demands=[{"source": "CL1", "target": "SRV_APP", "amount": 300.0}],
        overload_threshold=1.0,
        max_simulation_rounds=5
    )

    timeline = sim_res.timeline
    assert len(timeline) >= 2

    # Round 1: PR1 was initial failure
    r1 = timeline[1]
    assert "PR1" in r1["newly_failed_nodes"]

    # Round 2: BR1 received the rerouted traffic, exceeding its capacity of 350
    r2 = timeline[2]
    assert "BR1" in r2["newly_failed_nodes"]

    # Final state: Both PR1 and BR1 are dead
    assert "PR1" in sim_res.failed_nodes
    assert "BR1" in sim_res.failed_nodes

    # Check unserved traffic in timeline: all 300 traffic becomes unserved
    final_round = timeline[-1]
    assert final_round["traffic_served"] == 0.0
    assert final_round["traffic_unserved"] == 300.0

