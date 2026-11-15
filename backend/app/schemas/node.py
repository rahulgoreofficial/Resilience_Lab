"""
Pydantic Schemas for Network Nodes.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class NodeBase(BaseModel):
    node_id: str = Field(..., min_length=1, max_length=64, description="User-defined node identifier")
    node_type: str = Field(default="router", max_length=32)
    importance: float = Field(default=1.0, ge=0.0)
    capacity: float = Field(default=100.0, gt=0.0)
    current_load: float = Field(default=0.0, ge=0.0)
    failure_probability: float = Field(default=0.01, ge=0.0, le=1.0)
    is_critical: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NodeCreate(NodeBase):
    pass


class NodeUpdate(BaseModel):
    node_type: Optional[str] = Field(default=None, max_length=32)
    importance: Optional[float] = Field(default=None, ge=0.0)
    capacity: Optional[float] = Field(default=None, gt=0.0)
    current_load: Optional[float] = Field(default=None, ge=0.0)
    failure_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    is_critical: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class NodeResponse(NodeBase):
    id: int
    network_id: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
