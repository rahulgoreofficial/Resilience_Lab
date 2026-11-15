# RESILIENCE LAB — REST & WebSocket API Reference

**API Specification Version:** v1.0.0  
**Base URL:** `http://localhost:8000/api/v1`  
**WebSocket URL:** `ws://localhost:8000/api/v1/ws`  
**Interactive Swagger UI:** `http://localhost:8000/api/v1/docs`  
**ReDoc Documentation:** `http://localhost:8000/api/v1/redoc`  

---

## 1. Overview & Response Conventions

All REST endpoints adhere to JSON standards with uniform status codes and structured error handling.

### Standard Success Response:
```json
{
  "status": "success",
  "data": { ... }
}
```

### Standard Error Response:
```json
{
  "error": {
    "code": "ENTITY_NOT_FOUND",
    "message": "Network with ID 'net_123' does not exist.",
    "details": null
  }
}
```

| HTTP Status Code | Meaning |
|---|---|
| `200 OK` | Request succeeded; response payload contains requested entity. |
| `201 Created` | Entity was successfully created. |
| `204 No Content` | Action succeeded with zero return body (e.g., successful deletion). |
| `400 Bad Request` | Client validation failure (e.g. self-loop edge, negative weight). |
| `404 Not Found` | Requested network, node, or edge ID does not exist. |
| `409 Conflict` | Optimistic concurrency conflict or duplicate identifier. |
| `500 Server Error`| Internal unhandled error (intercepted by centralized handler). |

---

## 2. System Health & Metadata Endpoints

### 2.1 Get System Health
```http
GET /api/v1/health
```
**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "project": "RESILIENCE LAB"
}
```

### 2.2 Get Database Health
```http
GET /api/v1/database-health
```
**Response (200 OK):**
```json
{
  "database": "connected",
  "engine": "sqlite",
  "active_networks": 3
}
```

---

## 3. Networks API (`/networks`)

### 3.1 List Networks
```http
GET /api/v1/networks?skip=0&limit=20
```
**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "e8a93940-21a4-4a25-8622-48f886f77839",
      "name": "Enterprise Tier-3 Datacenter",
      "description": "High-availability datacenter topology...",
      "network_type": "enterprise",
      "node_count": 12,
      "edge_count": 20,
      "version": 1,
      "created_at": "2026-11-02T09:30:00Z"
    }
  ],
  "total": 3
}
```

### 3.2 Create Network
```http
POST /api/v1/networks
Content-Type: application/json

{
  "name": "Metro Distribution Ring",
  "description": "Redundant ring topology with cross chords",
  "network_type": "campus",
  "nodes": [
    { "node_id": "r1", "node_type": "router", "capacity": 500.0, "importance": 0.8 },
    { "node_id": "r2", "node_type": "router", "capacity": 500.0, "importance": 0.8 }
  ],
  "edges": [
    { "edge_id": "e_r1_r2", "source": "r1", "target": "r2", "weight": 1.0, "bandwidth": 1000.0 }
  ]
}
```
**Response (201 Created):** Full `NetworkResponse` schema including generated UUID.

### 3.3 Get Network Topology (Cytoscape Format)
```http
GET /api/v1/networks/{network_id}/topology
```
**Response (200 OK):**
```json
{
  "network_id": "e8a93940-21a4-4a25-8622-48f886f77839",
  "elements": {
    "nodes": [
      {
        "data": {
          "id": "gw_core_1",
          "label": "gw_core_1",
          "type": "gateway",
          "capacity": 1000.0,
          "load": 150.0,
          "importance": 1.0
        }
      }
    ],
    "edges": [
      {
        "data": {
          "id": "e_gw1_gw2",
          "source": "gw_core_1",
          "target": "gw_core_2",
          "weight": 1.0,
          "bandwidth": 10000.0
        }
      }
    ]
  }
}
```

---

## 4. Graph Analysis & Vulnerability Endpoints

### 4.1 Degree Analysis & Euler's Handshaking Lemma
```http
GET /api/v1/networks/{network_id}/analysis/degrees
```
**Response (200 OK):**
```json
{
  "degrees": {
    "gw_core_1": 4,
    "gw_core_2": 4,
    "fw_edge_1": 3
  },
  "min_degree": 2,
  "max_degree": 4,
  "avg_degree": 3.33,
  "degree_sum": 40,
  "edge_count": 20,
  "handshaking_lemma_verified": true
}
```

### 4.2 Tarjan's Articulation Points (Cut-Vertices)
```http
GET /api/v1/networks/{network_id}/analysis/articulation-points
```
**Response (200 OK):**
```json
{
  "articulation_points": ["sw_access_1", "r_dist_2"],
  "count": 2,
  "discovery_times": { "gw_core_1": 1, "r_dist_1": 2 },
  "low_links": { "gw_core_1": 1, "r_dist_1": 1 }
}
```

