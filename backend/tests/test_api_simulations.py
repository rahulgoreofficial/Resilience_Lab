"""
Integration Tests for Simulation & Resilience REST API Endpoints.
Verifies all FastAPI route handlers for Phase 5, Phase 6, and Phase 7.
"""

import pytest
from fastapi import HTTPException
from app.main import (
    api_simulate_node_failure,
    api_simulate_edge_failure,
    api_simulate_multiple_failure,
    api_simulate_random_failure,
    api_simulate_targeted_failure,
    api_simulate_cascading_failure,
    api_list_simulations,
    api_get_simulation,
    api_get_simulation_results,
    api_get_simulation_events,
    api_analyze_resilience,
    api_node_criticality,
    api_edge_criticality,
    api_alternative_routes,
    api_compare_scenarios,
    api_generate_report
)
from app.schemas.graph_schema import GraphDataSchema
from app.schemas.simulation_schema import (
    NodeFailureRequest,
    EdgeFailureRequest,
    MultipleFailureRequest,
    RandomFailureRequest,
    TargetedFailureRequest,
    CascadingFailureRequest
)
from app.schemas.resilience_schema import (
    ResilienceAnalysisRequest,
    CriticalityRequest,
    AlternativeRoutesRequest,
    ScenarioComparisonRequest
)


@pytest.fixture
def api_test_graph_payload():
    return GraphDataSchema(
        name="API_Test_Network",
        directed=False,
        multigraph=False,
        nodes=[
            {"node_id": "GW1", "node_type": "gateway", "capacity": 100.0, "current_load": 0.0},
            {"node_id": "R1", "node_type": "router", "capacity": 50.0, "current_load": 0.0},
            {"node_id": "R2", "node_type": "router", "capacity": 15.0, "current_load": 0.0},
            {"node_id": "DB1", "node_type": "database", "capacity": 100.0, "current_load": 0.0}
        ],
        edges=[
            {"edge_id": "e1", "source": "GW1", "target": "R1", "weight": 1.0, "capacity": 50.0},
            {"edge_id": "e2", "source": "R1", "target": "DB1", "weight": 1.0, "capacity": 50.0},
            {"edge_id": "e3", "source": "GW1", "target": "R2", "weight": 2.0, "capacity": 20.0},
            {"edge_id": "e4", "source": "R2", "target": "DB1", "weight": 2.0, "capacity": 20.0}
        ]
    )


# --- Simulation Endpoints ---

def test_api_node_failure(api_test_graph_payload):
    req = NodeFailureRequest(
        graph=api_test_graph_payload,
        failed_node_ids=["R1"],
        entry_points=["GW1"],
        critical_services=["DB1"]
    )
    res = api_simulate_node_failure(req)
    assert res["status"] == "COMPLETED"
    assert res["failed_nodes"] == ["R1"]
    assert "e1" in res["failed_edges"]
    assert "e2" in res["failed_edges"]
    # R2 path remains active, so DB1 is still reachable
    assert "DB1" in res["reachable_critical_services"]


def test_api_node_failure_invalid_node_raises_400(api_test_graph_payload):
    req = NodeFailureRequest(
        graph=api_test_graph_payload,
        failed_node_ids=["UNKNOWN_NODE"]
    )
    with pytest.raises(HTTPException) as exc_info:
        api_simulate_node_failure(req)
    assert exc_info.value.status_code == 400


def test_api_edge_failure(api_test_graph_payload):
    req = EdgeFailureRequest(
        graph=api_test_graph_payload,
        failed_edges=["e1"]
    )
    res = api_simulate_edge_failure(req)
    assert res["status"] == "COMPLETED"
    assert res["failed_edges"] == ["e1"]
    assert "alternative_routes" in res["metrics"]


def test_api_multiple_failure(api_test_graph_payload):
    req = MultipleFailureRequest(
        graph=api_test_graph_payload,
        failed_node_ids=["R1"],
        failed_edges=["e3"]
    )
    res = api_simulate_multiple_failure(req)
    assert res["status"] == "COMPLETED"
    assert "combinatorics" in res["metrics"]


