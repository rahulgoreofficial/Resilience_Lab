"""
Pydantic Schemas for Network Edges (Communication Links).
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class EdgeBase(BaseModel):
    edge_id: str = Field(..., min_length=1, max_length=64, description="Unique edge identifier")
    source_node_id: str = Field(..., min_length=1, max_length=64)
    target_node_id: str = Field(..., min_length=1, max_length=64)
    weight: float = Field(default=1.0, ge=0.0)
    latency: float = Field(default=1.0, ge=0.0)
    capacity: float = Field(default=10.0, gt=0.0)
    reliability: float = Field(default=0.99, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EdgeCreate(EdgeBase):
    pass


class EdgeUpdate(BaseModel):
    weight: Optional[float] = Field(default=None, ge=0.0)
    latency: Optional[float] = Field(default=None, ge=0.0)
    capacity: Optional[float] = Field(default=None, gt=0.0)
    reliability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None


class EdgeResponse(EdgeBase):
    id: int
    network_id: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
