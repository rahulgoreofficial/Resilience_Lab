"""
Unit and Integration Tests for Phase 7: Advanced Failure Simulation Engine.
Verifies Random Failure (Monte Carlo percolation), Targeted Adversarial Attacks,
Traffic Redistribution, and Cascading Overload Failures.
"""

import pytest
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_model import Node, Edge
from app.graph_engine.graph_validation import NodeNotFoundError, GraphException
from app.simulation import (
    TrafficDemand,
    route_traffic_flows,
    simulate_cascading_failure,
    simulate_random_failure,
    simulate_targeted_failure
)


@pytest.fixture
def diamond_network():
    """
    Diamond bottleneck network:
        S -> A (cap 50) -> D
        S -> B (cap 10) -> D
    S has 2 paths to D: via A (primary, weight 1) and via B (secondary, weight 2).
    """
    g = NetworkGraph.create("Diamond_Bottleneck")
    g.add_node(Node(node_id="S", node_type="gateway", capacity=100.0, current_load=0.0))
    g.add_node(Node(node_id="A", node_type="router", capacity=50.0, current_load=0.0))
    g.add_node(Node(node_id="B", node_type="router", capacity=15.0, current_load=0.0))
    g.add_node(Node(node_id="D", node_type="server", capacity=100.0, current_load=0.0))

    g.add_edge(Edge(edge_id="e_sa", source="S", target="A", weight=1.0, capacity=60.0))
    g.add_edge(Edge(edge_id="e_ad", source="A", target="D", weight=1.0, capacity=60.0))
    g.add_edge(Edge(edge_id="e_sb", source="S", target="B", weight=2.0, capacity=20.0))
    g.add_edge(Edge(edge_id="e_bd", source="B", target="D", weight=2.0, capacity=20.0))
    return g


@pytest.fixture
def star_network():
    """Star network S6: Central hub H with leaves L1..L5."""
    g = NetworkGraph.create("Star_S6")
    g.add_node(Node(node_id="H", node_type="switch", capacity=200.0, failure_probability=0.05))
    for i in range(1, 6):
        g.add_node(Node(node_id=f"L{i}", node_type="server", capacity=50.0, failure_probability=0.01))
        g.add_edge(Edge(edge_id=f"e{i}", source="H", target=f"L{i}", weight=1.0))
    return g


# --- Traffic Flow & Routing Tests ---

def test_traffic_routing_shortest_path(diamond_network):
    demands = [TrafficDemand(source="S", destination="D", amount=25.0)]
    routing = route_traffic_flows(diamond_network, demands)

    assert routing["total_traffic_demanded"] == 25.0
    assert routing["total_traffic_served"] == 25.0
    assert routing["total_traffic_unserved"] == 0.0

    # Path should take S -> A -> D (cost 2) over S -> B -> D (cost 4)
    served = routing["served_demands"][0]
    assert served["path"] == ["S", "A", "D"]
    assert routing["node_loads"]["A"] == 25.0
    assert routing["node_loads"]["B"] == 0.0


def test_traffic_demand_validation():
    with pytest.raises(GraphException):
        TrafficDemand(source="A", destination="A", amount=10.0)
    with pytest.raises(GraphException):
        TrafficDemand(source="A", destination="B", amount=-5.0)


# --- Cascading Failure Tests ---

def test_cascading_failure_no_overload(diamond_network):
    """Initial failure of node B causes no cascade because traffic is routed through A."""
    demands = [TrafficDemand(source="S", destination="D", amount=20.0)]
    res = simulate_cascading_failure(
        graph=diamond_network,
        initial_failed_nodes=["B"],
        traffic_demands=demands,
        overload_threshold=1.0,
        max_simulation_rounds=5
    )
    # Only B fails; A easily carries 20.0 (capacity 50.0)
    assert res.failed_nodes == ["B"]
    assert "STABLE" in res.metrics["termination_reason"]
    assert res.active_node_count == 3


