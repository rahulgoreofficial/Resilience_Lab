"""
Graph Engine Core: GraphBuilder and NetworkGraph.
Implements the 13 fundamental graph operations for undirected simple graphs.
Independent of web frameworks or UI components.
"""

import json
from typing import Dict, List, Optional, Any, Set, Tuple
from app.graph_engine.graph_model import Node, Edge
from app.graph_engine.graph_validation import (
    DuplicateNodeError,
    DuplicateEdgeError,
    NodeNotFoundError,
    EdgeNotFoundError,
    SelfLoopError,
    GraphStructureError
)


class NetworkGraph:
    """
    Mathematical Representation of an attributed undirected simple graph G = (V, E).
    
    Invariants:
    - Simple graph: No self-loops, no parallel/multi-edges.
    - Symmetric: Edge {u, v} is bidirectional.
    - Consistency: An edge can only exist if both endpoints exist in V.
    - Deletion consistency: Removing a node removes all incident edges.
    """

    def __init__(self, name: str = "Infrastructure_Graph"):
        self.name = name
        # Node storage: node_id -> Node
        self._nodes: Dict[str, Node] = {}
        # Edge storage: edge_id -> Edge
        self._edges: Dict[str, Edge] = {}
        # Undirected edge uniqueness tracking: frozenset({u, v}) -> edge_id
        self._edge_endpoints_map: Dict[frozenset, str] = {}
        # Incident edges adjacency: node_id -> set of edge_ids
        self._incident_edges: Dict[str, Set[str]] = {}

    @property
    def node_count(self) -> int:
        """Returns |V|, the order of the graph."""
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        """Returns |E|, the size of the graph."""
        return len(self._edges)

    # 1. Create Graph (Class method factory)
    @classmethod
    def create(cls, name: str = "Infrastructure_Graph") -> "NetworkGraph":
        """Factory method to instantiate a new empty graph."""
        return cls(name=name)

    # 2. Add Node
    def add_node(self, node: Node) -> None:
        """
        Adds a vertex v to V.
        Raises DuplicateNodeError if node_id already exists.
        """
        if node.node_id in self._nodes:
            raise DuplicateNodeError(f"Node with ID '{node.node_id}' already exists in graph.")
        self._nodes[node.node_id] = node
        self._incident_edges[node.node_id] = set()

    # 3. Add Edge
    def add_edge(self, edge: Edge) -> None:
        """
        Adds an undirected edge e = {source, target} to E.
        Raises NodeNotFoundError if either endpoint does not exist.
        Raises SelfLoopError if source == target.
        Raises DuplicateEdgeError if edge or parallel edge already exists.
        """
        if edge.source not in self._nodes:
            raise NodeNotFoundError(f"Source node '{edge.source}' does not exist in graph.")
        if edge.target not in self._nodes:
            raise NodeNotFoundError(f"Target node '{edge.target}' does not exist in graph.")
        if edge.source == edge.target:
            raise SelfLoopError(f"Self-loops are forbidden: '{edge.source}' -> '{edge.target}'.")

        key = edge.endpoints_key
        if key in self._edge_endpoints_map:
            existing_edge_id = self._edge_endpoints_map[key]
            raise DuplicateEdgeError(
                f"Undirected edge between '{edge.source}' and '{edge.target}' already exists (ID: '{existing_edge_id}')."
            )

        if edge.edge_id in self._edges:
            raise DuplicateEdgeError(f"Edge with ID '{edge.edge_id}' already exists in graph.")

        self._edges[edge.edge_id] = edge
        self._edge_endpoints_map[key] = edge.edge_id
        self._incident_edges[edge.source].add(edge.edge_id)
        self._incident_edges[edge.target].add(edge.edge_id)

    # 4. Remove Node
    def remove_node(self, node_id: str) -> Node:
        """
        Removes a vertex v from V, simultaneously deleting all incident edges.
        Raises NodeNotFoundError if node_id does not exist.
        """
        if node_id not in self._nodes:
            raise NodeNotFoundError(f"Cannot remove: Node '{node_id}' not found.")

        # Identify all incident edges to safely remove them
        incident_edge_ids = list(self._incident_edges.get(node_id, set()))
        for edge_id in incident_edge_ids:
            self.remove_edge(edge_id)

        # Remove the node
        removed_node = self._nodes.pop(node_id)
        self._incident_edges.pop(node_id, None)
        return removed_node

    # 5. Remove Edge
    def remove_edge(self, edge_id: str) -> Edge:
        """
        Removes an edge e from E.
        Raises EdgeNotFoundError if edge_id does not exist.
        """
        if edge_id not in self._edges:
            raise EdgeNotFoundError(f"Cannot remove: Edge '{edge_id}' not found.")

        edge = self._edges.pop(edge_id)
        key = edge.endpoints_key
        self._edge_endpoints_map.pop(key, None)

        if edge.source in self._incident_edges:
            self._incident_edges[edge.source].discard(edge_id)
        if edge.target in self._incident_edges:
            self._incident_edges[edge.target].discard(edge_id)

        return edge

    def remove_edge_by_endpoints(self, source: str, target: str) -> Edge:
        """Removes edge by endpoint vertex IDs."""
        key = frozenset([source, target])
        if key not in self._edge_endpoints_map:
            raise EdgeNotFoundError(f"No edge connects '{source}' and '{target}'.")
        edge_id = self._edge_endpoints_map[key]
        return self.remove_edge(edge_id)

    # 6. Retrieve Node
    def get_node(self, node_id: str) -> Node:
        """
        Retrieves a node by ID.
        Raises NodeNotFoundError if not found.
        """
        if node_id not in self._nodes:
            raise NodeNotFoundError(f"Node '{node_id}' not found in graph.")
        return self._nodes[node_id]

    def has_node(self, node_id: str) -> bool:
        """Returns True if node exists in V."""
        return node_id in self._nodes

    # 7. Retrieve Edge
    def get_edge(self, edge_id: str) -> Edge:
        """
        Retrieves an edge by ID.
        Raises EdgeNotFoundError if not found.
        """
        if edge_id not in self._edges:
            raise EdgeNotFoundError(f"Edge '{edge_id}' not found in graph.")
        return self._edges[edge_id]

    def get_edge_between(self, source: str, target: str) -> Optional[Edge]:
        """Returns edge between source and target, or None if not connected."""
        key = frozenset([source, target])
        if key in self._edge_endpoints_map:
            edge_id = self._edge_endpoints_map[key]
            return self._edges[edge_id]
        return None

    def has_edge(self, source: str, target: str) -> bool:
        """Checks if an undirected edge connects source and target."""
        return frozenset([source, target]) in self._edge_endpoints_map

    def has_edge_between(self, source: str, target: str) -> bool:
        """Alias for has_edge."""
        return self.has_edge(source, target)

    # 8. List All Nodes
    def get_all_nodes(self) -> List[Node]:
        """Returns a deterministically sorted list of all nodes."""
        return [self._nodes[nid] for nid in sorted(self._nodes.keys())]

    def get_node_ids(self) -> List[str]:
        """Returns sorted list of node IDs."""
        return sorted(list(self._nodes.keys()))

    # 9. List All Edges
    def get_all_edges(self) -> List[Edge]:
        """Returns a deterministically sorted list of all edges."""
        return [self._edges[eid] for eid in sorted(self._edges.keys())]

    # 10. Update Node Properties
    def update_node(self, node_id: str, **kwargs) -> Node:
        """
        Updates node properties and validates updated attributes.
        Raises NodeNotFoundError if node_id does not exist.
        """
        if node_id not in self._nodes:
            raise NodeNotFoundError(f"Cannot update: Node '{node_id}' not found.")

        current_node = self._nodes[node_id]
        current_data = current_node.to_dict()

        for key, value in kwargs.items():
            if key in current_data and key != "node_id":
                current_data[key] = value

        updated_node = Node.from_dict(current_data)
        self._nodes[node_id] = updated_node
        return updated_node

    # 11. Update Edge Properties
    def update_edge(self, edge_id: str, **kwargs) -> Edge:
        """
        Updates edge properties and validates updated attributes.
        Raises EdgeNotFoundError if edge_id does not exist.
        """
        if edge_id not in self._edges:
            raise EdgeNotFoundError(f"Cannot update: Edge '{edge_id}' not found.")

        current_edge = self._edges[edge_id]
        current_data = current_edge.to_dict()

        for key, value in kwargs.items():
            if key in current_data and key not in ("edge_id", "source", "target"):
                current_data[key] = value

        updated_edge = Edge.from_dict(current_data)
        self._edges[edge_id] = updated_edge
        return updated_edge

    # Neighbors and Incident Edges helper
    def get_neighbors(self, node_id: str) -> List[str]:
        """
        Returns sorted list of neighboring vertex IDs for node_id.
        Raises NodeNotFoundError if node_id does not exist.
        """
        if node_id not in self._nodes:
            raise NodeNotFoundError(f"Node '{node_id}' not found.")

        neighbors: Set[str] = set()
        for edge_id in self._incident_edges[node_id]:
            edge = self._edges[edge_id]
            opp = edge.get_opposite_endpoint(node_id)
            if opp:
                neighbors.add(opp)
        return sorted(list(neighbors))

    # 12. Export Graph to JSON
    def to_json(self, indent: int = 2) -> str:
        """Exports graph to a standard JSON string."""
        data = {
            "name": self.name,
            "directed": False,
            "multigraph": False,
            "nodes": [node.to_dict() for node in self.get_all_nodes()],
            "edges": [edge.to_dict() for edge in self.get_all_edges()]
        }
        return json.dumps(data, indent=indent)

    def to_dict(self) -> Dict[str, Any]:
        """Exports graph to a dictionary."""
        return {
            "name": self.name,
            "directed": False,
            "multigraph": False,
            "nodes": [node.to_dict() for node in self.get_all_nodes()],
            "edges": [edge.to_dict() for edge in self.get_all_edges()]
        }

    # 13. Import Graph from JSON
    @classmethod
    def from_json(cls, json_str: str) -> "NetworkGraph":
        """
        Imports and validates a graph from a JSON string.
        Raises GraphStructureError if JSON is malformed or invalid.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as exc:
            raise GraphStructureError(f"Invalid JSON provided: {exc}")

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NetworkGraph":
        """Imports and validates a graph from a dictionary."""
        name = data.get("name", "Imported_Graph")
        graph = cls(name=name)

        if "nodes" not in data or not isinstance(data["nodes"], list):
            raise GraphStructureError("Input data must contain a 'nodes' list.")

        for node_data in data["nodes"]:
            node = Node.from_dict(node_data)
            graph.add_node(node)

        edges_data = data.get("edges") or data.get("links") or []
        if not isinstance(edges_data, list):
            raise GraphStructureError("Edge data must be a list under 'edges' or 'links'.")

        for edge_data in edges_data:
            edge = Edge.from_dict(edge_data)
            graph.add_edge(edge)

        return graph

    def clone(self, new_name: Optional[str] = None) -> "NetworkGraph":
        """
        Creates an isolated deep clone of this NetworkGraph.
        All nodes and edges are duplicated; modifications to the clone do not affect the original.
        """
        cloned_graph = NetworkGraph(name=new_name or f"{self.name}_copy")
        for node in self.get_all_nodes():
            cloned_graph.add_node(Node.from_dict(node.to_dict()))
        for edge in self.get_all_edges():
            cloned_graph.add_edge(Edge.from_dict(edge.to_dict()))
        return cloned_graph

    def clear(self) -> None:
        """Clears all nodes and edges from the graph."""
        self._nodes.clear()
        self._edges.clear()
        self._edge_endpoints_map.clear()
        self._incident_edges.clear()

