"""
Tarjan's Linear-Time Articulation Point (Cut-Vertex) Detection Algorithm.
Time Complexity: O(V + E)
Space Complexity: O(V)

Mathematical Basis (Hopcroft & Tarjan, 1973):
An articulation point (cut-vertex) is a vertex v whose removal strictly increases
the number of connected components: kappa(G - v) > kappa(G).

In a DFS tree:
1. Root vertex r is an articulation point if and only if it has >= 2 children in the DFS tree.
2. Non-root vertex u is an articulation point if and only if it has a DFS tree child v such that:
   low[v] >= discovery[u]
   which proves that no vertex in the subtree rooted at v has a back-edge to a proper ancestor of u.
"""

import sys
from typing import Dict, List, Set, Optional, Any
from app.graph_engine.graph_builder import NetworkGraph

# Ensure adequate recursion depth for large network topologies
if sys.getrecursionlimit() < 100000:
    try:
        sys.setrecursionlimit(100000)
    except Exception:
        pass


def find_articulation_points(graph: NetworkGraph) -> Dict[str, Any]:
    """
    Finds all articulation points in graph G using Tarjan's low-link algorithm.
    Correctly explores all connected components in disconnected graphs.
    
    Args:
        graph: The NetworkGraph instance.
        
    Returns:
        dict:
            - 'articulation_points': List[str], sorted list of articulation point IDs.
            - 'count': int, total number of articulation points found.
            - 'discovery_times': Dict[str, int]
            - 'low_links': Dict[str, int]
    """
    all_nodes = graph.get_node_ids()
    discovery: Dict[str, int] = {}
    low: Dict[str, int] = {}
    visited: Set[str] = set()
    articulation_points_set: Set[str] = set()
    timer = 0

    def dfs(u: str, parent: Optional[str]) -> None:
        nonlocal timer
        timer += 1
        discovery[u] = timer
        low[u] = timer
        visited.add(u)
        dfs_children = 0

        # Deterministic neighbor order
        neighbors = graph.get_neighbors(u)
        for v in neighbors:
            if v == parent:
                # Do not traverse back immediately through the direct tree edge to parent
                continue

            if v in visited:
                # Back-edge detected: v is an ancestor of u
                low[u] = min(low[u], discovery[v])
            else:
                # Tree edge: v is a newly discovered child in the DFS tree
                dfs_children += 1
                dfs(v, u)

                # Upon return from subtree v, propagate low-link
                low[u] = min(low[u], low[v])

                # Non-root condition: child v cannot reach above u
                if parent is not None and low[v] >= discovery[u]:
                    articulation_points_set.add(u)

        # Root condition: root of a DFS tree with >= 2 children
        if parent is None and dfs_children >= 2:
            articulation_points_set.add(u)

    # Outer loop guarantees all components in a disconnected graph are visited
    for node in all_nodes:
        if node not in visited:
            dfs(node, None)

    ap_list = sorted(list(articulation_points_set))

    return {
        "articulation_points": ap_list,
        "count": len(ap_list),
        "discovery_times": discovery,
        "low_links": low
    }

