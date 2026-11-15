"""
Service: NetworkService.
Coordinates network infrastructure business logic, CRUD, Cytoscape topology conversions,
and immutable snapshot generation.
"""

from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.network import Network
from app.models.node import NodeModel
from app.models.edge import EdgeModel
from app.models.network_snapshot import NetworkSnapshot
from app.repositories.network_repository import NetworkRepository
from app.repositories.node_repository import NodeRepository
from app.repositories.edge_repository import EdgeRepository
from app.repositories.simulation_repository import SimulationRepository
from app.schemas.network import (
    NetworkCreate,
    NetworkUpdate,
    NetworkTopologyResponse,
    CytoscapeElements,
    CytoscapeNodeElement,
    CytoscapeNodeData,
    CytoscapeEdgeElement,
    CytoscapeEdgeData,
    NetworkImportRequest,
    NetworkExportResponse
)
from app.schemas.node import NodeCreate, NodeUpdate, NodeResponse
from app.schemas.edge import EdgeCreate, EdgeUpdate, EdgeResponse
from app.core.exceptions import (
    NetworkNotFoundError,
    NodeNotFoundError,
    EdgeNotFoundError,
    DuplicateEntityError,
    BadRequestError
)
from app.core.security import validate_network_size
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_model import Node as EngineNode, Edge as EngineEdge
from app.simulation.simulation_utils import hash_graph_topology


