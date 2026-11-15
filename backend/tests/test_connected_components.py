"""
Unit tests for Connected Component Detection and NetworkX validation.
Verifies component count, partitioning equivalence, non-overlapping invariant, and isolated nodes.
"""

import networkx as nx
from app.algorithms.connected_components import find_connected_components


def to_networkx_graph(graph) -> nx.Graph:
    G = nx.Graph()
    for node in graph.get_all_nodes():
        G.add_node(node.node_id)
    for edge in graph.get_all_edges():
        G.add_edge(edge.source, edge.target)
    return G


def test_connected_components_empty(empty_graph):
    """Verify component detection on empty graph."""
    res = find_connected_components(empty_graph)
    assert res["component_count"] == 0
    assert res["components"] == []
    assert res["is_connected"] is False
    assert res["giant_component"] == []


def test_connected_components_single_node(single_node_graph):
    """Verify single node graph has 1 component and 1 isolated node."""
    res = find_connected_components(single_node_graph)
    assert res["component_count"] == 1
    assert res["components"] == [["N1"]]
    assert res["is_connected"] is True
    assert res["isolated_nodes"] == ["N1"]


def test_connected_components_connected_graphs(linear_graph_p5, cycle_graph_c5, complete_graph_k5):
    """Verify connected graphs have component_count == 1."""
    for g in [linear_graph_p5, cycle_graph_c5, complete_graph_k5]:
        res = find_connected_components(g)
        assert res["component_count"] == 1
        assert res["is_connected"] is True
        assert len(res["giant_component"]) == g.node_count
        assert res["isolated_nodes"] == []


def test_connected_components_disconnected(disconnected_graph):
    """Verify disconnected graph with 2 components."""
    res = find_connected_components(disconnected_graph)
    assert res["component_count"] == 2
    assert res["is_connected"] is False
    assert res["giant_component"] == ["A", "B", "C"]
    assert ["D", "E"] in res["components"]

    # Mathematical Invariant 1: Disjointness (No overlapping vertices)
    c1, c2 = set(res["components"][0]), set(res["components"][1])
    assert c1.isdisjoint(c2)

    # Mathematical Invariant 2: Union equals V
    assert (c1 | c2) == set(disconnected_graph.get_node_ids())

    # NetworkX Validation
    nx_g = to_networkx_graph(disconnected_graph)
    nx_components = [sorted(list(c)) for c in nx.connected_components(nx_g)]
    nx_components.sort(key=lambda c: (-len(c), c[0]))
    assert res["components"] == nx_components


def test_connected_components_sample_network(sample_network):
    """Verify sample network has exactly 3 components and 1 isolated node."""
    res = find_connected_components(sample_network)
    assert res["component_count"] == 3
    assert res["is_connected"] is False
    assert res["isolated_nodes"] == ["SRV_STANDBY"]
    assert res["giant_component_size"] == 15
    assert ["R_BRANCH", "SRV_BRANCH"] in res["components"]
    assert ["SRV_STANDBY"] in res["components"]

    # NetworkX Validation
    nx_g = to_networkx_graph(sample_network)
    assert nx.number_connected_components(nx_g) == 3
