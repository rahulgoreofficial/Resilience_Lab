"""
Tests for Mathematical Invariants, Graph Theory Axioms, and Edge Cases (Phase 10).
Formally verifies:
1. Euler's Handshake Lemma: sum(deg(v)) == 2 * |E|
2. Adjacency Matrix Symmetry: A = A^T with zero diagonal
3. Custom algorithm parity vs NetworkX reference models
4. Extreme boundary graphs: empty, singleton, disconnected, complete Kn, cycle Cn, star Sk
5. Immutability of original graph under failure simulations
"""

import pytest
import networkx as nx
import numpy as np

from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_model import Node, Edge
from app.graph_engine.graph_representation import GraphRepresentation
from app.algorithms.connected_components import find_connected_components
from app.algorithms.articulation_points import find_articulation_points
from app.algorithms.bridges import find_bridges
from app.algorithms.shortest_path import dijkstra_shortest_path
from app.algorithms.degree_analysis import all_vertex_degrees
from app.simulation import (
    simulate_node_failure,
    simulate_edge_failure,
    simulate_multiple_failures,
    simulate_random_failure,
    simulate_targeted_failure,
    simulate_cascading_failure
)
from app.resilience.metrics import (
    calculate_pairwise_connectivity,
    calculate_lcc_ratio
)


def _build_network(nodes_list, edges_list):
    """Helper to instantiate NetworkGraph from nodes and edges."""
    g = NetworkGraph(name="Invariant Test Graph")
    for n in nodes_list:
        g.add_node(Node(node_id=n, node_type="router"))
    for src, dst, w in edges_list:
        g.add_edge(Edge(edge_id=f"e_{src}_{dst}", source=src, target=dst, weight=w))
    return g


# =========================================================================
# 1. EULER'S HANDSHAKE LEMMA VERIFICATION
# =========================================================================

def test_handshake_lemma_complete_graph():
    """Verify sum(deg(v)) == 2 * |E| for complete graph K_6."""
    n = 6
    nodes = [f"N{i}" for i in range(n)]
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((nodes[i], nodes[j], 1.0))

    graph = _build_network(nodes, edges)
    degrees = all_vertex_degrees(graph)

    sum_degrees = sum(degrees.values())
    expected_edges = n * (n - 1) // 2
    assert graph.edge_count == expected_edges
    assert sum_degrees == 2 * graph.edge_count
    # In complete graph Kn, every vertex has degree n - 1
    assert all(deg == n - 1 for deg in degrees.values())


def test_handshake_lemma_star_graph():
    """Verify Handshake Lemma for Star graph S_8 (1 hub + 7 leaves)."""
    hub = "HUB"
    leaves = [f"L{i}" for i in range(7)]
    edges = [(hub, leaf, 1.0) for leaf in leaves]

    graph = _build_network([hub] + leaves, edges)
    degrees = all_vertex_degrees(graph)

    sum_degrees = sum(degrees.values())
    assert sum_degrees == 2 * len(edges)
    assert degrees[hub] == 7
    assert all(degrees[leaf] == 1 for leaf in leaves)


def test_handshake_lemma_cycle_graph():
    """Verify Handshake Lemma for 2-regular Cycle graph C_10."""
    n = 10
    nodes = [f"C{i}" for i in range(n)]
    edges = [(nodes[i], nodes[(i + 1) % n], 1.0) for i in range(n)]

    graph = _build_network(nodes, edges)
    degrees = all_vertex_degrees(graph)

    sum_degrees = sum(degrees.values())
    assert sum_degrees == 2 * n
    assert all(deg == 2 for deg in degrees.values())


# =========================================================================
# 2. ADJACENCY MATRIX SYMMETRY & STRUCTURAL INTEGRITY
# =========================================================================

