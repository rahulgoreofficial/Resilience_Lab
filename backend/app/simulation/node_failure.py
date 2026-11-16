"""
Dynamic Node Failure Simulation Module.
Simulates removal of vertices v in V, removing incident edges and recalculating topology.
Baseline network remains strictly unmodified.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import NodeNotFoundError
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
    compute_reachability,
    evaluate_service_reachability
)


def simulate_node_failure(
    graph: NetworkGraph,
    failed_node_ids: List[str],
    entry_points: Optional[List[str]] = None,
    critical_services: Optional[List[str]] = None,
    simulation_id: Optional[str] = None
) -> SimulationResult:
    """
    Simulates failure of one or more vertices on an isolated copy of the network.
    
    Args:
        graph: Baseline network graph (will NOT be mutated).
        failed_node_ids: List of node IDs to fail and remove.
        entry_points: Optional ingress nodes to evaluate user-reachability.
        critical_services: Optional designated servers/databases.
        simulation_id: Optional custom UUID.
        
    Returns:
        SimulationResult containing post-failure metrics, connected components,
        unreachable vertices, and event log.
        
    Raises:
        NodeNotFoundError: If any requested failed_node_id does not exist in the graph.
    """
    sim_id = simulation_id or str(uuid.uuid4())
    start_time = datetime.now(timezone.utc).isoformat()
    network_hash = hash_graph_topology(graph)

    # 1. Validation: Verify all requested nodes exist in the baseline graph
    baseline_nodes = graph.get_node_ids()
    baseline_edges = [e.edge_id for e in graph.get_all_edges()]
    
    unique_failed_nodes = list(dict.fromkeys(failed_node_ids))  # preserve order, deduplicate
    for nid in unique_failed_nodes:
        if not graph.has_node(nid):
            raise NodeNotFoundError(f"Cannot simulate failure: Node '{nid}' does not exist in the network.")

    events: List[Dict[str, Any]] = []
    events.append(SimulationEvent("simulation_started", data={
        "simulation_id": sim_id,
        "type": SimulationType.NODE_FAILURE.value,
        "requested_failures": unique_failed_nodes
    }).to_dict())

    # 2. Compute baseline connectivity before any failures
    baseline_comp_info = find_connected_components(graph)
    baseline_component_count = baseline_comp_info["component_count"]

    # 3. Create isolated snapshot
    sim_graph = create_isolated_graph_snapshot(graph, snapshot_name=f"sim_{sim_id}")

    # 3. Apply node failures and record incident edge deletions
    removed_edges: List[str] = []
    for nid in unique_failed_nodes:
        # Determine incident edges prior to node removal
        incident_edges = [
            e.edge_id for e in sim_graph.get_all_edges() if e.has_endpoint(nid)
        ]
        removed_edges.extend(incident_edges)
        
        sim_graph.remove_node(nid)
        events.append(SimulationEvent("node_failed", data={
            "node_id": nid,
            "incident_edges_disconnected": incident_edges
        }).to_dict())

    # 4. Recalculate network connectivity on active snapshot
    comp_info = find_connected_components(sim_graph)
    events.append(SimulationEvent("connectivity_recalculated", data={
        "component_count": comp_info["component_count"],
        "giant_component_size": comp_info["giant_component_size"]
    }).to_dict())

    # 5. Evaluate Reachability and Service Impact
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

    # Basic metrics
    active_nodes_count = sim_graph.node_count
    active_edges_count = sim_graph.edge_count
    lcc_ratio = (comp_info["giant_component_size"] / active_nodes_count) if active_nodes_count > 0 else 0.0

    return SimulationResult(
        simulation_id=sim_id,
        simulation_type=SimulationType.NODE_FAILURE,
        status=SimulationStatus.COMPLETED,
        network_hash=network_hash,
        start_time=start_time,
        end_time=end_time,
        parameters={
            "failed_nodes": unique_failed_nodes,
            "entry_points": entry_points or [],
            "critical_services": critical_services or [],
            "baseline_component_count": baseline_component_count
        },
        events=events,
        failed_nodes=unique_failed_nodes,
        failed_edges=sorted(list(set(removed_edges))),
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
            "failed_node_count": len(unique_failed_nodes),
            "failed_edge_count": len(set(removed_edges))
        }
    )

