# Phase 5: Failure Simulation Engine Design

## 1. Architectural Overview & Design Philosophy

The Failure Simulation Engine provides an isolated, dynamic sandbox for evaluating how computer and communication network topologies degrade under physical component disruptions.

A critical design requirement is **absolute baseline immutability**:
$$\forall \text{ Simulation } S, \quad G_{\text{baseline}} \equiv \text{unmodified}, \quad G_{\text{active}} \subset G_{\text{baseline}}$$

Every simulation executes on an isolated memory snapshot of the network graph $G = (V, E)$, ensuring that repeated user simulations, concurrent requests, or erroneous failure parameters cannot corrupt the underlying network model.

```
                      +-----------------------------+
                      |   Baseline Network Graph    |
                      |          G = (V, E)         |
                      +--------------+--------------+
                                     |
                                     | .clone() / Isolated Snapshot
                                     v
                      +-----------------------------+
                      |     Simulation Graph        |
                      |       G_sim = (V', E')      |
                      +--------------+--------------+
                                     |
           +-------------------------+-------------------------+
           |                         |                         |
           v                         v                         v
+---------------------+   +---------------------+   +---------------------+
| Node Failure Engine |   | Edge Failure Engine |   | Multiple Component  |
|      v in V         |   |      e in E         |   | Failure Engine      |
+----------+----------+   +----------+----------+   +----------+----------+
           |                         |                         |
           +-------------------------+-------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |  Simulation Registry        |
                      |  & Chronological Event Log  |
                      +-----------------------------+
```

---

## 2. Core Modules in `backend/app/simulation/`

### 2.1 `simulation_state.py`
Defines standardized data models and execution statuses:
* **`SimulationStatus`**: Enum (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`).
* **`SimulationType`**: Enum (`NODE_FAILURE`, `EDGE_FAILURE`, `MULTIPLE_FAILURE`, `RANDOM_FAILURE`, `TARGETED_FAILURE`, `CASCADING_FAILURE`).
* **`SimulationEvent`**: Chronological event entry with ISO-8601 UTC timestamp and structured payload.
* **`SimulationResult`**: Serialized response containing baseline counts, active counts, failed roster, connected component partition $V / R$, unreachable nodes, and resilience metrics.

### 2.2 `simulation_utils.py`
Provides foundational snapshotting and combinatorial counting:
* **`create_isolated_graph_snapshot(graph)`**: Performs deep graph duplication.
* **`hash_graph_topology(graph)`**: Computes deterministic SHA-256 fingerprint for snapshot auditability.
* **`calculate_combination_count(n, k)`**: Binomial coefficient $C(n, k) = \frac{n!}{k!(n-k)!}$.

### 2.3 `node_failure.py`
Implements dynamic vertex elimination:
1. Input validation: Asserts $\forall v \in V_{\text{failed}}, v \in V(G)$.
2. Incident edge cascading: Removing $v$ automatically purges all incident communication links $\{ (u, v) \in E \}$.
3. Topological recalculation: Decomposes active graph into connected components via BFS $O(V + E)$.
4. Ingress reachability: Traces paths from configured entry points to critical services.

### 2.4 `edge_failure.py`
Implements communication link severance:
1. Endpoint resolution: Supports explicit edge IDs or undirected $(u, v)$ endpoint pairs.
2. Link removal: Deletes $\{u, v\}$ from edge table and incident sets.
3. Alternative route discovery: For each disabled link $e = \{u, v\}$, executes Dijkstra shortest path on active snapshot to check if an alternative detour exists.

### 2.5 `multiple_failure.py`
Simulates simultaneous multi-element disruptions:
* Calculates cumulative non-additive impact on a single snapshot.
* Computes discrete scenario space cardinality:
  $$\Omega = \binom{|V|}{k_{\text{nodes}}} \times \binom{|E|}{k_{\text{edges}}}$$

### 2.6 `simulation_registry.py` & `simulation_manager.py`
Thread-safe execution repository managing simulation lifecycles, historical retrieval by UUID, and WebSocket progress event dispatching.

