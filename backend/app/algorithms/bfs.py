"""
Breadth-First Search (BFS) Algorithm Implementation.
Time Complexity: O(V + E)
Space Complexity: O(V)

Features:
- Deterministic neighbor traversal (sorted neighbor ordering).
- Full support for isolated vertices and disconnected components.
- Returns traversal order, discovery levels (distances), and visited set.
"""

from collections import deque
from typing import Dict, List, Set, Any
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import NodeNotFoundError


def breadth_first_search(graph: NetworkGraph, start_node: str) -> Dict[str, Any]:
    """
    Executes Breadth-First Search starting from start_node.
    
    Args:
        graph: The NetworkGraph instance.
        start_node: The starting vertex ID.
        
    Returns:
        dict containing:
            - 'traversal_order': List[str] of nodes in order visited from start_node.
            - 'visited': Set[str] of all reachable nodes.
            - 'distances': Dict[str, int] minimum hop count from start_node to reachable nodes.
            - 'predecessors': Dict[str, Optional[str]] BFS spanning tree parent pointers.
            
    Raises:
        NodeNotFoundError: If start_node is not in the graph.
    """
    if not graph.has_node(start_node):
        raise NodeNotFoundError(f"BFS start node '{start_node}' does not exist in graph.")

    visited: Set[str] = set()
    traversal_order: List[str] = []
    distances: Dict[str, int] = {}
    predecessors: Dict[str, Any] = {}

    queue: deque = deque([start_node])
    visited.add(start_node)
    distances[start_node] = 0
    predecessors[start_node] = None

    while queue:
        current = queue.popleft()
        traversal_order.append(current)

        # Retrieve neighbors in deterministic sorted order
        for neighbor in graph.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                distances[neighbor] = distances[current] + 1
                predecessors[neighbor] = current
                queue.append(neighbor)

    return {
        "start_node": start_node,
        "traversal_order": traversal_order,
        "visited": visited,
        "distances": distances,
        "predecessors": predecessors,
        "reachable_count": len(visited)
    }


def full_graph_bfs(graph: NetworkGraph) -> List[List[str]]:
    """
    Executes BFS across the entire graph, traversing all connected components
    even if the graph is disconnected.
    
    Returns:
        List of traversal orders, one per connected component.
    """
    all_nodes = graph.get_node_ids()
    visited_global: Set[str] = set()
    component_traversals: List[List[str]] = []

    for node in all_nodes:
        if node not in visited_global:
            result = breadth_first_search(graph, node)
            visited_global.update(result["visited"])
            component_traversals.append(result["traversal_order"])

    return component_traversals

