"""
Node (Component Vertex) Management Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_database
from app.schemas.node import NodeCreate, NodeUpdate, NodeResponse
from app.services.network_service import NetworkService

router = APIRouter(prefix="/networks/{network_id}/nodes", tags=["Nodes"])


@router.post("", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def add_node(
    network_id: str,
    payload: NodeCreate,
    db: Session = Depends(get_database)
) -> NodeResponse:
    """Adds a new component vertex to the network."""
    node = NetworkService.add_node(db, network_id, payload)
    return NodeResponse(
        id=node.id,
        network_id=node.network_id,
        node_id=node.node_id,
        node_type=node.node_type,
        importance=node.importance,
        capacity=node.capacity,
        current_load=node.current_load,
        failure_probability=node.failure_probability,
        is_critical=node.is_critical,
        metadata=node.metadata_json,
        created_at=node.created_at.isoformat(),
        updated_at=node.updated_at.isoformat()
    )


@router.get("", response_model=List[NodeResponse])
def list_nodes(
    network_id: str,
    db: Session = Depends(get_database)
) -> List[NodeResponse]:
    """Lists all nodes belonging to the network."""
    network = NetworkService.get_network(db, network_id)
    return [
        NodeResponse(
            id=n.id,
            network_id=n.network_id,
            node_id=n.node_id,
            node_type=n.node_type,
            importance=n.importance,
            capacity=n.capacity,
            current_load=n.current_load,
            failure_probability=n.failure_probability,
            is_critical=n.is_critical,
            metadata=n.metadata_json,
            created_at=n.created_at.isoformat(),
            updated_at=n.updated_at.isoformat()
        )
        for n in network.nodes
    ]


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(
    network_id: str,
    node_id: str,
    db: Session = Depends(get_database)
) -> NodeResponse:
    """Retrieves a specific node within the network."""
    node = NetworkService.get_node(db, network_id, node_id)
    return NodeResponse(
        id=node.id,
        network_id=node.network_id,
        node_id=node.node_id,
        node_type=node.node_type,
        importance=node.importance,
        capacity=node.capacity,
        current_load=node.current_load,
        failure_probability=node.failure_probability,
        is_critical=node.is_critical,
        metadata=node.metadata_json,
        created_at=node.created_at.isoformat(),
        updated_at=node.updated_at.isoformat()
    )


@router.patch("/{node_id}", response_model=NodeResponse)
def update_node(
    network_id: str,
    node_id: str,
    payload: NodeUpdate,
    db: Session = Depends(get_database)
) -> NodeResponse:
    """Updates properties of a node and increments network version."""
    node = NetworkService.update_node(db, network_id, node_id, payload)
    return NodeResponse(
        id=node.id,
        network_id=node.network_id,
        node_id=node.node_id,
        node_type=node.node_type,
        importance=node.importance,
        capacity=node.capacity,
        current_load=node.current_load,
        failure_probability=node.failure_probability,
        is_critical=node.is_critical,
        metadata=node.metadata_json,
        created_at=node.created_at.isoformat(),
        updated_at=node.updated_at.isoformat()
    )


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(
    network_id: str,
    node_id: str,
    db: Session = Depends(get_database)
) -> None:
    """Deletes a node and cascades deletion of incident communication links."""
    NetworkService.delete_node(db, network_id, node_id)

