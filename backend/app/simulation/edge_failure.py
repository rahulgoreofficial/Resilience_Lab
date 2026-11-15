"""
Dynamic Edge (Communication Link) Failure Simulation Module.
Simulates removal of communication links e in E, checks for alternative routes,
and recalculates network connectivity on an isolated snapshot.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Union

from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import EdgeNotFoundError, NodeNotFoundError
from app.algorithms.connected_components import find_connected_components
from app.algorithms.shortest_path import dijkstra_shortest_path
from app.simulation.simulation_state import (
    SimulationResult,
    SimulationStatus,
    SimulationType,
    SimulationEvent
)
from app.simulation.simulation_utils import (
    create_isolated_graph_snapshot,
    hash_graph_topology,
    compute_reachability,
    evaluate_service_reachability
)


def _resolve_edge_id(graph: NetworkGraph, identifier: Union[str, Dict[str, str], Tuple[str, str], List[str]]) -> Tuple[str, str, str]:
    """
    Resolves an edge identifier into (edge_id, source, target).
    Supports direct edge_id, dict {'source': u, 'target': v}, or (u, v) pair.
    """
    if isinstance(identifier, str):
        if graph.has_node(identifier):
            # Not an edge ID, but might be edge ID string
            pass
        edge = graph.get_edge(identifier)
        return edge.edge_id, edge.source, edge.target

    elif isinstance(identifier, dict):
        u = identifier.get("source") or identifier.get("u")
        v = identifier.get("target") or identifier.get("v")
        if not u or not v:
            raise EdgeNotFoundError(f"Invalid edge dict format: {identifier}")
        edge = graph.get_edge_between(u, v)
        if not edge:
            raise EdgeNotFoundError(f"No edge exists connecting '{u}' and '{v}'.")
        return edge.edge_id, edge.source, edge.target

    elif isinstance(identifier, (list, tuple)) and len(identifier) == 2:
        u, v = identifier[0], identifier[1]
        edge = graph.get_edge_between(u, v)
        if not edge:
            raise EdgeNotFoundError(f"No edge exists connecting '{u}' and '{v}'.")
        return edge.edge_id, edge.source, edge.target

    raise EdgeNotFoundError(f"Unrecognized edge identifier type: {identifier}")


def simulate_edge_failure(
    graph: NetworkGraph,
    failed_edges: List[Union[str, Dict[str, str], Tuple[str, str], List[str]]],
    entry_points: Optional[List[str]] = None,
    critical_services: Optional[List[str]] = None,
    simulation_id: Optional[str] = None
) -> SimulationResult:
    """
    Simulates failure of one or more communication links on an isolated copy of the network.
    Performs alternative route detection between disconnected endpoints.
    
    Args:
        graph: Baseline network graph (unmodified).
        failed_edges: List of edge IDs or (source, target) endpoint pairs.
        entry_points: Optional network ingress node IDs.
        critical_services: Optional critical service node IDs.
        simulation_id: Optional custom simulation UUID.
        
    Returns:
        SimulationResult containing alternative paths, components, and event log.
    """
    sim_id = simulation_id or str(uuid.uuid4())
    start_time = datetime.now(timezone.utc).isoformat()
    network_hash = hash_graph_topology(graph)

    # 1. Validate all requested edges exist in baseline graph
    baseline_nodes = graph.get_node_ids()
    baseline_edges = [e.edge_id for e in graph.get_all_edges()]

    resolved_edge_tuples: List[Tuple[str, str, str]] = []
    seen_edge_ids = set()
    for item in failed_edges:
        edge_id, u, v = _resolve_edge_id(graph, item)
        if edge_id not in seen_edge_ids:
            seen_edge_ids.add(edge_id)
            resolved_edge_tuples.append((edge_id, u, v))

    events: List[Dict[str, Any]] = []
    events.append(SimulationEvent("simulation_started", data={
        "simulation_id": sim_id,
        "type": SimulationType.EDGE_FAILURE.value,
        "requested_failures": [e[0] for e in resolved_edge_tuples]
    }).to_dict())

    # 2. Create isolated snapshot
    sim_graph = create_isolated_graph_snapshot(graph, snapshot_name=f"sim_{sim_id}")

    # 3. Disable requested communication links
    for edge_id, u, v in resolved_edge_tuples:
        sim_graph.remove_edge(edge_id)
        events.append(SimulationEvent("edge_failed", data={
            "edge_id": edge_id,
            "source": u,
            "target": v
        }).to_dict())

    # 4. Search for alternative communication paths in active snapshot
    alternative_routes: Dict[str, Any] = {}
    for edge_id, u, v in resolved_edge_tuples:
        # Check if an alternative route exists in sim_graph
        try:
            sp_res = dijkstra_shortest_path(sim_graph, source=u, target=v)
            has_alt = sp_res["distance"] != float("inf")
            alternative_routes[edge_id] = {
                "source": u,
                "target": v,
                "alternative_path_exists": has_alt,
                "alternative_path": sp_res["path"] if has_alt else [],
                "alternative_cost": sp_res["distance"] if has_alt else None
            }
        except Exception:
            alternative_routes[edge_id] = {
                "source": u,
                "target": v,
                "alternative_path_exists": False,
                "alternative_path": [],
                "alternative_cost": None
            }

    # 5. Recalculate network connectivity on active snapshot
    comp_info = find_connected_components(sim_graph)
    events.append(SimulationEvent("connectivity_recalculated", data={
        "component_count": comp_info["component_count"],
        "giant_component_size": comp_info["giant_component_size"]
    }).to_dict())

    # 6. Evaluate Reachability and Service Impact
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
        simulation_type=SimulationType.EDGE_FAILURE,
        status=SimulationStatus.COMPLETED,
        network_hash=network_hash,
        start_time=start_time,
        end_time=end_time,
        parameters={
            "failed_edges": [e[0] for e in resolved_edge_tuples],
            "entry_points": entry_points or [],
            "critical_services": critical_services or []
        },
        events=events,
        failed_nodes=[],
        failed_edges=sorted([e[0] for e in resolved_edge_tuples]),
        active_node_count=active_nodes_count,
        active_edge_count=active_edges_count,
        baseline_node_count=len(baseline_nodes),
        baseline_edge_count=len(baseline_edges),
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
            "failed_edge_count": len(resolved_edge_tuples),
            "alternative_routes": alternative_routes
        }
    )

