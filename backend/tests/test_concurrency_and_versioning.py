"""
Tests for Optimistic Concurrency Control, Standardized Error Schema, and Validation Security (Phase 8).
Validates version tracking (HTTP 409 conflict detection) and unified error envelope.
"""

import pytest

from app.services.network_service import NetworkService
from app.schemas.network import NetworkCreate, NetworkUpdate
from app.core.exceptions import (
    AppException,
    EntityNotFoundError,
    NetworkNotFoundError,
    NodeNotFoundError,
    EdgeNotFoundError,
    SimulationNotFoundError,
    ConflictError,
    NetworkVersionConflictError,
    DuplicateEntityError,
    BadRequestError,
    PayloadTooLargeError,
    DatabaseUnavailableError
)
from app.core.security import (
    validate_payload_size,
    validate_file_format,
    validate_network_size
)


def test_optimistic_concurrency_control_conflict(db_session):
    """
    Verify optimistic concurrency control: updating with a stale expected_version
    raises NetworkVersionConflictError (HTTP 409), preventing lost updates.
    """
    # 1. Create network at version 1
    net = NetworkService.create_network(db_session, NetworkCreate(name="Original Network"))
    net_id = net.id
    assert net.version == 1

    # 2. Process B updates the network with expected_version=1 -> version becomes 2
    update_b = NetworkUpdate(name="Updated by Process B", expected_version=1)
    updated_net = NetworkService.update_network(db_session, net_id, update_b)
    assert updated_net.version == 2
    assert updated_net.name == "Updated by Process B"

    # 3. Process A tries to update using stale expected_version=1 -> Must raise NetworkVersionConflictError
    update_a_stale = NetworkUpdate(name="Overwrite by Process A", expected_version=1)
    with pytest.raises(NetworkVersionConflictError) as exc_info:
        NetworkService.update_network(db_session, net_id, update_a_stale)
    
    assert exc_info.value.status_code == 409
    assert exc_info.value.error_code == "VERSION_CONFLICT"

    # 4. Verify network in database was NOT overwritten
    current = NetworkService.get_network(db_session, net_id)
    assert current.name == "Updated by Process B"
    assert current.version == 2

    # 5. Process A refreshes, sees version 2, and updates with expected_version=2 -> Succeeds
    update_a_fresh = NetworkUpdate(name="Resolved by Process A", expected_version=2)
    final_net = NetworkService.update_network(db_session, net_id, update_a_fresh)
    assert final_net.version == 3
    assert final_net.name == "Resolved by Process A"


def test_standardized_error_response_schema():
    """
    Verify that all application exceptions produce the exact standard schema:
    {"error": {"code": str, "message": str, "details": Any}}
    """
    exceptions_to_test = [
        (NetworkNotFoundError("Network not found"), 404, "NETWORK_NOT_FOUND"),
        (NodeNotFoundError("Node missing"), 404, "NODE_NOT_FOUND"),
        (EdgeNotFoundError("Edge missing"), 404, "EDGE_NOT_FOUND"),
        (SimulationNotFoundError("Sim missing"), 404, "SIMULATION_NOT_FOUND"),
        (NetworkVersionConflictError("Version stale"), 409, "VERSION_CONFLICT"),
        (DuplicateEntityError("Duplicate device"), 409, "DUPLICATE_ENTITY"),
        (BadRequestError("Malformed syntax"), 400, "BAD_REQUEST"),
        (PayloadTooLargeError("File too large"), 413, "PAYLOAD_TOO_LARGE"),
        (DatabaseUnavailableError("DB down"), 503, "DATABASE_UNAVAILABLE"),
    ]

    for exc, expected_status, expected_code in exceptions_to_test:
        assert exc.status_code == expected_status
        assert exc.error_code == expected_code
        error_dict = exc.to_dict()

        assert "error" in error_dict
        err = error_dict["error"]
        assert "code" in err
        assert "message" in err
        assert "details" in err
        assert err["code"] == expected_code
        assert err["message"] == exc.message


def test_security_payload_size_validation():
    """Verify security guardrails on upload payload size."""
    # Under limit passes
    validate_payload_size(b"x" * 1024)

    # Exceeding 10MB limit raises PayloadTooLargeError
    with pytest.raises(PayloadTooLargeError):
        validate_payload_size(b"x" * (11 * 1024 * 1024))


def test_security_file_extension_validation():
    """Verify security guardrails on allowed import file formats."""
    # Allowed extensions
    assert validate_file_format("topology.json") == "json"
    assert validate_file_format("network_data.csv") == "csv"

    # Disallowed extensions
    with pytest.raises(BadRequestError):
        validate_file_format("malicious.exe")
    with pytest.raises(BadRequestError):
        validate_file_format("script.py")


def test_security_graph_order_and_size_validation():
    """Verify graph complexity limiters (|V| <= 10000, |E| <= 50000)."""
    # Acceptable order
    validate_network_size(node_count=100, edge_count=200)

    # Exceeding max nodes
    with pytest.raises(BadRequestError):
        validate_network_size(node_count=15000, edge_count=100)

    # Exceeding max edges
    with pytest.raises(BadRequestError):
        validate_network_size(node_count=100, edge_count=60000)