def test_adjacency_matrix_properties():
    """Verify adjacency matrix A is symmetric, has zero diagonal, and shape |V| x |V|."""
    nodes = ["R1", "R2", "SW1", "S1", "DB1"]
    edges = [
        ("R1", "R2", 1.5),
        ("R2", "SW1", 2.0),
        ("SW1", "S1", 1.0),
        ("SW1", "DB1", 3.0),
        ("R1", "SW1", 4.0),
    ]
    graph = _build_network(nodes, edges)
    repr_engine = GraphRepresentation(graph)

    _, _, matrix = repr_engine.to_adjacency_matrix()
    _, weighted_matrix = repr_engine.to_weighted_adjacency_matrix(attribute="weight")

    # 1. Dimensions
    assert matrix.shape == (len(nodes), len(nodes))
    assert weighted_matrix.shape == (len(nodes), len(nodes))

    # 2. Symmetry: A = A^T
    np.testing.assert_array_equal(matrix, matrix.T)
    np.testing.assert_array_equal(weighted_matrix, weighted_matrix.T)

    # 3. Zero diagonal (no self-loops)
    np.testing.assert_array_equal(np.diag(matrix), np.zeros(len(nodes)))
    np.testing.assert_array_equal(np.diag(weighted_matrix), np.zeros(len(nodes)))


# =========================================================================
# 3. MATHEMATICAL ALGORITHM PARITY VS NETWORKX
# =========================================================================

def test_parity_articulation_points_and_bridges_vs_networkx():
    """
    Construct a non-trivial benchmark graph containing:
    - 2 cycles
    - 1 bridge link
    - 2 articulation points
    Compare custom Tarjan outputs against NetworkX.
    """
    # Graph: (A-B-C-A) -- [Bridge C-D] -- (D-E-F-D)
    nodes = ["A", "B", "C", "D", "E", "F"]
    edges = [
        ("A", "B", 1.0), ("B", "C", 1.0), ("C", "A", 1.0),
        ("C", "D", 2.5),  # Bridge
        ("D", "E", 1.0), ("E", "F", 1.0), ("F", "D", 1.0)
    ]
    graph = _build_network(nodes, edges)

    # NetworkX reference
    nx_g = nx.Graph()
    nx_g.add_nodes_from(nodes)
    for u, v, w in edges:
        nx_g.add_edge(u, v, weight=w)

    # 1. Articulation Points
    custom_aps = set(find_articulation_points(graph)["articulation_points"])
    nx_aps = set(nx.articulation_points(nx_g))
    assert custom_aps == nx_aps
    assert custom_aps == {"C", "D"}

    # 2. Bridges
    custom_bridges = {tuple(sorted(b)) for b in find_bridges(graph)["bridges"]}
    nx_bridges = {tuple(sorted(b)) for b in nx.bridges(nx_g)}
    assert custom_bridges == nx_bridges
    assert custom_bridges == {("C", "D")}

    # 3. Connected Components
    custom_comps = [set(c) for c in find_connected_components(graph)["components"]]
    nx_comps = [set(c) for c in nx.connected_components(nx_g)]
    assert custom_comps == nx_comps
    assert len(custom_comps) == 1


def test_parity_dijkstra_shortest_paths_vs_networkx():
    """Verify custom Dijkstra paths and distances exactly match NetworkX."""
    nodes = ["A", "B", "C", "D", "E"]
    edges = [
        ("A", "B", 4.0),
        ("A", "C", 2.0),
        ("C", "B", 1.0),  # A->C->B (3.0) is shorter than A->B (4.0)
        ("B", "D", 5.0),
        ("C", "D", 8.0),
        ("D", "E", 2.0),
    ]
    graph = _build_network(nodes, edges)

    nx_g = nx.Graph()
    for u, v, w in edges:
        nx_g.add_edge(u, v, weight=w)

    for target in ["B", "C", "D", "E"]:
        custom_res = dijkstra_shortest_path(graph, source="A", target=target)
        nx_dist, nx_path = nx.single_source_dijkstra(nx_g, source="A", target=target, weight="weight")

        assert custom_res["path"] == nx_path
        assert custom_res["distance"] == pytest.approx(nx_dist)


# =========================================================================
# 4. EXTREME BOUNDARY & EDGE-CASE TOPOLOGIES
# =========================================================================

