"""
Tests for SQLAlchemy Database Models and Integrity Constraints (Phase 8).
Verifies table schemas, unique constraints, check constraints, and cascade deletes.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.network import Network
from app.models.node import NodeModel
from app.models.edge import EdgeModel
from app.models.network_snapshot import NetworkSnapshot
from app.models.simulation import SimulationModel
from app.models.simulation_event import SimulationEventModel
from app.database.base import Base


def test_schema_table_names(test_engine):
    """Verify that all 6 normalized tables are registered in Base metadata."""
    expected_tables = {
        "networks",
        "nodes",
        "edges",
        "network_snapshots",
        "simulations",
        "simulation_events"
    }
    assert expected_tables.issubset(set(Base.metadata.tables.keys()))


def test_network_creation_and_defaults(db_session):
    """Verify basic network creation with default version and metadata."""
    net = Network(name="Campus Backbone", description="Primary university core network")
    db_session.add(net)
    db_session.commit()
    db_session.refresh(net)

    assert net.id is not None
    assert net.name == "Campus Backbone"
    assert net.version == 1
    assert net.network_type == "COMMUNICATION_NETWORK"
    assert net.metadata_json == {}
    assert net.created_at is not None
    assert net.updated_at is not None


def test_node_unique_constraint(db_session):
    """Verify unique constraint on (network_id, node_id)."""
    net = Network(name="Test Network")
    db_session.add(net)
    db_session.commit()

    n1 = NodeModel(network_id=net.id, node_id="R1", node_type="router")
    db_session.add(n1)
    db_session.commit()

    # Attempt to insert identical node_id into the same network
    n2 = NodeModel(network_id=net.id, node_id="R1", node_type="switch")
    db_session.add(n2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_node_check_constraints(db_session):
    """Verify check constraints for capacity, importance, load, and failure probability."""
    net = Network(name="Constraint Test Net")
    db_session.add(net)
    db_session.commit()

    # Capacity must be positive (> 0)
    invalid_capacity_node = NodeModel(
        network_id=net.id, node_id="N_BadCap", node_type="server", capacity=0.0
    )
    db_session.add(invalid_capacity_node)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Failure probability must be between 0.0 and 1.0
    invalid_prob_node = NodeModel(
        network_id=net.id, node_id="N_BadProb", node_type="server", failure_probability=1.5
    )
    db_session.add(invalid_prob_node)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Importance must be non-negative (>= 0)
    invalid_imp_node = NodeModel(
        network_id=net.id, node_id="N_BadImp", node_type="server", importance=-0.5
    )
    db_session.add(invalid_imp_node)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_edge_undirected_unique_constraint(db_session):
    """Verify undirected edge uniqueness via canonical endpoints (canonical_u, canonical_v)."""
    net = Network(name="Edge Unique Test Net")
    db_session.add(net)
    db_session.commit()

    e1 = EdgeModel(
        network_id=net.id,
        edge_id="e1",
        source_node_id="A",
        target_node_id="B",
        canonical_u="A",
        canonical_v="B",
        weight=1.0
    )
    db_session.add(e1)
    db_session.commit()

    # Second edge with same canonical endpoints (even if edge_id differs)
    e2 = EdgeModel(
        network_id=net.id,
        edge_id="e2",
        source_node_id="B",
        target_node_id="A",
        canonical_u="A",
        canonical_v="B",
        weight=2.0
    )
    db_session.add(e2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_edge_no_self_loops_constraint(db_session):
    """Verify check constraint preventing self-loops (canonical_u != canonical_v)."""
    net = Network(name="Self Loop Test Net")
    db_session.add(net)
    db_session.commit()

    self_loop = EdgeModel(
        network_id=net.id,
        edge_id="e_loop",
        source_node_id="A",
        target_node_id="A",
        canonical_u="A",
        canonical_v="A"
    )
    db_session.add(self_loop)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_cascade_delete_network(db_session):
    """
    Verify that deleting a parent Network cascades and automatically deletes
    its associated nodes, edges, snapshots, simulations, and simulation events.
    """
    # 1. Create Network
    net = Network(name="Cascade Target Network")
    db_session.add(net)
    db_session.commit()
    net_id = net.id

    # 2. Add Nodes
    n1 = NodeModel(network_id=net_id, node_id="R1", node_type="router")
    n2 = NodeModel(network_id=net_id, node_id="S1", node_type="switch")
    db_session.add_all([n1, n2])
    db_session.commit()

    # 3. Add Edge
    e1 = EdgeModel(
        network_id=net_id,
        edge_id="e1",
        source_node_id="R1",
        target_node_id="S1",
        canonical_u="R1",
        canonical_v="S1"
    )
    db_session.add(e1)
    db_session.commit()

    # 4. Add Snapshot
    snap = NetworkSnapshot(
        network_id=net_id,
        network_version=1,
        graph_snapshot={"nodes": ["R1", "S1"], "edges": [["R1", "S1"]]},
        snapshot_hash="abc123hash"
    )
    db_session.add(snap)
    db_session.commit()

    # 5. Add Simulation & Event
    sim = SimulationModel(
        network_id=net_id,
        snapshot_id=snap.id,
        simulation_type="node_failure",
        status="completed"
    )
    db_session.add(sim)
    db_session.commit()
    sim_id = sim.id

    event = SimulationEventModel(
        simulation_id=sim_id,
        sequence_number=1,
        event_type="NODE_FAILED",
        event_data={"failed_node": "R1"}
    )
    db_session.add(event)
    db_session.commit()

    # Verify entities exist
    assert db_session.scalar(select(NodeModel).where(NodeModel.network_id == net_id)) is not None
    assert db_session.scalar(select(EdgeModel).where(EdgeModel.network_id == net_id)) is not None
    assert db_session.scalar(select(NetworkSnapshot).where(NetworkSnapshot.network_id == net_id)) is not None
    assert db_session.scalar(select(SimulationModel).where(SimulationModel.network_id == net_id)) is not None
    assert db_session.scalar(select(SimulationEventModel).where(SimulationEventModel.simulation_id == sim_id)) is not None

    # Delete Network
    db_session.delete(net)
    db_session.commit()
    db_session.expunge_all()

    # Verify everything cascaded
    assert db_session.scalars(select(NodeModel).where(NodeModel.network_id == net_id)).all() == []
    assert db_session.scalars(select(EdgeModel).where(EdgeModel.network_id == net_id)).all() == []
    assert db_session.scalars(select(NetworkSnapshot).where(NetworkSnapshot.network_id == net_id)).all() == []
    assert db_session.scalars(select(SimulationModel).where(SimulationModel.network_id == net_id)).all() == []
    assert db_session.scalars(select(SimulationEventModel).where(SimulationEventModel.simulation_id == sim_id)).all() == []
