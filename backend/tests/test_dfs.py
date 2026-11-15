"""
Unit tests for Depth-First Search (DFS) and NetworkX validation.
"""

import pytest
import networkx as nx
from app.algorithms.dfs import depth_first_search, full_graph_dfs
from app.graph_engine.graph_validation import NodeNotFoundError


def to_networkx_graph(graph) -> nx.Graph:
    G = nx.Graph()
    for node in graph.get_all_nodes():
        G.add_node(node.node_id)
    for edge in graph.get_all_edges():
        G.add_edge(edge.source, edge.target)
    return G


def test_dfs_linear_p5(linear_graph_p5):
    """Verify DFS traversal order on linear graph."""
    result = depth_first_search(linear_graph_p5, "v1")

    assert result["traversal_order"] == ["v1", "v2", "v3", "v4", "v5"]
    assert result["visited"] == {"v1", "v2", "v3", "v4", "v5"}
    assert result["reachable_count"] == 5

    # Invariant: No vertex visited twice
    assert len(result["traversal_order"]) == len(set(result["traversal_order"]))

    # Validation against NetworkX DFS edges
    nx_g = to_networkx_graph(linear_graph_p5)
    nx_nodes = list(nx.dfs_preorder_nodes(nx_g, "v1"))
    assert result["traversal_order"] == nx_nodes


def test_dfs_cycle_c5(cycle_graph_c5):
    """Verify DFS explores path around the cycle without infinite loop."""
    result = depth_first_search(cycle_graph_c5, "v1")

    assert len(result["traversal_order"]) == 5
    assert result["traversal_order"][0] == "v1"
    # Deterministic neighbor order chooses v2 first (v2 < v5)
    assert result["traversal_order"][1] == "v2"
    assert result["visited"] == {"v1", "v2", "v3", "v4", "v5"}


def test_dfs_isolated_node(sample_network):
    """Verify DFS on isolated node halts immediately."""
    result = depth_first_search(sample_network, "SRV_STANDBY")

    assert result["traversal_order"] == ["SRV_STANDBY"]
    assert result["visited"] == {"SRV_STANDBY"}
    assert result["reachable_count"] == 1


def test_dfs_disconnected_graph(disconnected_graph):
    """Verify single DFS explores only its connected component."""
    result = depth_first_search(disconnected_graph, "D")

    assert result["visited"] == {"D", "E"}
    assert "A" not in result["visited"]

    # Full graph DFS visits both components
    all_traversals = full_graph_dfs(disconnected_graph)
    assert len(all_traversals) == 2


def test_dfs_invalid_start_node(cycle_graph_c5):
    """Verify error on invalid start node."""
    with pytest.raises(NodeNotFoundError):
        depth_first_search(cycle_graph_c5, "UNKNOWN")

