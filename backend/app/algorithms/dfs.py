"""
Depth-First Search (DFS) Algorithm Implementation.
Time Complexity: O(V + E)
Space Complexity: O(V)

Features:
- Predictable iterative stack-based implementation avoiding Python recursion limits.
- Deterministic neighbor traversal.
- Handles isolated vertices and disconnected components.
- Returns traversal order, visited set, and discovered discovery order.
"""

from typing import Dict, List, Set, Any, Optional
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import NodeNotFoundError


def depth_first_search(graph: NetworkGraph, start_node: str) -> Dict[str, Any]:
    """
    Executes iterative Depth-First Search starting from start_node.
    
    Args:
        graph: The NetworkGraph instance.
        start_node: The starting vertex ID.
        
    Returns:
        dict containing:
            - 'traversal_order': List[str] of nodes in the order they were first visited.
            - 'visited': Set[str] of reachable nodes.
            - 'predecessors': Dict[str, Optional[str]] DFS parent pointers.
            
    Raises:
        NodeNotFoundError: If start_node is not in the graph.
    """
    if not graph.has_node(start_node):
        raise NodeNotFoundError(f"DFS start node '{start_node}' does not exist in graph.")

    visited: Set[str] = set()
    traversal_order: List[str] = []
    predecessors: Dict[str, Optional[str]] = {start_node: None}

    # Stack holds tuples of (current_node, parent_node)
    stack: List[tuple] = [(start_node, None)]

    while stack:
        current, parent = stack.pop()

        if current not in visited:
            visited.add(current)
            traversal_order.append(current)
            predecessors[current] = parent

            # Push neighbors in reverse sorted order so that the smallest neighbor is popped first
            neighbors = graph.get_neighbors(current)
            for neighbor in reversed(neighbors):
                if neighbor not in visited:
                    stack.append((neighbor, current))

    return {
        "start_node": start_node,
        "traversal_order": traversal_order,
        "visited": visited,
        "predecessors": predecessors,
        "reachable_count": len(visited)
    }


def full_graph_dfs(graph: NetworkGraph) -> List[List[str]]:
    """
    Executes DFS across all connected components of the graph.
    
    Returns:
        List of traversal orders, one per connected component.
    """
    all_nodes = graph.get_node_ids()
    visited_global: Set[str] = set()
    component_traversals: List[List[str]] = []

    for node in all_nodes:
        if node not in visited_global:
            result = depth_first_search(graph, node)
            visited_global.update(result["visited"])
            component_traversals.append(result["traversal_order"])

    return component_traversals

