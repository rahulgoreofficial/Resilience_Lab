"""
Unit tests for Tarjan's Articulation Point Detection and NetworkX validation.
Verifies cut-vertex definition: kappa(G - v) > kappa(G).
"""

import networkx as nx
from app.algorithms.articulation_points import find_articulation_points
from app.algorithms.connected_components import find_connected_components


def to_networkx_graph(graph) -> nx.Graph:
    G = nx.Graph()
    for node in graph.get_all_nodes():
        G.add_node(node.node_id)
    for edge in graph.get_all_edges():
        G.add_edge(edge.source, edge.target)
    return G


def test_ap_empty_and_single_node(empty_graph, single_node_graph):
    """Verify empty and single-node graphs have zero articulation points."""
    assert find_articulation_points(empty_graph)["articulation_points"] == []
    assert find_articulation_points(single_node_graph)["articulation_points"] == []


def test_ap_complete_and_cycle(complete_graph_k5, cycle_graph_c5):
    """Verify 2-connected graphs (K5, C5) have zero articulation points."""
    assert find_articulation_points(complete_graph_k5)["articulation_points"] == []
    assert find_articulation_points(cycle_graph_c5)["articulation_points"] == []


def test_ap_star_s5(star_graph_s5):
    """Verify hub H is the unique articulation point in a star graph."""
    res = find_articulation_points(star_graph_s5)
    assert res["articulation_points"] == ["H"]
    assert res["count"] == 1

    # NetworkX Validation
    nx_g = to_networkx_graph(star_graph_s5)
    assert set(nx.articulation_points(nx_g)) == {"H"}


def test_ap_linear_p5(linear_graph_p5):
    """Verify interior vertices of a path graph are articulation points."""
    res = find_articulation_points(linear_graph_p5)
    assert res["articulation_points"] == ["v2", "v3", "v4"]
    assert res["count"] == 3

    # NetworkX Validation
    nx_g = to_networkx_graph(linear_graph_p5)
    assert set(nx.articulation_points(nx_g)) == {"v2", "v3", "v4"}


def test_ap_mathematical_definition_satisfaction(sample_network):
    """
    Mathematical Invariant Verification:
    For every vertex v reported as an articulation point, removing v from the graph
    MUST strictly increase the number of connected components: kappa(G - v) > kappa(G).
    """
    baseline_components = find_connected_components(sample_network)["component_count"]
    res = find_articulation_points(sample_network)
    detected_aps = res["articulation_points"]

    assert len(detected_aps) == 6
    assert detected_aps == ["FW1", "FW2", "R1", "SW1", "SW2", "SW3"]

    # Verify mathematical cut-vertex property for each detected AP
    for ap in detected_aps:
        g_copy = sample_network.from_json(sample_network.to_json())
        g_copy.remove_node(ap)
        post_failure_components = find_connected_components(g_copy)["component_count"]
        assert post_failure_components > baseline_components, (
            f"Vertex {ap} was flagged as AP but kappa(G - {ap}) did not increase!"
        )

    # NetworkX Cross-Validation
    nx_g = to_networkx_graph(sample_network)
    nx_aps = set(nx.articulation_points(nx_g))
    assert set(detected_aps) == nx_aps

