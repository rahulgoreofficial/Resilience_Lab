"""
Degree Analysis and Euler's Handshaking Lemma Validation.
Time Complexity: O(V + E)
Space Complexity: O(V)

Mathematical Basis:
Handshaking Lemma (Euler, 1736):
sum_{v in V} deg(v) = 2 * |E|
"""

from typing import Dict, List, Any
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import NodeNotFoundError


def vertex_degree(graph: NetworkGraph, node_id: str) -> int:
    """Returns the degree of a specific node."""
    if not graph.has_node(node_id):
        raise NodeNotFoundError(f"Node '{node_id}' not found.")
    return len(graph.get_neighbors(node_id))


def all_vertex_degrees(graph: NetworkGraph) -> Dict[str, int]:
    """Returns a dictionary mapping every node_id to its degree."""
    return {node_id: len(graph.get_neighbors(node_id)) for node_id in graph.get_node_ids()}


def analyze_degrees(graph: NetworkGraph) -> Dict[str, Any]:
    """
    Computes comprehensive degree metrics for the graph.
    
    Returns:
        dict:
            - 'degrees': Dict[str, int]
            - 'min_degree': int
            - 'max_degree': int
            - 'avg_degree': float
            - 'highest_degree_nodes': List[str]
            - 'degree_sum': int
            - 'handshaking_lemma_verified': bool
    """
    degrees = all_vertex_degrees(graph)
    total_nodes = len(degrees)

    if total_nodes == 0:
        return {
            "degrees": {},
            "min_degree": 0,
            "max_degree": 0,
            "avg_degree": 0.0,
            "highest_degree_nodes": [],
            "degree_sum": 0,
            "handshaking_lemma_verified": True
        }

    degree_values = list(degrees.values())
    min_deg = min(degree_values)
    max_deg = max(degree_values)
    deg_sum = sum(degree_values)
    avg_deg = deg_sum / total_nodes

    highest_degree_nodes = sorted([nid for nid, deg in degrees.items() if deg == max_deg])

    # Validate Euler's Handshaking Lemma: sum(deg) == 2 * |E|
    expected_sum = 2 * graph.edge_count
    handshaking_valid = (deg_sum == expected_sum)

    return {
        "degrees": degrees,
        "min_degree": min_deg,
        "max_degree": max_deg,
        "avg_degree": round(avg_deg, 4),
        "highest_degree_nodes": highest_degree_nodes,
        "degree_sum": deg_sum,
        "expected_degree_sum_2E": expected_sum,
        "handshaking_lemma_verified": handshaking_valid
    }

