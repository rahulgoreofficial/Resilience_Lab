"""
NetworkX Independent Verification & Ground Truth Validation Suite.
Cross-validates custom first-principles graph algorithms, percolation simulations,
and resilience calculations against standard NetworkX reference implementations.
"""

import pytest
import networkx as nx
import math
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_model import Node, Edge
from app.algorithms.connected_components import find_connected_components
from app.algorithms.articulation_points import find_articulation_points
from app.algorithms.bridges import find_bridges
from app.algorithms.shortest_path import dijkstra_shortest_path
from app.algorithms.degree_analysis import all_vertex_degrees
from app.resilience.metrics import calculate_pairwise_connectivity
from app.simulation.targeted_failure import _rank_targets


def convert_custom_graph_to_networkx(custom_graph: NetworkGraph) -> nx.Graph:
    """Converts a custom NetworkGraph to a NetworkX Graph instance for validation."""
    nx_g = nx.Graph()
    for n in custom_graph.get_all_nodes():
        nx_g.add_node(n.node_id, **n.to_dict())
    for e in custom_graph.get_all_edges():
        nx_g.add_edge(e.source, e.target, weight=e.weight, edge_id=e.edge_id)
    return nx_g


@pytest.fixture
def complex_benchmark_graph():
    """
    Constructs a non-trivial benchmark graph with multiple cycles, bridges, and cut-vertices.
    Structure:
    Cycle 1: (A, B, C, A)
    Bridge: (C, D)
    Node D connects to Cycle 2: (D, E, F, D)
    Leaf bridge: (F, G)
    """
    g = NetworkGraph.create("Complex_Benchmark")
    for nid in ["A", "B", "C", "D", "E", "F", "G"]:
        g.add_node(Node(node_id=nid, node_type="router"))

    # Cycle 1
    g.add_edge(Edge(edge_id="e1", source="A", target="B", weight=2.0))
    g.add_edge(Edge(edge_id="e2", source="B", target="C", weight=3.0))
    g.add_edge(Edge(edge_id="e3", source="C", target="A", weight=4.0))

    # Bridge between cycles
    g.add_edge(Edge(edge_id="e4", source="C", target="D", weight=1.5))

    # Cycle 2
    g.add_edge(Edge(edge_id="e5", source="D", target="E", weight=2.5))
    g.add_edge(Edge(edge_id="e6", source="E", target="F", weight=3.5))
    g.add_edge(Edge(edge_id="e7", source="F", target="D", weight=1.0))

    # Leaf bridge
    g.add_edge(Edge(edge_id="e8", source="F", target="G", weight=5.0))
    return g


def test_connected_components_validation(complex_benchmark_graph):
    nx_g = convert_custom_graph_to_networkx(complex_benchmark_graph)
    custom_comp = find_connected_components(complex_benchmark_graph)

    nx_comps = [sorted(list(c)) for c in nx.connected_components(nx_g)]
    nx_comps.sort(key=lambda c: (-len(c), c[0]))

    assert custom_comp["component_count"] == nx.number_connected_components(nx_g)
    assert custom_comp["components"] == nx_comps
    assert custom_comp["giant_component_size"] == max(len(c) for c in nx_comps)


def test_articulation_points_validation(complex_benchmark_graph):
    nx_g = convert_custom_graph_to_networkx(complex_benchmark_graph)
    custom_aps = set(find_articulation_points(complex_benchmark_graph)["articulation_points"])
    nx_aps = set(nx.articulation_points(nx_g))

    # Expected APs: C, D, F
    assert custom_aps == nx_aps
    assert custom_aps == {"C", "D", "F"}


def test_bridges_validation(complex_benchmark_graph):
    nx_g = convert_custom_graph_to_networkx(complex_benchmark_graph)
    custom_bridges = {frozenset(e) for e in find_bridges(complex_benchmark_graph)["bridges"]}
    nx_bridges = {frozenset(e) for e in nx.bridges(nx_g)}

    # Expected Bridges: {C, D} and {F, G}
    assert custom_bridges == nx_bridges
    assert custom_bridges == {frozenset(["C", "D"]), frozenset(["F", "G"])}


def test_dijkstra_shortest_path_validation(complex_benchmark_graph):
    nx_g = convert_custom_graph_to_networkx(complex_benchmark_graph)

    # Test all pairs shortest path distances
    for src in complex_benchmark_graph.get_node_ids():
        for dst in complex_benchmark_graph.get_node_ids():
            custom_res = dijkstra_shortest_path(complex_benchmark_graph, source=src, target=dst)
            nx_dist = nx.shortest_path_length(nx_g, source=src, target=dst, weight="weight")
            assert custom_res["distance"] == pytest.approx(nx_dist, 1e-4)


def test_pairwise_connectivity_validation(complex_benchmark_graph):
    """Verify pairwise connectivity matches exact combinatorial pairs from NetworkX components."""
    nx_g = convert_custom_graph_to_networkx(complex_benchmark_graph)
    nx_comps = list(nx.connected_components(nx_g))
    total_nodes = nx_g.number_of_nodes()

    nx_connected_pairs = sum(math.comb(len(c), 2) for c in nx_comps if len(c) >= 2)
    nx_total_pairs = math.comb(total_nodes, 2)
    expected_pair_conn = round(nx_connected_pairs / nx_total_pairs, 4)

    custom_comp_sizes = [len(c) for c in nx_comps]
    custom_pair_conn = calculate_pairwise_connectivity(custom_comp_sizes, total_nodes)
    assert custom_pair_conn == expected_pair_conn


def test_degree_ranking_validation(complex_benchmark_graph):
    nx_g = convert_custom_graph_to_networkx(complex_benchmark_graph)
    custom_degrees = all_vertex_degrees(complex_benchmark_graph)
    nx_degrees = dict(nx_g.degree())

    assert custom_degrees == nx_degrees

    custom_ranked = _rank_targets(complex_benchmark_graph, strategy="DEGREE")
    nx_ranked = sorted(nx_degrees.keys(), key=lambda n: (-nx_degrees[n], n))
    assert custom_ranked == nx_ranked

