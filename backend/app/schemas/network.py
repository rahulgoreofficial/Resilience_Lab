"""
Pydantic Schemas for Networks and Cytoscape.js Topologies.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.node import NodeResponse, NodeCreate
from app.schemas.edge import EdgeResponse, EdgeCreate


class NetworkBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, description="Human-readable network name")
    description: Optional[str] = Field(default=None, description="Optional network description")
    network_type: str = Field(default="COMMUNICATION_NETWORK", max_length=64)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NetworkCreate(NetworkBase):
    nodes: Optional[List[NodeCreate]] = Field(default=None, description="Initial nodes")
    edges: Optional[List[EdgeCreate]] = Field(default=None, description="Initial links")


class NetworkUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    description: Optional[str] = None
    network_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    expected_version: Optional[int] = Field(default=None, description="Optimistic concurrency control version")


class NetworkResponse(NetworkBase):
    id: str
    version: int
    node_count: int = 0
    edge_count: int = 0
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class CytoscapeNodeData(BaseModel):
    id: str
    label: str
    node_type: str
    importance: float
    capacity: float
    current_load: float
    failure_probability: float
    is_critical: bool
    metadata: Dict[str, Any]


class CytoscapeEdgeData(BaseModel):
    id: str
    source: str
    target: str
    weight: float
    latency: float
    capacity: float
    reliability: float
    metadata: Dict[str, Any]


class CytoscapeNodeElement(BaseModel):
    data: CytoscapeNodeData


class CytoscapeEdgeElement(BaseModel):
    data: CytoscapeEdgeData


class CytoscapeElements(BaseModel):
    nodes: List[CytoscapeNodeElement]
    edges: List[CytoscapeEdgeElement]


class NetworkTopologyResponse(BaseModel):
    network_id: str
    name: str
    version: int
    elements: CytoscapeElements
    nodes: List[NodeResponse]
    edges: List[EdgeResponse]


class NetworkImportRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = None
    network_type: str = Field(default="COMMUNICATION_NETWORK")
    data: Dict[str, Any] = Field(..., description="JSON graph representation with nodes and edges")


class NetworkExportResponse(BaseModel):
    network_id: str
    name: str
    version: int
    directed: bool = False
    multigraph: bool = False
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
