"""
Simulation Utilities: Snapshotting, Combinatorics, Hashing, and Reachability.
Ensures snapshot isolation so that baseline graphs are never mutated.
"""

import hashlib
import json
import math
from typing import List, Set, Tuple, Dict, Any, Optional
from collections import deque

from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_model import Node, Edge
from app.graph_engine.reachability import compute_reachability, evaluate_service_reachability


def create_isolated_graph_snapshot(graph: NetworkGraph, snapshot_name: Optional[str] = None) -> NetworkGraph:
    """
    Creates an isolated snapshot of graph G.
    Guarantees that all subsequent mutations occur strictly on the snapshot.
    """
    return graph.clone(new_name=snapshot_name or f"{graph.name}_sim_snapshot")


def hash_graph_topology(graph: NetworkGraph) -> str:
    """
    Generates a deterministic SHA-256 fingerprint of the graph topology.
    Used for audit trails and verifying baseline snapshot integrity.
    """
    canonical_repr = {
        "nodes": sorted([
            {"id": n.node_id, "type": n.node_type, "capacity": n.capacity, "load": n.current_load}
            for n in graph.get_all_nodes()
        ], key=lambda x: x["id"]),
        "edges": sorted([
            {"id": e.edge_id, "u": min(e.source, e.target), "v": max(e.source, e.target), "weight": e.weight}
            for e in graph.get_all_edges()
        ], key=lambda x: (x["u"], x["v"]))
    }
    encoded = json.dumps(canonical_repr, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def calculate_combination_count(n: int, k: int) -> int:
    """
    Calculates binomial coefficient C(n, k) = n! / (k! * (n - k)!).
    Models the number of distinct k-component failure scenarios in an n-component network.
    """
    if n < 0 or k < 0 or k > n:
        return 0
    return math.comb(n, k)


def compute_reachability(
    graph: NetworkGraph,
    entry_points: Optional[List[str]] = None,
    all_known_nodes: Optional[List[str]] = None
) -> Tuple[List[str], List[str]]:
    """
    Computes reachable and unreachable nodes starting from a set of entry points.
    
    Args:
        graph: Active NetworkGraph (failed components already removed).
        entry_points: List of ingress router/gateway node IDs.
        all_known_nodes: Optional baseline node list. If provided, any node in this list
                         not reachable in active graph is flagged unreachable.
                         
    Returns:
        (reachable_nodes, unreachable_nodes) both sorted alphabetically.
    """
    active_nodes = set(graph.get_node_ids())
    baseline_nodes = set(all_known_nodes) if all_known_nodes else active_nodes

    if not entry_points:
        # If no entry points are configured, all active nodes are considered in-service
        return sorted(list(active_nodes)), sorted(list(baseline_nodes - active_nodes))

    # Filter entry points that are still active
    valid_active_entries = [ep for ep in entry_points if ep in active_nodes]
    if not valid_active_entries:
        # All entry points are down or unreachable
        return [], sorted(list(baseline_nodes))

    visited: Set[str] = set()
    queue = deque(valid_active_entries)
    for ep in valid_active_entries:
        visited.add(ep)

    while queue:
        curr = queue.popleft()
        for neighbor in graph.get_neighbors(curr):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    reachable = sorted(list(visited))
    unreachable = sorted(list(baseline_nodes - visited))
    return reachable, unreachable


def evaluate_service_reachability(
    graph: NetworkGraph,
    critical_services: Optional[List[str]],
    entry_points: Optional[List[str]],
    all_known_nodes: Optional[List[str]] = None
) -> Tuple[List[str], List[str], str]:
    """
    Evaluates reachability of designated critical services from active entry points.
    
    Returns:
        (reachable_services, affected_services, status_string)
    """
    if not critical_services:
        return [], [], "NOT CONFIGURED"

    reachable_nodes, _ = compute_reachability(
        graph=graph,
        entry_points=entry_points,
        all_known_nodes=all_known_nodes
    )
    reachable_set = set(reachable_nodes)
    
    reachable_services = sorted([s for s in critical_services if s in reachable_set])
    affected_services = sorted([s for s in critical_services if s not in reachable_set])
    
    return reachable_services, affected_services, "CONFIGURED"
