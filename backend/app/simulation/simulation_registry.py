"""
Simulation Registry: In-memory repository for simulation executions and results.
Provides thread-safe access and can be backed by database persistence.
"""

from typing import Dict, List, Optional, Any
from threading import Lock
from app.simulation.simulation_state import SimulationResult


class SimulationRegistry:
    """Thread-safe registry holding simulation results and execution history."""

    def __init__(self):
        self._storage: Dict[str, SimulationResult] = {}
        self._lock = Lock()

    def register(self, result: SimulationResult) -> SimulationResult:
        """Stores a completed or in-progress simulation result."""
        with self._lock:
            self._storage[result.simulation_id] = result
        return result

    def get(self, simulation_id: str) -> Optional[SimulationResult]:
        """Retrieves a simulation result by ID."""
        with self._lock:
            return self._storage.get(simulation_id)

    def list_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Returns metadata summaries for all recorded simulations."""
        with self._lock:
            results = list(self._storage.values())
        
        # Sort descending by start_time
        results.sort(key=lambda r: r.start_time, reverse=True)
        return [
            {
                "simulation_id": r.simulation_id,
                "simulation_type": r.simulation_type.value if hasattr(r.simulation_type, "value") else str(r.simulation_type),
                "status": r.status.value if hasattr(r.status, "value") else str(r.status),
                "start_time": r.start_time,
                "end_time": r.end_time,
                "network_hash": r.network_hash,
                "failed_node_count": len(r.failed_nodes),
                "failed_edge_count": len(r.failed_edges),
                "active_node_count": r.active_node_count,
                "component_count": r.connected_component_count
            }
            for r in results[:limit]
        ]

    def delete(self, simulation_id: str) -> bool:
        """Deletes a simulation record by ID."""
        with self._lock:
            if simulation_id in self._storage:
                del self._storage[simulation_id]
                return True
        return False

    def clear(self) -> None:
        """Clears all registered simulations."""
        with self._lock:
            self._storage.clear()


# Global singleton instance
simulation_registry = SimulationRegistry()

