"""
Targeted Failure Simulation Engine: Adversarial Attack Strategies.
Implements Degree-Based, Articulation-Point-Based, and Impact-Based attacks.
Supports static and adaptive targeting with deterministic tie-breaking.
Generates step-by-step resilience degradation percolation curves.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import GraphException
from app.algorithms.connected_components import find_connected_components
from app.algorithms.degree_analysis import all_vertex_degrees
from app.algorithms.articulation_points import find_articulation_points
from app.resilience.metrics import calculate_lcc_ratio, calculate_pairwise_connectivity
from app.simulation.simulation_state import (
    SimulationResult,
    SimulationStatus,
    SimulationType,
    SimulationEvent
)
from app.simulation.simulation_utils import (
    create_isolated_graph_snapshot,
    hash_graph_topology,
    evaluate_service_reachability
)


def _rank_targets(
    graph: NetworkGraph,
    strategy: str,
    entry_points: Optional[List[str]] = None,
    critical_services: Optional[List[str]] = None
) -> List[str]:
    """
    Ranks active nodes by the specified targeting strategy with deterministic tie-breaking.
    """
    strat = strategy.upper()
    active_nodes = graph.get_node_ids()
    if not active_nodes:
        return []

    if strat == "DEGREE":
        degrees = all_vertex_degrees(graph)
        # Sort descending by degree, tie-break ascending by node_id
        return sorted(active_nodes, key=lambda nid: (-degrees.get(nid, 0), nid))

    elif strat == "ARTICULATION_POINT":
        ap_res = find_articulation_points(graph)
        ap_set = set(ap_res["articulation_points"])
        degrees = all_vertex_degrees(graph)
        # Prioritize APs, then degree, then node_id
        return sorted(
            active_nodes,
            key=lambda nid: (0 if nid in ap_set else 1, -degrees.get(nid, 0), nid)
        )

    elif strat == "IMPACT":
        from app.resilience.criticality_analysis import analyze_node_criticality
        crit_res = analyze_node_criticality(
            graph=graph,
            entry_points=entry_points,
            critical_services=critical_services
        )
        return [item["node_id"] for item in crit_res]

    else:
        raise GraphException(f"Unknown targeting strategy: '{strategy}'. Supported: DEGREE, ARTICULATION_POINT, IMPACT")


def simulate_targeted_failure(
    graph: NetworkGraph,
    strategy: str = "DEGREE",
    failure_count: Optional[int] = None,
    failure_percentage: Optional[float] = None,
    adaptive: bool = True,
    entry_points: Optional[List[str]] = None,
    critical_services: Optional[List[str]] = None,
    simulation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Simulates adversarial targeted component attacks step-by-step.
    
    Args:
        graph: Baseline network graph (unmodified).
        strategy: "DEGREE", "ARTICULATION_POINT", or "IMPACT".
        failure_count: Maximum number of nodes to remove.
        failure_percentage: Percentage of network nodes to target [0, 100].
        adaptive: If True, recomputes rankings after each step; if False, uses initial static ranking.
        entry_points: Ingress entry points for reachability.
        critical_services: Critical server IDs.
        simulation_id: Optional custom UUID.
        
    Returns:
        Structured result containing step-by-step degradation curve for charting.
    """
    sim_id = simulation_id or str(uuid.uuid4())
    start_time = datetime.now(timezone.utc).isoformat()
    network_hash = hash_graph_topology(graph)

    baseline_nodes = graph.get_node_ids()
    total_nodes = len(baseline_nodes)

    # Determine attack budget K
    budget = total_nodes
    if failure_count is not None:
        budget = min(total_nodes, max(0, failure_count))
    elif failure_percentage is not None:
        budget = min(total_nodes, max(0, int(round(total_nodes * failure_percentage / 100.0))))

    sim_graph = create_isolated_graph_snapshot(graph, snapshot_name=f"targeted_{sim_id}")

    # Degradation curve: step 0 is baseline
    step_curve: List[Dict[str, Any]] = []
    comp_b = find_connected_components(sim_graph)
    reach_b, _, _ = evaluate_service_reachability(sim_graph, critical_services, entry_points, baseline_nodes)

    step_curve.append({
        "step": 0,
        "removed_node": None,
        "active_nodes_count": total_nodes,
        "active_edges_count": sim_graph.edge_count,
        "component_count": comp_b["component_count"],
        "giant_component_size": comp_b["giant_component_size"],
        "lcc_ratio": calculate_lcc_ratio(comp_b["giant_component_size"], total_nodes),
        "pairwise_connectivity": calculate_pairwise_connectivity([len(c) for c in comp_b["components"]], total_nodes),
        "reachable_critical_services_count": len(reach_b)
    })

    removed_sequence: List[str] = []
    static_ranking: Optional[List[str]] = None
    if not adaptive:
        static_ranking = _rank_targets(sim_graph, strategy, entry_points, critical_services)

    for step_idx in range(1, budget + 1):
        if sim_graph.node_count == 0:
            break

        # Select next target
        if adaptive:
            target_list = _rank_targets(sim_graph, strategy, entry_points, critical_services)
            if not target_list:
                break
            target_node = target_list[0]
        else:
            # Find next target from static ranking that is still in graph
            target_node = None
            for cand in static_ranking:
                if sim_graph.has_node(cand):
                    target_node = cand
                    break
            if not target_node:
                break

        # Remove target node
        sim_graph.remove_node(target_node)
        removed_sequence.append(target_node)

        # Measure degradation
        active_v = sim_graph.node_count
        comp_curr = find_connected_components(sim_graph)
        reach_curr, _, _ = evaluate_service_reachability(sim_graph, critical_services, entry_points, baseline_nodes)

        lcc = calculate_lcc_ratio(comp_curr["giant_component_size"], active_v)
        pair_conn = calculate_pairwise_connectivity([len(c) for c in comp_curr["components"]], active_v)

        step_curve.append({
            "step": step_idx,
            "removed_node": target_node,
            "active_nodes_count": active_v,
            "active_edges_count": sim_graph.edge_count,
            "component_count": comp_curr["component_count"],
            "giant_component_size": comp_curr["giant_component_size"],
            "lcc_ratio": lcc,
            "pairwise_connectivity": pair_conn,
            "reachable_critical_services_count": len(reach_curr)
        })

    end_time = datetime.now(timezone.utc).isoformat()

    return {
        "simulation_id": sim_id,
        "simulation_type": SimulationType.TARGETED_FAILURE.value,
        "status": SimulationStatus.COMPLETED.value,
        "network_hash": network_hash,
        "start_time": start_time,
        "end_time": end_time,
        "parameters": {
            "strategy": strategy.upper(),
            "failure_count": failure_count,
            "failure_percentage": failure_percentage,
            "budget": budget,
            "adaptive": adaptive
        },
        "removed_nodes_sequence": removed_sequence,
        "final_metrics": {
            "active_nodes_count": sim_graph.node_count,
            "active_edges_count": sim_graph.edge_count,
            "component_count": step_curve[-1]["component_count"],
            "giant_component_size": step_curve[-1]["giant_component_size"],
            "lcc_ratio": step_curve[-1]["lcc_ratio"],
            "pairwise_connectivity": step_curve[-1]["pairwise_connectivity"]
        },
        "degradation_curve": step_curve
    }
