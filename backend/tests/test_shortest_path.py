"""
Unit tests for Dijkstra's Shortest Path Algorithm and NetworkX validation.
"""

import pytest
import networkx as nx
from app.graph_engine.graph_model import Node, Edge
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import NodeNotFoundError
from app.algorithms.shortest_path import dijkstra_shortest_path


def to_networkx_graph(graph) -> nx.Graph:
    G = nx.Graph()
    for node in graph.get_all_nodes():
        G.add_node(node.node_id)
    for edge in graph.get_all_edges():
        G.add_edge(edge.source, edge.target, weight=edge.weight)
    return G


def test_dijkstra_triangle_indirect_path():
    """
    Verify Dijkstra selects the lower-cost indirect path:
    Direct A -> B has weight 10.0.
    Indirect A -> C -> B has weight 2.0 + 3.0 = 5.0.
    """
    g = NetworkGraph.create()
    for n in ["A", "B", "C"]:
        g.add_node(Node(n, "router"))
    g.add_edge(Edge("e_ab", "A", "B", weight=10.0))
    g.add_edge(Edge("e_ac", "A", "C", weight=2.0))
    g.add_edge(Edge("e_cb", "C", "B", weight=3.0))

    res = dijkstra_shortest_path(g, "A", "B")
    assert res["distance"] == 5.0
    assert res["path"] == ["A", "C", "B"]
    assert res["is_reachable"] is True

    # NetworkX Validation
    nx_g = to_networkx_graph(g)
    assert nx.dijkstra_path_length(nx_g, "A", "B") == 5.0
    assert nx.dijkstra_path(nx_g, "A", "B") == ["A", "C", "B"]


def test_dijkstra_unreachable_destination(disconnected_graph):
    """Verify Dijkstra returns infinity and empty path for unreachable pairs."""
    res = dijkstra_shortest_path(disconnected_graph, "A", "E")
    assert res["distance"] == float("inf")
    assert res["path"] == []
    assert res["is_reachable"] is False


def test_dijkstra_single_source_all_destinations(linear_graph_p5):
    """Verify computing shortest paths to all reachable vertices when target is None."""
    res = dijkstra_shortest_path(linear_graph_p5, "v1", target=None)
    assert res["all_distances"]["v1"] == 0.0
    assert res["all_distances"]["v3"] == 2.0
    assert res["all_distances"]["v5"] == 4.0

    # NetworkX Validation
    nx_g = to_networkx_graph(linear_graph_p5)
    nx_lengths = nx.single_source_dijkstra_path_length(nx_g, "v1")
    assert res["all_distances"] == nx_lengths


def test_dijkstra_sample_network_gw_to_db(sample_network):
    """Verify Dijkstra shortest path from Gateway (GW1) to Primary Database (DB_PRIMARY)."""
    res = dijkstra_shortest_path(sample_network, "GW1", "DB_PRIMARY")
    assert res["is_reachable"] is True
    assert res["path"][0] == "GW1"
    assert res["path"][-1] == "DB_PRIMARY"

    # Cross-validate distance with NetworkX
    nx_g = to_networkx_graph(sample_network)
    nx_dist = nx.dijkstra_path_length(nx_g, "GW1", "DB_PRIMARY")
    assert res["distance"] == pytest.approx(nx_dist, rel=1e-5)


def test_dijkstra_invalid_nodes(linear_graph_p5):
    """Verify error on invalid source or target ID."""
    with pytest.raises(NodeNotFoundError):
        dijkstra_shortest_path(linear_graph_p5, "INVALID_SRC", "v2")
    with pytest.raises(NodeNotFoundError):
        dijkstra_shortest_path(linear_graph_p5, "v1", "INVALID_TGT")

