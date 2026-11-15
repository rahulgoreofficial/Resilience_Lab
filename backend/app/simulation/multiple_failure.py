"""
Multiple Component Failure Simulation Module.
Simulates simultaneous combinations of node and edge failures.
Calculates cumulative non-additive impact and combinatorial scenario statistics.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union, Tuple

from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import NodeNotFoundError, EdgeNotFoundError
from app.algorithms.connected_components import find_connected_components
from app.simulation.simulation_state import (
    SimulationResult,
    SimulationStatus,
    SimulationType,
    SimulationEvent
)
from app.simulation.simulation_utils import (
    create_isolated_graph_snapshot,
    hash_graph_topology,
    calculate_combination_count,
    compute_reachability,
    evaluate_service_reachability
)
from app.simulation.edge_failure import _resolve_edge_id


def simulate_multiple_failures(
    graph: NetworkGraph,
    failed_node_ids: Optional[List[str]] = None,
    failed_edges: Optional[List[Union[str, Dict[str, str], Tuple[str, str], List[str]]]] = None,
    entry_points: Optional[List[str]] = None,
    critical_services: Optional[List[str]] = None,
    simulation_id: Optional[str] = None
) -> SimulationResult:
    """
    Simulates simultaneous combinations of node and edge failures on an isolated snapshot.
    Calculates exact cumulative topology disruption without additive approximation.
    
    Args:
        graph: Baseline network graph (unmodified).
        failed_node_ids: Optional list of node IDs to disable.
        failed_edges: Optional list of edge IDs or endpoint pairs to disable.
        entry_points: Optional ingress router IDs.
        critical_services: Optional critical server IDs.
        simulation_id: Optional custom UUID.
        
    Returns:
        SimulationResult containing cumulative topology degradation,
        combinatorial combination metrics, and chronological events.
    """
    sim_id = simulation_id or str(uuid.uuid4())
    start_time = datetime.now(timezone.utc).isoformat()
    network_hash = hash_graph_topology(graph)

    raw_nodes = failed_node_ids or []
    raw_edges = failed_edges or []

    # 1. Validate nodes
    baseline_nodes = graph.get_node_ids()
    baseline_edges = [e.edge_id for e in graph.get_all_edges()]

    unique_failed_nodes = list(dict.fromkeys(raw_nodes))
    for nid in unique_failed_nodes:
        if not graph.has_node(nid):
            raise NodeNotFoundError(f"Cannot simulate failure: Node '{nid}' not found in graph.")

    # 2. Validate edges
    resolved_edges: List[Tuple[str, str, str]] = []
    seen_edge_ids = set()
    for item in raw_edges:
        eid, u, v = _resolve_edge_id(graph, item)
        if eid not in seen_edge_ids:
            seen_edge_ids.add(eid)
            resolved_edges.append((eid, u, v))

    # Discrete Mathematics Combinatorics: Scenario Space Cardinality
    k_nodes = len(unique_failed_nodes)
    k_edges = len(resolved_edges)
    total_v = len(baseline_nodes)
    total_e = len(baseline_edges)

    node_combinations_count = calculate_combination_count(total_v, k_nodes)
    edge_combinations_count = calculate_combination_count(total_e, k_edges)
    total_scenario_space = node_combinations_count * (edge_combinations_count if k_edges > 0 else 1)

    events: List[Dict[str, Any]] = []
    events.append(SimulationEvent("simulation_started", data={
        "simulation_id": sim_id,
        "type": SimulationType.MULTIPLE_FAILURE.value,
        "k_nodes": k_nodes,
        "k_edges": k_edges,
        "combinatorial_scenarios_C_n_k": total_scenario_space
    }).to_dict())

    # 3. Create isolated graph snapshot
    sim_graph = create_isolated_graph_snapshot(graph, snapshot_name=f"sim_{sim_id}")

    # 4. Apply edge failures first (if any)
    for eid, u, v in resolved_edges:
        if sim_graph.has_edge(u, v):
            sim_graph.remove_edge(eid)
            events.append(SimulationEvent("edge_failed", data={
                "edge_id": eid,
                "source": u,
                "target": v
            }).to_dict())

    # 5. Apply node failures (automatically removing incident edges)
    all_removed_edges = list(seen_edge_ids)
    for nid in unique_failed_nodes:
        if sim_graph.has_node(nid):
            incident = [e.edge_id for e in sim_graph.get_all_edges() if e.has_endpoint(nid)]
            all_removed_edges.extend(incident)
            sim_graph.remove_node(nid)
            events.append(SimulationEvent("node_failed", data={
                "node_id": nid,
                "incident_edges_disconnected": incident
            }).to_dict())

    # 6. Recalculate connectivity
    comp_info = find_connected_components(sim_graph)
    events.append(SimulationEvent("connectivity_recalculated", data={
        "component_count": comp_info["component_count"],
        "giant_component_size": comp_info["giant_component_size"]
    }).to_dict())

    # 7. Evaluate Reachability and Services
    reachable_nodes, unreachable_nodes = compute_reachability(
        graph=sim_graph,
        entry_points=entry_points,
        all_known_nodes=baseline_nodes
    )

    reachable_svcs, affected_svcs, svc_status = evaluate_service_reachability(
        graph=sim_graph,
        critical_services=critical_services,
        entry_points=entry_points,
        all_known_nodes=baseline_nodes
    )

    end_time = datetime.now(timezone.utc).isoformat()
    events.append(SimulationEvent("simulation_completed", data={
        "status": SimulationStatus.COMPLETED.value
    }).to_dict())

    active_nodes_count = sim_graph.node_count
    active_edges_count = sim_graph.edge_count
    lcc_ratio = (comp_info["giant_component_size"] / active_nodes_count) if active_nodes_count > 0 else 0.0

    return SimulationResult(
        simulation_id=sim_id,
        simulation_type=SimulationType.MULTIPLE_FAILURE,
        status=SimulationStatus.COMPLETED,
        network_hash=network_hash,
        start_time=start_time,
        end_time=end_time,
        parameters={
            "failed_nodes": unique_failed_nodes,
            "failed_edges": list(seen_edge_ids),
            "entry_points": entry_points or [],
            "critical_services": critical_services or []
        },
        events=events,
        failed_nodes=unique_failed_nodes,
        failed_edges=sorted(list(set(all_removed_edges))),
        active_node_count=active_nodes_count,
        active_edge_count=active_edges_count,
        baseline_node_count=total_v,
        baseline_edge_count=total_e,
        connected_components=comp_info["components"],
        connected_component_count=comp_info["component_count"],
        giant_component=comp_info["giant_component"],
        giant_component_size=comp_info["giant_component_size"],
        isolated_nodes=comp_info["isolated_nodes"],
        reachable_nodes=reachable_nodes,
        unreachable_nodes=unreachable_nodes,
        affected_critical_services=affected_svcs,
        reachable_critical_services=reachable_svcs,
        metrics={
            "lcc_ratio": round(lcc_ratio, 4),
            "service_availability_status": svc_status,
            "failed_node_count": len(unique_failed_nodes),
            "failed_edge_count": len(set(all_removed_edges)),
            "combinatorics": {
                "n_vertices": total_v,
                "k_node_failures": k_nodes,
                "vertex_combinations_C_n_k": node_combinations_count,
                "n_edges": total_e,
                "k_edge_failures": k_edges,
                "edge_combinations_C_n_k": edge_combinations_count,
                "scenario_space_size": total_scenario_space
            }
        }
    )

