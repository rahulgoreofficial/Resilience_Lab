"""
Integration tests for Persistent Network CRUD, Cytoscape Topology, Import/Export APIs (Phase 8).
Directly tests API route handlers with isolated transactional database sessions.
"""

import pytest
from app.api.v1.networks import (
    create_network,
    list_networks,
    get_network,
    update_network,
    delete_network,
    get_network_topology,
    export_network,
    import_network
)
from app.api.v1.nodes import (
    add_node,
    list_nodes,
    get_node,
    update_node,
    delete_node
)
from app.api.v1.edges import (
    add_edge,
    list_edges,
    get_edge,
    update_edge,
    delete_edge
)
from app.schemas.common import PaginationParams
from app.schemas.network import NetworkCreate, NetworkUpdate, NetworkImportRequest
from app.schemas.node import NodeCreate, NodeUpdate
from app.schemas.edge import EdgeCreate, EdgeUpdate
from app.core.exceptions import (
    EntityNotFoundError,
    DuplicateEntityError,
    AppException
)
from app.graph_engine.graph_validation import GraphStructureError


def test_network_crud_lifecycle(db_session):
    """Test full CRUD lifecycle for networks: Create, Read, Update, Delete."""
    # 1. Create Network
    create_payload = NetworkCreate(
        name="Enterprise Data Center Backbone",
        description="High-availability multi-tier network",
        network_type="DATA_CENTER",
        metadata={"region": "us-east-1", "tier": 1}
    )
    res = create_network(create_payload, db=db_session)
    net_id = res.id
    assert res.name == create_payload.name
    assert res.version == 1
    assert res.node_count == 0
    assert res.edge_count == 0

    # 2. Read single network
    retrieved = get_network(net_id, db=db_session)
    assert retrieved.id == net_id
    assert retrieved.name == create_payload.name

    # 3. List networks
    paginated = list_networks(pagination=PaginationParams(skip=0, limit=20), db=db_session)
    assert paginated.total >= 1
    assert any(item.id == net_id for item in paginated.items)

    # 4. Update network
    update_payload = NetworkUpdate(
        name="Enterprise Data Center Backbone v2",
        description="Updated topology descriptions",
        expected_version=1
    )
    updated = update_network(net_id, update_payload, db=db_session)
    assert updated.name == "Enterprise Data Center Backbone v2"
    assert updated.version == 2

    # 5. Delete network
    delete_network(net_id, db=db_session)

    # 6. Read deleted network raises EntityNotFoundError (HTTP 404)
    with pytest.raises(EntityNotFoundError):
        get_network(net_id, db=db_session)


def test_node_crud_lifecycle(db_session):
    """Test full CRUD lifecycle for nodes within a network."""
    # Create parent network
    net = create_network(NetworkCreate(name="Node Test Net"), db=db_session)
    net_id = net.id

    # 1. Add Router node
    node_payload_1 = NodeCreate(
        node_id="CR1",
        node_type="router",
        importance=3.0,
        capacity=500.0,
        current_load=50.0,
        failure_probability=0.02,
        is_critical=True,
        metadata={"vendor": "Cisco", "model": "ASR9000"}
    )
    n1 = add_node(net_id, node_payload_1, db=db_session)
    assert n1.node_id == "CR1"
    assert n1.node_type == "router"
    assert n1.is_critical is True

    # 2. Add Switch node
    node_payload_2 = NodeCreate(
        node_id="SW1",
        node_type="switch",
        importance=1.5,
        capacity=200.0
    )
    n2 = add_node(net_id, node_payload_2, db=db_session)
    assert n2.node_id == "SW1"

    # 3. List nodes
    nodes = list_nodes(net_id, db=db_session)
    assert len(nodes) == 2
    assert {n.node_id for n in nodes} == {"CR1", "SW1"}

    # 4. Get specific node
    retrieved_n1 = get_node(net_id, "CR1", db=db_session)
    assert retrieved_n1.node_id == "CR1"
    assert retrieved_n1.capacity == 500.0

    # 5. Update node
    updated_n1 = update_node(net_id, "CR1", NodeUpdate(capacity=600.0, is_critical=False), db=db_session)
    assert updated_n1.capacity == 600.0
    assert updated_n1.is_critical is False

    # 6. Attempt to add duplicate node_id in same network raises DuplicateEntityError
    with pytest.raises(DuplicateEntityError):
        add_node(net_id, NodeCreate(node_id="CR1", node_type="server"), db=db_session)

    # 7. Delete node
    delete_node(net_id, "SW1", db=db_session)
    with pytest.raises(EntityNotFoundError):
        get_node(net_id, "SW1", db=db_session)


