"""
Unit tests for NetworkGraph and GraphBuilder core functionality.
Tests the 13 fundamental graph operations and state transitions.
"""

import pytest
from app.graph_engine.graph_model import Node, Edge
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import NodeNotFoundError, EdgeNotFoundError


def test_create_graph(empty_graph):
    """Verify initialization of empty graph."""
    assert empty_graph.node_count == 0
    assert empty_graph.edge_count == 0
    assert empty_graph.get_all_nodes() == []
    assert empty_graph.get_all_edges() == []


def test_add_and_retrieve_node(empty_graph):
    """Verify adding and retrieving a node."""
    node = Node("R1", "router", importance=3.0, capacity=200.0)
    empty_graph.add_node(node)

    assert empty_graph.node_count == 1
    assert empty_graph.has_node("R1") is True
    retrieved = empty_graph.get_node("R1")
    assert retrieved.node_id == "R1"
    assert retrieved.capacity == 200.0


def test_add_and_retrieve_edge(empty_graph):
    """Verify adding and retrieving edges."""
    empty_graph.add_node(Node("A", "switch"))
    empty_graph.add_node(Node("B", "server"))
    edge = Edge("e_ab", "A", "B", weight=2.5, latency=0.8)
    empty_graph.add_edge(edge)

    assert empty_graph.edge_count == 1
    assert empty_graph.has_edge("A", "B") is True
    assert empty_graph.has_edge("B", "A") is True  # Symmetric
    retrieved = empty_graph.get_edge("e_ab")
    assert retrieved.weight == 2.5
    assert retrieved.latency == 0.8


def test_remove_edge(two_node_graph):
    """Verify removing an edge preserves the endpoint nodes."""
    assert two_node_graph.edge_count == 1
    removed = two_node_graph.remove_edge("e1")
    assert removed.edge_id == "e1"
    assert two_node_graph.edge_count == 0
    # Nodes still exist
    assert two_node_graph.node_count == 2
    assert two_node_graph.has_node("A") is True
    assert two_node_graph.has_node("B") is True


def test_remove_node_cascades_to_incident_edges(two_node_graph):
    """Verify removing a node removes all of its incident edges."""
    assert two_node_graph.node_count == 2
    assert two_node_graph.edge_count == 1

    removed_node = two_node_graph.remove_node("A")
    assert removed_node.node_id == "A"
    assert two_node_graph.node_count == 1
    assert two_node_graph.edge_count == 0  # Incident edge e1 was removed!
    assert two_node_graph.has_edge("A", "B") is False


def test_update_node_properties(empty_graph):
    """Verify updating node attributes."""
    empty_graph.add_node(Node("S1", "switch", capacity=100.0, current_load=20.0))
    updated = empty_graph.update_node("S1", capacity=300.0, current_load=50.0, is_critical=True)

    assert updated.capacity == 300.0
    assert updated.current_load == 50.0
    assert updated.is_critical is True
    assert empty_graph.get_node("S1").capacity == 300.0


def test_update_edge_properties(two_node_graph):
    """Verify updating edge attributes."""
    updated = two_node_graph.update_edge("e1", weight=5.0, latency=2.0)
    assert updated.weight == 5.0
    assert updated.latency == 2.0
    assert two_node_graph.get_edge("e1").weight == 5.0


def test_get_neighbors(star_graph_s5):
    """Verify neighbor retrieval for hub and leaves."""
    hub_neighbors = star_graph_s5.get_neighbors("H")
    assert hub_neighbors == ["L1", "L2", "L3", "L4"]

    leaf_neighbors = star_graph_s5.get_neighbors("L1")
    assert leaf_neighbors == ["H"]


def test_json_export_and_import(star_graph_s5):
    """Verify graph serialization to JSON and subsequent deserialization."""
    json_str = star_graph_s5.to_json()
    imported_graph = NetworkGraph.from_json(json_str)

    assert imported_graph.node_count == star_graph_s5.node_count
    assert imported_graph.edge_count == star_graph_s5.edge_count
    assert imported_graph.get_node_ids() == star_graph_s5.get_node_ids()
    assert imported_graph.get_neighbors("H") == ["L1", "L2", "L3", "L4"]


def test_nonexistent_node_error(empty_graph):
    """Verify querying non-existent node raises NodeNotFoundError."""
    with pytest.raises(NodeNotFoundError):
        empty_graph.get_node("GHOST")
    with pytest.raises(NodeNotFoundError):
        empty_graph.remove_node("GHOST")


def test_nonexistent_edge_error(empty_graph):
    """Verify querying non-existent edge raises EdgeNotFoundError."""
    with pytest.raises(EdgeNotFoundError):
        empty_graph.get_edge("GHOST_EDGE")
    with pytest.raises(EdgeNotFoundError):
        empty_graph.remove_edge("GHOST_EDGE")

