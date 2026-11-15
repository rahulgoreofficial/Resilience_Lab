"""
Connected Components Detection Algorithm.
Time Complexity: O(V + E)
Space Complexity: O(V)

Mathematical Basis:
Decomposes the vertex set V into disjoint equivalence classes under the
Reachability Relation R: V / R = {V_1, V_2, ..., V_k}.
Each V_i induces a connected subgraph.
"""

from typing import Dict, List, Set, Any
from collections import deque
from app.graph_engine.graph_builder import NetworkGraph


def find_connected_components(graph: NetworkGraph) -> Dict[str, Any]:
    """
    Identifies all connected components in the undirected graph.
    
    Args:
        graph: The NetworkGraph instance.
        
    Returns:
        dict:
            - 'component_count': int, total number of connected components kappa(G).
            - 'components': List[List[str]], list of component vertex rosters.
            - 'is_connected': bool, True if component_count == 1 (and |V| > 0).
            - 'giant_component': List[str], the largest connected component.
            - 'isolated_nodes': List[str], nodes with degree 0.
    """
    all_nodes = graph.get_node_ids()  # Deterministically sorted
    visited: Set[str] = set()
    components: List[List[str]] = []
    isolated_nodes: List[str] = []

    for node in all_nodes:
        if node not in visited:
            # Check for isolated node (degree == 0)
            neighbors = graph.get_neighbors(node)
            if not neighbors:
                isolated_nodes.append(node)

            # Discover component using BFS
            current_component: List[str] = []
            queue = deque([node])
            visited.add(node)

            while queue:
                curr = queue.popleft()
                current_component.append(curr)

                for neighbor in graph.get_neighbors(curr):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            current_component.sort()
            components.append(current_component)

    # Sort components deterministically: primary key by length descending, secondary by first node ID
    components.sort(key=lambda c: (-len(c), c[0] if c else ""))

    giant_component = components[0] if components else []
    is_connected = (len(components) == 1) if all_nodes else False

    return {
        "component_count": len(components),
        "components": components,
        "is_connected": is_connected,
        "giant_component": giant_component,
        "giant_component_size": len(giant_component),
        "isolated_nodes": sorted(isolated_nodes)
    }

