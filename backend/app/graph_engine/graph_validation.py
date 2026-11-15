"""
Custom exceptions and validation logic for the Graph Engine.
Ensures strict discrete mathematical integrity (no self-loops, simple graph enforcement).
"""

from typing import Any, Set


class GraphException(Exception):
    """Base exception for all graph engine errors."""
    pass


class NodeValidationError(GraphException):
    """Raised when a node fails attribute or structural validation."""
    pass


class EdgeValidationError(GraphException):
    """Raised when an edge fails attribute or structural validation."""
    pass


class DuplicateNodeError(GraphException):
    """Raised when attempting to add a node with an ID that already exists."""
    pass


class DuplicateEdgeError(GraphException):
    """Raised when attempting to add an edge between vertices that are already connected."""
    pass


class NodeNotFoundError(GraphException):
    """Raised when referencing a node ID that does not exist in the graph."""
    pass


class EdgeNotFoundError(GraphException):
    """Raised when referencing an edge that does not exist in the graph."""
    pass


class SelfLoopError(GraphException):
    """Raised when attempting to create a self-loop (edge with source == target)."""
    pass


class GraphStructureError(GraphException):
    """Raised when the graph enters an inconsistent or unsupported state."""
    pass


ALLOWED_NODE_TYPES: Set[str] = {
    "router",
    "switch",
    "server",
    "database",
    "firewall",
    "gateway"
}


def validate_node_attributes(
    node_id: str,
    node_type: str,
    importance: float,
    capacity: float,
    current_load: float,
    failure_probability: float
) -> None:
    """Validates node constraints according to Phase 3 specification."""
    if not isinstance(node_id, str) or not node_id.strip():
        raise NodeValidationError("Node ID must be a non-empty string.")
    
    normalized_type = node_type.lower().strip()
    if normalized_type not in ALLOWED_NODE_TYPES:
        raise NodeValidationError(
            f"Invalid node type '{node_type}'. Allowed types: {sorted(list(ALLOWED_NODE_TYPES))}"
        )
    
    if importance < 0:
        raise NodeValidationError(f"Importance must be non-negative. Got: {importance}")
        
    if capacity <= 0:
        raise NodeValidationError(f"Capacity must be strictly positive (> 0). Got: {capacity}")
        
    if current_load < 0:
        raise NodeValidationError(f"Current load must be non-negative. Got: {current_load}")
        
    if not (0.0 <= failure_probability <= 1.0):
        raise NodeValidationError(
            f"Failure probability must be in range [0, 1]. Got: {failure_probability}"
        )


def validate_edge_attributes(
    source: str,
    target: str,
    weight: float,
    latency: float,
    capacity: float,
    reliability: float
) -> None:
    """Validates edge constraints according to Phase 3 specification."""
    if not isinstance(source, str) or not source.strip():
        raise EdgeValidationError("Source node ID must be a non-empty string.")
        
    if not isinstance(target, str) or not target.strip():
        raise EdgeValidationError("Target node ID must be a non-empty string.")
        
    if source == target:
        raise SelfLoopError(f"Self-loops are rejected in simple graphs. Source '{source}' equals target.")
        
    if weight < 0:
        raise EdgeValidationError(f"Edge weight must be non-negative. Got: {weight}")
        
    if latency < 0:
        raise EdgeValidationError(f"Edge latency must be non-negative. Got: {latency}")
        
    if capacity <= 0:
        raise EdgeValidationError(f"Edge capacity must be strictly positive (> 0). Got: {capacity}")
        
    if not (0.0 <= reliability <= 1.0):
        raise EdgeValidationError(f"Reliability must be in range [0, 1]. Got: {reliability}")