def test_api_random_failure(api_test_graph_payload):
    req = RandomFailureRequest(
        graph=api_test_graph_payload,
        failure_target="NODES",
        failure_count=1,
        num_trials=5,
        random_seed=42
    )
    res = api_simulate_random_failure(req)
    assert res["status"] == "COMPLETED"
    assert "statistics" in res
    assert len(res["trials"]) == 5


def test_api_targeted_failure(api_test_graph_payload):
    req = TargetedFailureRequest(
        graph=api_test_graph_payload,
        strategy="DEGREE",
        failure_count=1
    )
    res = api_simulate_targeted_failure(req)
    assert res["status"] == "COMPLETED"
    assert "degradation_curve" in res


def test_api_cascading_failure(api_test_graph_payload):
    req = CascadingFailureRequest(
        graph=api_test_graph_payload,
        initial_failed_nodes=["R1"],
        traffic_demands=[{"source": "GW1", "destination": "DB1", "amount": 20.0}],
        overload_threshold=1.0,
        max_simulation_rounds=5
    )
    res = api_simulate_cascading_failure(req)
    assert res["status"] == "COMPLETED"
    assert len(res["timeline"]) >= 2

    # Check retrieval endpoints
    sim_id = res["simulation_id"]
    sim_detail = api_get_simulation(sim_id)
    assert sim_detail["simulation_id"] == sim_id

    sim_results = api_get_simulation_results(sim_id)
    assert "metrics" in sim_results

    sim_events = api_get_simulation_events(sim_id)
    assert len(sim_events["events"]) > 0

    all_sims = api_list_simulations(limit=10)
    assert any(s["simulation_id"] == sim_id for s in all_sims)


def test_api_get_simulation_nonexistent_raises_404():
    with pytest.raises(HTTPException) as exc_info:
        api_get_simulation("nonexistent-uuid-1234")
    assert exc_info.value.status_code == 404


# --- Resilience Endpoints ---

def test_api_resilience_analyze(api_test_graph_payload):
    req = ResilienceAnalysisRequest(
        graph=api_test_graph_payload,
        entry_points=["GW1"],
        critical_services=["DB1"]
    )
    res = api_analyze_resilience(req)
    assert res["active_vertices"] == 4
    assert res["pairwise_connectivity"] == 1.0
    assert "DB1" in res["reachable_critical_services"]


def test_api_criticality_nodes_and_edges(api_test_graph_payload):
    req = CriticalityRequest(graph=api_test_graph_payload)
    node_ranks = api_node_criticality(req)
    assert len(node_ranks) == 4
    assert node_ranks[0]["rank"] == 1

    edge_ranks = api_edge_criticality(req)
    assert len(edge_ranks) == 4
    assert edge_ranks[0]["rank"] == 1


def test_api_alternative_routes(api_test_graph_payload):
    req = AlternativeRoutesRequest(
        graph=api_test_graph_payload,
        flow_pairs=[["GW1", "DB1"]],
        failed_edge_ids=["e1"]
    )
    res = api_alternative_routes(req)
    assert len(res) == 1
    assert res[0]["primary_route"] == ["GW1", "R1", "DB1"]
    assert res[0]["alternative_route_available"] is True
    assert res[0]["alternative_route"] == ["GW1", "R2", "DB1"]


def test_api_compare_scenarios(api_test_graph_payload):
    req = ScenarioComparisonRequest(
        graph=api_test_graph_payload,
        scenarios=[
            {"scenario_id": "s1", "name": "Fail R1", "failed_nodes": ["R1"]},
            {"scenario_id": "s2", "name": "Fail R2", "failed_nodes": ["R2"]}
        ]
    )
    res = api_compare_scenarios(req)
    assert "baseline" in res
    assert len(res["scenarios"]) == 2


def test_api_generate_report(api_test_graph_payload):
    req = ResilienceAnalysisRequest(graph=api_test_graph_payload)
    report = api_generate_report(req)
    assert report["network_name"] == "API_Test_Network"
    assert "structural_health_rating" in report
    assert "recommendations" in report

