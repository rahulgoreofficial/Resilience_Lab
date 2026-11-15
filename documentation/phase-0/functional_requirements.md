# Phase 0: Functional Requirements Specification
## Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator

---

### 1. Introduction and Traceability

This document details the functional capabilities of the **Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator**. Every requirement is uniquely numbered, prioritized according to the MoSCoW framework, and explicitly linked to underlying discrete mathematical constructs and user interaction workflows.

---

### 2. User Roles and Interaction Scenarios

#### 2.1 User Roles
1. **Student / Learner**: Explores discrete mathematics and network architecture concepts, creates custom topologies, triggers failure scenarios, observes visual graph transformations, and examines degradation curves.
2. **Faculty Instructor / Evaluator**: Loads canonical benchmark topologies, evaluates student submissions, verifies algorithmic correctness of cut-vertices and bridges, and demonstrates percolation and cascade theory in lectures.
3. **Network Architecture Analyst**: Imports enterprise network topologies via JSON, runs batch stress-tests, evaluates structural single points of failure, and reviews algorithmic redundancy recommendations to optimize network connectivity.

#### 2.2 Key User Interaction Stories
- **Story 1 (SPOF Discovery)**: *As a Network Architecture Analyst, I want to upload a proposed campus network JSON file and instantly see all routers, switches, and firewalls that act as articulation points highlighted in pulsing red, so that I can eliminate single points of failure prior to purchasing hardware.*
- **Story 2 (Interactive Failure & Rerouting)**: *As a Student, I want to click on a core distribution router on the canvas to disable it, so that I can immediately see which servers become disconnected and whether an alternate communication path exists between my workstation and the database.*
- **Story 3 (Comparative Stress-Testing)**: *As a Faculty Instructor, I want to execute an automated stress-test comparing random node failures against targeted attacks on high-degree hubs, so that I can visually demonstrate to my class why scale-free network topologies are resilient to random accidents but highly vulnerable to deliberate attacks.*
- **Story 4 (Cascading Failure Demonstration)**: *As a Learner, I want to set a capacity tolerance parameter ($\alpha = 0.2$), trigger the failure of a high-betweenness router, and step through the resulting cascade iteration by iteration, so that I can understand how traffic load diversion triggers secondary overloads.*
- **Story 5 (Redundancy Recommendation)**: *As a Network Designer, I want the system to suggest the minimum number of new communication links needed to make my network 2-vertex-connected, so that no single node failure can partition the infrastructure.*

---

### 3. Detailed Functional Requirements

#### 3.1 Module 1: Network Topology Modeling & Graph Ingestion
- **FR-01: Graph Data Model Representation**
  - *Priority*: Must Have
  - *Description*: The system shall model network topologies as an attributed graph $G = (V, E)$, supporting directed and undirected configurations. Vertices shall support attributes: `id` (unique string), `label`, `device_type`, `capacity` (float), and optional `metadata` (JSON). Edges shall support `source`, `target`, `weight` (latency/distance), `bandwidth` (Gbps), and `status` (`UP`/`DOWN`).
  - *Input*: Graph initialization payload.
  - *Output*: In-memory graph structure in NetworkX and SQLAlchemy entity.

- **FR-02: Device Archetype Classification**
  - *Priority*: Must Have
  - *Description*: The system shall strictly enforce classification of nodes into 6 discrete network device archetypes: `ROUTER`, `SWITCH`, `SERVER`, `DATABASE_SERVER`, `FIREWALL`, `GATEWAY`.
  - *Validation*: Rejects any node creation payload containing an unrecognized archetype.

- **FR-03: JSON Topology Import & Schema Validation**
  - *Priority*: Must Have
  - *Description*: The system shall import network topologies defined in JSON format, validating the file against a strict Pydantic v2 schema.
  - *Validation*: If an edge references a non-existent node ID, or if duplicate node IDs exist, the system shall reject the upload with an explicit HTTP 422 error and descriptive error message.

- **FR-04: Interactive Visual Graph Construction**
  - *Priority*: Must Have
  - *Description*: The system shall provide an interactive GUI canvas (via Cytoscape.js) allowing users to add nodes, select device types, connect nodes with links, edit node/link properties, and delete components directly via mouse interactions.

