"""
Unit tests for GraphRepresentation: Adjacency Matrix and Adjacency List.
Verifies mathematical invariants, symmetry, dimensions, and representation equivalence.
"""

import numpy as np
from app.graph_engine.graph_representation import GraphRepresentation
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_model import Node


def test_empty_graph_representations(empty_graph):
    """Verify representation behavior on an empty graph."""
    rep = GraphRepresentation(empty_graph)
    nodes, matrix_list, matrix_np = rep.to_adjacency_matrix()
    adj_list = rep.to_adjacency_list()

    assert nodes == []
    assert matrix_list == []
    assert matrix_np.shape == (0, 0)
    assert adj_list == {}
    assert rep.verify_representation_consistency() is True


def test_single_node_representations(single_node_graph):
    """Verify representation of single isolated vertex K1."""
    rep = GraphRepresentation(single_node_graph)
    nodes, matrix_list, matrix_np = rep.to_adjacency_matrix()
    adj_list = rep.to_adjacency_list()

    assert nodes == ["N1"]
    assert matrix_list == [[0]]
    assert matrix_np.shape == (1, 1)
    assert adj_list == {"N1": []}
    assert rep.verify_representation_consistency() is True


def test_linear_p5_adjacency_matrix(linear_graph_p5):
    """Verify Adjacency Matrix for linear graph P5."""
    rep = GraphRepresentation(linear_graph_p5)
    nodes, matrix_list, matrix_np = rep.to_adjacency_matrix()

    assert nodes == ["v1", "v2", "v3", "v4", "v5"]
    assert matrix_np.shape == (5, 5)

    # Invariant: Symmetry
    assert np.array_equal(matrix_np, matrix_np.T)

    # Invariant: Zero diagonal
    assert np.all(np.diag(matrix_np) == 0)

    # Row checks
    expected_v1 = [0, 1, 0, 0, 0]
    expected_v2 = [1, 0, 1, 0, 0]
    assert matrix_list[0] == expected_v1
    assert matrix_list[1] == expected_v2

    assert rep.verify_representation_consistency() is True


def test_cycle_c5_adjacency_list(cycle_graph_c5):
    """Verify Adjacency List for 2-regular cycle graph C5."""
    rep = GraphRepresentation(cycle_graph_c5)
    adj_list = rep.to_adjacency_list()

    assert set(adj_list.keys()) == {"v1", "v2", "v3", "v4", "v5"}
    assert adj_list["v1"] == ["v2", "v5"]
    assert adj_list["v2"] == ["v1", "v3"]
    assert adj_list["v3"] == ["v2", "v4"]
    assert adj_list["v4"] == ["v3", "v5"]
    assert adj_list["v5"] == ["v1", "v4"]

    assert rep.verify_representation_consistency() is True


def test_complete_k5_representations(complete_graph_k5):
    """Verify Complete Graph K5 representations."""
    rep = GraphRepresentation(complete_graph_k5)
    nodes, matrix_list, matrix_np = rep.to_adjacency_matrix()

    assert matrix_np.shape == (5, 5)
    # Complete graph has 1 everywhere except the diagonal
    expected = np.ones((5, 5), dtype=int) - np.eye(5, dtype=int)
    assert np.array_equal(matrix_np, expected)

    assert rep.verify_representation_consistency() is True


def test_isolated_node_in_disconnected_graph():
    """Verify representation correctly includes isolated vertex alongside a connected cluster."""
    g = NetworkGraph.create()
    g.add_node(Node("A", "server"))
    g.add_node(Node("B", "server"))
    g.add_node(Node("ISO", "server"))  # Isolated vertex
    from app.graph_engine.graph_model import Edge
    g.add_edge(Edge("e1", "A", "B"))

    rep = GraphRepresentation(g)
    nodes, matrix_list, matrix_np = rep.to_adjacency_matrix()
    adj_list = rep.to_adjacency_list()

    assert nodes == ["A", "B", "ISO"]
    assert adj_list["ISO"] == []
    # ISO is index 2, row 2 and column 2 should be all zeros
    assert matrix_list[2] == [0, 0, 0]
    assert [row[2] for row in matrix_list] == [0, 0, 0]

    assert rep.verify_representation_consistency() is True


def test_sample_network_consistency(sample_network):
    """Verify representation consistency across the entire 18-node benchmark topology."""
    rep = GraphRepresentation(sample_network)
    nodes, matrix_list, matrix_np = rep.to_adjacency_matrix()

    assert len(nodes) == 18
    assert matrix_np.shape == (18, 18)
    assert np.array_equal(matrix_np, matrix_np.T)
    assert np.all(np.diag(matrix_np) == 0)
    assert rep.verify_representation_consistency() is True
