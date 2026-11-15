"""
Random Failure Simulation Engine: Stochastic Percolation Analysis.
Performs multiple Monte Carlo trials under uniform or probability-weighted removal.
Computes mean, median, min, max, and standard deviation of resilience degradation.
Deterministic and reproducible via explicit random.Random instance seeds.
"""

import uuid
import random
import statistics
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_validation import GraphException
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


def simulate_random_failure(
    graph: NetworkGraph,
    failure_target: str = "NODES",
    failure_count: Optional[int] = None,
    failure_percentage: Optional[float] = None,
    num_trials: int = 10,
    random_seed: Optional[int] = 42,
    selection_method: str = "UNIFORM",
    entry_points: Optional[List[str]] = None,
    critical_services: Optional[List[str]] = None,
    simulation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes multiple stochastic failure trials on isolated graph snapshots.
    
    Args:
        graph: Baseline network graph (unmodified).
        failure_target: "NODES", "EDGES", or "BOTH".
        failure_count: Explicit number of components to remove per trial.
        failure_percentage: Percentage of components to remove per trial [0, 100].
        num_trials: Number of stochastic trials (1 to 200).
        random_seed: Deterministic integer seed for reproducibility.
        selection_method: "UNIFORM" or "WEIGHTED_PROBABILITY".
        entry_points: Ingress entry points for reachability.
        critical_services: Critical service IDs.
        simulation_id: Optional custom UUID.
        
    Returns:
        Structured dictionary containing statistical distribution and individual trial logs.
    """
    if num_trials < 1 or num_trials > 500:
        raise GraphException(f"Number of trials must be between 1 and 500, got {num_trials}")

    sim_id = simulation_id or str(uuid.uuid4())
    start_time = datetime.now(timezone.utc).isoformat()
    network_hash = hash_graph_topology(graph)

    # Initialize isolated PRNG with fixed seed
    rng = random.Random(random_seed)

    baseline_nodes = graph.get_node_ids()
    baseline_edges = [e.edge_id for e in graph.get_all_edges()]
    total_nodes = len(baseline_nodes)
    total_edges = len(baseline_edges)

    # Determine failure budgets
    target_upper = failure_target.upper()
    nodes_to_remove_count = 0
    edges_to_remove_count = 0

    if target_upper in ("NODES", "BOTH"):
        if failure_count is not None:
            nodes_to_remove_count = min(total_nodes, max(0, failure_count))
        elif failure_percentage is not None:
            nodes_to_remove_count = min(total_nodes, max(0, int(round(total_nodes * failure_percentage / 100.0))))

    if target_upper in ("EDGES", "BOTH"):
        if failure_count is not None:
            edges_to_remove_count = min(total_edges, max(0, failure_count))
        elif failure_percentage is not None:
            edges_to_remove_count = min(total_edges, max(0, int(round(total_edges * failure_percentage / 100.0))))

    trial_results: List[Dict[str, Any]] = []
    pair_conns: List[float] = []
    lcc_ratios: List[float] = []
    comp_counts: List[int] = []
    reachable_svc_counts: List[int] = []

    for trial_idx in range(1, num_trials + 1):
        # Generate deterministic per-trial seed
        trial_seed = rng.randint(1, 10_000_000)
        trial_rng = random.Random(trial_seed)

        # 1. Select nodes to fail
        chosen_nodes: List[str] = []
        if nodes_to_remove_count > 0:
            if selection_method.upper() == "WEIGHTED_PROBABILITY":
                # Sample using failure_probability weights without replacement
                weights = [graph.get_node(nid).failure_probability for nid in baseline_nodes]
                # Avoid all-zero weights
                if sum(weights) <= 0:
                    weights = [1.0] * total_nodes
                
                # Weighted sample without replacement
                pool = list(baseline_nodes)
                pool_weights = list(weights)
                for _ in range(nodes_to_remove_count):
                    selected = trial_rng.choices(pool, weights=pool_weights, k=1)[0]
                    chosen_nodes.append(selected)
                    sel_idx = pool.index(selected)
                    pool.pop(sel_idx)
                    pool_weights.pop(sel_idx)
            else:
                chosen_nodes = trial_rng.sample(baseline_nodes, k=nodes_to_remove_count)

        # 2. Select edges to fail
        chosen_edges: List[str] = []
        if edges_to_remove_count > 0:
            chosen_edges = trial_rng.sample(baseline_edges, k=edges_to_remove_count)

        # 3. Create isolated snapshot and apply removals
        sim_graph = create_isolated_graph_snapshot(graph, snapshot_name=f"rand_{sim_id}_t{trial_idx}")
        for eid in chosen_edges:
            sim_graph.remove_edge(eid)
        for nid in chosen_nodes:
            sim_graph.remove_node(nid)

        # 4. Measure connectivity and resilience
        comp_info = find_connected_components(sim_graph)
        active_v = sim_graph.node_count
        comp_sizes = [len(c) for c in comp_info["components"]]

        lcc = calculate_lcc_ratio(comp_info["giant_component_size"], active_v)
        pair_conn = calculate_pairwise_connectivity(comp_sizes, active_v)

        reachable_svcs, affected_svcs, _ = evaluate_service_reachability(
            graph=sim_graph,
            critical_services=critical_services,
            entry_points=entry_points,
            all_known_nodes=baseline_nodes
        )

        pair_conns.append(pair_conn)
        lcc_ratios.append(lcc)
        comp_counts.append(comp_info["component_count"])
        reachable_svc_counts.append(len(reachable_svcs))

        trial_results.append({
            "trial_index": trial_idx,
            "trial_seed": trial_seed,
            "failed_nodes": chosen_nodes,
            "failed_edges": chosen_edges,
            "active_nodes_count": active_v,
            "active_edges_count": sim_graph.edge_count,
            "component_count": comp_info["component_count"],
            "giant_component_size": comp_info["giant_component_size"],
            "lcc_ratio": lcc,
            "pairwise_connectivity": pair_conn,
            "reachable_critical_services": reachable_svcs
        })

    end_time = datetime.now(timezone.utc).isoformat()

    # Aggregate statistical summaries
    def _stats(arr: List[float]) -> Dict[str, float]:
        if not arr:
            return {"mean": 0.0, "median": 0.0, "min": 0.0, "max": 0.0, "std_dev": 0.0}
        return {
            "mean": round(statistics.mean(arr), 4),
            "median": round(statistics.median(arr), 4),
            "min": round(min(arr), 4),
            "max": round(max(arr), 4),
            "std_dev": round(statistics.stdev(arr) if len(arr) > 1 else 0.0, 4)
        }

    return {
        "simulation_id": sim_id,
        "simulation_type": SimulationType.RANDOM_FAILURE.value,
        "status": SimulationStatus.COMPLETED.value,
        "network_hash": network_hash,
        "start_time": start_time,
        "end_time": end_time,
        "parameters": {
            "failure_target": target_upper,
            "failure_count": failure_count,
            "failure_percentage": failure_percentage,
            "nodes_removed_per_trial": nodes_to_remove_count,
            "edges_removed_per_trial": edges_to_remove_count,
            "num_trials": num_trials,
            "random_seed": random_seed,
            "selection_method": selection_method.upper()
        },
        "statistics": {
            "pairwise_connectivity": _stats(pair_conns),
            "lcc_ratio": _stats(lcc_ratios),
            "component_count": _stats(comp_counts),
            "reachable_critical_services_count": _stats(reachable_svc_counts)
        },
        "trials": trial_results
    }

