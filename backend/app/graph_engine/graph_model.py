"""
Data models for network nodes (devices) and edges (links).
Enforces mathematical validation rules and provides serialization.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from app.graph_engine.graph_validation import (
    validate_node_attributes,
    validate_edge_attributes,
    ALLOWED_NODE_TYPES
)


@dataclass
class Node:
    """
    Represents an infrastructure vertex v in G = (V, E).
    
    Attributes:
        node_id: Unique identifier for the component.
        node_type: Role archetype (router, switch, server, database, firewall, gateway).
        importance: Relative priority weight (default: 1.0).
        capacity: Maximum operational load capacity (default: 100.0).
        current_load: Current active load on the device (default: 0.0).
        failure_probability: Stochastic baseline failure probability in [0, 1] (default: 0.01).
        is_critical: Boolean flag for high-consequence infrastructure (default: False).
        metadata: Optional application metadata for UI or subnet details.
    """
    node_id: str
    node_type: str
    importance: float = 1.0
    capacity: float = 100.0
    current_load: float = 0.0
    failure_probability: float = 0.01
    is_critical: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.node_id = str(self.node_id).strip()
        self.node_type = str(self.node_type).lower().strip()
        self.importance = float(self.importance)
        self.capacity = float(self.capacity)
        self.current_load = float(self.current_load)
        self.failure_probability = float(self.failure_probability)
        self.is_critical = bool(self.is_critical)
        
        validate_node_attributes(
            node_id=self.node_id,
            node_type=self.node_type,
            importance=self.importance,
            capacity=self.capacity,
            current_load=self.current_load,
            failure_probability=self.failure_probability
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes node to dictionary."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "importance": self.importance,
            "capacity": self.capacity,
            "current_load": self.current_load,
            "failure_probability": self.failure_probability,
            "is_critical": self.is_critical,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        """Instantiates Node from dictionary with validation."""
        return cls(
            node_id=data["node_id"],
            node_type=data["node_type"],
            importance=data.get("importance", 1.0),
            capacity=data.get("capacity", 100.0),
            current_load=data.get("current_load", 0.0),
            failure_probability=data.get("failure_probability", 0.01),
            is_critical=data.get("is_critical", False),
            metadata=data.get("metadata", {})
        )


@dataclass
class Edge:
    """
    Represents an undirected communication link e = {source, target} in G = (V, E).
    
    Attributes:
        edge_id: Unique string identifier for the edge.
        source: ID of the first endpoint.
        target: ID of the second endpoint.
        weight: Cost metric for shortest path algorithms (default: 1.0).
        latency: Physical latency in milliseconds (default: 1.0).
        capacity: Bandwidth capacity in Gbps (default: 10.0).
        reliability: Operational transmission reliability in [0, 1] (default: 0.99).
        metadata: Optional application metadata.
    """
    edge_id: str
    source: str
    target: str
    weight: float = 1.0
    latency: float = 1.0
    capacity: float = 10.0
    reliability: float = 0.99
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.edge_id = str(self.edge_id).strip()
        self.source = str(self.source).strip()
        self.target = str(self.target).strip()
        self.weight = float(self.weight)
        self.latency = float(self.latency)
        self.capacity = float(self.capacity)
        self.reliability = float(self.reliability)
        
        validate_edge_attributes(
            source=self.source,
            target=self.target,
            weight=self.weight,
            latency=self.latency,
            capacity=self.capacity,
            reliability=self.reliability
        )

    @property
    def endpoints_key(self) -> frozenset:
        """Returns frozenset of {source, target} for undirected uniqueness comparisons."""
        return frozenset([self.source, self.target])

    def has_endpoint(self, node_id: str) -> bool:
        """Checks if the edge connects to the given node."""
        return self.source == node_id or self.target == node_id

    def get_opposite_endpoint(self, node_id: str) -> Optional[str]:
        """Returns the other endpoint connected to this edge."""
        if self.source == node_id:
            return self.target
        elif self.target == node_id:
            return self.source
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serializes edge to dictionary."""
        return {
            "edge_id": self.edge_id,
            "source": self.source,
            "target": self.target,
            "weight": self.weight,
            "latency": self.latency,
            "capacity": self.capacity,
            "reliability": self.reliability,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Edge":
        """Instantiates Edge from dictionary with validation."""
        return cls(
            edge_id=data.get("edge_id") or f"{data['source']}--{data['target']}",
            source=data["source"],
            target=data["target"],
            weight=data.get("weight", 1.0),
            latency=data.get("latency", 1.0),
            capacity=data.get("capacity", 10.0),
            reliability=data.get("reliability", 0.99),
            metadata=data.get("metadata", {})
        )

