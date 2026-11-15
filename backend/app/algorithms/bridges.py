"""
Tarjan's Linear-Time Bridge (Cut-Edge) Detection Algorithm.
Time Complexity: O(V + E)
Space Complexity: O(V)

Mathematical Basis (Tarjan, 1972):
An edge e = {u, v} is a bridge if and only if its removal strictly increases
the number of connected components: kappa(G - e) > kappa(G).

In a DFS tree:
A tree edge (u, v) (where u is the parent of v) is a bridge if and only if:
    low[v] > discovery[u]
This condition proves that no back-edge exists from v or any descendant in the
subtree of v to u or any ancestor of u. Thus, (u, v) is the sole physical conduit
connecting the subtree to the rest of the network.
"""

import sys
from typing import Dict, List, Set, Optional, Tuple, Any
from app.graph_engine.graph_builder import NetworkGraph

# Ensure adequate recursion depth for large network topologies
if sys.getrecursionlimit() < 100000:
    try:
        sys.setrecursionlimit(100000)
    except Exception:
        pass


def find_bridges(graph: NetworkGraph) -> Dict[str, Any]:
    """
    Finds all bridges (cut-edges) in graph G using Tarjan's low-link algorithm.
    Explores all connected components in disconnected graphs.
    
    Args:
        graph: The NetworkGraph instance.
        
    Returns:
        dict:
            - 'bridges': List[Tuple[str, str]], list of bridges as canonical sorted endpoint pairs (u, v) where u < v.
            - 'count': int, total number of bridges.
            - 'discovery_times': Dict[str, int]
            - 'low_links': Dict[str, int]
    """
    all_nodes = graph.get_node_ids()
    discovery: Dict[str, int] = {}
    low: Dict[str, int] = {}
    visited: Set[str] = set()
    bridges: List[Tuple[str, str]] = []
    timer = 0

    def dfs(u: str, parent: Optional[str]) -> None:
        nonlocal timer
        timer += 1
        discovery[u] = timer
        low[u] = timer
        visited.add(u)

        neighbors = graph.get_neighbors(u)
        for v in neighbors:
            if v == parent:
                # Do not backtrack along the immediate tree edge
                continue

            if v in visited:
                # Back-edge to an ancestor of u
                low[u] = min(low[u], discovery[v])
            else:
                # Tree edge
                dfs(v, u)

                # Low-link propagation
                low[u] = min(low[u], low[v])

                # Bridge condition: low[v] > discovery[u]
                if low[v] > discovery[u]:
                    # Format as canonical sorted tuple (u, v) where u < v
                    canonical_edge = (min(u, v), max(u, v))
                    bridges.append(canonical_edge)

    for node in all_nodes:
        if node not in visited:
            dfs(node, None)

    # Sort bridges deterministically
    bridges.sort()

    return {
        "bridges": bridges,
        "count": len(bridges),
        "discovery_times": discovery,
        "low_links": low
    }

