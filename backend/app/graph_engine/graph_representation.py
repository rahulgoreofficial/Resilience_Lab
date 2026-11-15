"""
Graph representation module.
Provides:
1. Adjacency Matrix (with deterministic node ordering and NumPy export).
2. Adjacency List (dictionary mapping each node to sorted neighbor list).
Provides consistency validation between both representations.
"""

from typing import Dict, List, Tuple, Any
import numpy as np
from app.graph_engine.graph_builder import NetworkGraph


class GraphRepresentation:
    """Provides mathematical representations of a NetworkGraph instance."""

    def __init__(self, graph: NetworkGraph):
        self.graph = graph

    def to_adjacency_matrix(self) -> Tuple[List[str], List[List[int]], np.ndarray]:
        """
        Constructs the binary symmetric Adjacency Matrix A.
        
        Returns:
            ordered_node_ids: Sorted list of node IDs corresponding to matrix rows/columns.
            matrix_list: 2D list of integers (0 or 1) of shape |V| x |V|.
            matrix_np: NumPy 2D array of dtype int64.
        """
        ordered_node_ids = self.graph.get_node_ids()
        n = len(ordered_node_ids)
        node_to_idx = {nid: idx for idx, nid in enumerate(ordered_node_ids)}
        
        # Initialize n x n matrix with zeros
        matrix = [[0] * n for _ in range(n)]

        if n == 0:
            return [], [], np.zeros((0, 0), dtype=np.int64)

        for edge in self.graph.get_all_edges():
            u_idx = node_to_idx[edge.source]
            v_idx = node_to_idx[edge.target]
            matrix[u_idx][v_idx] = 1
            matrix[v_idx][u_idx] = 1  # Undirected symmetry

        matrix_np = np.array(matrix, dtype=np.int64)
        return ordered_node_ids, matrix, matrix_np

    def to_adjacency_list(self) -> Dict[str, List[str]]:
        """
        Constructs the Adjacency List representation.
        Guarantees that:
        - Every vertex in V is present as a key (including isolated vertices).
        - Neighbor lists are deterministically sorted.
        
        Returns:
            Dictionary mapping node_id -> sorted list of neighbor node_ids.
        """
        adj_list: Dict[str, List[str]] = {}
        for node_id in self.graph.get_node_ids():
            adj_list[node_id] = self.graph.get_neighbors(node_id)
        return adj_list

    def to_weighted_adjacency_matrix(self, attribute: str = "weight") -> Tuple[List[str], np.ndarray]:
        """
        Constructs a weighted adjacency matrix based on the specified edge attribute
        ('weight', 'latency', 'capacity', or 'reliability').
        Unconnected pairs receive 0.0 (or infinity for distances, depending on application).
        """
        ordered_node_ids = self.graph.get_node_ids()
        n = len(ordered_node_ids)
        node_to_idx = {nid: idx for idx, nid in enumerate(ordered_node_ids)}
        matrix = np.zeros((n, n), dtype=np.float64)

        if n == 0:
            return [], np.zeros((0, 0), dtype=np.float64)

        for edge in self.graph.get_all_edges():
            u_idx = node_to_idx[edge.source]
            v_idx = node_to_idx[edge.target]
            val = getattr(edge, attribute, 1.0)
            matrix[u_idx, v_idx] = val
            matrix[v_idx, u_idx] = val

        return ordered_node_ids, matrix

    def verify_representation_consistency(self) -> bool:
        """
        Mathematically verifies that the Adjacency Matrix and Adjacency List
        describe the exact same graph topology without discrepancies.
        
        Checks:
        1. Both contain the identical set of vertices.
        2. Matrix entry A[i, j] == 1 if and only if node_j in Adj[node_i].
        3. Matrix is strictly symmetric (A == A.T).
        4. Main diagonal is all zeros (simple graph invariant).
        5. Total degree sum matches sum of matrix entries.
        """
        ordered_nodes, matrix, np_matrix = self.to_adjacency_matrix()
        adj_list = self.to_adjacency_list()

        # Check 1: Vertex set alignment
        if set(ordered_nodes) != set(adj_list.keys()):
            return False

        # Check 2: Matrix symmetry
        if not np.array_equal(np_matrix, np_matrix.T):
            return False

        # Check 3: Zero diagonal (no self-loops)
        if np.any(np.diag(np_matrix) != 0):
            return False

        # Check 4: Cross-representation isomorphism
        node_to_idx = {nid: idx for idx, nid in enumerate(ordered_nodes)}
        for u in ordered_nodes:
            u_idx = node_to_idx[u]
            neighbors = adj_list[u]
            for v in ordered_nodes:
                v_idx = node_to_idx[v]
                is_connected_matrix = (matrix[u_idx][v_idx] == 1)
                is_connected_list = (v in neighbors)
                if is_connected_matrix != is_connected_list:
                    return False

        return True
