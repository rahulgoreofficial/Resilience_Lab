"""
Pydantic Request and Response Schemas for Simulation Endpoints.
Ensures validation of dynamic parameters and data serialization.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from app.schemas.graph_schema import GraphDataSchema


class NodeFailureRequest(BaseModel):
    graph: Optional[GraphDataSchema] = Field(default=None, description="Graph data if not targeting persistent network")
    failed_node_ids: List[str] = Field(..., min_length=1, description="List of node IDs to fail")
    entry_points: Optional[List[str]] = Field(default=None, description="Ingress router/gateway IDs")
    critical_services: Optional[List[str]] = Field(default=None, description="Critical service/server IDs")


class EdgeFailureRequest(BaseModel):
    graph: Optional[GraphDataSchema] = Field(default=None)
    failed_edges: List[Any] = Field(..., min_length=1, description="List of edge IDs or endpoint pairs")
    entry_points: Optional[List[str]] = Field(default=None)
    critical_services: Optional[List[str]] = Field(default=None)


class MultipleFailureRequest(BaseModel):
    graph: Optional[GraphDataSchema] = Field(default=None)
    failed_node_ids: Optional[List[str]] = Field(default=None)
    failed_edges: Optional[List[Any]] = Field(default=None)
    entry_points: Optional[List[str]] = Field(default=None)
    critical_services: Optional[List[str]] = Field(default=None)


class RandomFailureRequest(BaseModel):
    graph: Optional[GraphDataSchema] = Field(default=None)
    failure_target: str = Field(default="NODES", description="'NODES', 'EDGES', or 'BOTH'")
    failure_count: Optional[int] = Field(default=None, ge=0)
    failure_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    num_trials: int = Field(default=10, ge=1, le=500)
    random_seed: Optional[int] = Field(default=42)
    selection_method: str = Field(default="UNIFORM", description="'UNIFORM' or 'WEIGHTED_PROBABILITY'")
    entry_points: Optional[List[str]] = Field(default=None)
    critical_services: Optional[List[str]] = Field(default=None)


class TargetedFailureRequest(BaseModel):
    graph: Optional[GraphDataSchema] = Field(default=None)
    strategy: str = Field(default="DEGREE", description="'DEGREE', 'ARTICULATION_POINT', or 'IMPACT'")
    failure_count: Optional[int] = Field(default=None, ge=0)
    failure_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    adaptive: bool = Field(default=True, description="Recalculate rankings dynamically after each removal")
    entry_points: Optional[List[str]] = Field(default=None)
    critical_services: Optional[List[str]] = Field(default=None)


class CascadingFailureRequest(BaseModel):
    graph: Optional[GraphDataSchema] = Field(default=None)
    initial_failed_nodes: Optional[List[str]] = Field(default=None)
    initial_failed_edges: Optional[List[Any]] = Field(default=None)
    traffic_demands: Optional[List[Dict[str, Any]]] = Field(default=None)
    overload_threshold: float = Field(default=1.0, gt=0.0, description="Multiplier for capacity limits")
    max_simulation_rounds: int = Field(default=10, ge=1, le=100)
    entry_points: Optional[List[str]] = Field(default=None)
    critical_services: Optional[List[str]] = Field(default=None)

