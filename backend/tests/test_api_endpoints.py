"""
Integration tests for FastAPI REST API endpoints.
Tests health checks, version information, database status, and algorithm endpoints.
"""

from app.main import (
    get_health,
    get_version,
    get_database_health,
    get_graph_representations,
    run_bfs,
    run_connected_components,
    run_articulation_points,
    run_bridges,
    run_shortest_path
)
from app.schemas.graph_schema import GraphDataSchema, BFSRequest, DijkstraRequest


def test_api_health():
    """Verify get_health endpoint responds with healthy status and metadata."""
    data = get_health()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "project" in data


def test_api_version():
    """Verify get_version endpoint returns version info."""
    data = get_version()
    assert data["version"] == "1.0.0"
    assert "project_name" in data


def test_api_database_health():
    """
    Verify get_database_health reports database status without crashing
    even when PostgreSQL is not running.
    """
    data = get_database_health()
    assert data["status"] in ("healthy", "unavailable")
    assert data["database"] == "infrastructure_resilience"


def test_api_graph_representations_and_algorithms():
    """Verify graph algorithms via API route handlers."""
    sample_payload = GraphDataSchema(
        name="Test_Network",
        directed=False,
        multigraph=False,
        nodes=[
            {"node_id": "A", "node_type": "router"},
            {"node_id": "B", "node_type": "switch"},
            {"node_id": "C", "node_type": "server"}
        ],
        edges=[
            {"edge_id": "e1", "source": "A", "target": "B", "weight": 2.0},
            {"edge_id": "e2", "source": "B", "target": "C", "weight": 3.0}
        ]
    )

    # 1. Representations
    rep_data = get_graph_representations(sample_payload)
    assert rep_data["is_consistent"] is True
    assert rep_data["ordered_nodes"] == ["A", "B", "C"]
    assert rep_data["adjacency_matrix"] == [[0, 1, 0], [1, 0, 1], [0, 1, 0]]

    # 2. Connected Components
    cc_data = run_connected_components(sample_payload)
    assert cc_data["component_count"] == 1
    assert cc_data["is_connected"] is True

    # 3. BFS
    bfs_data = run_bfs(sample_payload, BFSRequest(start_node="A"))
    assert bfs_data["traversal_order"] == ["A", "B", "C"]
    assert bfs_data["distances"] == {"A": 0, "B": 1, "C": 2}

    # 4. Articulation Points
    ap_data = run_articulation_points(sample_payload)
    assert ap_data["articulation_points"] == ["B"]

    # 5. Bridges
    br_data = run_bridges(sample_payload)
    assert br_data["count"] == 2
    assert ("A", "B") in br_data["bridges"]
    assert ("B", "C") in br_data["bridges"]

    # 6. Dijkstra
    dijk_data = run_shortest_path(sample_payload, DijkstraRequest(source="A", target="C"))
    assert dijk_data["distance"] == 5.0
    assert dijk_data["path"] == ["A", "B", "C"]


def test_api_system_shutdown_and_spa():
    """Verify system shutdown security check and SPA resolution."""
    from app.main import api_system_shutdown, find_frontend_dist
    from unittest.mock import MagicMock
    from fastapi import HTTPException
    
    # Unauthorized remote client should be rejected with 403
    remote_req = MagicMock()
    remote_req.client.host = "192.168.1.100"
    try:
        api_system_shutdown(remote_req)
        assert False, "Expected 403 HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 403

    # Local client is allowed
    local_req = MagicMock()
    local_req.client.host = "127.0.0.1"
    res = api_system_shutdown(local_req)
    assert res["status"] == "shutting_down"

    # Frontend dist locator should identify built frontend
    dist_path = find_frontend_dist()
    assert dist_path is not None
    assert (dist_path / "index.html").is_file()

