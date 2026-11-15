# RESILIENCE LAB — Bug, Defect, and Fix Tracking Log

**Document Version:** 1.0.0  
**Phase:** Phase 10 — Quality Assurance & Release Hardening  
**Project:** Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator  
**Status:** All Identified Defects Resolved & Verified  

---

## 1. Defect Classification Scheme

| Severity Level | Definition | SLA / Resolution Priority |
|---|---|---|
| **CRITICAL** | System crash, incorrect mathematical calculation, data corruption, or graph mutation leakage. | Immediate fix required prior to test pass. |
| **HIGH** | Algorithm failure under specific scale/topology, blocking API errors, or unhandled exceptions. | Must be fixed and regression tested. |
| **MEDIUM** | Environment dependency failures (e.g. database driver fallback), performance bottlenecks. | Addressed before release candidate. |
| **LOW** | Minor schema mismatches, deprecation notices, or path warnings. | Polished and standardized. |

---

## 2. Bug & Fix Register

### BUG-001 (CRITICAL): Graph Mutation Leakage During Failure Simulation
- **Severity:** Critical
- **Component:** `backend/app/simulation/simulation_utils.py`, `node_failure.py`, `edge_failure.py`
- **Description:** Early prototype simulation runs directly manipulated node and edge dictionaries within the active in-memory `NetworkGraph` instance. Subsequent simulations or queries reflected severed links and missing nodes, violating network immutability.
- **Root Cause:** Direct reference assignment `active_graph = graph` instead of deep structural cloning of `Node` and `Edge` objects.
- **Fix Implemented:** Created `create_isolated_graph_snapshot(graph: NetworkGraph) -> NetworkGraph` in `simulation_utils.py` that clones every node and edge with fresh metadata, ensuring mathematical operations never mutate the baseline infrastructure.
- **Regression Test:** `backend/tests/test_mathematical_invariants.py::test_original_graph_immutability` explicitly checks node count, edge count, and node status before and after running multi-node failure simulations.

---

### BUG-002 (CRITICAL): Zero-Division and Boundary Invariants in Resilience Metrics
- **Severity:** Critical
- **Component:** `backend/app/resilience/metrics.py`
- **Description:** Calling resilience metrics on empty graphs ($|V|=0$) or singleton graphs ($|V|=1$) caused unhandled `ZeroDivisionError` when computing normalized pairwise connectivity $\frac{2 \sum \binom{s_i}{2}}{|V|(|V|-1)}$.
- **Root Cause:** Denominator $|V|(|V|-1)$ evaluates to $0$ when $|V| \in \{0, 1\}$.
- **Fix Implemented:** Added guard conditions:
  ```python
  if active_nodes_count <= 1:
      return 1.0 if active_nodes_count == 1 else 0.0
  ```
  Similar boundary guards were added for LCC ratio ($0.0$ when $|V|=0$, $1.0$ when $|V|=1$).
- **Regression Test:** `backend/tests/test_mathematical_invariants.py::test_empty_and_singleton_graph_invariants` verifies $|V|=0$ and $|V|=1$ return expected invariants without exception.

---

### BUG-003 (HIGH): Maximum Recursion Depth Exceeded in Tarjan AP/Bridge at Scale
- **Severity:** High
- **Component:** `backend/app/algorithms/articulation_points.py`, `bridges.py`
- **Description:** When analyzing deep topologies with $|V| \ge 2,500$ nodes, Python raised `RecursionError: maximum recursion depth exceeded in comparison` during the Tarjan DFS low-link traversal.
- **Root Cause:** Python default interpreter recursion limit is set to 1,000 stack frames. Deep graphs or linear chains exceed this limit during recursive exploration.
- **Fix Implemented:** Added dynamic recursion limit escalation:
  ```python
  if sys.getrecursionlimit() < 100000:
      try:
          sys.setrecursionlimit(100000)
      except Exception:
          pass
  ```
- **Regression Test:** `tools/run_benchmarks.py` successfully completed Extended scale ($|V|=2,500$, $|E|=4,000$) in $4.498$ ms without recursion exceptions.

---

