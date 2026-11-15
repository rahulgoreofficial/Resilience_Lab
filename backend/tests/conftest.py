"""
Pytest configuration and shared fixtures for Graph Engine and Algorithms.
"""

import os
import sys

# Ensure backend app is in sys.path and tests use an isolated in-memory database
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest

from app.graph_engine.graph_model import Node, Edge
from app.graph_engine.graph_builder import NetworkGraph


@pytest.fixture
def empty_graph():
    """Returns a graph with |V| = 0, |E| = 0."""
    return NetworkGraph.create("Empty_Graph")


@pytest.fixture
def single_node_graph():
    """Returns a graph with 1 node, 0 edges."""
    g = NetworkGraph.create("Single_Node")
    g.add_node(Node("N1", "server"))
    return g


@pytest.fixture
def two_node_graph():
    """Returns a graph with 2 nodes and 1 edge."""
    g = NetworkGraph.create("Two_Nodes")
    g.add_node(Node("A", "router"))
    g.add_node(Node("B", "switch"))
    g.add_edge(Edge("e1", "A", "B", weight=2.0))
    return g


@pytest.fixture
def linear_graph_p5():
    """Returns a path graph P5: 1 - 2 - 3 - 4 - 5."""
    g = NetworkGraph.create("Linear_P5")
    for i in range(1, 6):
        g.add_node(Node(f"v{i}", "router"))
    for i in range(1, 5):
        g.add_edge(Edge(f"e{i}_{i+1}", f"v{i}", f"v{i+1}", weight=1.0))
    return g


@pytest.fixture
def star_graph_s5():
    """Returns a star graph S5 with center hub H and 4 leaves L1..L4."""
    g = NetworkGraph.create("Star_S5")
    g.add_node(Node("H", "router"))
    for i in range(1, 5):
        g.add_node(Node(f"L{i}", "server"))
        g.add_edge(Edge(f"e_h_l{i}", "H", f"L{i}", weight=1.0))
    return g


@pytest.fixture
def cycle_graph_c5():
    """Returns a cycle graph C5: v1 - v2 - v3 - v4 - v5 - v1."""
    g = NetworkGraph.create("Cycle_C5")
    for i in range(1, 6):
        g.add_node(Node(f"v{i}", "switch"))
    for i in range(1, 5):
        g.add_edge(Edge(f"e{i}", f"v{i}", f"v{i+1}", weight=2.0))
    g.add_edge(Edge("e5", "v5", "v1", weight=2.0))
    return g


@pytest.fixture
def complete_graph_k5():
    """Returns a complete graph K5."""
    g = NetworkGraph.create("Complete_K5")
    for i in range(1, 6):
        g.add_node(Node(f"v{i}", "router"))
    for i in range(1, 6):
        for j in range(i + 1, 6):
            g.add_edge(Edge(f"e_{i}_{j}", f"v{i}", f"v{j}", weight=1.0))
    return g


@pytest.fixture
def disconnected_graph():
    """Returns disconnected graph: Triangle (A-B-C-A) + Segment (D-E)."""
    g = NetworkGraph.create("Disconnected")
    for n in ["A", "B", "C", "D", "E"]:
        g.add_node(Node(n, "server"))
    g.add_edge(Edge("e_ab", "A", "B"))
    g.add_edge(Edge("e_bc", "B", "C"))
    g.add_edge(Edge("e_ca", "C", "A"))
    g.add_edge(Edge("e_de", "D", "E"))
    return g


@pytest.fixture
def sample_network():
    """Loads the calibrated benchmark network from datasets/sample_network.json."""
    dataset_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "sample_network.json")
    )
    with open(dataset_path, "r", encoding="utf-8") as f:
        json_content = f.read()
    return NetworkGraph.from_json(json_content)


# =====================================================================
# Database & API Client Fixtures (Phase 8)
# =====================================================================

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.database.base import Base
from app.database.session import get_db, set_engine_and_session
import app.models  # Ensure all models are registered with Base.metadata
from app.main import app


@pytest.fixture(scope="session")
def test_engine():
    """
    Session-wide in-memory SQLite engine configured with StaticPool
    and foreign key enforcement.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Configure session module to use this engine
    set_engine_and_session(engine)
    return engine


@pytest.fixture
def db_session(test_engine) -> Session:
    """
    Provides an isolated database session per test with cleanly reset tables.
    """
    set_engine_and_session(test_engine)
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    SessionClass = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionClass()
    try:
        yield session
    finally:
        session.close()


