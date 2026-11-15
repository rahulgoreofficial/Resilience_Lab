"""
Scenario Comparison Module: Multi-Scenario Resilience Evaluation.
Compares topological degradation and service availability across multiple failure hypotheses.
Generates structured comparative tabular and chart data.
"""

from typing import Dict, List, Any, Optional
from app.graph_engine.graph_builder import NetworkGraph
from app.resilience.connectivity_analysis import analyze_network_connectivity
from app.resilience.metrics import calculate_service_resilience_score
from app.simulation.simulation_utils import create_isolated_graph_snapshot
from app.simulation.edge_failure import _resolve_edge_id


def compare_failure_scenarios(
    graph: NetworkGraph,
    scenarios: List[Dict[str, Any]],
    entry_points: Optional[List[str]] = None,
    critical_services: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Compares baseline resilience against multiple simulated failure scenarios.
    
    Args:
        graph: Baseline network graph.
        scenarios: List of scenario definitions:
            [
                {
                    "scenario_id": "scenario_a",
                    "name": "Core Router R1 Failure",
                    "failed_nodes": ["R1"],
                    "failed_edges": []
                },
                ...
            ]
        entry_points: Optional ingress router node IDs.
        critical_services: Optional critical service node IDs.
        
    Returns:
        Structured comparison object with baseline profile and per-scenario comparisons.
    """
    # 1. Baseline Profile
    baseline = analyze_network_connectivity(
        graph=graph,
        entry_points=entry_points,
        critical_services=critical_services
    )
    baseline_reachable_svcs = baseline["reachable_critical_services"]
    all_known_nodes = graph.get_node_ids()

    comparison_results: List[Dict[str, Any]] = []

    for sc in scenarios:
        sc_id = sc.get("scenario_id", f"scenario_{len(comparison_results)+1}")
        sc_name = sc.get("name", sc_id)
        failed_nodes = sc.get("failed_nodes", [])
        failed_edges_raw = sc.get("failed_edges", [])

        # Create isolated snapshot
        sim_graph = create_isolated_graph_snapshot(graph, snapshot_name=f"comp_{sc_id}")

        # Apply edge failures
        removed_edges: List[str] = []
        for item in failed_edges_raw:
            try:
                eid, u, v = _resolve_edge_id(graph, item)
                if sim_graph.has_edge(u, v):
                    sim_graph.remove_edge(eid)
                    removed_edges.append(eid)
            except Exception:
                pass

        # Apply node failures
        for nid in failed_nodes:
            if sim_graph.has_node(nid):
                sim_graph.remove_node(nid)

        # Analyze post-failure connectivity
        post = analyze_network_connectivity(
            graph=sim_graph,
            entry_points=entry_points,
            critical_services=critical_services,
            baseline_node_ids=all_known_nodes
        )

        # Service Resilience Score R
        r_score = calculate_service_resilience_score(
            reachable_services_post=post["reachable_critical_services"],
            reachable_services_baseline=baseline_reachable_svcs
        )

        # Delta metrics relative to baseline
        delta_pair_conn = round(baseline["pairwise_connectivity"] - post["pairwise_connectivity"], 4)
        delta_lcc = baseline["giant_component_size"] - post["giant_component_size"]
        delta_components = post["component_count"] - baseline["component_count"]

        comparison_results.append({
            "scenario_id": sc_id,
            "name": sc_name,
            "failed_nodes": failed_nodes,
            "failed_edges": removed_edges,
            "active_vertices": post["active_vertices"],
            "active_edges": post["active_edges"],
            "component_count": post["component_count"],
            "giant_component_size": post["giant_component_size"],
            "lcc_ratio": post["lcc_ratio"],
            "pairwise_connectivity": post["pairwise_connectivity"],
            "connectivity_loss": post["connectivity_loss"],
            "delta_pairwise_connectivity": delta_pair_conn,
            "delta_giant_component_size": delta_lcc,
            "component_increase": delta_components,
            "reachable_critical_services": post["reachable_critical_services"],
            "unreachable_critical_services": post["unreachable_critical_services"],
            "service_resilience_score_R": r_score
        })

    return {
        "baseline": {
            "total_vertices": baseline["active_vertices"],
            "total_edges": baseline["active_edges"],
            "component_count": baseline["component_count"],
            "giant_component_size": baseline["giant_component_size"],
            "lcc_ratio": baseline["lcc_ratio"],
            "pairwise_connectivity": baseline["pairwise_connectivity"],
            "reachable_critical_services": baseline_reachable_svcs,
            "critical_services_count": len(critical_services or [])
        },
        "scenarios": comparison_results
    }

