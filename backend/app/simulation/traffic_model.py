"""
Traffic Flow and Capacity Redistribution Model.
Simulates indivisible traffic demand flows routed along shortest paths in G.
Computes load aggregation on nodes and communication links.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import NodeNotFoundError, GraphException
from app.algorithms.shortest_path import dijkstra_shortest_path


@dataclass
class TrafficDemand:
    """Represents an indivisible traffic demand from source to destination."""
    source: str
    destination: str
    amount: float

    def __post_init__(self):
        self.source = str(self.source).strip()
        self.destination = str(self.destination).strip()
        self.amount = float(self.amount)
        if self.amount <= 0.0:
            raise GraphException(f"Traffic demand amount must be positive, got {self.amount}")
        if self.source == self.destination:
            raise GraphException(f"Traffic demand source and destination cannot be identical ('{self.source}')")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "destination": self.destination,
            "amount": self.amount
        }


def validate_traffic_demands(graph: NetworkGraph, demands: List[TrafficDemand]) -> None:
    """Validates that all demand endpoints exist in the graph."""
    for d in demands:
        if not graph.has_node(d.source):
            raise NodeNotFoundError(f"Traffic demand source '{d.source}' does not exist in graph.")
        if not graph.has_node(d.destination):
            raise NodeNotFoundError(f"Traffic demand destination '{d.destination}' does not exist in graph.")


def route_traffic_flows(
    graph: NetworkGraph,
    demands: List[TrafficDemand],
    weight_attribute: str = "weight"
) -> Dict[str, Any]:
    """
    Routes all traffic demands over the active graph topology using Dijkstra shortest paths.
    Aggregates traffic load onto traversed nodes and links.
    
    Args:
        graph: Active network snapshot.
        demands: List of traffic demands.
        weight_attribute: Edge cost metric for routing.
        
    Returns:
        dict:
            - 'node_loads': Dict[str, float] (background load + routed traffic load)
            - 'node_routed_loads': Dict[str, float]
            - 'edge_routed_loads': Dict[str, float]
            - 'served_demands': List[Dict]
            - 'unserved_demands': List[Dict]
            - 'total_traffic_demanded': float
            - 'total_traffic_served': float
            - 'total_traffic_unserved': float
    """
    all_nodes = graph.get_node_ids()
    all_edges = [e.edge_id for e in graph.get_all_edges()]

    # Initialize load counters
    node_routed_loads: Dict[str, float] = {nid: 0.0 for nid in all_nodes}
    edge_routed_loads: Dict[str, float] = {eid: 0.0 for eid in all_edges}

    served_demands: List[Dict[str, Any]] = []
    unserved_demands: List[Dict[str, Any]] = []
    total_demanded = sum(d.amount for d in demands)
    total_served = 0.0
    total_unserved = 0.0

    for d in demands:
        # Check if endpoints exist in active graph
        if not graph.has_node(d.source) or not graph.has_node(d.destination):
            unserved_demands.append({
                "source": d.source,
                "destination": d.destination,
                "amount": d.amount,
                "reason": "Endpoints down or missing in active topology"
            })
            total_unserved += d.amount
            continue

        sp = dijkstra_shortest_path(graph, source=d.source, target=d.destination, weight_attribute=weight_attribute)
        if sp["distance"] == float("inf"):
            # Unreachable / Partitioned
            unserved_demands.append({
                "source": d.source,
                "destination": d.destination,
                "amount": d.amount,
                "reason": "No active route connects source and destination"
            })
            total_unserved += d.amount
            continue

        # Route successfully found
        path = sp["path"]
        total_served += d.amount
        served_demands.append({
            "source": d.source,
            "destination": d.destination,
            "amount": d.amount,
            "path": path,
            "path_cost": sp["distance"]
        })

        # Add load to traversed nodes
        for node_id in path:
            node_routed_loads[node_id] += d.amount

        # Add load to traversed edges
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge = graph.get_edge_between(u, v)
            if edge:
                edge_routed_loads[edge.edge_id] += d.amount

    # Total Node Load = Background Load + Routed Traffic Load
    total_node_loads: Dict[str, float] = {}
    for nid in all_nodes:
        node = graph.get_node(nid)
        total_node_loads[nid] = round(node.current_load + node_routed_loads[nid], 4)

    return {
        "node_loads": total_node_loads,
        "node_routed_loads": {k: round(v, 4) for k, v in node_routed_loads.items()},
        "edge_routed_loads": {k: round(v, 4) for k, v in edge_routed_loads.items()},
        "served_demands": served_demands,
        "unserved_demands": unserved_demands,
        "total_traffic_demanded": round(total_demanded, 4),
        "total_traffic_served": round(total_served, 4),
        "total_traffic_unserved": round(total_unserved, 4)
    }

