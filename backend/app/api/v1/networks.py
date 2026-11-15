"""
Network Infrastructure Management Endpoints.
Implements CRUD, Cytoscape topology retrieval, import, and export.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_database, get_pagination
from app.schemas.common import PaginationParams, PaginatedResponse
from app.schemas.network import (
    NetworkCreate,
    NetworkUpdate,
    NetworkResponse,
    NetworkTopologyResponse,
    NetworkImportRequest,
    NetworkExportResponse
)
from app.services.network_service import NetworkService

router = APIRouter(prefix="/networks", tags=["Networks"])


@router.post("", response_model=NetworkResponse, status_code=status.HTTP_201_CREATED)
def create_network(
    payload: NetworkCreate,
    db: Session = Depends(get_database)
) -> NetworkResponse:
    """Creates a new network infrastructure entity."""
    network = NetworkService.create_network(db, payload)
    return NetworkResponse(
        id=network.id,
        name=network.name,
        description=network.description,
        network_type=network.network_type,
        metadata=network.metadata_json,
        version=network.version,
        node_count=len(network.nodes),
        edge_count=len(network.edges),
        created_at=network.created_at.isoformat(),
        updated_at=network.updated_at.isoformat()
    )


@router.get("", response_model=PaginatedResponse[NetworkResponse])
def list_networks(
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_database)
) -> PaginatedResponse[NetworkResponse]:
    """Retrieves paginated list of all stored networks."""
    networks, total = NetworkService.list_networks(db, skip=pagination.skip, limit=pagination.limit)
    items = [
        NetworkResponse(
            id=n.id,
            name=n.name,
            description=n.description,
            network_type=n.network_type,
            metadata=n.metadata_json,
            version=n.version,
            node_count=len(n.nodes),
            edge_count=len(n.edges),
            created_at=n.created_at.isoformat(),
            updated_at=n.updated_at.isoformat()
        )
        for n in networks
    ]
    return PaginatedResponse(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit
    )


@router.post("/demonstrations/seed", response_model=Dict[str, Any])
def seed_demonstration_networks(
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Ensures demonstration topologies (Campus IT Infrastructure, Cascading Failure) are available."""
    from app.services.persistence_service import PersistenceService
    return PersistenceService.seed_all_demonstrations(db)


@router.get("/demonstrations/campus", response_model=NetworkResponse)
def get_campus_demonstration(
    reset: bool = False,
    db: Session = Depends(get_database)
) -> NetworkResponse:
    """Retrieves or restores the 12-node Campus IT Network demonstration."""
    from app.services.persistence_service import PersistenceService
    from fastapi import HTTPException
    network = PersistenceService.seed_campus_network(db, force_new=reset)
    if not network:
        raise HTTPException(status_code=404, detail="Campus demonstration network could not be loaded.")
    return NetworkResponse(
        id=network.id,
        name=network.name,
        description=network.description,
        network_type=network.network_type,
        metadata=network.metadata_json,
        version=network.version,
        node_count=len(network.nodes),
        edge_count=len(network.edges),
        created_at=network.created_at.isoformat(),
        updated_at=network.updated_at.isoformat()
    )


@router.get("/demonstrations/cascading", response_model=NetworkResponse)
def get_cascading_demonstration(
    reset: bool = False,
    db: Session = Depends(get_database)
) -> NetworkResponse:
    """Retrieves or restores the 5-node Cascading Failure demonstration."""
    from app.services.persistence_service import PersistenceService
    from fastapi import HTTPException
    network = PersistenceService.seed_cascading_network(db, force_new=reset)
    if not network:
        raise HTTPException(status_code=404, detail="Cascading demonstration network could not be loaded.")
    return NetworkResponse(
        id=network.id,
        name=network.name,
        description=network.description,
        network_type=network.network_type,
        metadata=network.metadata_json,
        version=network.version,
        node_count=len(network.nodes),
        edge_count=len(network.edges),
        created_at=network.created_at.isoformat(),
        updated_at=network.updated_at.isoformat()
    )


@router.get("/{network_id}", response_model=NetworkResponse)

def get_network(
    network_id: str,
    db: Session = Depends(get_database)
) -> NetworkResponse:
    """Retrieves details of a specific network."""
    network = NetworkService.get_network(db, network_id)
    return NetworkResponse(
        id=network.id,
        name=network.name,
        description=network.description,
        network_type=network.network_type,
        metadata=network.metadata_json,
        version=network.version,
        node_count=len(network.nodes),
        edge_count=len(network.edges),
        created_at=network.created_at.isoformat(),
        updated_at=network.updated_at.isoformat()
    )


@router.put("/{network_id}", response_model=NetworkResponse)
def update_network(
    network_id: str,
    payload: NetworkUpdate,
    db: Session = Depends(get_database)
) -> NetworkResponse:
    """Updates network metadata and increments version with optimistic concurrency."""
    network = NetworkService.update_network(db, network_id, payload)
    return NetworkResponse(
        id=network.id,
        name=network.name,
        description=network.description,
        network_type=network.network_type,
        metadata=network.metadata_json,
        version=network.version,
        node_count=len(network.nodes),
        edge_count=len(network.edges),
        created_at=network.created_at.isoformat(),
        updated_at=network.updated_at.isoformat()
    )


@router.delete("/{network_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_network(
    network_id: str,
    db: Session = Depends(get_database)
) -> None:
    """Deletes a network and cascades removal of all associated nodes and links."""
    NetworkService.delete_network(db, network_id)


@router.get("/{network_id}/topology", response_model=NetworkTopologyResponse)
def get_network_topology(
    network_id: str,
    db: Session = Depends(get_database)
) -> NetworkTopologyResponse:
    """Returns the full network graph structure in Cytoscape.js compatible format."""
    return NetworkService.get_topology(db, network_id)


@router.post("/import", response_model=NetworkResponse, status_code=status.HTTP_201_CREATED)
def import_network(
    payload: NetworkImportRequest,
    db: Session = Depends(get_database)
) -> NetworkResponse:
    """Imports and validates a network from JSON/CSV graph data."""
    network = NetworkService.import_network(db, payload)
    return NetworkResponse(
        id=network.id,
        name=network.name,
        description=network.description,
        network_type=network.network_type,
        metadata=network.metadata_json,
        version=network.version,
        node_count=len(network.nodes),
        edge_count=len(network.edges),
        created_at=network.created_at.isoformat(),
        updated_at=network.updated_at.isoformat()
    )


@router.get("/{network_id}/export", response_model=NetworkExportResponse)
def export_network(
    network_id: str,
    db: Session = Depends(get_database)
) -> NetworkExportResponse:
    """Exports network topology to standard JSON graph format."""
    return NetworkService.export_network(db, network_id)

