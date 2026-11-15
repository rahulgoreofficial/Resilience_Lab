"""
Pydantic Request and Response Schemas for Resilience Analysis Endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.graph_schema import GraphDataSchema


class ResilienceAnalysisRequest(BaseModel):
    graph: Optional[GraphDataSchema] = None
    entry_points: Optional[List[str]] = Field(default=None)
    critical_services: Optional[List[str]] = Field(default=None)


class CriticalityRequest(BaseModel):
    graph: Optional[GraphDataSchema] = None
    entry_points: Optional[List[str]] = Field(default=None)
    critical_services: Optional[List[str]] = Field(default=None)
    max_components: Optional[int] = Field(default=None, ge=1)


class AlternativeRoutesRequest(BaseModel):
    graph: Optional[GraphDataSchema] = None
    flow_pairs: List[List[str]] = Field(..., description="List of [source, target] node pairs")
    failed_node_ids: Optional[List[str]] = Field(default=None)
    failed_edge_ids: Optional[List[str]] = Field(default=None)
    weight_attribute: str = Field(default="weight")


class ScenarioComparisonRequest(BaseModel):
    graph: Optional[GraphDataSchema] = None
    scenarios: List[Dict[str, Any]] = Field(..., min_length=1, description="List of scenario dicts")
    entry_points: Optional[List[str]] = Field(default=None)
    critical_services: Optional[List[str]] = Field(default=None)


class CandidateLinkRequest(BaseModel):
    graph: Optional[GraphDataSchema] = None
    target_bridge_id: Optional[str] = Field(default=None, description="Specific bridge under study, e.g. E_C1_L1")
    target_failure_nodes: Optional[List[str]] = Field(default=None, description="Simulated failure node endpoints, e.g. ['C1', 'L1']")
    entry_points: Optional[List[str]] = Field(default=None)
    critical_services: Optional[List[str]] = Field(default=None)
    max_recommendations: int = Field(default=10, ge=1, le=50)
