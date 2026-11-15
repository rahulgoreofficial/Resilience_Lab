# RESILIENCE LAB — Developer & Architectural Guide

**Project:** Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator  
**Target Audience:** Core Contributors, Backend Engineers, Frontend Developers, Algorithm Researchers  

---

## 1. Architectural Philosophy & Design Principles

RESILIENCE LAB is built according to strict software engineering standards:
1. **Separation of Concerns:** Business logic, algorithmic graph computation, data persistence, and API transport are completely decoupled.
2. **First-Principles Graph Computations:** The core graph engine (`backend/app/graph_engine/`) and algorithms (`backend/app/algorithms/`) operate on pure Python data structures without external graph framework dependencies.
3. **Graph Snapshot Immutability:** Simulations must never mutate active in-memory or database topologies. All failure operations deep-clone the graph via `create_isolated_graph_snapshot`.
4. **Zero-Mock Policy:** All API endpoints, resilience metrics, and dynamic mutation experiments execute real mathematical computations against actual database state.
5. **Deterministic Invariant Validation:** Any new graph algorithm must be verified by formal mathematical invariants and cross-validated against NetworkX reference implementations.

---

## 2. Directory Structure & Component Organization

```
backend/
├── app/
│   ├── algorithms/          # Pure graph algorithms (BFS, DFS, Tarjan, Dijkstra)
│   ├── api/                 # FastAPI REST and WebSocket endpoints
│   ├── core/                # Configuration, logging, security, custom exceptions
│   ├── database/            # SQLAlchemy session management and engine init
│   ├── graph_engine/        # NetworkGraph, Node, Edge, Validation classes
│   ├── models/              # SQLAlchemy 2.0 ORM database models
│   ├── repositories/        # Repository pattern for database access & version locks
│   ├── resilience/          # Resilience metrics, LCC, NPC, criticality ranking
│   ├── schemas/             # Pydantic v2 data transfer schemas
│   ├── services/            # Transactional business logic coordination
│   ├── simulation/          # Motter-Lai, Monte Carlo, and Attack engines
│   └── websockets/          # WebSocket connection manager and event broadcasters
└── tests/                   # 152 automated pytest test cases
```

---

## 3. How to Implement a New Graph Algorithm

To illustrate the development flow, follow this step-by-step guide to implement a new graph algorithm (e.g., **Biconnected Components** or **K-Core Decomposition**):

### Step 1: Implement the Algorithm from First Principles
Create `backend/app/algorithms/k_core.py`:
```python
from typing import Dict, Set, List
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_model import Node

def compute_k_core(graph: NetworkGraph, k: int) -> Dict[str, Any]:
    """
    Computes the k-core of graph G by iteratively pruning vertices with degree < k.
    Complexity: O(|V| + |E|)
    """
    # Create isolated degree tracking
    degrees = {nid: len(graph.get_neighbors(nid)) for nid in graph.get_node_ids()}
    active_nodes = set(graph.get_node_ids())
    
    changed = True
    while changed:
        changed = False
        to_remove = [nid for nid in active_nodes if degrees[nid] < k]
        for nid in to_remove:
            active_nodes.remove(nid)
            changed = True
            for neighbor in graph.get_neighbors(nid):
                if neighbor in active_nodes:
                    degrees[neighbor] -= 1

    return {
        "k": k,
        "core_nodes": sorted(list(active_nodes)),
        "core_size": len(active_nodes)
    }
```

### Step 2: Add Pytest Unit & Invariant Tests
Create `backend/tests/test_k_core.py`:
- Test empty graphs ($|V|=0$) and singletons ($|V|=1$).
- Test complete graph $K_n$ (all nodes have degree $n-1$, so $k$-core for $k \le n-1$ is the entire graph).
- Verify parity against `networkx.k_core(nx_graph, k=k)`.

### Step 3: Wire into the Service Layer & API Endpoint
1. Expose the method in `backend/app/services/network_service.py`.
2. Add a route in `backend/app/api/endpoints/analysis.py`.
3. Verify through Swagger UI at `http://localhost:8000/api/v1/docs`.

---

## 4. How to Implement a New Failure Simulation Mode

1. **Define Schema:** Add request and response schemas in `backend/app/schemas/simulation.py`.
2. **Implement Logic:** Create `backend/app/simulation/my_failure_mode.py`.
   - Always call `snapshot = create_isolated_graph_snapshot(graph)`.
   - Perform failure modifications strictly on `snapshot`.
   - Calculate post-failure metrics using `calculate_lcc_ratio` and `calculate_pairwise_connectivity`.
   - Record simulation events in `SimulationEvent` log.
3. **Register:** Add the simulation type to `SimulationType` enum in `backend/app/simulation/simulation_state.py`.
4. **Expose:** Add router endpoint in `backend/app/api/endpoints/simulations.py`.

---

## 5. Database Schema & Migration Guidelines

- **ORM Engine:** SQLAlchemy 2.0 with declarative base in `backend/app/database/base.py`.
- **Foreign Key Constraints:** Foreign keys are strictly enforced. When running on SQLite, PRAGMA foreign keys are enabled via connection listeners in `backend/app/database/session.py`.
- **Optimistic Concurrency Locking:** Any modification to `Network` or its child entities must check `network.version` and increment upon successful commit.

---

## 6. Frontend Development Workflow

The frontend is a Vite-powered React 19 single-page application using TypeScript and Tailwind CSS:
```bash
cd frontend
npm run dev        # Starts hot-reloading dev server on http://localhost:5173
npm run lint       # Runs Oxlint for high-speed TypeScript analysis
npm run build      # Produces optimized production bundle in dist/
```

### Cytoscape Integration:
The canvas controller resides in `frontend/src/components/NetworkCanvas.tsx`:
- Node styling dynamically updates based on analytical metadata (`is_articulation_point`, `is_failed`, `is_on_shortest_path`).
- Layout recalculations run on web workers to prevent UI thread blocking.

---

## 7. Testing Standards & CI Validation

Always execute the complete test suite before committing code:
```bash
# Sandboxed pytest run:
backend/venv/Scripts/pytest backend/tests/ -v

# Verification of invariant tests:
backend/venv/Scripts/pytest backend/tests/test_mathematical_invariants.py -v
```
All pull requests must maintain a **100% test pass rate** with zero regression failures.