def test_empty_graph_invariants():
    """Verify behavior on null/empty graph (|V| = 0, |E| = 0)."""
    graph = NetworkGraph(name="Null Graph")
    assert graph.node_count == 0
    assert graph.edge_count == 0
    assert find_connected_components(graph)["components"] == []
    assert find_articulation_points(graph)["articulation_points"] == []
    assert find_bridges(graph)["bridges"] == []
    assert calculate_pairwise_connectivity([], 0) == 0.0
    assert calculate_lcc_ratio(0, 0) == 0.0


def test_singleton_graph_invariants():
    """Verify behavior on single isolated node (|V| = 1, |E| = 0)."""
    graph = NetworkGraph(name="Singleton")
    graph.add_node(Node(node_id="SOLO", node_type="server"))

    assert graph.node_count == 1
    assert graph.edge_count == 0
    assert find_connected_components(graph)["components"] == [["SOLO"]]
    assert find_articulation_points(graph)["articulation_points"] == []
    assert find_bridges(graph)["bridges"] == []
    assert calculate_pairwise_connectivity([1], 1) == 1.0
    assert calculate_lcc_ratio(1, 1) == 1.0


def test_disconnected_clusters_resilience():
    """Verify resilience metrics on partitioned disjoint graph."""
    # Two disconnected 3-node triangles: (A-B-C) and (X-Y-Z)
    nodes = ["A", "B", "C", "X", "Y", "Z"]
    edges = [
        ("A", "B", 1.0), ("B", "C", 1.0), ("C", "A", 1.0),
        ("X", "Y", 1.0), ("Y", "Z", 1.0), ("Z", "X", 1.0)
    ]
    graph = _build_network(nodes, edges)

    comp_res = find_connected_components(graph)
    assert comp_res["component_count"] == 2
    comps = comp_res["components"]
    assert len(comps) == 2

    # Total pairs = 6 * 5 / 2 = 15.
    # Connected pairs = 3 (in cluster 1) + 3 (in cluster 2) = 6.
    # Expected pairwise connectivity = 6 / 15 = 0.40.
    sizes = [len(c) for c in comps]
    phi = calculate_pairwise_connectivity(sizes, len(nodes))
    assert pytest.approx(phi, 0.001) == 0.40

    # LCC ratio = 3 / 6 = 0.50
    assert calculate_lcc_ratio(max(sizes), len(nodes)) == 0.50


# =========================================================================
# 5. ORIGINAL GRAPH IMMUTABILITY UNDER SIMULATIONS
# =========================================================================

def test_original_graph_remains_strictly_immutable():
    """
    Verify that executing node failure, edge failure, random outage,
    targeted attack, and cascading failure never mutates the original graph.
    """
    nodes = ["GW1", "R1", "R2", "SW1", "SRV1", "DB1"]
    edges = [
        ("GW1", "R1", 1.0),
        ("R1", "R2", 2.0),
        ("R2", "SW1", 1.0),
        ("SW1", "SRV1", 1.0),
        ("SW1", "DB1", 1.0),
    ]
    graph = _build_network(nodes, edges)

    initial_nodes = set(graph.get_node_ids())
    initial_edges = {(e.source, e.target) for e in graph.get_all_edges()}
    initial_node_count = graph.node_count
    initial_edge_count = graph.edge_count

    # Execute all simulation modes
    simulate_node_failure(graph, failed_node_ids=["R1"])
    simulate_edge_failure(graph, failed_edges=[["R1", "R2"]])
    simulate_multiple_failures(graph, failed_node_ids=["SW1"], failed_edges=[["GW1", "R1"]])
    simulate_random_failure(graph, failure_count=2, num_trials=5, random_seed=42)
    simulate_targeted_failure(graph, strategy="degree", failure_count=2)
    simulate_cascading_failure(graph, initial_failed_nodes=["R1"], overload_threshold=1.2, max_simulation_rounds=5)

    # Assert exact immutability
    assert graph.node_count == initial_node_count
    assert graph.edge_count == initial_edge_count
    assert set(graph.get_node_ids()) == initial_nodes
    current_edges = {(e.source, e.target) for e in graph.get_all_edges()}
    assert current_edges == initial_edges
