# Phase 8: REST API Reference & Endpoint Specifications

## 1. Overview & Prefix Conventions

All Phase 8 endpoints are organized under the versioned prefix `/api/v1`. The system also maintains legacy compatibility routes under `/api` for Phase 2-7 mathematical algorithms.

All requests accept and return `Content-Type: application/json`. Error responses follow the unified envelope:
```json
{
  "error": {
    "code": "STRING_ERROR_CODE",
    "message": "Human readable explanation.",
    "details": null
  }
}
```

---

## 2. Health & System Endpoints

### `GET /api/v1/health`
Returns system status, active version, and project metadata.
- **Status**: `200 OK`
- **Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "project": "Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator"
}
```

### `GET /api/v1/health/db`
Reports persistent database connectivity status and dialect.
- **Status**: `200 OK`
- **Response**:
```json
{
  "status": "healthy",
  "database": "infrastructure_resilience",
  "host": "localhost",
  "port": 5432,
  "dialect": "postgresql"
}
```

---

## 3. Persistent Network Endpoints (`/api/v1/networks`)

### `POST /api/v1/networks`
Creates a new persistent network infrastructure.
- **Status**: `201 Created`
- **Request Body**:
```json
{
  "name": "Enterprise Campus Backbone",
  "description": "Multi-tier core distribution access network",
  "network_type": "COMMUNICATION_NETWORK",
  "metadata": {"location": "Building A"}
}
```
- **Response**: `NetworkResponse` with `id` (UUIDv4), `version: 1`, `node_count: 0`, `edge_count: 0`.

### `GET /api/v1/networks`
Lists stored networks with offset/limit pagination.
- **Query Params**: `skip=0`, `limit=50`
- **Status**: `200 OK`
- **Response**: `PaginatedResponse[NetworkResponse]` (`items`, `total`, `skip`, `limit`).

### `GET /api/v1/networks/{network_id}`
Retrieves a single network summary by UUID.
- **Status**: `200 OK` (or `404 Not Found` if missing).

### `PUT /api/v1/networks/{network_id}`
Updates network attributes with optimistic concurrency control.
- **Request Body**:
```json
{
  "name": "Updated Backbone Name",
  "description": "Updated topology notes",
  "expected_version": 1
}
```
- **Status**: `200 OK` (increments `version` to 2), or `409 Conflict` (`VERSION_CONFLICT`) if `expected_version` mismatches.

### `DELETE /api/v1/networks/{network_id}`
Deletes network and cascades to all its nodes, edges, snapshots, simulations, and events.
- **Status**: `204 No Content`.

### `GET /api/v1/networks/{network_id}/topology`
Exports network graph in **Cytoscape.js** compatible element format for interactive canvas rendering.
- **Status**: `200 OK`
- **Response Structure**:
```json
{
  "network_id": "...",
  "name": "...",
  "version": 1,
  "elements": {
    "nodes": [
      {
        "data": {
          "id": "R1",
          "label": "R1",
          "node_type": "router",
          "importance": 1.0,
          "capacity": 100.0,
          "current_load": 0.0,
          "failure_probability": 0.01,
          "is_critical": false
        }
      }
    ],
    "edges": [
      {
        "data": {
          "id": "e_r1_s1",
          "source": "R1",
          "target": "S1",
          "weight": 1.0,
          "latency": 2.0,
          "capacity": 10.0,
          "reliability": 0.99
        }
      }
    ]
  }
}
```

### `GET /api/v1/networks/{network_id}/export`
Exports network to standard JSON topology format.
- **Status**: `200 OK`.

### `POST /api/v1/networks/import`
Imports a network from JSON/CSV graph structure and creates a persistent network record.
- **Status**: `201 Created`.

---

## 4. Node Management Endpoints (`/api/v1/networks/{id}/nodes`)

### `POST /api/v1/networks/{network_id}/nodes`
Adds a new device vertex to the network.
- **Status**: `201 Created`
- **Request Body**:
```json
{
  "node_id": "CR1",
  "node_type": "router",
  "importance": 2.5,
  "capacity": 500.0,
  "current_load": 30.0,
  "failure_probability": 0.01,
  "is_critical": true,
  "metadata": {"vendor": "Cisco"}
}
```

### `GET /api/v1/networks/{network_id}/nodes`
Lists all component vertices in the network.
- **Status**: `200 OK`.

### `GET /api/v1/networks/{network_id}/nodes/{node_id}`
Retrieves details of a specific device vertex.
- **Status**: `200 OK` (or `404 Not Found`).

### `PUT /api/v1/networks/{network_id}/nodes/{node_id}`
Updates device specifications, operational load, or criticality status.
- **Status**: `200 OK`.

### `DELETE /api/v1/networks/{network_id}/nodes/{node_id}`
Removes the node and cascade-deletes all incident edges. Increments network version.
- **Status**: `204 No Content`.

---

## 5. Edge Management Endpoints (`/api/v1/networks/{id}/edges`)

### `POST /api/v1/networks/{network_id}/edges`
Adds a bidirectional communication link between two existing nodes.
- **Status**: `201 Created`
- **Request Body**:
```json
{
  "edge_id": "e_r1_r2",
  "source_node_id": "R1",
  "target_node_id": "R2",
  "weight": 1.5,
  "latency": 3.0,
  "capacity": 50.0,
  "reliability": 0.999
}
```

### `GET /api/v1/networks/{network_id}/edges`
Lists all communication links.
- **Status**: `200 OK`.

### `DELETE /api/v1/networks/{network_id}/edges/{edge_id}`
Deletes communication link and increments network version.
- **Status**: `204 No Content`.

---

## 6. Simulation & History Endpoints (`/api/v1/simulations`)

All simulation triggers execute the mathematical engines against an immutable point-in-time topology snapshot and record their results and events in the database.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/simulations/node-failure` | Simulates component vertex failure and evaluates reachability. |
| `POST` | `/api/v1/simulations/edge-failure` | Simulates link severance and calculates alternative detour routes. |
| `POST` | `/api/v1/simulations/multiple-failure` | Simulates simultaneous node and edge failure combinations. |
| `POST` | `/api/v1/simulations/random` | Executes stochastic percolation failure trials with fixed seed. |
| `POST` | `/api/v1/simulations/targeted` | Adversarial attacks targeting hubs, articulation points, or impact. |
| `POST` | `/api/v1/simulations/cascading` | Simulates dynamic traffic redistribution and overload cascades. |
| `GET` | `/api/v1/simulations` | Lists historical simulations with optional `?network_id=` filter. |
| `GET` | `/api/v1/networks/{id}/simulations` | Lists all simulation runs executed on a given network. |
| `GET` | `/api/v1/simulations/{id}` | Retrieves full simulation record, status, and configuration. |
| `GET` | `/api/v1/simulations/{id}/results` | Retrieves computed resilience metrics from simulation output. |
| `GET` | `/api/v1/simulations/{id}/events` | Retrieves chronological event sequence log ($1, 2, \dots$). |

---

## 7. Analytics Endpoints (`/api/v1/networks/{id}/analytics`)

Performs deep discrete mathematical graph evaluations on persistent networks:

- `POST /api/v1/networks/{id}/analysis`: Comprehensive connectivity analysis ($|V|$, $|E|$, density, degree distribution, connected components).
- `POST /api/v1/networks/{id}/criticality`: Node and edge criticality ranking based on articulation points, bridge scores, and degree centrality.
- `POST /api/v1/networks/{id}/connectivity`: Component decomposition, bridge enumeration, and cut-vertex detection.
- `POST /api/v1/networks/{id}/resilience`: Computes Largest Connected Component (LCC) ratio, Pairwise Connectivity Ratio, and Service Resilience Scores.
- `POST /api/v1/networks/{id}/comparisons`: Comparative resilience evaluation across different failure scenarios.
- `POST /api/v1/networks/{id}/report`: Compiles an exhaustive, formatted Markdown resilience audit report ready for export.