- **FR-05: Pre-configured Benchmark Topology Library**
  - *Priority*: Must Have
  - *Description*: The system shall provide a built-in library of at least 6 canonical benchmark network topologies:
    1. Simple Linear Tree (high vulnerability).
    2. Centralized Star (extreme single point of failure).
    3. Token Ring (2-regular, single failure resilience).
    4. Enterprise 3-Tier (Core, Distribution, Access hierarchical architecture).
    5. Data Center Spine-Leaf / Clos (high biconnectivity).
    6. ARPANET Historic Topology (irregular mesh).

#### 3.2 Module 2: Graph Traversal & Structural Vulnerability Analysis
- **FR-06: Connected Components & Partitioning Analysis**
  - *Priority*: Must Have
  - *Description*: The system shall implement BFS and DFS algorithms to decompose the graph into its maximal connected components, computing the number of connected components $\kappa(G)$, the node roster of each component, and the size of the Giant Connected Component (GCC).
  - *Complexity*: $O(|V| + |E|)$.

- **FR-07: Tarjan's Articulation Point (Cut-Vertex) Detection**
  - *Priority*: Must Have
  - *Description*: The system shall implement Tarjan's linear-time DFS algorithm to identify every articulation point (node whose removal strictly increases the number of connected components).
  - *Mathematical Condition*: Root with $\ge 2$ children, or non-root $u$ with child $v$ such that $\text{low}[v] \ge d[u]$.
  - *Output*: List of articulation point node IDs, each annotated with the count of nodes isolated upon its failure.

- **FR-08: Tarjan's Bridge (Cut-Edge) Detection**
  - *Priority*: Must Have
  - *Description*: The system shall implement Tarjan's linear-time DFS algorithm to identify all bridges (edges whose removal increases $\kappa(G)$).
  - *Mathematical Condition*: Edge $(u, v)$ such that $\text{low}[v] > d[u]$.
  - *Output*: List of bridge edges `(source, target)`.

- **FR-09: Pairwise Reachability & Shortest Path Query**
  - *Priority*: Must Have
  - *Description*: The system shall allow users to select any source node $s$ and destination node $t$ to compute:
    1. Reachability status (boolean).
    2. Primary shortest path (sequence of nodes and edges) via Dijkstra or BFS.
    3. Alternate disjoint paths (if redundant paths exist).

