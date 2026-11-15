"""
Unit tests for Tarjan's Bridge (Cut-Edge) Detection and NetworkX validation.
Verifies cut-edge definition: kappa(G - e) > kappa(G).
"""

import networkx as nx
from app.algorithms.bridges import find_bridges
from app.algorithms.connected_components import find_connected_components


def to_networkx_graph(graph) -> nx.Graph:
    G = nx.Graph()
    for node in graph.get_all_nodes():
        G.add_node(node.node_id)
    for edge in graph.get_all_edges():
        G.add_edge(edge.source, edge.target)
    return G


def test_bridges_empty_and_cycle(empty_graph, cycle_graph_c5, complete_graph_k5):
    """Verify graphs with cycles (C5, K5) and empty graphs have zero bridges."""
    assert find_bridges(empty_graph)["bridges"] == []
    assert find_bridges(cycle_graph_c5)["bridges"] == []
    assert find_bridges(complete_graph_k5)["bridges"] == []


def test_bridges_linear_p5(linear_graph_p5):
    """Verify all edges in a tree / path graph are bridges."""
    res = find_bridges(linear_graph_p5)
    expected = [("v1", "v2"), ("v2", "v3"), ("v3", "v4"), ("v4", "v5")]
    assert res["bridges"] == expected
    assert res["count"] == 4

    # NetworkX Validation
    nx_g = to_networkx_graph(linear_graph_p5)
    nx_b = sorted([tuple(sorted(e)) for e in nx.bridges(nx_g)])
    assert res["bridges"] == nx_b


def test_bridges_star_s5(star_graph_s5):
    """Verify all spokes in a star graph are bridges."""
    res = find_bridges(star_graph_s5)
    expected = [("H", "L1"), ("H", "L2"), ("H", "L3"), ("H", "L4")]
    assert res["bridges"] == expected
    assert res["count"] == 4


def test_bridges_mathematical_definition_satisfaction(sample_network):
    """
    Mathematical Invariant Verification:
    For every edge {u, v} reported as a bridge, removing {u, v} MUST strictly
    increase the number of connected components: kappa(G - e) > kappa(G).
    """
    baseline_components = find_connected_components(sample_network)["component_count"]
    res = find_bridges(sample_network)
    detected_bridges = res["bridges"]

    assert len(detected_bridges) == 10

    # Verify mathematical bridge property for each detected bridge
    for u, v in detected_bridges:
        g_copy = sample_network.from_json(sample_network.to_json())
        g_copy.remove_edge_by_endpoints(u, v)
        post_failure_components = find_connected_components(g_copy)["component_count"]
        assert post_failure_components > baseline_components, (
            f"Edge ({u}, {v}) was flagged as bridge but kappa(G - e) did not increase!"
        )

    # NetworkX Cross-Validation
    nx_g = to_networkx_graph(sample_network)
    nx_bridges = sorted([tuple(sorted(e)) for e in nx.bridges(nx_g)])
    assert detected_bridges == nx_bridges