class NetworkService:
    """Service layer managing network infrastructure operations."""

    @staticmethod
    def create_network(db: Session, data: NetworkCreate) -> Network:
        network = Network(
            name=data.name,
            description=data.description,
            network_type=data.network_type,
            metadata_json=data.metadata
        )
        NetworkRepository.create(db, network)

        # Populate initial nodes if provided
        if data.nodes:
            seen_nodes = set()
            for n in data.nodes:
                if n.node_id in seen_nodes:
                    raise DuplicateEntityError(message=f"Duplicate initial node '{n.node_id}' provided.")
                seen_nodes.add(n.node_id)
                node_obj = NodeModel(
                    network_id=network.id,
                    node_id=n.node_id,
                    node_type=n.node_type,
                    importance=n.importance,
                    capacity=n.capacity,
                    current_load=n.current_load,
                    failure_probability=n.failure_probability,
                    is_critical=n.is_critical,
                    metadata_json=n.metadata
                )
                NodeRepository.create(db, node_obj)

        # Populate initial edges if provided
        if data.edges:
            seen_edges = set()
            seen_endpoints = set()
            node_ids = {n.node_id for n in (data.nodes or [])}
            for e in data.edges:
                if e.source_node_id not in node_ids or e.target_node_id not in node_ids:
                    raise BadRequestError(message=f"Edge endpoints '{e.source_node_id}' - '{e.target_node_id}' must exist.")
                if e.source_node_id == e.target_node_id:
                    raise BadRequestError(message=f"Self-loops are forbidden: '{e.source_node_id}'.")
                
                can_u, can_v = min(e.source_node_id, e.target_node_id), max(e.source_node_id, e.target_node_id)
                if (can_u, can_v) in seen_endpoints or e.edge_id in seen_edges:
                    raise DuplicateEntityError(message=f"Duplicate edge '{e.edge_id}' or undirected link '{can_u}'-'{can_v}'.")
                seen_edges.add(e.edge_id)
                seen_endpoints.add((can_u, can_v))

                edge_obj = EdgeModel(
                    network_id=network.id,
                    edge_id=e.edge_id,
                    source_node_id=e.source_node_id,
                    target_node_id=e.target_node_id,
                    canonical_u=can_u,
                    canonical_v=can_v,
                    weight=e.weight,
                    latency=e.latency,
                    capacity=e.capacity,
                    reliability=e.reliability,
                    metadata_json=e.metadata
                )
                EdgeRepository.create(db, edge_obj)

        db.commit()
        db.refresh(network)
        return network

    @staticmethod
    def get_network(db: Session, network_id: str) -> Network:
        network = NetworkRepository.get_by_id_with_elements(db, network_id)
        if not network:
            raise NetworkNotFoundError(message=f"Network '{network_id}' not found.")
        return network

    @staticmethod
    def list_networks(db: Session, skip: int = 0, limit: int = 50) -> Tuple[List[Network], int]:
        return NetworkRepository.list_all(db, skip=skip, limit=limit)

    @staticmethod
    def update_network(db: Session, network_id: str, data: NetworkUpdate) -> Network:
        network = NetworkService.get_network(db, network_id)
        update_data = {
            "name": data.name,
            "description": data.description,
            "network_type": data.network_type,
            "metadata_json": data.metadata
        }
        updated = NetworkRepository.update(
            db=db,
            network=network,
            update_data=update_data,
            expected_version=data.expected_version
        )
        db.commit()
        db.refresh(updated)
        return updated

    @staticmethod
    def delete_network(db: Session, network_id: str) -> None:
        network = NetworkService.get_network(db, network_id)
        NetworkRepository.delete(db, network)
        db.commit()

    @staticmethod
    def add_node(db: Session, network_id: str, data: NodeCreate) -> NodeModel:
        network = NetworkService.get_network(db, network_id)
        existing = NodeRepository.get_by_node_id(db, network_id, data.node_id)
        if existing:
            raise DuplicateEntityError(message=f"Node '{data.node_id}' already exists in network '{network_id}'.")

        validate_network_size(len(network.nodes) + 1, len(network.edges))

        node = NodeModel(
            network_id=network_id,
            node_id=data.node_id,
            node_type=data.node_type,
            importance=data.importance,
            capacity=data.capacity,
            current_load=data.current_load,
            failure_probability=data.failure_probability,
            is_critical=data.is_critical,
            metadata_json=data.metadata
        )
        NodeRepository.create(db, node)
        NetworkRepository.increment_version(db, network)
        db.commit()
        db.refresh(node)
        return node

    @staticmethod
    def get_node(db: Session, network_id: str, node_id: str) -> NodeModel:
        node = NodeRepository.get_by_node_id(db, network_id, node_id)
        if not node:
            raise NodeNotFoundError(message=f"Node '{node_id}' not found in network '{network_id}'.")
        return node

    @staticmethod
    def update_node(db: Session, network_id: str, node_id: str, data: NodeUpdate) -> NodeModel:
        network = NetworkService.get_network(db, network_id)
        node = NetworkService.get_node(db, network_id, node_id)
        update_data = data.model_dump(exclude_unset=True)
        if "metadata" in update_data:
            update_data["metadata_json"] = update_data.pop("metadata")

        NodeRepository.update(db, node, update_data)
        NetworkRepository.increment_version(db, network)
        db.commit()
        db.refresh(node)
        return node

    @staticmethod
    def delete_node(db: Session, network_id: str, node_id: str) -> None:
        network = NetworkService.get_network(db, network_id)
        node = NetworkService.get_node(db, network_id, node_id)
        NodeRepository.delete(db, node)
        NetworkRepository.increment_version(db, network)
        db.commit()

    @staticmethod
    def add_edge(db: Session, network_id: str, data: EdgeCreate) -> EdgeModel:
        network = NetworkService.get_network(db, network_id)
        # Validate endpoints exist
        src = NodeRepository.get_by_node_id(db, network_id, data.source_node_id)
        if not src:
            raise NodeNotFoundError(message=f"Source node '{data.source_node_id}' not found.")
        dst = NodeRepository.get_by_node_id(db, network_id, data.target_node_id)
        if not dst:
            raise NodeNotFoundError(message=f"Target node '{data.target_node_id}' not found.")
        if data.source_node_id == data.target_node_id:
            raise BadRequestError(message=f"Self-loops are forbidden: '{data.source_node_id}'.")

        # Check for duplicate edge_id or undirected endpoints
        if EdgeRepository.get_by_edge_id(db, network_id, data.edge_id):
            raise DuplicateEntityError(message=f"Edge ID '{data.edge_id}' already exists in network.")

        can_u = min(data.source_node_id, data.target_node_id)
        can_v = max(data.source_node_id, data.target_node_id)
        if EdgeRepository.get_by_endpoints(db, network_id, can_u, can_v):
            raise DuplicateEntityError(message=f"Undirected link between '{can_u}' and '{can_v}' already exists.")

        validate_network_size(len(network.nodes), len(network.edges) + 1)

        edge = EdgeModel(
            network_id=network_id,
            edge_id=data.edge_id,
            source_node_id=data.source_node_id,
            target_node_id=data.target_node_id,
            canonical_u=can_u,
            canonical_v=can_v,
            weight=data.weight,
            latency=data.latency,
            capacity=data.capacity,
            reliability=data.reliability,
            metadata_json=data.metadata
        )
        EdgeRepository.create(db, edge)
        NetworkRepository.increment_version(db, network)
        db.commit()
        db.refresh(edge)
        return edge

    @staticmethod
    def get_edge(db: Session, network_id: str, edge_id: str) -> EdgeModel:
        edge = EdgeRepository.get_by_edge_id(db, network_id, edge_id)
        if not edge:
            raise EdgeNotFoundError(message=f"Edge '{edge_id}' not found in network '{network_id}'.")
        return edge

    @staticmethod
    def update_edge(db: Session, network_id: str, edge_id: str, data: EdgeUpdate) -> EdgeModel:
        network = NetworkService.get_network(db, network_id)
        edge = NetworkService.get_edge(db, network_id, edge_id)
        update_data = data.model_dump(exclude_unset=True)
        if "metadata" in update_data:
            update_data["metadata_json"] = update_data.pop("metadata")

        EdgeRepository.update(db, edge, update_data)
        NetworkRepository.increment_version(db, network)
        db.commit()
        db.refresh(edge)
        return edge

    @staticmethod
    def delete_edge(db: Session, network_id: str, edge_id: str) -> None:
        network = NetworkService.get_network(db, network_id)
        edge = NetworkService.get_edge(db, network_id, edge_id)
        EdgeRepository.delete(db, edge)
        NetworkRepository.increment_version(db, network)
        db.commit()

    @staticmethod
    def get_topology(db: Session, network_id: str) -> NetworkTopologyResponse:
        network = NetworkService.get_network(db, network_id)
        nodes_list = NodeRepository.list_by_network(db, network_id)
        edges_list = EdgeRepository.list_by_network(db, network_id)

        cy_nodes = [
            CytoscapeNodeElement(
                data=CytoscapeNodeData(
                    id=n.node_id,
                    label=n.node_id,
                    node_type=n.node_type,
                    importance=n.importance,
                    capacity=n.capacity,
                    current_load=n.current_load,
                    failure_probability=n.failure_probability,
                    is_critical=n.is_critical,
                    metadata=n.metadata_json
                )
            )
            for n in nodes_list
        ]

        cy_edges = [
            CytoscapeEdgeElement(
                data=CytoscapeEdgeData(
                    id=e.edge_id,
                    source=e.source_node_id,
                    target=e.target_node_id,
                    weight=e.weight,
                    latency=e.latency,
                    capacity=e.capacity,
                    reliability=e.reliability,
                    metadata=e.metadata_json
                )
            )
            for e in edges_list
        ]

        node_responses = [
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
            for n in nodes_list
        ]

        edge_responses = [
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
            for e in edges_list
        ]

        return NetworkTopologyResponse(
            network_id=network.id,
            name=network.name,
            version=network.version,
            elements=CytoscapeElements(nodes=cy_nodes, edges=cy_edges),
            nodes=node_responses,
            edges=edge_responses
        )

    @staticmethod
    def to_graph_engine(db: Session, network_id: str) -> NetworkGraph:
        """Constructs an active NetworkGraph instance from database records."""
        network = NetworkService.get_network(db, network_id)
        nodes = NodeRepository.list_by_network(db, network_id)
        edges = EdgeRepository.list_by_network(db, network_id)

        graph = NetworkGraph.create(name=network.name)
        for n in nodes:
            graph.add_node(EngineNode(
                node_id=n.node_id,
                node_type=n.node_type,
                importance=n.importance,
                capacity=n.capacity,
                current_load=n.current_load,
                failure_probability=n.failure_probability,
                is_critical=n.is_critical,
                metadata=n.metadata_json
            ))

        for e in edges:
            graph.add_edge(EngineEdge(
                edge_id=e.edge_id,
                source=e.source_node_id,
                target=e.target_node_id,
                weight=e.weight,
                latency=e.latency,
                capacity=e.capacity,
                reliability=e.reliability,
                metadata=e.metadata_json
            ))
        return graph

    @staticmethod
    def create_snapshot(db: Session, network_id: str) -> NetworkSnapshot:
        """Creates an immutable serialized graph snapshot in the database."""
        network = NetworkService.get_network(db, network_id)
        graph_engine = NetworkService.to_graph_engine(db, network_id)
        serialized_graph = graph_engine.to_dict()
        snapshot_hash = hash_graph_topology(graph_engine)

        snapshot = NetworkSnapshot(
            network_id=network_id,
            network_version=network.version,
            graph_snapshot=serialized_graph,
            snapshot_hash=snapshot_hash
        )
        SimulationRepository.create_snapshot(db, snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    @staticmethod
    def import_network(db: Session, req: NetworkImportRequest) -> Network:
        data = req.data
        if not isinstance(data, dict):
            raise BadRequestError(message="Import data must be a valid JSON object.")

        # Support Cytoscape elements structure
        if "elements" in data and isinstance(data["elements"], dict):
            nodes_raw = data["elements"].get("nodes", [])
            edges_raw = data["elements"].get("edges", [])
        else:
            nodes_raw = data.get("nodes", [])
            edges_raw = data.get("edges") or data.get("links") or []

        # Unwrap data object if nested
        unwrapped_nodes = [
            n.get("data", n) if isinstance(n, dict) else {}
            for n in nodes_raw
        ]
        unwrapped_edges = [
            e.get("data", e) if isinstance(e, dict) else {}
            for e in edges_raw
        ]

        validate_network_size(len(unwrapped_nodes), len(unwrapped_edges))

        seen_nodes = set()
        node_creates = []
        for idx, n in enumerate(unwrapped_nodes):
            nid = str(n.get("node_id") or n.get("id") or f"node_{idx+1}").strip()
            if not nid or nid in seen_nodes:
                continue
            seen_nodes.add(nid)
            node_creates.append(
                NodeCreate(
                    node_id=nid,
                    node_type=str(n.get("node_type") or n.get("type", "router")).lower(),
                    importance=float(n.get("importance", 1.0)),
                    capacity=float(n.get("capacity", 500.0)),
                    current_load=float(n.get("current_load") or n.get("load", 0.0)),
                    failure_probability=float(n.get("failure_probability", 0.01)),
                    is_critical=bool(n.get("is_critical", False)),
                    metadata=n.get("metadata", {})
                )
            )

        # Build set of valid node IDs
        valid_node_ids = {n.node_id for n in node_creates}

        seen_edges = set()
        seen_endpoints = set()
        edge_creates = []
        for idx, e in enumerate(unwrapped_edges):
            eid = str(e.get("edge_id") or e.get("id") or f"edge_{idx+1}").strip()
            src = str(e.get("source_node_id") or e.get("source") or "").strip()
            tgt = str(e.get("target_node_id") or e.get("target") or "").strip()

            if not src or not tgt or src == tgt:
                continue

            # Auto-create endpoint nodes if they weren't in the explicit nodes list
            for endpoint in [src, tgt]:
                if endpoint not in valid_node_ids:
                    node_creates.append(
                        NodeCreate(
                            node_id=endpoint,
                            node_type="router",
                            importance=0.8,
                            capacity=500.0,
                            current_load=20.0
                        )
                    )
                    valid_node_ids.add(endpoint)

            can_pair = (min(src, tgt), max(src, tgt))
            if can_pair in seen_endpoints or eid in seen_edges:
                continue
            seen_endpoints.add(can_pair)
            seen_edges.add(eid)

            edge_creates.append(
                EdgeCreate(
                    edge_id=eid,
                    source_node_id=src,
                    target_node_id=tgt,
                    weight=float(e.get("weight", 1.0)),
                    latency=float(e.get("latency", 1.0)),
                    capacity=float(e.get("capacity", 1000.0)),
                    reliability=float(e.get("reliability", 0.99)),
                    metadata=e.get("metadata", {})
                )
            )

        create_req = NetworkCreate(
            name=req.name,
            description=req.description or "Imported from JSON graph topology.",
            network_type=req.network_type or "COMMUNICATION_NETWORK",
            nodes=node_creates,
            edges=edge_creates
        )
        return NetworkService.create_network(db, create_req)

    @staticmethod
    def export_network(db: Session, network_id: str) -> NetworkExportResponse:
        network = NetworkService.get_network(db, network_id)
        nodes = NodeRepository.list_by_network(db, network_id)
        edges = EdgeRepository.list_by_network(db, network_id)

        return NetworkExportResponse(
            network_id=network.id,
            name=network.name,
            version=network.version,
            directed=False,
            multigraph=False,
            nodes=[n.to_dict() for n in nodes],
            edges=[e.to_dict() for e in edges]
        )