- **FR-10: Multi-Metric Centrality Computation**
  - *Priority*: Should Have
  - *Description*: The system shall compute degree centrality ($C_D$), betweenness centrality ($C_B$ via Brandes' algorithm), and closeness centrality ($C_C$) for all active nodes in the network, ranking nodes in tabular and visual formats.

- **FR-11: Spectral Robustness (Algebraic Connectivity)**
  - *Priority*: Should Have
  - *Description*: The system shall construct the graph Laplacian matrix $L = D - A$ and compute its eigenvalues using NumPy. The second-smallest eigenvalue (Fiedler value $\lambda_2$) shall be displayed as the algebraic connectivity metric.

- **FR-12: Global Network Efficiency Computation**
  - *Priority*: Should Have
  - *Description*: The system shall compute Latora-Marchiori Global Efficiency:
    $$E_{\text{glob}}(G) = \frac{1}{n(n-1)} \sum_{u \neq v} \frac{1}{d(u,v)}$$
    guaranteeing mathematically valid outputs even when the graph is disconnected ($d(u, v) = \infty \implies 1/d(u,v) = 0$).

#### 3.3 Module 3: Failure Simulation Engine
- **FR-13: Interactive Manual Component Knockout**
  - *Priority*: Must Have
  - *Description*: The system shall allow the user to click any node or link to toggle its status between `UP` and `DOWN`. The system shall immediately recalculate and visually reflect the residual induced subgraph $G'$, highlighting isolated subnets and orphaned servers.

- **FR-14: Batch Multiple-Failure Injection ($N-k$ Contingency)**
  - *Priority*: Should Have
  - *Description*: The system shall allow users to select a set of $k$ nodes or links to fail simultaneously, computing the resulting partition vector and metric drop.

- **FR-15: Automated Random Failure Simulation (Percolation)**
  - *Priority*: Should Have
  - *Description*: The system shall simulate uniform random node failure over fractions $f \in [0, 1]$ (step size $\Delta f = 0.05$). The simulation shall run $K = 20$ Monte Carlo trials, computing mean and standard deviation for Giant Component fraction $S(f)$ and efficiency $E(f)$.

- **FR-16: Automated Targeted Attack Simulation**
  - *Priority*: Should Have
  - *Description*: The system shall simulate deliberate targeted attacks by sequentially removing nodes in descending order of:
    1. Degree Centrality (high-degree hub attack).
    2. Initial Betweenness Centrality (chokepoint attack).
    3. Dynamically Re-calculated Betweenness Centrality.
  - *Output*: Comparative degradation curves plotted alongside random failure results.

- **FR-17: Dynamic Cascading Failure Simulation (Motter-Lai Model)**
  - *Priority*: Should Have
  - *Description*: The system shall simulate load-dependent cascading failures based on betweenness centrality:
    1. Assign initial load $L_i(0) = C_B(i)$ and capacity $C_i = (1 + \alpha) L_i(0)$, where $\alpha \ge 0$ is a user-configurable tolerance parameter.
    2. Upon initial node failure, recalculate shortest paths and loads $L_i(t)$ on surviving nodes.
    3. Mark any node with $L_i(t) > C_i$ as failed due to overload.
    4. Repeat iteratively until steady-state equilibrium or total collapse is reached.
  - *Output*: Detailed step-by-step event log of newly overloaded nodes per iteration.

#### 3.4 Module 4: Resilience Analytics, Redundancy & Persistence
- **FR-18: Real-Time Resilience Dashboard & Degradation Plots**
  - *Priority*: Should Have
  - *Description*: The system shall render interactive dual-axis charts (via Recharts) displaying $S(f)$ and $E(f)$ as functions of node removal fraction $f$, with toggleable series for Random vs. Targeted attacks.

- **FR-19: Percolation Threshold ($f_c$) Calculation**
  - *Priority*: Should Have
  - *Description*: The system shall compute and display the critical failure threshold $f_c$ (the point at which the giant connected component disintegrates, defined as $S(f) < 0.1$).

- **FR-20: Algorithmic Redundancy Link Recommender**
  - *Priority*: Could Have
  - *Description*: The system shall analyze biconnected components and suggest up to 3 candidate edges whose addition would:
    1. Eliminate the maximum number of articulation points and bridges.
    2. Maximize the gain in algebraic connectivity $\Delta \lambda_2$ and global efficiency $\Delta E_{\text{glob}}$.
  - *Output*: Ranked list of proposed edges with projected metric improvements.

- **FR-21: Topology & Experiment Persistence**
  - *Priority*: Could Have
  - *Description*: The system shall persist user-created topologies, failure scenarios, and simulation logs in a PostgreSQL database using SQLAlchemy ORM, allowing users to save, rename, reload, and delete simulation sessions.

- **FR-22: Comprehensive Audit Report Export**
  - *Priority*: Could Have
  - *Description*: The system shall export a complete resilience audit report containing topology summary, identified SPOFs, centrality tables, and simulation degradation curves in JSON and printable HTML/PDF formats.

---

### 4. Requirements Traceability Matrix

| Requirement ID | Module | Primary Mathematical Concept | Target Phase |
| :--- | :--- | :--- | :--- |
| **FR-01 to FR-05** | Graph Modeling & Presets | Graph representation $G=(V,E)$, attributes | Phase 1 |
| **FR-06 to FR-09** | Traversal & SPOF Engine | BFS/DFS, Tarjan $\text{low}[u]$, Shortest Path | Phase 1 |
| **FR-10 to FR-12** | Centrality & Spectral | Brandes betweenness, Laplacian spectrum, Efficiency | Phase 2 |
| **FR-13 to FR-14** | Interactive Manual Knockout | Subgraphs $G[V \setminus V_{\text{failed}}]$, dynamic reachability | Phase 2 |
| **FR-15 to FR-16** | Automated Percolation Tests | Random vs. Targeted percolation, $S(f)$ curves | Phase 2 |
| **FR-17** | Cascading Failure Engine | Motter-Lai load-capacity thresholds | Phase 3 |
| **FR-18 to FR-19** | Visualization & Dashboard | Recharts plots, Cytoscape styles, $f_c$ threshold | Phase 3 |
| **FR-20** | Redundancy Optimization | 2-connectivity augmentation heuristic | Phase 4 |
| **FR-21 to FR-22** | Persistence & Reporting | PostgreSQL relational storage, JSON/PDF export | Phase 4 |

