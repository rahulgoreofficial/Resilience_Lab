"""
Pydantic v2 schemas for API requests and responses.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NodeSchema(BaseModel):
    node_id: str
    node_type: str
    importance: float = 1.0
    capacity: float = 100.0
    current_load: float = 0.0
    failure_probability: float = 0.01
    is_critical: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EdgeSchema(BaseModel):
    edge_id: Optional[str] = None
    source: str
    target: str
    weight: float = 1.0
    latency: float = 1.0
    capacity: float = 10.0
    reliability: float = 0.99
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphDataSchema(BaseModel):
    name: str = "Enterprise_Network"
    directed: bool = False
    multigraph: bool = False
    nodes: List[NodeSchema]
    edges: List[EdgeSchema]


class BFSRequest(BaseModel):
    start_node: str


class DijkstraRequest(BaseModel):
    source: str
    target: Optional[str] = None
    weight_attribute: str = "weight"


class HealthResponse(BaseModel):
    status: str
    version: str
    project: str


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str
    host: str
    port: int
    driver: Optional[str] = None
    error: Optional[str] = None

