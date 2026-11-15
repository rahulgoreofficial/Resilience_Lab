"""
Unit tests for Degree Analysis and Euler's Handshaking Lemma.
"""

import networkx as nx
from app.algorithms.degree_analysis import (
    vertex_degree,
    all_vertex_degrees,
    analyze_degrees
)


def to_networkx_graph(graph) -> nx.Graph:
    G = nx.Graph()
    for node in graph.get_all_nodes():
        G.add_node(node.node_id)
    for edge in graph.get_all_edges():
        G.add_edge(edge.source, edge.target)
    return G


def test_degree_empty(empty_graph):
    """Verify degree analysis on empty graph."""
    res = analyze_degrees(empty_graph)
    assert res["degrees"] == {}
    assert res["degree_sum"] == 0
    assert res["handshaking_lemma_verified"] is True


def test_degree_star_s5(star_graph_s5):
    """Verify star graph degree properties."""
    assert vertex_degree(star_graph_s5, "H") == 4
    for leaf in ["L1", "L2", "L3", "L4"]:
        assert vertex_degree(star_graph_s5, leaf) == 1

    res = analyze_degrees(star_graph_s5)
    assert res["min_degree"] == 1
    assert res["max_degree"] == 4
    assert res["highest_degree_nodes"] == ["H"]
    assert res["degree_sum"] == 8  # 2 * 4 edges
    assert res["handshaking_lemma_verified"] is True


def test_degree_cycle_c5(cycle_graph_c5):
    """Verify cycle graph is 2-regular."""
    res = analyze_degrees(cycle_graph_c5)
    assert res["min_degree"] == 2
    assert res["max_degree"] == 2
    assert res["avg_degree"] == 2.0
    assert res["degree_sum"] == 10  # 2 * 5 edges
    assert res["handshaking_lemma_verified"] is True


def test_degree_complete_k5(complete_graph_k5):
    """Verify complete graph K5 is (n-1)-regular = 4-regular."""
    res = analyze_degrees(complete_graph_k5)
    assert res["min_degree"] == 4
    assert res["max_degree"] == 4
    assert res["avg_degree"] == 4.0
    assert res["degree_sum"] == 20  # 2 * 10 edges
    assert res["handshaking_lemma_verified"] is True


def test_handshaking_lemma_on_sample_network(sample_network):
    """Verify Euler's Handshaking Lemma holds on complex benchmark topology."""
    res = analyze_degrees(sample_network)
    assert res["handshaking_lemma_verified"] is True
    assert res["degree_sum"] == 2 * sample_network.edge_count

    # NetworkX Validation
    nx_g = to_networkx_graph(sample_network)
    nx_degrees = dict(nx_g.degree())
    assert res["degrees"] == nx_degrees

