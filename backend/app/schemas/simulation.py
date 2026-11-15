"""
Pydantic Schemas for Simulation Requests, Execution Records, and Event Logs.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.simulation_schema import (
    NodeFailureRequest,
    EdgeFailureRequest,
    MultipleFailureRequest,
    RandomFailureRequest,
    TargetedFailureRequest,
    CascadingFailureRequest
)


class SimulationRecordResponse(BaseModel):
    id: str
    network_id: str
    snapshot_id: Optional[str] = None
    simulation_type: str
    status: str
    configuration: Dict[str, Any]
    random_seed: Optional[int] = None
    results: Optional[Dict[str, Any]] = None
    error_summary: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class SimulationEventRecordResponse(BaseModel):
    sequence_number: int
    event_type: str
    event_data: Dict[str, Any]
    created_at: str

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "NodeFailureRequest",
    "EdgeFailureRequest",
    "MultipleFailureRequest",
    "RandomFailureRequest",
    "TargetedFailureRequest",
    "CascadingFailureRequest",
    "SimulationRecordResponse",
    "SimulationEventRecordResponse"
]