### 4.3 Tarjan's Bridges (Cut-Edges)
```http
GET /api/v1/networks/{network_id}/analysis/bridges
```
**Response (200 OK):**
```json
{
  "bridges": [
    ["r_dist_1", "sw_access_1"],
    ["sw_access_2", "srv_app_2"]
  ],
  "count": 2
}
```

### 4.4 Dijkstra Shortest Path Calculation
```http
POST /api/v1/networks/{network_id}/analysis/shortest-path
Content-Type: application/json

{
  "source": "gw_core_1",
  "target": "srv_db_primary",
  "weight_attribute": "weight"
}
```
**Response (200 OK):**
```json
{
  "source": "gw_core_1",
  "target": "srv_db_primary",
  "distance": 3.5,
  "path": ["gw_core_1", "fw_edge_1", "r_dist_1", "srv_app_1", "srv_db_primary"],
  "hop_count": 4
}
```

---

## 5. Failure Simulation Engine Endpoints

### 5.1 Single / Multi-Node Failure
```http
POST /api/v1/simulations/node-failure
Content-Type: application/json

{
  "network_id": "e8a93940-21a4-4a25-8622-48f886f77839",
  "failed_node_ids": ["gw_core_1", "r_dist_1"]
}
```
**Response (200 OK):**
```json
{
  "simulation_id": "7fa12c6a-4952-4467-bc5b-486950ee0b44",
  "simulation_type": "NODE_FAILURE",
  "initial_nodes_count": 12,
  "active_nodes_count": 10,
  "failed_nodes": ["gw_core_1", "r_dist_1"],
  "connected_component_count": 2,
  "isolated_nodes_count": 0,
  "metrics": {
    "lcc_size": 9,
    "lcc_ratio": 0.75,
    "pairwise_connectivity": 0.612,
    "fragmentation_index": 0.388
  }
}
```

### 5.2 Link Severance
```http
POST /api/v1/simulations/edge-failure
Content-Type: application/json

{
  "network_id": "e8a93940-21a4-4a25-8622-48f886f77839",
  "failed_edge_id": "e_gw1_gw2"
}
```

### 5.3 Monte Carlo Stochastic Random Failure
```http
POST /api/v1/simulations/random-failure
Content-Type: application/json

{
  "network_id": "e8a93940-21a4-4a25-8622-48f886f77839",
  "failure_count": 3,
  "num_trials": 10,
  "random_seed": 42
}
```
**Response (200 OK):** Returns mean, median, min, max, and standard deviation of LCC retention across all trials.

### 5.4 Adversarial Targeted Attack
```http
POST /api/v1/simulations/targeted-attack
Content-Type: application/json

{
  "network_id": "e8a93940-21a4-4a25-8622-48f886f77839",
  "strategy": "DEGREE",
  "failure_percentage": 25.0,
  "adaptive": true
}
```
**Response (200 OK):** Returns step-by-step percolation degradation curve.

### 5.5 Motter-Lai Cascading Overload Simulation
```http
POST /api/v1/simulations/cascading-failure
Content-Type: application/json

{
  "network_id": "e8a93940-21a4-4a25-8622-48f886f77839",
  "initial_failed_nodes": ["r_dist_1"],
  "overload_threshold": 1.1,
  "max_simulation_rounds": 6
}
```
**Response (200 OK):**
```json
{
  "simulation_id": "casc_8921e491",
  "cascade_rounds": 3,
  "is_stabilized": true,
  "total_failed_nodes": 4,
  "failed_nodes_timeline": [
    { "round": 0, "failed_nodes": ["r_dist_1"], "reason": "Initial Trigger" },
    { "round": 1, "failed_nodes": ["r_dist_2"], "reason": "Capacity Overload (128%)" },
    { "round": 2, "failed_nodes": ["sw_access_1", "sw_access_2"], "reason": "Cascading Overload" }
  ],
  "final_metrics": {
    "lcc_ratio": 0.583,
    "pairwise_connectivity": 0.450
  }
}
```

---

## 6. WebSocket Live Simulation Telemetry

```http
ws://localhost:8000/api/v1/simulations/ws/{simulation_id}
```
Clients subscribe to receive synchronous discrete round updates during cascading simulations.

**Frame Payload:**
```json
{
  "event": "ROUND_COMPLETED",
  "simulation_id": "casc_8921e491",
  "round": 2,
  "overloaded_nodes": ["sw_access_1", "sw_access_2"],
  "current_lcc_ratio": 0.583,
  "active_node_count": 8
}
```

