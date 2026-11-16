"""
Simulation State and Event Tracking Data Models.
Maintains isolated simulation execution lifecycle, event logs, and results.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional


class SimulationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SimulationType(str, Enum):
    NODE_FAILURE = "NODE_FAILURE"
    EDGE_FAILURE = "EDGE_FAILURE"
    MULTIPLE_FAILURE = "MULTIPLE_FAILURE"
    RANDOM_FAILURE = "RANDOM_FAILURE"
    TARGETED_FAILURE = "TARGETED_FAILURE"
    CASCADING_FAILURE = "CASCADING_FAILURE"


@dataclass
class SimulationEvent:
    """Represents a discrete chronological event during simulation execution."""
    event: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "event": self.event,
            "timestamp": self.timestamp
        }
        if self.data:
            result.update(self.data)
        return result


@dataclass
class SimulationResult:
    """
    Standardized, serializable simulation output contract.
    Contains before-and-after graph state, failed components, reachability,
    event chronology, and mathematical resilience metrics.
    """
    simulation_id: str
    simulation_type: SimulationType
    status: SimulationStatus
    network_hash: str
    start_time: str
    end_time: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    failed_nodes: List[str] = field(default_factory=list)
    failed_edges: List[str] = field(default_factory=list)
    active_node_count: int = 0
    active_edge_count: int = 0
    baseline_node_count: int = 0
    baseline_edge_count: int = 0
    connected_components: List[List[str]] = field(default_factory=list)
    connected_component_count: int = 0
    giant_component: List[str] = field(default_factory=list)
    giant_component_size: int = 0
    isolated_nodes: List[str] = field(default_factory=list)
    reachable_nodes: List[str] = field(default_factory=list)
    unreachable_nodes: List[str] = field(default_factory=list)
    affected_critical_services: List[str] = field(default_factory=list)
    reachable_critical_services: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    timeline: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serializes result into a clean JSON-serializable dictionary."""
        import math

        # Compute derived metrics for frontend consumption
        active = self.active_node_count
        baseline = self.baseline_node_count

        # LCC ratio: fraction of *active* nodes in the giant component
        lcc_ratio = round(self.giant_component_size / active, 4) if active > 0 else 0.0

        # Pairwise connectivity ratio: sum C(|Ci|,2) / C(|active|,2)
        component_sizes = [len(c) for c in self.connected_components] if self.connected_components else []
        total_pairs = math.comb(active, 2) if active >= 2 else 0
        connected_pairs = sum(math.comb(s, 2) for s in component_sizes if s >= 2)
        pairwise_ratio = round(connected_pairs / total_pairs, 4) if total_pairs > 0 else (1.0 if active <= 1 else 0.0)

        # Baseline (pre-failure) component count is always 1 for a connected network,
        # but we store it in parameters.  Fallback to 1.
        initial_components = self.parameters.get("baseline_component_count", 1)
        final_components = self.connected_component_count

        return {
            "simulation_id": self.simulation_id,
            "simulation_type": self.simulation_type.value if isinstance(self.simulation_type, SimulationType) else str(self.simulation_type),
            "status": self.status.value if isinstance(self.status, SimulationStatus) else str(self.status),
            "network_hash": self.network_hash,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "parameters": self.parameters,
            "events": self.events,
            "failed_nodes": sorted(self.failed_nodes),
            "failed_edges": sorted(self.failed_edges),
            "active_node_count": active,
            "active_edge_count": self.active_edge_count,
            "baseline_node_count": baseline,
            "baseline_edge_count": self.baseline_edge_count,
            "connected_components": self.connected_components,
            "connected_component_count": final_components,
            "giant_component": self.giant_component,
            "giant_component_size": self.giant_component_size,
            "isolated_nodes": self.isolated_nodes,
            "reachable_nodes": self.reachable_nodes,
            "unreachable_nodes": self.unreachable_nodes,
            "affected_critical_services": self.affected_critical_services,
            "reachable_critical_services": self.reachable_critical_services,
            "metrics": self.metrics,
            "timeline": self.timeline,
            "error_message": self.error_message,
            # ── Frontend-consumable top-level metrics ──────────────────────────
            "lcc_ratio": lcc_ratio,
            "pairwise_connectivity_ratio": pairwise_ratio,
            "initial_components": initial_components,
            "final_components": final_components,
            "initial_lcc_size": baseline,
            "final_lcc_size": self.giant_component_size,
        }

