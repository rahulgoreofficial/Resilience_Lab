"""
Unit tests for Breadth-First Search (BFS) and NetworkX validation.
"""

import pytest
import networkx as nx
from app.algorithms.bfs import breadth_first_search, full_graph_bfs
from app.graph_engine.graph_validation import NodeNotFoundError


def to_networkx_graph(graph) -> nx.Graph:
    """Helper to convert NetworkGraph to networkx.Graph for independent validation."""
    G = nx.Graph()
    for node in graph.get_all_nodes():
        G.add_node(node.node_id)
    for edge in graph.get_all_edges():
        G.add_edge(edge.source, edge.target, weight=edge.weight)
    return G


def test_bfs_linear_p5(linear_graph_p5):
    """Verify BFS traversal and distances on linear path P5."""
    result = breadth_first_search(linear_graph_p5, "v1")

    assert result["start_node"] == "v1"
    assert result["traversal_order"] == ["v1", "v2", "v3", "v4", "v5"]
    assert result["distances"]["v1"] == 0
    assert result["distances"]["v3"] == 2
    assert result["distances"]["v5"] == 4
    assert len(result["visited"]) == 5

    # Invariant: No vertex visited twice
    assert len(result["traversal_order"]) == len(set(result["traversal_order"]))

    # Validation against NetworkX
    nx_g = to_networkx_graph(linear_graph_p5)
    nx_lengths = nx.single_source_shortest_path_length(nx_g, "v1")
    assert result["distances"] == nx_lengths


def test_bfs_star_s5(star_graph_s5):
    """Verify BFS traversal on star graph: hub first, then all leaves at distance 1."""
    result = breadth_first_search(star_graph_s5, "H")

    assert result["traversal_order"][0] == "H"
    assert sorted(result["traversal_order"][1:]) == ["L1", "L2", "L3", "L4"]
    for leaf in ["L1", "L2", "L3", "L4"]:
        assert result["distances"][leaf] == 1


def test_bfs_isolated_node(sample_network):
    """Verify BFS starting from isolated node reaches only itself."""
    result = breadth_first_search(sample_network, "SRV_STANDBY")

    assert result["traversal_order"] == ["SRV_STANDBY"]
    assert result["visited"] == {"SRV_STANDBY"}
    assert result["reachable_count"] == 1
    assert result["distances"] == {"SRV_STANDBY": 0}


def test_bfs_disconnected_component(disconnected_graph):
    """Verify BFS does not cross disconnected component boundaries."""
    result = breadth_first_search(disconnected_graph, "A")

    assert result["visited"] == {"A", "B", "C"}
    assert "D" not in result["visited"]
    assert "E" not in result["visited"]

    # Full graph BFS traverses both components
    all_traversals = full_graph_bfs(disconnected_graph)
    assert len(all_traversals) == 2


def test_bfs_invalid_start_node(linear_graph_p5):
    """Verify error on invalid start vertex."""
    with pytest.raises(NodeNotFoundError):
        breadth_first_search(linear_graph_p5, "NON_EXISTENT")

