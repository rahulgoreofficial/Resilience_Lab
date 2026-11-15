# RESILIENCE LAB — Network Resilience Analysis & Infrastructure Design Platform

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.162-teal.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.3-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-7.0-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-8.3-646cff.svg)](https://vitejs.dev/)
[![Tests Passing](https://img.shields.io/badge/Tests-157%2F157%20Passed-brightgreen.svg)]()

> **"An interactive network resilience analysis and infrastructure design platform that helps engineers model network topology, identify critical components, simulate hypothetical disruptions and evaluate network improvements through mathematical analysis."**

Developed as an advanced second-year Computer Engineering course project for **Discrete Mathematics**, applying classical graph theory, connectivity decomposition, and percolation dynamics to real-world communication infrastructure.

---

## Key Platform Capabilities & Engineering Use Cases

### 1. Primary Demonstration: 12-Node Campus IT Infrastructure
The platform features an editable canonical college campus network topology calibrated to demonstrate structural vulnerabilities:
- **12 Attributed Vertices**:
  - `G1` — Perimeter Internet Gateway (Ingress)
  - `R1` — Campus Edge Router
  - `C1` — Central Core Switch
  - `L1` — Academic Laboratory Switch
  - `LS1` — Laboratory Compute Server (Critical Service)
  - `B1` — Digital Library Switch
  - `LS2` — Library Repository Server (Critical Service)
  - `A1` — Administration Subnet Switch
  - `AS1` — Administrative Records Server (Critical Service)
  - `D1` — Campus Data Center Switch
  - `LMS` — Learning Management System Server (Critical Service)
  - `DB1` — Central Database Server
- **11 Transmission Links**: `G1-R1`, `R1-C1`, `C1-L1`, `L1-LS1`, `C1-B1`, `B1-LS2`, `C1-A1`, `A1-AS1`, `C1-D1`, `D1-LMS`, `LMS-DB1`.
- **Tree Topology Determinism**: Because $|E| = |V| - 1$ and the graph is connected, all 11 edges act as structural bridges.

### 2. Guided Disruption Walkthrough: "Campus Laboratory Connectivity Failure"
An end-to-end live simulation tracing how a single transmission bridge disruption impacts systemic reachability:
- **Step A — Baseline**: Verifies 1 connected component, 100% Giant Component ratio (LCC = 1.0), 100% Pairwise Connectivity, and 4 of 4 critical services reachable from `G1`.
- **Step B — Identify Vulnerability**: Tarjan's algorithm highlights `C1-L1` as a bridge. The laboratory branch $\{L1, LS1\}$ possesses zero alternative routes.
- **Step C — Simulate Failure**: Link `C1-L1` is severed on an isolated snapshot.
  - Splits into 2 components: $\{L1, LS1\}$ (size 2) and main campus (size 10).
  - LCC drops to **83.33%** ($10/12$).
  - Pairwise Connectivity drops to **69.70%** ($92/132$).
  - Critical Service Reachability drops to **75.0%** (`LS1` is severed).
- **Step D — Network Hardening**: User inspects and confirms candidate backup trunk `L1-B1` (connecting Laboratory and Library switches).
- **Step E — Repeat Identical Failure**: Re-simulating `C1-L1` severance on the hardened graph preserves **1 connected component**, **100% LCC**, **100% Pairwise Connectivity**, and **100% Service Reachability**.
- **Step F — Comparison & Alternative Routing**: Proves alternative path dynamic rerouting: `G1 → R1 → C1 → B1 → L1 → LS1`.

### 3. Resilience Design Studio
A dedicated engineering studio (`/design-studio`) supporting:
- **Isolated Working Copies**: Changes occur initially in a local draft copy (`draftNetwork`), preserving the database snapshot until explicitly saved.
- **Topology Editing**: Add/remove backup connections, edit capacity, latency, and node importance.
- **Automated Candidate-Link Evaluator**: Ranks non-existent edges $(u, v) \notin E$ by resilience gain ($\Delta\text{LCC}$, $\Delta\text{Pairwise}$, eliminated bridges) and cost-benefit ratio.
- **Side-by-Side Disruption Tester**: Simulates link failures on both baseline and working copy concurrently, outputting live comparative charts.

### 4. Controlled Cascading Failure Demonstration
A controlled 5-node scenario illustrating dynamic load redistribution and capacity-based cascade collapse:
- Nodes: Client Workstation (`CL1`), Primary Router (`PR1`), Backup Router (`BR1`), Core Switch (`CS1`), Server (`SRV_APP`).
- Parameters: Client traffic demand = 300 Mbps; `PR1` capacity = 500, background load = 100; `BR1` capacity = 350, background load = 100.
- Propagation: Failing `PR1` reroutes 300 Mbps onto `BR1`. In Round 2, `BR1` total load ($100 + 300 = 400$) exceeds its 350 capacity, triggering a secondary overload failure and disconnecting `SRV_APP`.

### 5. Faculty Demonstration Mode
A 10-step presenter-controlled walkthrough designed for clear academic presentation:
1. Campus network introduction.
2. Network topology analysis ($G = (V, E)$).
3. Critical bridge identification (Tarjan's algorithm).
4. Communication-link failure.
5. Affected service analysis.
6. Backup-link creation (cycle formation).
7. Repeated failure under hardening.
8. Before/after mathematical comparison.
9. Cascading failure demonstration.
10. Mathematical conclusion (Whitney's Theorem and percolation guarantees).

### 6. Engineering Deployment Disclaimer
> **Real-World Engineering Caveats:** Mathematical resilience gain on an abstract graph does not automatically imply physical feasibility. Production enterprise deployment requires configuring 802.1Q VLAN trunking, Rapid Spanning Tree Protocol (RSTP / IEEE 802.1w) to avoid broadcast loops, verifying physical fiber/Cat6 conduit pathways between buildings, and firewall policy synchronization.

---

## Architectural Highlights Across Phases

### Phase 2, 3 & 4: Core Engine & Graph Algorithms
- **Pure Mathematical Graph Engine**: Vertex-attributed and edge-attributed undirected simple graph representation $G = (V, E, \alpha, \beta)$ supporting 6 network device archetypes (`router`, `switch`, `server`, `database`, `firewall`, `gateway`).
- **Graph Representations**: Dual representation supporting binary symmetric **Adjacency Matrices** (NumPy array export) and **Adjacency Lists** with deterministic node ordering.
- **Linear-Time SPOF Detection**: Tarjan's Articulation Point Algorithm and Tarjan's Bridge Detection Algorithm in $\Theta(V + E)$ using DFS low-link values.
- **Core Traversals & Paths**: Breadth-First Search (BFS), Depth-First Search (DFS), Connected Components decomposition $V / \mathcal{R}$, Euler Handshaking Lemma check $\sum \deg(v) = 2|E|$, and Dijkstra Shortest Path in $O((V+E) \log V)$.

### Phase 5: Dynamic Failure Simulation Engine
- **Baseline Immutability**: Every simulation operates on an isolated snapshot; the original network is never mutated.
- **Dynamic Node Failure**: Systematic elimination of vertices $v \in V$ with automated incident edge cascading.
- **Dynamic Edge Failure**: Severance of communication links $e \in E$ with automated alternative detour path discovery.
- **Multiple Simultaneous Failures**: Exact cumulative topology disruption calculation without additive approximation.
- **Discrete Combinatorics**: Calculates scenario space cardinality $C(|V|, k_{\text{nodes}}) \times C(|E|, k_{\text{edges}})$.
- **Chronological Event Tracking**: Microsecond-accurate ISO-8601 timeline logging every simulation event.

### Phase 6: Resilience Analysis Engine
- **Largest Connected Component (LCC) Ratio**: $\frac{|V_{\text{giant}}|}{|V_{\text{active}}|}$.
- **Pairwise Connectivity**: Combinatorial metric measuring the fraction of reachable vertex pairs:
  $$\text{Pairwise Connectivity} = \frac{\sum_{i=1}^k \binom{|C_i|}{2}}{\binom{|V_{\text{active}}|}{2}}$$
- **Service Resilience Score ($R$)**: Ingress-to-service reachability ratio $R = \frac{|S_{\text{post}}|}{|S_{\text{baseline}}|}$ and importance-weighted $R_{\text{weighted}}$.
- **Empirical Criticality Profiling**: Quantitative node and edge ranking evaluating measured $\Delta \text{Pairwise Connectivity}$ and Tarjan SPOF classifications.
- **Scenario Comparison**: Side-by-side delta metrics comparing competing failure hypotheses against baseline.
- **Resilience Audit Report**: Automated executive structural health audit and mitigation recommendations.

### Phase 7: Advanced Failure Simulation Engine
- **Stochastic Random Percolation**: Uniform or probability-weighted Monte Carlo trials ($M \le 500$) with deterministic PRNG seeds, reporting mean, median, min, max, and standard deviation.
- **Adversarial Targeted Attacks**: Degree-based (hub), Articulation-point-based (cut-vertex), and Impact-based attacks with adaptive recalculation and deterministic tie-breaking.
- **Cascading Overload Simulation**: Capacity-based traffic redistribution model (Motter-Lai formulation) routing traffic demands $D = \{(s, t, A)\}$ via Dijkstra shortest paths, computing node and edge overloads, and executing synchronous propagation rounds.
- **Live Progress Updates**: WebSocket channel at `/ws/simulations/{simulation_id}` for streaming round-by-round events.

### Phase 8: Professional Backend Architecture & Database Persistence
- **Clean Layered Architecture**: Decoupled presentation (`api/v1/`), service orchestration (`services/`), data access (`repositories/`), and typed ORM persistence (`models/`, `database/`).
- **Normalized PostgreSQL 3NF Schema**: 6 core relational tables (`networks`, `nodes`, `edges`, `network_snapshots`, `simulations`, `simulation_events`) with strict check constraints and cascade deletes.
- **Alembic Database Migrations**: Version-controlled migration management with automated upgrade/downgrade verification (`alembic upgrade head`).
- **Optimistic Concurrency Control (OCC)**: Version-tracked network updates detecting concurrent edit conflicts (HTTP 409 `VERSION_CONFLICT`).
- **Snapshot Immutability Guarantee**: Simulations execute against frozen topology snapshots identified by deterministic SHA-256 fingerprints, ensuring historical results remain 100% reproducible.
- **Crash Recovery Routine**: Automatic startup scanner (`recover_interrupted_simulations`) cleanly transitioning in-flight interrupted runs to safe terminal states.
- **Standardized Error Envelope**: Centralized exception mapping producing uniform `{"error": {"code": "...", "message": "...", "details": ...}}` JSON schemas.
- **Zero-Dependency Local Fallback**: Dynamic engine switching to local SQLite with full `PRAGMA foreign_keys=ON` parity when PostgreSQL is offline or sandboxed.

---

## Technology Stack

- **Backend**: Python 3.12, FastAPI, Uvicorn, NetworkX, NumPy, Pandas, Pydantic v2, SQLAlchemy, PostgreSQL, Pytest.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Cytoscape.js, Recharts, Axios, Lucide Icons.
- **DevOps**: Docker, Docker Compose, Git.

---

## Quickstart Guide

### 1. Backend Setup & Tests
```powershell
# Navigate to backend and activate virtual environment
cd backend
venv\Scripts\Activate.ps1

# Apply Alembic database migrations
$env:PYTHONPATH='.'
alembic upgrade head

# Run the automated Pytest suite (142 tests, 100% passing in ~0.7s)
pytest -v

# Start the FastAPI development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI Documentation: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

### 2. Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install packages
npm install

# Start Vite development server
npm run dev

# Build production bundle
npm run build
```
Access Frontend Dashboard: [http://localhost:5173](http://localhost:5173)

---

## Complete API Surface

### Phase 8 Versioned REST API (`/api/v1`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service liveness & version verification |
| `GET` | `/api/v1/health/db` | Database health & active dialect |
| `POST` | `/api/v1/networks` | Create persistent network infrastructure |
| `GET` | `/api/v1/networks` | Paginated listing of stored networks |
| `GET` | `/api/v1/networks/{id}` | Retrieve network summary and counts |
| `PUT` | `/api/v1/networks/{id}` | Update network with optimistic concurrency (`version` check) |
| `DELETE` | `/api/v1/networks/{id}` | Cascade delete network, nodes, edges, snapshots & simulations |
| `GET` | `/api/v1/networks/{id}/topology` | Export Cytoscape.js compatible graph canvas elements |
| `GET` | `/api/v1/networks/{id}/export` | Export network topology to standard JSON format |
| `POST` | `/api/v1/networks/import` | Import and validate network from JSON/CSV graph data |
| `POST` | `/api/v1/networks/{id}/nodes` | Add vertex component ($v \in V$) with physical constraints |
| `GET` | `/api/v1/networks/{id}/nodes` | List all component vertices in network |
| `GET` | `/api/v1/networks/{id}/nodes/{node_id}` | Retrieve specific component vertex details |
| `PUT` | `/api/v1/networks/{id}/nodes/{node_id}` | Update vertex specifications & load |
| `DELETE` | `/api/v1/networks/{id}/nodes/{node_id}` | Delete node and automatically cascade delete incident edges |
| `POST` | `/api/v1/networks/{id}/edges` | Add communication link with canonical undirected ordering |
| `GET` | `/api/v1/networks/{id}/edges` | List communication links in network |
| `GET` | `/api/v1/networks/{id}/edges/{edge_id}` | Retrieve specific communication link details |
| `PUT` | `/api/v1/networks/{id}/edges/{edge_id}` | Update link capacity, weight, or latency |
| `DELETE` | `/api/v1/networks/{id}/edges/{edge_id}` | Delete communication link |
| `POST` | `/api/v1/simulations/node-failure` | Execute node failure against frozen topology snapshot |
| `POST` | `/api/v1/simulations/edge-failure` | Execute edge severance with alternative path routing |
| `POST` | `/api/v1/simulations/multiple-failure` | Execute simultaneous combination failures |
| `POST` | `/api/v1/simulations/random` | Execute stochastic Monte Carlo percolation trials |
| `POST` | `/api/v1/simulations/targeted` | Execute adversarial targeted attacks (Degree, AP, Impact) |
| `POST` | `/api/v1/simulations/cascading` | Execute capacity-based traffic redistribution cascades |
| `GET` | `/api/v1/simulations` | List historical simulation executions |
| `GET` | `/api/v1/networks/{id}/simulations` | List simulation executions for a specific network |
| `GET` | `/api/v1/simulations/{id}` | Retrieve full simulation record & metadata |
| `GET` | `/api/v1/simulations/{id}/results` | Retrieve computed resilience metrics for simulation |
| `GET` | `/api/v1/simulations/{id}/events` | Retrieve chronological execution event stream ($1..N$) |
| `POST` | `/api/v1/networks/{id}/analysis` | Compute topological connectivity metrics on network |
| `POST` | `/api/v1/networks/{id}/criticality` | Compute node & edge vulnerability rankings on network |
| `POST` | `/api/v1/networks/{id}/connectivity` | Articulation points, bridges, and components decomposition |
| `POST` | `/api/v1/networks/{id}/resilience` | Full resilience evaluation (LCC, Pairwise Connectivity) |
| `POST` | `/api/v1/networks/{id}/comparisons` | Multi-scenario delta matrix comparison |
| `POST` | `/api/v1/networks/{id}/report` | Generate comprehensive executive Markdown audit report |
| `WS` | `/ws/simulations/{id}` | Live simulation execution WebSocket with database replay |

### Legacy Mathematical Algorithms & Ad-Hoc APIs (`/api`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System health status |
| `GET` | `/api/version` | Project version and current phases |
| `GET` | `/api/database-health` | Storage connectivity status |
| `POST` | `/api/graph/representations` | Generate Adjacency Matrix & List |
| `POST` | `/api/algorithms/bfs` | Breadth-First Search traversal |
| `POST` | `/api/algorithms/dfs` | Depth-First Search traversal |
| `POST` | `/api/algorithms/connected-components` | Connected components & giant component |
| `POST` | `/api/algorithms/degree-analysis` | Degree metrics & Handshaking Lemma check |
| `POST` | `/api/algorithms/articulation-points` | Tarjan cut-vertex detection |
| `POST` | `/api/algorithms/bridges` | Tarjan cut-edge detection |
| `POST` | `/api/algorithms/shortest-path` | Dijkstra shortest path |
| `POST` | `/api/simulations/node-failure` | Ad-hoc single/multiple node outages |
| `POST` | `/api/simulations/edge-failure` | Ad-hoc communication link failures |
| `POST` | `/api/simulations/multiple-failure` | Ad-hoc combined failures |
| `POST` | `/api/simulations/random` | Ad-hoc stochastic percolation failure trials |
| `POST` | `/api/simulations/targeted` | Ad-hoc adversarial attacks |
| `POST` | `/api/simulations/cascading` | Ad-hoc cascading traffic redistribution |
| `POST` | `/api/resilience/analyze` | Ad-hoc topological resilience profile |
| `POST` | `/api/resilience/criticality/nodes` | Ad-hoc node criticality ranking |
| `POST` | `/api/resilience/criticality/edges` | Ad-hoc edge criticality ranking |
| `POST` | `/api/resilience/alternative-routes` | Ad-hoc primary vs backup route evaluation |
| `POST` | `/api/resilience/compare-scenarios` | Ad-hoc scenario comparison |
| `POST` | `/api/resilience/report` | Ad-hoc resilience audit report |

---

## Project Structure

```
.
├── backend/                  # FastAPI REST API & Core Simulation Engines
│   ├── alembic/              # Database schema migrations
│   │   ├── versions/         # 001_initial_normalized_schema.py
│   │   └── env.py            # Migration runtime environment
│   ├── app/
│   │   ├── algorithms/       # Pure first-principles graph algorithms (Phases 3-4)
│   │   ├── api/              # Route controllers & API v1 assemble
│   │   │   ├── v1/           # Health, Networks, Nodes, Edges, Simulations, Analytics
│   │   │   └── dependencies.py # Database & pagination dependencies
│   │   ├── core/             # Pydantic Settings, exceptions, logging, security
│   │   ├── database/         # Session pooling, Base, engine fallback, startup recovery
│   │   ├── graph_engine/     # NetworkGraph, Node, Edge, Reachability, Representations
│   │   ├── models/           # SQLAlchemy 2.x Declarative ORM entities (6 tables)
│   │   ├── repositories/     # Data Access Layer & optimistic version checking
│   │   ├── resilience/       # Resilience Analysis Engine (Phase 6)
│   │   ├── schemas/          # Pydantic v2 validation & response DTOs
│   │   ├── services/         # Business logic, Cytoscape export, snapshot generation
│   │   ├── simulation/       # Failure Simulation Engines (Phases 5 & 7)
│   │   ├── websockets/       # WebSocket streaming endpoints
│   │   └── main.py           # Application entrypoint & centralized error handlers
│   └── tests/                # 142 automated unit, integration, and validation tests
├── frontend/                 # React 19 + TypeScript + Vite + Tailwind UI
│   └── src/
│       ├── services/         # Axios API client
│       └── App.tsx           # Dashboard shell & Cytoscape canvas
├── datasets/                 # Calibrated benchmark networks
│   └── sample_network.json   # 18-node, 18-link benchmark topology
├── documentation/            # Academic & engineering documentation (43 documents)
│   ├── phase-0/              # Planning & Requirements (10 documents)
│   ├── phase-1/              # Mathematical Foundations & Syllabus (9 documents)
│   ├── phase-2/              # Environment Setup (4 documents)
│   ├── phase-3/              # Graph Engine Architecture (3 documents)
│   ├── phase-4/              # Algorithm Specifications & Logs (3 documents)
│   ├── phase-5/              # Failure Simulation Engine Specs (3 documents)
│   ├── phase-6/              # Resilience Metrics & Criticality Specs (3 documents)
│   ├── phase-7/              # Advanced Simulation & Testing Dossier (4 documents)
│   └── phase-8/              # Layered Architecture & Database Persistence (11 documents)
├── PROJECT_CHARTER.md        # Executive Project Charter
├── MATHEMATICAL_DESIGN.md    # Master Mathematical Architecture
└── README.md
```
