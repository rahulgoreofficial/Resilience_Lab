"""
Failure Simulation Module.
Exports simulation manager, state models, execution functions,
traffic models, and live update handlers.
"""

from app.simulation.simulation_state import (
    SimulationStatus,
    SimulationType,
    SimulationEvent,
    SimulationResult
)
from app.simulation.simulation_registry import SimulationRegistry, simulation_registry
from app.simulation.simulation_manager import SimulationManager, simulation_manager
from app.simulation.node_failure import simulate_node_failure
from app.simulation.edge_failure import simulate_edge_failure
from app.simulation.multiple_failure import simulate_multiple_failures
from app.simulation.traffic_model import TrafficDemand, route_traffic_flows, validate_traffic_demands
from app.simulation.cascading_failure import simulate_cascading_failure
from app.simulation.random_failure import simulate_random_failure
from app.simulation.targeted_failure import simulate_targeted_failure
from app.simulation.websocket_manager import ConnectionManager, ws_manager
from app.simulation.simulation_utils import (
    create_isolated_graph_snapshot,
    hash_graph_topology,
    calculate_combination_count,
    compute_reachability,
    evaluate_service_reachability
)

__all__ = [
    "SimulationStatus",
    "SimulationType",
    "SimulationEvent",
    "SimulationResult",
    "SimulationRegistry",
    "simulation_registry",
    "SimulationManager",
    "simulation_manager",
    "simulate_node_failure",
    "simulate_edge_failure",
    "simulate_multiple_failures",
    "TrafficDemand",
    "route_traffic_flows",
    "validate_traffic_demands",
    "simulate_cascading_failure",
    "simulate_random_failure",
    "simulate_targeted_failure",
    "ConnectionManager",
    "ws_manager",
    "create_isolated_graph_snapshot",
    "hash_graph_topology",
    "calculate_combination_count",
    "compute_reachability",
    "evaluate_service_reachability"
]
