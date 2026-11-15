# Phase 5: Failure Simulation REST API Reference

## 1. Overview

The Failure Simulation API exposes endpoints for simulating single, multiple, and combined component disruptions on arbitrary user-provided network graphs.

---

## 2. API Endpoints

### 2.1 Node Failure Simulation
* **Method & Path**: `POST /api/simulations/node-failure`
* **Content-Type**: `application/json`

#### Request Payload
```json
{
  "graph": {
    "name": "Datacenter_Core",
    "directed": false,
    "multigraph": false,
    "nodes": [
      {"node_id": "GW1", "node_type": "gateway", "capacity": 100.0, "current_load": 10.0},
      {"node_id": "R1", "node_type": "router", "capacity": 50.0, "current_load": 5.0},
      {"node_id": "DB1", "node_type": "database", "capacity": 100.0, "current_load": 20.0}
    ],
    "edges": [
      {"edge_id": "e1", "source": "GW1", "target": "R1", "weight": 1.0, "capacity": 40.0},
      {"edge_id": "e2", "source": "R1", "target": "DB1", "weight": 1.5, "capacity": 40.0}
    ]
  },
  "failed_node_ids": ["R1"],
  "entry_points": ["GW1"],
  "critical_services": ["DB1"]
}
```

#### Response (200 OK)
```json
{
  "simulation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "simulation_type": "NODE_FAILURE",
  "status": "COMPLETED",
  "network_hash": "a1b2c3d4e5f67890",
  "start_time": "2026-11-02T07:30:00.000Z",
  "end_time": "2026-11-02T07:30:00.045Z",
  "failed_nodes": ["R1"],
  "failed_edges": ["e1", "e2"],
  "active_node_count": 2,
  "active_edge_count": 0,
  "connected_components": [["DB1"], ["GW1"]],
  "connected_component_count": 2,
  "giant_component": ["DB1"],
  "giant_component_size": 1,
  "isolated_nodes": ["DB1", "GW1"],
  "reachable_nodes": ["GW1"],
  "unreachable_nodes": ["DB1", "R1"],
  "affected_critical_services": ["DB1"],
  "reachable_critical_services": [],
  "metrics": {
    "lcc_ratio": 0.5,
    "service_availability_status": "CONFIGURED",
    "failed_node_count": 1,
    "failed_edge_count": 2
  },
  "events": [
    {"event": "simulation_started", "timestamp": "2026-11-02T07:30:00.000Z"},
    {"event": "node_failed", "node_id": "R1", "incident_edges_disconnected": ["e1", "e2"]},
    {"event": "connectivity_recalculated", "component_count": 2},
    {"event": "simulation_completed", "status": "COMPLETED"}
  ]
}
```

---

### 2.2 Edge Failure Simulation
* **Method & Path**: `POST /api/simulations/edge-failure`
* **Request**:
```json
{
  "graph": { ... },
  "failed_edges": ["e1"],
  "entry_points": ["GW1"],
  "critical_services": ["DB1"]
}
```
* **Response Details**: Includes `metrics.alternative_routes` reporting detour path existence and cost inflation.

---

### 2.3 Multiple Failure Simulation
* **Method & Path**: `POST /api/simulations/multiple-failure`
* **Request**: Accepts combinations of `failed_node_ids` and `failed_edges`.
* **Response**: Reports exact cumulative topology disruption and combinatorial space metrics:
```json
{
  "metrics": {
    "combinatorics": {
      "n_vertices": 18,
      "k_node_failures": 2,
      "vertex_combinations_C_n_k": 153,
      "n_edges": 18,
      "k_edge_failures": 1,
      "edge_combinations_C_n_k": 18,
      "scenario_space_size": 2754
    }
  }
}
```

---

### 2.4 Simulation Retrieval Endpoints
* `GET /api/simulations`: Lists metadata of all registered simulations.
* `GET /api/simulations/{simulation_id}`: Retrieves complete simulation snapshot by UUID.
* `GET /api/simulations/{simulation_id}/results`: Compact summary of topology and metrics.
* `GET /api/simulations/{simulation_id}/events`: Chronological execution log.

