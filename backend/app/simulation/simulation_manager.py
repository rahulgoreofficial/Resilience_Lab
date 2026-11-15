"""
Simulation Manager: Orchestrates simulation execution and lifecycle.
Serves as the unified facade for running node, edge, multiple, and advanced simulations.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from app.graph_engine.graph_builder import NetworkGraph
from app.simulation.simulation_state import SimulationResult, SimulationStatus, SimulationType
from app.simulation.simulation_registry import simulation_registry, SimulationRegistry
from app.simulation.node_failure import simulate_node_failure
from app.simulation.edge_failure import simulate_edge_failure
from app.simulation.multiple_failure import simulate_multiple_failures


class SimulationManager:
    """Unified coordinator for infrastructure failure simulations."""

    def __init__(self, registry: Optional[SimulationRegistry] = None):
        self.registry = registry or simulation_registry

    def run_node_failure(
        self,
        graph: NetworkGraph,
        failed_node_ids: List[str],
        entry_points: Optional[List[str]] = None,
        critical_services: Optional[List[str]] = None,
        simulation_id: Optional[str] = None
    ) -> SimulationResult:
        """Executes a node failure simulation and registers the result."""
        result = simulate_node_failure(
            graph=graph,
            failed_node_ids=failed_node_ids,
            entry_points=entry_points,
            critical_services=critical_services,
            simulation_id=simulation_id
        )
        self.registry.register(result)
        return result

    def run_edge_failure(
        self,
        graph: NetworkGraph,
        failed_edges: List[Union[str, Dict[str, str], Tuple[str, str], List[str]]],
        entry_points: Optional[List[str]] = None,
        critical_services: Optional[List[str]] = None,
        simulation_id: Optional[str] = None
    ) -> SimulationResult:
        """Executes an edge failure simulation and registers the result."""
        result = simulate_edge_failure(
            graph=graph,
            failed_edges=failed_edges,
            entry_points=entry_points,
            critical_services=critical_services,
            simulation_id=simulation_id
        )
        self.registry.register(result)
        return result

    def run_multiple_failures(
        self,
        graph: NetworkGraph,
        failed_node_ids: Optional[List[str]] = None,
        failed_edges: Optional[List[Union[str, Dict[str, str], Tuple[str, str], List[str]]]] = None,
        entry_points: Optional[List[str]] = None,
        critical_services: Optional[List[str]] = None,
        simulation_id: Optional[str] = None
    ) -> SimulationResult:
        """Executes multiple simultaneous component failures and registers the result."""
        result = simulate_multiple_failures(
            graph=graph,
            failed_node_ids=failed_node_ids,
            failed_edges=failed_edges,
            entry_points=entry_points,
            critical_services=critical_services,
            simulation_id=simulation_id
        )
        self.registry.register(result)
        return result

    def get_simulation(self, simulation_id: str) -> Optional[SimulationResult]:
        """Retrieves simulation result from registry."""
        return self.registry.get(simulation_id)

    def list_simulations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Lists metadata of past simulations."""
        return self.registry.list_all(limit=limit)


# Global singleton instance
simulation_manager = SimulationManager()

