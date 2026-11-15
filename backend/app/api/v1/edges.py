"""
Edge (Communication Link) Management Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_database
from app.schemas.edge import EdgeCreate, EdgeUpdate, EdgeResponse
from app.services.network_service import NetworkService

router = APIRouter(prefix="/networks/{network_id}/edges", tags=["Edges"])


@router.post("", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
def add_edge(
    network_id: str,
    payload: EdgeCreate,
    db: Session = Depends(get_database)
) -> EdgeResponse:
    """Adds a new communication link to the network."""
    edge = NetworkService.add_edge(db, network_id, payload)
    return EdgeResponse(
        id=edge.id,
        network_id=edge.network_id,
        edge_id=edge.edge_id,
        source_node_id=edge.source_node_id,
        target_node_id=edge.target_node_id,
        weight=edge.weight,
        latency=edge.latency,
        capacity=edge.capacity,
        reliability=edge.reliability,
        metadata=edge.metadata_json,
        created_at=edge.created_at.isoformat(),
        updated_at=edge.updated_at.isoformat()
    )


@router.get("", response_model=List[EdgeResponse])
def list_edges(
    network_id: str,
    db: Session = Depends(get_database)
) -> List[EdgeResponse]:
    """Lists all communication links in the network."""
    network = NetworkService.get_network(db, network_id)
    return [
        EdgeResponse(
            id=e.id,
            network_id=e.network_id,
            edge_id=e.edge_id,
            source_node_id=e.source_node_id,
            target_node_id=e.target_node_id,
            weight=e.weight,
            latency=e.latency,
            capacity=e.capacity,
            reliability=e.reliability,
            metadata=e.metadata_json,
            created_at=e.created_at.isoformat(),
            updated_at=e.updated_at.isoformat()
        )
        for e in network.edges
    ]


@router.get("/{edge_id}", response_model=EdgeResponse)
def get_edge(
    network_id: str,
    edge_id: str,
    db: Session = Depends(get_database)
) -> EdgeResponse:
    """Retrieves a specific communication link."""
    edge = NetworkService.get_edge(db, network_id, edge_id)
    return EdgeResponse(
        id=edge.id,
        network_id=edge.network_id,
        edge_id=edge.edge_id,
        source_node_id=edge.source_node_id,
        target_node_id=edge.target_node_id,
        weight=edge.weight,
        latency=edge.latency,
        capacity=edge.capacity,
        reliability=edge.reliability,
        metadata=edge.metadata_json,
        created_at=edge.created_at.isoformat(),
        updated_at=edge.updated_at.isoformat()
    )


@router.patch("/{edge_id}", response_model=EdgeResponse)
def update_edge(
    network_id: str,
    edge_id: str,
    payload: EdgeUpdate,
    db: Session = Depends(get_database)
) -> EdgeResponse:
    """Updates attributes of a communication link."""
    edge = NetworkService.update_edge(db, network_id, edge_id, payload)
    return EdgeResponse(
        id=edge.id,
        network_id=edge.network_id,
        edge_id=edge.edge_id,
        source_node_id=edge.source_node_id,
        target_node_id=edge.target_node_id,
        weight=edge.weight,
        latency=edge.latency,
        capacity=edge.capacity,
        reliability=edge.reliability,
        metadata=edge.metadata_json,
        created_at=edge.created_at.isoformat(),
        updated_at=edge.updated_at.isoformat()
    )


@router.delete("/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_edge(
    network_id: str,
    edge_id: str,
    db: Session = Depends(get_database)
) -> None:
    """Deletes a communication link from the network."""
    NetworkService.delete_edge(db, network_id, edge_id)

