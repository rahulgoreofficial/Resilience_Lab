"""
Resilience Report Generator: Automated Infrastructure Audit.
Compiles baseline topological metrics, Tarjan single-points-of-failure,
and criticality rankings into a comprehensive audit dossier.
"""

from typing import Dict, Any, Optional, List
from app.graph_engine.graph_builder import NetworkGraph
from app.algorithms.articulation_points import find_articulation_points
from app.algorithms.bridges import find_bridges
from app.resilience.connectivity_analysis import analyze_network_connectivity
from app.resilience.criticality_analysis import analyze_node_criticality, analyze_edge_criticality


def generate_resilience_report(
    graph: NetworkGraph,
    entry_points: Optional[List[str]] = None,
    critical_services: Optional[List[str]] = None,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Generates an executive mathematical resilience evaluation for network graph G.
    
    Args:
        graph: NetworkGraph to audit.
        entry_points: Ingress entry points.
        critical_services: Critical servers/services.
        top_k: Number of most critical components to highlight.
        
    Returns:
        Structured resilience report dictionary.
    """
    # 1. Baseline Profile
    baseline = analyze_network_connectivity(
        graph=graph,
        entry_points=entry_points,
        critical_services=critical_services
    )

    # 2. Structural SPOF Identification
    ap_res = find_articulation_points(graph)
    bridge_res = find_bridges(graph)

    # 3. Criticality Rankings
    top_nodes = analyze_node_criticality(
        graph=graph,
        entry_points=entry_points,
        critical_services=critical_services
    )[:top_k]

    top_edges = analyze_edge_criticality(
        graph=graph,
        entry_points=entry_points,
        critical_services=critical_services
    )[:top_k]

    # 4. Synthesize Resilience Classification
    is_resilient = (
        baseline["component_count"] == 1 and
        ap_res["count"] == 0 and
        bridge_res["count"] == 0
    )

    structural_health = "HIGH" if is_resilient else ("MODERATE" if ap_res["count"] <= 2 else "VULNERABLE")

    recommendations: List[str] = []
    if ap_res["count"] > 0:
        recommendations.append(
            f"Add redundant bypass links around articulation points: {', '.join(ap_res['articulation_points'][:4])} to eliminate SPOFs."
        )
    if bridge_res["count"] > 0:
        recommendations.append(
            f"Introduce redundant mesh links for critical bridges ({bridge_res['count']} detected) to prevent bisection."
        )
    if baseline["component_count"] > 1:
        recommendations.append(
            f"Network is currently partitioned into {baseline['component_count']} disconnected components; inter-subnet interconnects required."
        )
    if not recommendations:
        recommendations.append("Network exhibits 2-connected biconnected reliability; zero single points of failure detected.")

    return {
        "network_name": graph.name,
        "structural_health_rating": structural_health,
        "is_biconnected": is_resilient,
        "baseline_summary": {
            "total_nodes": baseline["active_vertices"],
            "total_edges": baseline["active_edges"],
            "component_count": baseline["component_count"],
            "giant_component_size": baseline["giant_component_size"],
            "lcc_ratio": baseline["lcc_ratio"],
            "pairwise_connectivity": baseline["pairwise_connectivity"],
            "isolated_nodes_count": len(baseline["isolated_nodes"]),
            "critical_services_reachable_count": len(baseline["reachable_critical_services"]),
            "critical_services_total": len(critical_services or [])
        },
        "single_points_of_failure": {
            "articulation_points_count": ap_res["count"],
            "articulation_points": ap_res["articulation_points"],
            "bridges_count": bridge_res["count"],
            "bridges": bridge_res["bridges"]
        },
        "top_critical_nodes": top_nodes,
        "top_critical_edges": top_edges,
        "recommendations": recommendations
    }

