"""
Dijkstra's Shortest Path Algorithm Implementation.
Time Complexity: O((V + E) log V) with binary heap
Space Complexity: O(V)

Mathematical Basis:
Finds the path P* = (s = x_0, x_1, ..., x_k = t) that minimizes sum_{i=1}^k w(x_{i-1}, x_i).
Requires non-negative edge weights (w >= 0).
"""

import heapq
from typing import Dict, List, Optional, Any
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import NodeNotFoundError, EdgeValidationError


def dijkstra_shortest_path(
    graph: NetworkGraph,
    source: str,
    target: Optional[str] = None,
    weight_attribute: str = "weight"
) -> Dict[str, Any]:
    """
    Computes shortest paths from source to target (or all reachable nodes if target is None).
    
    Args:
        graph: The NetworkGraph instance.
        source: Source node ID.
        target: Optional target node ID.
        weight_attribute: Edge attribute to use as cost ('weight' or 'latency').
        
    Returns:
        dict:
            - 'source': str
            - 'target': Optional[str]
            - 'distance': float (or inf if unreachable)
            - 'path': List[str] (node sequence from source to target, or empty if unreachable)
            - 'all_distances': Dict[str, float]
            - 'predecessors': Dict[str, Optional[str]]
            
    Raises:
        NodeNotFoundError: If source or target does not exist.
        EdgeValidationError: If any traversed edge has a negative weight.
    """
    if not graph.has_node(source):
        raise NodeNotFoundError(f"Dijkstra source node '{source}' does not exist in graph.")
    if target is not None and not graph.has_node(target):
        raise NodeNotFoundError(f"Dijkstra target node '{target}' does not exist in graph.")

    all_nodes = graph.get_node_ids()
    distances: Dict[str, float] = {node: float("inf") for node in all_nodes}
    predecessors: Dict[str, Optional[str]] = {node: None for node in all_nodes}

    distances[source] = 0.0
    # Priority queue stores tuples of (current_distance, node_id)
    pq: List[tuple] = [(0.0, source)]
    visited_settled: set = set()

    while pq:
        dist_u, u = heapq.heappop(pq)

        if u in visited_settled:
            continue
        visited_settled.add(u)

        if target is not None and u == target:
            break

        for v in graph.get_neighbors(u):
            if v in visited_settled:
                continue

            edge = graph.get_edge_between(u, v)
            if edge is None:
                continue

            weight = getattr(edge, weight_attribute, 1.0)
            if weight < 0:
                raise EdgeValidationError(f"Negative weight {weight} found on edge between {u} and {v}.")

            alt = dist_u + weight
            if alt < distances[v]:
                distances[v] = alt
                predecessors[v] = u
                heapq.heappush(pq, (alt, v))

    # Reconstruct path if target was requested
    path: List[str] = []
    target_distance = float("inf")

    if target is not None:
        target_distance = distances[target]
        if target_distance != float("inf"):
            curr: Optional[str] = target
            while curr is not None:
                path.append(curr)
                curr = predecessors[curr]
            path.reverse()

    return {
        "source": source,
        "target": target,
        "distance": target_distance if target else None,
        "path": path,
        "is_reachable": (target_distance != float("inf")) if target else True,
        "all_distances": distances,
        "predecessors": predecessors
    }