### BUG-004 (HIGH): Missing Algorithm Parity with NetworkX Benchmark Control
- **Severity:** High
- **Component:** `backend/app/algorithms/`
- **Description:** Risk of algorithmic discrepancies between custom from-scratch graph algorithms and academic gold standards (NetworkX 3.x).
- **Root Cause:** Lack of automated cross-verification against reference libraries.
- **Fix Implemented:** Built formal parity test suites comparing custom Tarjan APs to `nx.articulation_points(nx_g)`, Tarjan Bridges to `nx.bridges(nx_g)`, and Dijkstra shortest paths and weights to `nx.shortest_path(nx_g)`.
- **Regression Test:** `test_mathematical_invariants.py::test_tarjan_articulation_points_parity_with_networkx`, `test_tarjan_bridges_parity_with_networkx`, and `test_dijkstra_shortest_path_parity_with_networkx`.

---

### BUG-005 (MEDIUM): Offline / Standalone Database Permission Denied
- **Severity:** Medium
- **Component:** `backend/app/database/session.py`, `tools/verify_dynamic_behaviour.py`
- **Description:** Standalone CLI tools, verification scripts, and offline development environments failed with `psycopg2.OperationalError: connection to server at 'localhost' (5432) failed: Permission denied` when PostgreSQL service was stopped.
- **Root Cause:** Hardcoded PostgreSQL default in connection strings without automated fallback.
- **Fix Implemented:** Added environment check and automated SQLite fallback:
  ```python
  DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///infrastructure_resilience.db")
  ```
  with `check_same_thread=False` and foreign key PRAGMA enforcement for SQLite.
- **Regression Test:** Verified clean SQLite execution in `tools/verify_dynamic_behaviour.py` and `backend/tests/`.

---

### BUG-006 (MEDIUM): Matplotlib Cache Permission Warnings on Windows
- **Severity:** Medium
- **Component:** `tools/run_benchmarks.py`
- **Description:** Matplotlib issued runtime stderr warnings `Matplotlib created a temporary cache directory at C:\Users\... because there was an issue with the default path`.
- **Root Cause:** User home directory path containing spaces or restricted permissions in enterprise Windows environments.
- **Fix Implemented:** Configured explicit local cache directory:
  ```python
  cache_dir = Path("documentation/phase-10/benchmark_results/.matplotlib_cache")
  cache_dir.mkdir(parents=True, exist_ok=True)
  os.environ["MPLCONFIGDIR"] = str(cache_dir.resolve())
  ```
- **Regression Test:** Benchmark script runs with zero stderr warnings.

---

### BUG-007 (LOW): Inconsistent Key Names in Simulation Return Payloads
- **Severity:** Low
- **Component:** `backend/app/services/simulation_service.py`
- **Description:** Some endpoints referred to post-failure component count as `final_components` while others used `connected_component_count`.
- **Root Cause:** Discrepancy between early prototype models and the Phase 8 standardized `SimulationResult` Pydantic model.
- **Fix Implemented:** Standardized `SimulationResult.to_dict()` and `SimulationService` to canonical schema (`connected_component_count`, `active_nodes_count`, `isolated_nodes_count`). Added backward-compatibility properties.
- **Regression Test:** Verified 152/152 tests passing with uniform schema handling across all endpoints.

---

### BUG-008 (LOW): Method Name Discrepancy in `NetworkGraph.has_edge`
- **Severity:** Low
- **Component:** `backend/app/graph_engine/graph_builder.py`
- **Description:** Calling `graph.has_edge_between(u, v)` caused `AttributeError`.
- **Root Cause:** Canonical method was implemented as `graph.has_edge(source, target)`.
- **Fix Implemented:** Kept `has_edge(source, target)` and added alias `has_edge_between(source, target)` for seamless ergonomics.
- **Regression Test:** Verified in graph builder unit tests and benchmarking scripts.

---

## 3. Summary of Quality Improvements

- **Total Bugs Logged:** 8
- **Critical Fixed:** 2 (100%)
- **High Fixed:** 2 (100%)
- **Medium Fixed:** 2 (100%)
- **Low Fixed:** 2 (100%)
- **Open Defects:** 0
- **Regression Pass Rate:** 100% (152/152 tests passing)

