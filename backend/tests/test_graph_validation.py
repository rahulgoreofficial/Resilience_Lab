"""
Unit tests for graph validation and constraint enforcement.
Verifies rejection of invalid node/edge attributes, self-loops, and duplicates.
"""

import pytest
from app.graph_engine.graph_model import Node, Edge
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import (
    NodeValidationError,
    EdgeValidationError,
    DuplicateNodeError,
    DuplicateEdgeError,
    NodeNotFoundError,
    SelfLoopError
)


def test_empty_node_id_rejected():
    """Verify empty or whitespace-only node ID is rejected."""
    with pytest.raises(NodeValidationError):
        Node("", "router")
    with pytest.raises(NodeValidationError):
        Node("   ", "switch")


def test_invalid_node_type_rejected():
    """Verify unapproved device types are rejected."""
    with pytest.raises(NodeValidationError):
        Node("v1", "quantum_computer")
    with pytest.raises(NodeValidationError):
        Node("v2", "satellite")


def test_negative_importance_rejected():
    """Verify negative importance values are rejected."""
    with pytest.raises(NodeValidationError):
        Node("v1", "router", importance=-1.0)


def test_zero_or_negative_capacity_rejected():
    """Verify capacity must be strictly positive."""
    with pytest.raises(NodeValidationError):
        Node("v1", "router", capacity=0.0)
    with pytest.raises(NodeValidationError):
        Node("v2", "router", capacity=-50.0)


def test_negative_current_load_rejected():
    """Verify current load cannot be negative."""
    with pytest.raises(NodeValidationError):
        Node("v1", "switch", current_load=-10.0)


def test_invalid_failure_probability_rejected():
    """Verify failure probability must be in range [0, 1]."""
    with pytest.raises(NodeValidationError):
        Node("v1", "server", failure_probability=-0.1)
    with pytest.raises(NodeValidationError):
        Node("v2", "server", failure_probability=1.05)


def test_duplicate_node_rejected():
    """Verify adding duplicate node ID raises DuplicateNodeError."""
    g = NetworkGraph.create()
    g.add_node(Node("R1", "router"))
    with pytest.raises(DuplicateNodeError):
        g.add_node(Node("R1", "switch"))


def test_self_loop_rejected():
    """Verify self-loops (source == target) are rejected."""
    with pytest.raises(SelfLoopError):
        Edge("e1", "R1", "R1")


def test_duplicate_edge_rejected():
    """Verify duplicate undirected edges in both forward and reverse directions are rejected."""
    g = NetworkGraph.create()
    g.add_node(Node("A", "router"))
    g.add_node(Node("B", "switch"))
    g.add_edge(Edge("e1", "A", "B"))

    # Duplicate forward direction
    with pytest.raises(DuplicateEdgeError):
        g.add_edge(Edge("e2", "A", "B"))

    # Duplicate reverse direction {B, A}
    with pytest.raises(DuplicateEdgeError):
        g.add_edge(Edge("e3", "B", "A"))


def test_edge_nonexistent_endpoints_rejected():
    """Verify edge cannot connect non-existent nodes."""
    g = NetworkGraph.create()
    g.add_node(Node("A", "router"))

    with pytest.raises(NodeNotFoundError):
        g.add_edge(Edge("e1", "A", "NON_EXISTENT"))

    with pytest.raises(NodeNotFoundError):
        g.add_edge(Edge("e2", "NON_EXISTENT", "A"))


def test_negative_edge_attributes_rejected():
    """Verify negative weight, latency, and invalid reliability are rejected."""
    with pytest.raises(EdgeValidationError):
        Edge("e1", "A", "B", weight=-1.0)

    with pytest.raises(EdgeValidationError):
        Edge("e2", "A", "B", latency=-0.5)

    with pytest.raises(EdgeValidationError):
        Edge("e3", "A", "B", capacity=-10.0)

    with pytest.raises(EdgeValidationError):
        Edge("e4", "A", "B", reliability=1.2)
