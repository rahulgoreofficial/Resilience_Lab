"""
Criticality Analysis Engine: Single-Component Vulnerability Profiling.
Calculates exact structural and service disruption caused by removing each node or edge individually.
Integrates Tarjan's Articulation Points and Bridges with quantitative resilience loss.
Complexity: O(V * (V + E)) for nodes, O(E * (V + E)) for edges.
"""

from typing import List, Dict, Any, Optional
from app.graph_engine.graph_builder import NetworkGraph
from app.algorithms.articulation_points import find_articulation_points
from app.algorithms.bridges import find_bridges
from app.resilience.connectivity_analysis import analyze_network_connectivity
from app.simulation.simulation_utils import create_isolated_graph_snapshot


def analyze_node_criticality(
    graph: NetworkGraph,
    entry_points: Optional[List[str]] = None,
    critical_services: Optional[List[str]] = None,
    max_nodes: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates individual node criticality by systematically simulating G - v for each v in V.
    
    Args:
        graph: Baseline network graph.
        entry_points: Ingress entry points for reachability evaluation.
        critical_services: Critical server IDs.
        max_nodes: Optional limit on the number of nodes evaluated (for large graphs).
        
    Returns:
        Sorted list of node criticality records ranked descending by impact.
    """
    baseline_analysis = analyze_network_connectivity(
        graph=graph,
        entry_points=entry_points,
        critical_services=critical_services
    )
    baseline_pair_conn = baseline_analysis["pairwise_connectivity"]
    baseline_lcc = baseline_analysis["giant_component_size"]
    baseline_comp_count = baseline_analysis["component_count"]
    baseline_reachable_svcs = len(baseline_analysis["reachable_critical_services"])

    # Tarjan Articulation Points
    ap_result = find_articulation_points(graph)
    ap_set = set(ap_result["articulation_points"])

    all_nodes = graph.get_node_ids()
    nodes_to_eval = all_nodes[:max_nodes] if max_nodes else all_nodes

    rankings: List[Dict[str, Any]] = []

    for nid in nodes_to_eval:
        node = graph.get_node(nid)
        # Snapshot isolation: G - v
        sim_graph = create_isolated_graph_snapshot(graph, snapshot_name=f"crit_node_{nid}")
        sim_graph.remove_node(nid)

        post_analysis = analyze_network_connectivity(
            graph=sim_graph,
            entry_points=entry_points,
            critical_services=critical_services,
            baseline_node_ids=all_nodes
        )

        post_pair_conn = post_analysis["pairwise_connectivity"]
        post_lcc = post_analysis["giant_component_size"]
        post_comp_count = post_analysis["component_count"]
        post_reachable_svcs = len(post_analysis["reachable_critical_services"])

        # Disruption metrics
        connectivity_impact = round(max(0.0, baseline_pair_conn - post_pair_conn), 4)
        lcc_impact = max(0, baseline_lcc - post_lcc)
        comp_increase = max(0, post_comp_count - baseline_comp_count)

        service_impact = 0.0
        if baseline_reachable_svcs > 0:
            lost_svcs = baseline_reachable_svcs - post_reachable_svcs
            service_impact = round(max(0.0, lost_svcs / baseline_reachable_svcs), 4)

        is_ap = nid in ap_set

        # Composite criticality score: balances pairwise degradation, service loss, and AP status
        composite_score = round(
            (0.4 * connectivity_impact) +
            (0.3 * service_impact) +
            (0.2 * (lcc_impact / len(all_nodes) if all_nodes else 0.0)) +
            (0.1 * (1.0 if is_ap else 0.0)),
            4
        )

        rankings.append({
            "node_id": nid,
            "node_type": node.node_type,
            "is_articulation_point": is_ap,
            "connectivity_impact": connectivity_impact,
            "service_impact": service_impact,
            "lcc_reduction": lcc_impact,
            "component_increase": comp_increase,
            "post_failure_components": post_comp_count,
            "criticality_score": composite_score
        })

    # Sort descending by composite criticality score, tie-breaking alphabetically by node_id
    rankings.sort(key=lambda item: (-item["criticality_score"], -item["connectivity_impact"], item["node_id"]))

    for rank_idx, record in enumerate(rankings, start=1):
        record["rank"] = rank_idx

    return rankings


def analyze_edge_criticality(
    graph: NetworkGraph,
    entry_points: Optional[List[str]] = None,
    critical_services: Optional[List[str]] = None,
    max_edges: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates individual edge criticality by systematically simulating G - e for each e in E.
    Combines Tarjan's bridge classification with measured topological and service impact.
    
    Args:
        graph: Baseline network graph.
        entry_points: Ingress entry points for reachability evaluation.
        critical_services: Critical server IDs.
        max_edges: Optional limit on the number of edges evaluated.
        
    Returns:
        Sorted list of edge criticality records ranked descending by impact.
    """
    baseline_analysis = analyze_network_connectivity(
        graph=graph,
        entry_points=entry_points,
        critical_services=critical_services
    )
    baseline_pair_conn = baseline_analysis["pairwise_connectivity"]
    baseline_comp_count = baseline_analysis["component_count"]
    baseline_reachable_svcs = len(baseline_analysis["reachable_critical_services"])

    # Tarjan Bridges
    bridge_result = find_bridges(graph)
    bridge_set = {frozenset([u, v]) for u, v in bridge_result["bridges"]}

    all_edges = graph.get_all_edges()
    edges_to_eval = all_edges[:max_edges] if max_edges else all_edges
    total_nodes_count = graph.node_count

    rankings: List[Dict[str, Any]] = []

    for edge in edges_to_eval:
        sim_graph = create_isolated_graph_snapshot(graph, snapshot_name=f"crit_edge_{edge.edge_id}")
        sim_graph.remove_edge(edge.edge_id)

        post_analysis = analyze_network_connectivity(
            graph=sim_graph,
            entry_points=entry_points,
            critical_services=critical_services
        )

        post_pair_conn = post_analysis["pairwise_connectivity"]
        post_comp_count = post_analysis["component_count"]
        post_reachable_svcs = len(post_analysis["reachable_critical_services"])

        connectivity_impact = round(max(0.0, baseline_pair_conn - post_pair_conn), 4)
        comp_increase = max(0, post_comp_count - baseline_comp_count)

        service_impact = 0.0
        if baseline_reachable_svcs > 0:
            lost_svcs = baseline_reachable_svcs - post_reachable_svcs
            service_impact = round(max(0.0, lost_svcs / baseline_reachable_svcs), 4)

        is_bridge = frozenset([edge.source, edge.target]) in bridge_set

        composite_score = round(
            (0.5 * connectivity_impact) +
            (0.3 * service_impact) +
            (0.2 * (1.0 if is_bridge else 0.0)),
            4
        )

        rankings.append({
            "edge_id": edge.edge_id,
            "source": edge.source,
            "target": edge.target,
            "is_bridge": is_bridge,
            "connectivity_impact": connectivity_impact,
            "service_impact": service_impact,
            "component_increase": comp_increase,
            "post_failure_components": post_comp_count,
            "criticality_score": composite_score
        })

    rankings.sort(key=lambda item: (-item["criticality_score"], -item["connectivity_impact"], item["edge_id"]))

    for rank_idx, record in enumerate(rankings, start=1):
        record["rank"] = rank_idx

    return rankings

