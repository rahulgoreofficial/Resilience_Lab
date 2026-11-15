"""
Cascading Failure Simulation Engine: Capacity-Based Network Overload Model.
Simulates iterative traffic redistribution, bottleneck overload propagation,
and secondary structural failures across synchronous discrete simulation rounds.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union, Tuple

from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import NodeNotFoundError, EdgeNotFoundError
from app.algorithms.connected_components import find_connected_components
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
    compute_reachability,
    evaluate_service_reachability
)
from app.simulation.edge_failure import _resolve_edge_id
from app.simulation.traffic_model import (
    TrafficDemand,
    validate_traffic_demands,
    route_traffic_flows
)


def simulate_cascading_failure(
    graph: NetworkGraph,
    initial_failed_nodes: Optional[List[str]] = None,
    initial_failed_edges: Optional[List[Union[str, Dict[str, str], Tuple[str, str], List[str]]]] = None,
    traffic_demands: Optional[List[Union[TrafficDemand, Dict[str, Any]]]] = None,
    overload_threshold: float = 1.0,
    max_simulation_rounds: int = 10,
    entry_points: Optional[List[str]] = None,
    critical_services: Optional[List[str]] = None,
    simulation_id: Optional[str] = None
) -> SimulationResult:
    """
    Executes a discrete multi-round capacity-based cascading overload simulation.
    
    Args:
        graph: Baseline network graph (unmodified).
        initial_failed_nodes: List of node IDs triggering the cascade.
        initial_failed_edges: List of edge identifiers triggering the cascade.
        traffic_demands: Traffic flow demands to route and redistribute.
        overload_threshold: Multiplier for capacity overload condition (e.g. 1.0 or 1.2).
        max_simulation_rounds: Maximum cascading iteration rounds to prevent infinite loops.
        entry_points: Ingress entry point IDs.
        critical_services: Critical service IDs.
        simulation_id: Optional custom UUID.
        
    Returns:
        SimulationResult containing chronological round timeline, termination reason,
        and final resilience degradation metrics.
    """
    sim_id = simulation_id or str(uuid.uuid4())
    start_time = datetime.now(timezone.utc).isoformat()
    network_hash = hash_graph_topology(graph)

    # 1. Parse & Validate Traffic Demands
    parsed_demands: List[TrafficDemand] = []
    if traffic_demands:
        for d in traffic_demands:
            if isinstance(d, TrafficDemand):
                parsed_demands.append(d)
            elif isinstance(d, dict):
                src = d.get("source")
                dst = d.get("destination") or d.get("target")
                amt = d.get("amount") if "amount" in d else d.get("demand", 0.0)
                parsed_demands.append(TrafficDemand(
                    source=str(src),
                    destination=str(dst),
                    amount=float(amt)
                ))
    validate_traffic_demands(graph, parsed_demands)

    # 2. Validate Initial Failures
    baseline_nodes = graph.get_node_ids()
    baseline_edges = [e.edge_id for e in graph.get_all_edges()]

    raw_init_nodes = initial_failed_nodes or []
    for nid in raw_init_nodes:
        if not graph.has_node(nid):
            raise NodeNotFoundError(f"Cannot simulate cascading failure: Initial node '{nid}' not found.")

    init_edges_resolved: List[Tuple[str, str, str]] = []
    for item in (initial_failed_edges or []):
        eid, u, v = _resolve_edge_id(graph, item)
        init_edges_resolved.append((eid, u, v))

    # 3. Check for pre-existing overloads at baseline (prior to any failure)
    baseline_routing = route_traffic_flows(graph, parsed_demands)
    pre_existing_overloaded_nodes: List[str] = []
    for nid in baseline_nodes:
        node = graph.get_node(nid)
        load = baseline_routing["node_loads"].get(nid, 0.0)
        if load > (node.capacity * overload_threshold):
            pre_existing_overloaded_nodes.append(nid)

    pre_existing_overloaded_edges: List[str] = []
    for eid in baseline_edges:
        edge = graph.get_edge(eid)
        load = baseline_routing["edge_routed_loads"].get(eid, 0.0)
        if load > (edge.capacity * overload_threshold):
            pre_existing_overloaded_edges.append(eid)

    events: List[Dict[str, Any]] = []
    events.append(SimulationEvent("simulation_started", data={
        "simulation_id": sim_id,
        "type": SimulationType.CASCADING_FAILURE.value,
        "overload_threshold": overload_threshold,
        "max_rounds": max_simulation_rounds,
        "initial_failed_nodes": raw_init_nodes,
        "initial_failed_edges": [e[0] for e in init_edges_resolved],
        "pre_existing_overloaded_nodes": pre_existing_overloaded_nodes,
        "pre_existing_overloaded_edges": pre_existing_overloaded_edges
    }).to_dict())

    # 4. Initialize Snapshot and Cascading State
    sim_graph = create_isolated_graph_snapshot(graph, snapshot_name=f"sim_cascade_{sim_id}")

    cumulative_failed_nodes: List[str] = []
    cumulative_failed_edges: List[str] = []
    timeline: List[Dict[str, Any]] = []
    termination_reason = "COMPLETED"

    # Round 0: Initial Baseline State
    comp_r0 = find_connected_components(sim_graph)
    timeline.append({
        "round": 0,
        "state_description": "Baseline Infrastructure (Pre-failure)",
        "active_nodes_count": sim_graph.node_count,
        "active_edges_count": sim_graph.edge_count,
        "newly_failed_nodes": [],
        "newly_failed_edges": [],
        "cumulative_failed_nodes": [],
        "cumulative_failed_edges": [],
        "traffic_served": baseline_routing["total_traffic_served"],
        "traffic_unserved": baseline_routing["total_traffic_unserved"],
        "lcc_ratio": calculate_lcc_ratio(comp_r0["giant_component_size"], sim_graph.node_count),
        "component_count": comp_r0["component_count"],
        "events": ["Baseline state initialized"]
    })

    # Round 1: Apply Initial Failures
    r1_failed_nodes = list(dict.fromkeys(raw_init_nodes))
    r1_failed_edges = [e[0] for e in init_edges_resolved]

    for eid, u, v in init_edges_resolved:
        if sim_graph.has_edge(u, v):
            sim_graph.remove_edge(eid)
            cumulative_failed_edges.append(eid)

    for nid in r1_failed_nodes:
        if sim_graph.has_node(nid):
            # Record incident edges
            incident = [e.edge_id for e in sim_graph.get_all_edges() if e.has_endpoint(nid)]
            cumulative_failed_edges.extend(incident)
            sim_graph.remove_node(nid)
            cumulative_failed_nodes.append(nid)

    cumulative_failed_nodes = sorted(list(set(cumulative_failed_nodes)))
    cumulative_failed_edges = sorted(list(set(cumulative_failed_edges)))

    # Route after initial failure
    r1_routing = route_traffic_flows(sim_graph, parsed_demands)
    comp_r1 = find_connected_components(sim_graph)

    timeline.append({
        "round": 1,
        "state_description": "Initial Trigger Failures Applied",
        "active_nodes_count": sim_graph.node_count,
        "active_edges_count": sim_graph.edge_count,
        "newly_failed_nodes": r1_failed_nodes,
        "newly_failed_edges": r1_failed_edges,
        "cumulative_failed_nodes": list(cumulative_failed_nodes),
        "cumulative_failed_edges": list(cumulative_failed_edges),
        "traffic_served": r1_routing["total_traffic_served"],
        "traffic_unserved": r1_routing["total_traffic_unserved"],
        "lcc_ratio": calculate_lcc_ratio(comp_r1["giant_component_size"], sim_graph.node_count),
        "component_count": comp_r1["component_count"],
        "events": [f"Triggered initial failure of {len(r1_failed_nodes)} nodes, {len(r1_failed_edges)} edges"]
    })

    current_routing = r1_routing
    current_round = 2

    # Cascade propagation loop
    while current_round <= max_simulation_rounds:
        # Check for overloaded nodes in the current active graph
        newly_overloaded_nodes: List[str] = []
        for nid in sim_graph.get_node_ids():
            orig_node = graph.get_node(nid)
            load = current_routing["node_loads"].get(nid, 0.0)
            capacity_limit = orig_node.capacity * overload_threshold
            if load > capacity_limit:
                newly_overloaded_nodes.append(nid)

        # Check for overloaded edges in current active graph
        newly_overloaded_edges: List[str] = []
        for edge in sim_graph.get_all_edges():
            orig_edge = graph.get_edge(edge.edge_id)
            load = current_routing["edge_routed_loads"].get(edge.edge_id, 0.0)
            capacity_limit = orig_edge.capacity * overload_threshold
            if load > capacity_limit:
                newly_overloaded_edges.append(edge.edge_id)

        # Termination Check A: System stabilized (no new overloads)
        if not newly_overloaded_nodes and not newly_overloaded_edges:
            termination_reason = "STABLE - No further overload cascades"
            events.append(SimulationEvent("cascade_stabilized", data={
                "round": current_round,
                "reason": termination_reason
            }).to_dict())
            break

        # Synchronous failure application: remove newly overloaded components
        round_events: List[str] = []
        for eid in newly_overloaded_edges:
            if eid in [e.edge_id for e in sim_graph.get_all_edges()]:
                sim_graph.remove_edge(eid)
                cumulative_failed_edges.append(eid)
                round_events.append(f"Edge '{eid}' failed due to capacity overload")

        for nid in newly_overloaded_nodes:
            if sim_graph.has_node(nid):
                incident = [e.edge_id for e in sim_graph.get_all_edges() if e.has_endpoint(nid)]
                cumulative_failed_edges.extend(incident)
                sim_graph.remove_node(nid)
                cumulative_failed_nodes.append(nid)
                round_events.append(f"Node '{nid}' failed due to capacity overload")

        cumulative_failed_nodes = sorted(list(set(cumulative_failed_nodes)))
        cumulative_failed_edges = sorted(list(set(cumulative_failed_edges)))

        # Recalculate routing and topology for the newly formed network
        current_routing = route_traffic_flows(sim_graph, parsed_demands)
        comp_curr = find_connected_components(sim_graph)

        timeline.append({
            "round": current_round,
            "state_description": f"Cascading Overload Propagation Round {current_round}",
            "active_nodes_count": sim_graph.node_count,
            "active_edges_count": sim_graph.edge_count,
            "newly_failed_nodes": newly_overloaded_nodes,
            "newly_failed_edges": newly_overloaded_edges,
            "cumulative_failed_nodes": list(cumulative_failed_nodes),
            "cumulative_failed_edges": list(cumulative_failed_edges),
            "traffic_served": current_routing["total_traffic_served"],
            "traffic_unserved": current_routing["total_traffic_unserved"],
            "lcc_ratio": calculate_lcc_ratio(comp_curr["giant_component_size"], sim_graph.node_count),
            "component_count": comp_curr["component_count"],
            "events": round_events
        })

        # Termination Check B: All critical services exhausted/unreachable
        if critical_services:
            reachable_svcs, _, _ = evaluate_service_reachability(
                graph=sim_graph,
                critical_services=critical_services,
                entry_points=entry_points,
                all_known_nodes=baseline_nodes
            )
            if not reachable_svcs:
                termination_reason = "CRITICAL_SERVICES_EXHAUSTED"
                events.append(SimulationEvent("critical_services_exhausted", data={"round": current_round}).to_dict())
                break

        current_round += 1

    if current_round > max_simulation_rounds and termination_reason == "COMPLETED":
        termination_reason = "MAX_ROUNDS_REACHED"

    # Final connectivity and service evaluation
    final_comp = find_connected_components(sim_graph)
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
        "status": SimulationStatus.COMPLETED.value,
        "termination_reason": termination_reason,
        "total_rounds": len(timeline) - 1
    }).to_dict())

    final_lcc_ratio = calculate_lcc_ratio(final_comp["giant_component_size"], sim_graph.node_count)

    return SimulationResult(
        simulation_id=sim_id,
        simulation_type=SimulationType.CASCADING_FAILURE,
        status=SimulationStatus.COMPLETED,
        network_hash=network_hash,
        start_time=start_time,
        end_time=end_time,
        parameters={
            "initial_failed_nodes": raw_init_nodes,
            "initial_failed_edges": [e[0] for e in init_edges_resolved],
            "overload_threshold": overload_threshold,
            "max_rounds": max_simulation_rounds,
            "traffic_demands": [d.to_dict() for d in parsed_demands]
        },
        events=events,
        failed_nodes=cumulative_failed_nodes,
        failed_edges=cumulative_failed_edges,
        active_node_count=sim_graph.node_count,
        active_edge_count=sim_graph.edge_count,
        baseline_node_count=len(baseline_nodes),
        baseline_edge_count=len(baseline_edges),
        connected_components=final_comp["components"],
        connected_component_count=final_comp["component_count"],
        giant_component=final_comp["giant_component"],
        giant_component_size=final_comp["giant_component_size"],
        isolated_nodes=final_comp["isolated_nodes"],
        reachable_nodes=reachable_nodes,
        unreachable_nodes=unreachable_nodes,
        affected_critical_services=affected_svcs,
        reachable_critical_services=reachable_svcs,
        metrics={
            "termination_reason": termination_reason,
            "total_cascading_rounds": len(timeline) - 1,
            "lcc_ratio": final_lcc_ratio,
            "final_traffic_served": current_routing["total_traffic_served"],
            "final_traffic_unserved": current_routing["total_traffic_unserved"],
            "pre_existing_overloaded_nodes": pre_existing_overloaded_nodes,
            "pre_existing_overloaded_edges": pre_existing_overloaded_edges
        },
        timeline=timeline
    )