def test_cascading_failure_secondary_overload(diamond_network):
    """
    Initial failure of primary router A forces 20.0 units of traffic onto backup router B.
    B's capacity is only 15.0 -> B overloads and fails in Round 2, leading to partition!
    """
    demands = [TrafficDemand(source="S", destination="D", amount=20.0)]
    res = simulate_cascading_failure(
        graph=diamond_network,
        initial_failed_nodes=["A"],
        traffic_demands=demands,
        overload_threshold=1.0,
        max_simulation_rounds=5
    )

    # Initial failure: A
    # Round 2: traffic rerouted S-B-D, load on B is 20.0 > 15.0 -> B fails!
    assert "A" in res.failed_nodes
    assert "B" in res.failed_nodes
    assert res.metrics["total_cascading_rounds"] >= 2
    # Verify timeline records round 2 overload
    assert len(res.timeline) >= 3
    r2 = res.timeline[2]
    assert "B" in r2["newly_failed_nodes"]
    assert res.metrics["final_traffic_unserved"] == 20.0


def test_cascading_failure_max_rounds_limit(diamond_network):
    """Simulation strictly obeys max_simulation_rounds."""
    demands = [TrafficDemand(source="S", destination="D", amount=10.0)]
    res = simulate_cascading_failure(
        graph=diamond_network,
        initial_failed_nodes=["A"],
        traffic_demands=demands,
        max_simulation_rounds=1
    )
    assert len(res.timeline) <= 2


# --- Random Failure Tests ---

def test_random_failure_reproducibility(star_network):
    """Identical seeds produce identical simulation outputs."""
    res1 = simulate_random_failure(
        graph=star_network,
        failure_target="NODES",
        failure_count=2,
        num_trials=5,
        random_seed=12345
    )
    res2 = simulate_random_failure(
        graph=star_network,
        failure_target="NODES",
        failure_count=2,
        num_trials=5,
        random_seed=12345
    )

    assert res1["statistics"] == res2["statistics"]
    for t1, t2 in zip(res1["trials"], res2["trials"]):
        assert t1["failed_nodes"] == t2["failed_nodes"]


def test_random_failure_percentage_and_stats(star_network):
    """50% removal of nodes across 10 trials generates non-trivial variance."""
    res = simulate_random_failure(
        graph=star_network,
        failure_target="NODES",
        failure_percentage=50.0,
        num_trials=10,
        random_seed=999
    )
    assert res["status"] == "COMPLETED"
    stats = res["statistics"]["pairwise_connectivity"]
    assert 0.0 <= stats["mean"] <= 1.0
    assert 0.0 <= stats["min"] <= stats["max"] <= 1.0


def test_random_failure_invalid_trials(star_network):
    with pytest.raises(GraphException):
        simulate_random_failure(star_network, num_trials=0)


# --- Targeted Failure Tests ---

def test_targeted_failure_degree_strategy(star_network):
    """Degree-based attack on star network immediately targets central hub H first."""
    res = simulate_targeted_failure(
        graph=star_network,
        strategy="DEGREE",
        failure_count=1,
        adaptive=True
    )
    assert res["removed_nodes_sequence"] == ["H"]
    # With hub H removed, the 5 leaf nodes become isolated: component count becomes 5
    final = res["final_metrics"]
    assert final["component_count"] == 5
    assert final["pairwise_connectivity"] == 0.0


def test_targeted_failure_articulation_point_strategy(star_network):
    """Articulation-point strategy prioritizes cut-vertex H."""
    res = simulate_targeted_failure(
        graph=star_network,
        strategy="ARTICULATION_POINT",
        failure_count=1
    )
    assert res["removed_nodes_sequence"] == ["H"]


def test_targeted_vs_random_resilience_comparison(star_network):
    """
    On star network, targeted attack of 1 node (hub H) destroys all pairwise connectivity (0.0).
    Random attack of 1 node has only 1/6 chance of picking H; mean connectivity is much higher.
    """
    targeted_res = simulate_targeted_failure(star_network, strategy="DEGREE", failure_count=1)
    targeted_pair_conn = targeted_res["final_metrics"]["pairwise_connectivity"]
    assert targeted_pair_conn == 0.0

    random_res = simulate_random_failure(star_network, failure_target="NODES", failure_count=1, num_trials=20, random_seed=42)
    random_mean_conn = random_res["statistics"]["pairwise_connectivity"]["mean"]
    assert random_mean_conn > targeted_pair_conn