def test_edge_crud_and_topology_retrieval(db_session):
    """Test Edge CRUD, incident edge cascade on node deletion, and Cytoscape format."""
    # 1. Create network with 3 nodes
    net = create_network(NetworkCreate(name="Edge Topology Net"), db=db_session)
    net_id = net.id

    for n_id, n_type in [("R1", "router"), ("R2", "router"), ("S1", "switch")]:
        add_node(net_id, NodeCreate(node_id=n_id, node_type=n_type), db=db_session)

    # 2. Add Edge R1 - R2
    edge_payload_1 = EdgeCreate(
        edge_id="e_r1_r2",
        source_node_id="R1",
        target_node_id="R2",
        weight=2.5,
        latency=5.0,
        capacity=100.0,
        reliability=0.999
    )
    e1 = add_edge(net_id, edge_payload_1, db=db_session)
    assert e1.edge_id == "e_r1_r2"
    assert e1.source_node_id == "R1"
    assert e1.target_node_id == "R2"

    # 3. Add Edge R2 - S1
    edge_payload_2 = EdgeCreate(
        edge_id="e_r2_s1",
        source_node_id="R2",
        target_node_id="S1",
        weight=1.0
    )
    e2 = add_edge(net_id, edge_payload_2, db=db_session)
    assert e2.edge_id == "e_r2_s1"

    # 4. Attempt to add self-loop (should fail with GraphStructureError)
    self_loop = EdgeCreate(
        edge_id="e_loop",
        source_node_id="R1",
        target_node_id="R1"
    )
    with pytest.raises((GraphStructureError, AppException)):
        add_edge(net_id, self_loop, db=db_session)

    # 5. Attempt to add edge to non-existent node (should fail with AppException)
    bad_edge = EdgeCreate(
        edge_id="e_bad",
        source_node_id="R1",
        target_node_id="NON_EXISTENT"
    )
    with pytest.raises(AppException):
        add_edge(net_id, bad_edge, db=db_session)

    # 6. Verify Cytoscape topology representation
    topo = get_network_topology(net_id, db=db_session)
    assert topo.elements is not None
    elements = topo.elements
    assert len(elements.nodes) == 3
    assert len(elements.edges) == 2

    # Check Cytoscape node structure
    cy_node = elements.nodes[0]
    assert cy_node.data.id in {"R1", "R2", "S1"}
    assert cy_node.data.label is not None

    # Check Cytoscape edge structure
    cy_edge = elements.edges[0]
    assert cy_edge.data.id in {"e_r1_r2", "e_r2_s1"}
    assert cy_edge.data.source is not None
    assert cy_edge.data.target is not None

    # 7. Delete node R2 -> Incident edges e_r1_r2 and e_r2_s1 must be cascade deleted
    delete_node(net_id, "R2", db=db_session)

    # Verify edge list is now empty
    edges = list_edges(net_id, db=db_session)
    assert len(edges) == 0


def test_network_export_and_import(db_session):
    """Test exporting a network to JSON format and importing it as a new network."""
    # 1. Create original network with nodes and edges
    orig_net = create_network(NetworkCreate(name="Original Export Net"), db=db_session)
    orig_net_id = orig_net.id

    add_node(orig_net_id, NodeCreate(node_id="A", node_type="router"), db=db_session)
    add_node(orig_net_id, NodeCreate(node_id="B", node_type="switch"), db=db_session)
    add_edge(
        orig_net_id,
        EdgeCreate(edge_id="e_ab", source_node_id="A", target_node_id="B", weight=4.2),
        db=db_session
    )

    # 2. Export network
    export_data = export_network(orig_net_id, db=db_session)
    assert export_data.name == "Original Export Net"
    assert len(export_data.nodes) == 2
    assert len(export_data.edges) == 1

    # 3. Import network with new name
    import_payload = NetworkImportRequest(
        name="Cloned Network From Export",
        description="Restored from exported backup",
        data={"nodes": export_data.nodes, "edges": export_data.edges}
    )
    cloned_net = import_network(import_payload, db=db_session)
    cloned_id = cloned_net.id
    assert cloned_id != orig_net_id
    assert cloned_net.name == "Cloned Network From Export"
    assert cloned_net.node_count == 2
    assert cloned_net.edge_count == 1

    # Verify cloned nodes and edges exist
    nodes = list_nodes(cloned_id, db=db_session)
    assert {n.node_id for n in nodes} == {"A", "B"}
    edges = list_edges(cloned_id, db=db_session)
    assert len(edges) == 1
    assert edges[0].weight == 4.2
