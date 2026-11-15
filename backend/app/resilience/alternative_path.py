"""
Alternative Path Analysis: Primary vs. Secondary Route Computation.
Uses Dijkstra's algorithm to analyze rerouting feasibility when critical paths are disrupted.
"""

from typing import List, Dict, Any, Optional, Tuple
from app.graph_engine.graph_builder import NetworkGraph
from app.algorithms.shortest_path import dijkstra_shortest_path
from app.simulation.simulation_utils import create_isolated_graph_snapshot


def analyze_alternative_routes(
    graph: NetworkGraph,
    flow_pairs: List[Tuple[str, str]],
    failed_node_ids: Optional[List[str]] = None,
    failed_edge_ids: Optional[List[str]] = None,
    weight_attribute: str = "weight"
) -> List[Dict[str, Any]]:
    """
    Evaluates primary vs alternative routes between critical endpoints under component failures.
    
    Args:
        graph: Baseline network graph.
        flow_pairs: List of (source, target) endpoint pairs to evaluate.
        failed_node_ids: Optional failed nodes to exclude.
        failed_edge_ids: Optional failed edges to exclude.
        weight_attribute: Cost metric ('weight' or 'latency').
        
    Returns:
        List of route evaluations detailing primary route, alternative route, and cost inflation.
    """
    # Create isolated snapshot with failures applied
    sim_graph = create_isolated_graph_snapshot(graph, snapshot_name="alt_path_sim")
    if failed_edge_ids:
        for eid in failed_edge_ids:
            if eid in [e.edge_id for e in sim_graph.get_all_edges()]:
                sim_graph.remove_edge(eid)
    if failed_node_ids:
        for nid in failed_node_ids:
            if sim_graph.has_node(nid):
                sim_graph.remove_node(nid)

    route_reports: List[Dict[str, Any]] = []

    for src, dst in flow_pairs:
        # Baseline Primary Route
        primary_sp = dijkstra_shortest_path(graph, source=src, target=dst, weight_attribute=weight_attribute)
        primary_exists = primary_sp["distance"] != float("inf")
        primary_path = primary_sp["path"] if primary_exists else []
        primary_cost = primary_sp["distance"] if primary_exists else None

        # Check if primary path is impacted by the failures
        impacted_by_failure = False
        if primary_exists:
            path_nodes = set(primary_path)
            if failed_node_ids and any(nid in path_nodes for nid in failed_node_ids):
                impacted_by_failure = True
            if failed_edge_ids:
                # Check if any traversed edge was failed
                for i in range(len(primary_path) - 1):
                    u, v = primary_path[i], primary_path[i + 1]
                    edge = graph.get_edge_between(u, v)
                    if edge and edge.edge_id in failed_edge_ids:
                        impacted_by_failure = True
                        break

        # Post-failure Alternative Route in sim_graph
        alt_exists = False
        alt_path: List[str] = []
        alt_cost: Optional[float] = None
        cost_increase_ratio: Optional[float] = None

        if sim_graph.has_node(src) and sim_graph.has_node(dst):
            alt_sp = dijkstra_shortest_path(sim_graph, source=src, target=dst, weight_attribute=weight_attribute)
            if alt_sp["distance"] != float("inf"):
                alt_exists = True
                alt_path = alt_sp["path"]
                alt_cost = alt_sp["distance"]
                if primary_cost and primary_cost > 0:
                    cost_increase_ratio = round((alt_cost - primary_cost) / primary_cost, 4)

        route_reports.append({
            "source": src,
            "target": dst,
            "primary_route": primary_path,
            "primary_cost": primary_cost,
            "impacted_by_failure": impacted_by_failure,
            "alternative_route_available": alt_exists,
            "alternative_route": alt_path,
            "alternative_cost": alt_cost,
            "cost_inflation_ratio": cost_increase_ratio
        })

    return route_reports

