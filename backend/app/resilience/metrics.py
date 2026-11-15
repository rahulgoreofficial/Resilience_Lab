"""
Resilience Metrics: Mathematical formulations for evaluating network resilience.
Computes Largest Connected Component (LCC) ratio, Pairwise Connectivity,
and Service Resilience Scores (unweighted and importance-weighted).
"""

import math
from typing import List, Dict, Optional, Any


def calculate_lcc_ratio(giant_component_size: int, active_nodes_count: int) -> float:
    """
    Computes the fraction of active vertices belonging to the giant connected component:
    LCC Ratio = |V_giant| / |V_active|
    
    Returns 0.0 if active_nodes_count == 0.
    """
    if active_nodes_count <= 0:
        return 0.0
    return round(float(giant_component_size) / float(active_nodes_count), 4)


def calculate_pairwise_connectivity(component_sizes: List[int], active_nodes_count: int) -> float:
    """
    Computes Pairwise Connectivity: the fraction of all possible vertex pairs
    that remain connected in the active graph:
    
    Pair Connectivity = ( sum_{i=1}^k C(|C_i|, 2) ) / C(|V_active|, 2)
    
    Edge Cases:
    - active_nodes_count == 0: 0.0
    - active_nodes_count == 1: 1.0 (a solitary component has no severed internal pairs)
    """
    if active_nodes_count <= 0:
        return 0.0
    if active_nodes_count == 1:
        return 1.0

    total_possible_pairs = math.comb(active_nodes_count, 2)
    if total_possible_pairs == 0:
        return 0.0

    connected_pairs = sum(math.comb(size, 2) for size in component_sizes if size >= 2)
    return round(connected_pairs / total_possible_pairs, 4)


def calculate_connectivity_loss(pairwise_connectivity: float) -> float:
    """Computes Connectivity Loss = 1.0 - Pairwise Connectivity."""
    return round(max(0.0, min(1.0, 1.0 - pairwise_connectivity)), 4)


def calculate_service_resilience_score(
    reachable_services_post: List[str],
    reachable_services_baseline: List[str]
) -> Optional[float]:
    """
    Computes Service Resilience Score R:
    R = |Reachable Critical Services After Failure| / |Reachable Critical Services Baseline|
    
    Returns None if no critical services were reachable at baseline (to prevent division by zero).
    """
    baseline_count = len(reachable_services_baseline)
    if baseline_count == 0:
        return None
    post_count = len(reachable_services_post)
    return round(post_count / baseline_count, 4)


def calculate_weighted_service_resilience_score(
    reachable_services_post: List[str],
    reachable_services_baseline: List[str],
    importance_map: Dict[str, float]
) -> Optional[float]:
    """
    Computes Weighted Service Resilience Score R_weighted:
    R_weighted = sum_{s in S_post} imp(s) / sum_{s in S_baseline} imp(s)
    
    Returns None if baseline importance denominator is 0.0.
    """
    baseline_sum = sum(importance_map.get(s, 1.0) for s in reachable_services_baseline)
    if baseline_sum <= 0.0:
        return None
    post_sum = sum(importance_map.get(s, 1.0) for s in reachable_services_post)
    return round(post_sum / baseline_sum, 4)

