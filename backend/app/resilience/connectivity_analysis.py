"""
Connectivity Analysis Module: Comprehensive topological profile computation.
Evaluates graph connectivity, reachability, and baseline invariants.
"""

from typing import Dict, List, Optional, Any
from app.graph_engine.graph_builder import NetworkGraph
from app.algorithms.connected_components import find_connected_components
from app.resilience.metrics import (
    calculate_lcc_ratio,
    calculate_pairwise_connectivity,
    calculate_connectivity_loss
)
from app.graph_engine.reachability import (
    compute_reachability,
    evaluate_service_reachability
)


def analyze_network_connectivity(
    graph: NetworkGraph,
    entry_points: Optional[List[str]] = None,
    critical_services: Optional[List[str]] = None,
    baseline_node_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Computes a comprehensive connectivity and resilience profile of graph G.
    
    Args:
        graph: NetworkGraph to analyze (either baseline or simulation snapshot).
        entry_points: Optional network ingress node IDs.
        critical_services: Optional designated server node IDs.
        baseline_node_ids: Optional list of original nodes to detect unreachable nodes.
        
    Returns:
        Structured dictionary containing counts, components, reachability, and metrics.
    """
    node_ids = graph.get_node_ids()
    edge_ids = [e.edge_id for e in graph.get_all_edges()]
    active_v = len(node_ids)
    active_e = len(edge_ids)

    # 1. Connected Components Decomposition
    comp_info = find_connected_components(graph)
    comp_sizes = [len(c) for c in comp_info["components"]]
    giant_size = comp_info["giant_component_size"]

    # 2. Resilience Metrics
    lcc_ratio = calculate_lcc_ratio(giant_size, active_v)
    pair_conn = calculate_pairwise_connectivity(comp_sizes, active_v)
    conn_loss = calculate_connectivity_loss(pair_conn)

    # 3. Ingress Reachability
    reachable_nodes, unreachable_nodes = compute_reachability(
        graph=graph,
        entry_points=entry_points,
        all_known_nodes=baseline_node_ids or node_ids
    )

    # 4. Critical Service Reachability
    reachable_svcs, affected_svcs, svc_status = evaluate_service_reachability(
        graph=graph,
        critical_services=critical_services,
        entry_points=entry_points,
        all_known_nodes=baseline_node_ids or node_ids
    )

    return {
        "active_vertices": active_v,
        "active_edges": active_e,
        "component_count": comp_info["component_count"],
        "components": comp_info["components"],
        "giant_component": comp_info["giant_component"],
        "giant_component_size": giant_size,
        "isolated_nodes": comp_info["isolated_nodes"],
        "lcc_ratio": lcc_ratio,
        "pairwise_connectivity": pair_conn,
        "connectivity_loss": conn_loss,
        "entry_points": entry_points or [],
        "reachable_nodes": reachable_nodes,
        "unreachable_nodes": unreachable_nodes,
        "critical_services_status": svc_status,
        "critical_services": critical_services or [],
        "reachable_critical_services": reachable_svcs,
        "unreachable_critical_services": affected_svcs
    }
