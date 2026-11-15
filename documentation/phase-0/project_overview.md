# Phase 0: Project Overview & Academic Architecture
## Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator

---

### 1. Project Background and Academic Purpose

In contemporary digital infrastructure, computer and telecommunication networks form the foundational substrate for commerce, governance, healthcare, and industrial control. From campus local area networks (LANs) and enterprise multi-tier data centers to wide area backbones (WANs) and autonomous systems (AS) on the global Internet, connectivity must remain robust against component failures. 

Traditional undergraduate engineering pedagogy often treats **Discrete Mathematics (Graph Theory)** and **Computer Networks** as siloed subjects:
- In Discrete Mathematics, students learn formal definitions of graphs, vertices, edges, paths, cycles, trees, connectivity, cut-vertices (articulation points), cut-edges (bridges), and adjacency matrices, often on small, abstract, toy graphs (5–8 nodes) using pencil and paper.
- In Computer Networks, students learn routing protocols (OSPF, BGP), switching, redundancy mechanisms (Spanning Tree Protocol, link aggregation), and packet telemetry, often viewing network reliability as an empirical or protocol-configuration exercise rather than an applied topological optimization problem.

The **Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator** is engineered specifically to eliminate this pedagogical gap. Developed as an advanced, industry-relevant second-year Computer Engineering course project, this system models communication network infrastructures as formal vertex- and edge-attributed graphs $G = (V, E)$. By leveraging rigorous discrete algorithms (such as Tarjan's linear-time cut-vertex and bridge detection, Breadth-First and Depth-First traversals, and Dijkstra shortest-path evaluations) alongside modern complex-network metrics, the application provides an interactive workbench for students, educators, and network engineers to mathematically inspect and simulate failure modes in computer networks.

---

### 2. Supported Infrastructure Domain & Node Archetypes

To ensure rigorous engineering depth rather than superficial domain breadth, the initial scope deliberately restricts modeling to **computer and communication networks**, avoiding the over-generalization of modeling power grids, water distribution, or transportation networks in Phase 1:

| Device Archetype | Mathematical Role ($v \in V$) | Network Functionality & Attributes | Default Structural Importance |
| :--- | :--- | :--- | :--- |
| **Router** | Inter-subnet routing node, forwarder | High degree ($k_v$), high betweenness centrality; routes traffic between network segments across IP subnets. | Critical transit node |
| **Switch** | Intra-subnet switching node | Aggregation point for servers and edge devices; forms Layer-2 broadcast domains. | Intermediate distribution node |
| **Server** | Compute endpoint / service provider | Application host (e.g., Web, Application, File services); communicates with clients and databases. | Leaf / Endpoint node |
| **Database Server** | Stateful storage endpoint | Core data repository; high inbound traffic; critical sink node in enterprise topologies. | High-value leaf / sink |
| **Firewall** | Security checkpoint / inspection node | Filtering node bridging security zones (e.g., DMZ, Internal LAN, Internet); frequently an articulation point. | Topologically critical chokepoint |
| **Gateway** | Default egress / ingress border node | Boundary router interfacing an autonomous system or enterprise LAN with external networks (WAN/ISP). | Topologically critical ingress/egress |
| **Communication Link** | Undirected / Directed edge ($e \in E$) | Physical or logical transmission channel characterized by bandwidth, latency, and status (Up / Down). | Transmission medium |

---

### 3. Technology Stack Rationale

The technology stack is carefully selected to balance algorithmic expressiveness, computational efficiency, industry relevance, and accessibility for a second-year engineering student:

```
+---------------------------------------------------------------------------------------+
|                                    PRESENTATION LAYER                                 |
|  React 18  |  TypeScript 5  |  Vite  |  Tailwind CSS  |  Cytoscape.js  |  Recharts    |
+---------------------------------------------------------------------------------------+
                                           |
                                [ RESTful JSON / OpenAPI ]
                                           v
+---------------------------------------------------------------------------------------+
|                                  APPLICATION / API LAYER                              |
|                      FastAPI (Python 3.11+)  |  Pydantic v2 Models                    |
+---------------------------------------------------------------------------------------+
                                           |
                                [ Algorithmic Execution ]
                                           v
+---------------------------------------------------------------------------------------+
|                                CORE ANALYTICAL ENGINES                                |
|  NetworkX (Graph Algorithms) | NumPy (Spectral & Matrix) | Pandas (Tabular Metrics)   |
|         Tarjan Cut-Vertex/Bridge Engine | Cascading Load Threshold Engine             |
+---------------------------------------------------------------------------------------+
                                           |
                                [ Persistence & Storage ]
                                           v
+---------------------------------------------------------------------------------------+
|                                   DATA STORAGE LAYER                                  |
|                PostgreSQL 16  |  SQLAlchemy 2.0 ORM  |  Alembic Migrations            |
+---------------------------------------------------------------------------------------+
|                          DEVELOPMENT, TESTING & REPRODUCIBILITY                       |
|                   Docker & Docker Compose  |  Pytest  |  Git / GitHub                 |
+---------------------------------------------------------------------------------------+
```

#### 3.1 Backend & Analytical Core
1. **Python 3.11+**:
   - *Rationale*: Python is the standard language for discrete mathematics, graph theory, and data science research. It offers unparalleled libraries for graph manipulation while maintaining high developer productivity.
2. **FastAPI**:
   - *Rationale*: Modern, high-performance web framework for building REST APIs with Python based on standard type hints. Offers automatic Swagger/OpenAPI documentation generation, asynchronous request handling, and strict schema validation via Pydantic.
3. **NetworkX**:
   - *Rationale*: The premier Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks. It natively implements graph data structures (adjacency dicts), graph traversal (DFS, BFS), shortest-path algorithms, and baseline connectivity metrics.
4. **NumPy & Pandas**:
   - *Rationale*: NumPy enables vectorized algebraic operations, particularly computing the Graph Laplacian ($L = D - A$) and spectral decomposition (Fiedler vector / algebraic connectivity $\lambda_2$). Pandas provides high-speed tabular processing for scenario metrics, failure logs, and degradation curve data series.

#### 3.2 Frontend & Visualization Core
1. **React 18 & TypeScript**:
   - *Rationale*: React offers a declarative, component-based user interface architecture. TypeScript enforces strict static typing across graph payload interfaces (nodes, edges, failure events, metric summaries), preventing runtime type mismatches between backend JSON responses and UI state.
2. **Vite**:
   - *Rationale*: Next-generation frontend tooling offering near-instantaneous Hot Module Replacement (HMR) and optimized Rollup-based production builds.
3. **Tailwind CSS**:
   - *Rationale*: Utility-first CSS framework enabling rapid construction of a clean, responsive, dark-mode-ready engineering dashboard without cumbersome stylesheet bloat.
4. **Cytoscape.js**:
   - *Rationale*: Cytoscape.js is the academic and industry gold standard for interactive graph and network analysis visualizations. It handles complex graph layouts (Cose, Dagre, Concat, BreadthFirst), allows rich dynamic styling (highlighting articulation points in red, bridges in amber, failed nodes in muted grey), supports pan/zoom physics, and performs efficiently on graphs with hundreds of nodes.
5. **Recharts**:
   - *Rationale*: Composable charting library built on React components and D3.js. Used to render degradation curves, comparing Giant Connected Component (GCC) fraction and Global Network Efficiency against the fraction of failed nodes ($f$).

#### 3.3 Persistence, Database & ORM
1. **PostgreSQL**:
   - *Rationale*: Robust, ACID-compliant open-source relational database. Ideal for storing network topology definitions (JSONB graph schemas), pre-configured benchmark networks, historical simulation runs, and user experiment states.
2. **SQLAlchemy 2.0**:
   - *Rationale*: Industry-standard Python SQL toolkit and Object Relational Mapper (ORM), providing clean repository abstractions over database transactions.

#### 3.4 Engineering, Testing & Reproducibility
1. **Pytest**:
   - *Rationale*: Mature testing framework enabling automated unit testing of graph algorithms against canonical mathematical graphs with known ground truths (e.g., cycle graphs, tree topologies, complete graphs).
2. **Docker & Docker Compose**:
   - *Rationale*: Containerizes the backend API, frontend client, and PostgreSQL database into unified, reproducible execution environments, eliminating the "works on my machine" syndrome during faculty evaluation and peer review.
3. **Git & GitHub**:
   - *Rationale*: Version control system maintaining a clean commit history, structured branching workflow (feature branches, pull requests), and issue tracking.

---

### 4. Mathematical Foundations Bridged

The platform explicitly bridges five core mathematical domains from Discrete Mathematics into computer engineering practice:

$$\begin{array}{|l|l|l|}
\hline
\textbf{Discrete Mathematics Concept} & \textbf{Formal Definition / Theorem} & \textbf{Computer Network Practical Equivalent} \\ \hline
\text{Graph Formulation} & G = (V, E), \quad n = |V|, \ m = |E| & \text{Network topology: devices } V \text{ and links } E. \\ \hline
\text{Connected Components} & \text{Maximal connected subgraph } G[V_i] & \text{Isolated network partitions unable to communicate.} \\ \hline
\text{Articulation Point (Cut-Vertex)} & v \in V \text{ such that } \kappa(G - v) > \kappa(G) & \text{Single Point of Failure (SPOF) router/switch/firewall.} \\ \hline
\text{Bridge (Cut-Edge)} & e \in E \text{ such that } \kappa(G - e) > \kappa(G) & \text{Critical transmission line whose cut fragments the LAN.} \\ \hline
\text{Tarjan's DFS Low-link} & \text{Discovery } d[u], \ \text{low}[u] = \min(d[u], d[w], \text{low}[v]) & \text{Linear-time } O(V+E) \text{ SPOF discovery algorithm.} \\ \hline
\text{Path Length \& Diameter} & d(u, v) = \min \text{ path length}; \ D = \max d(u, v) & \text{Hops, latency bounds, and packet delay.} \\ \hline
\text{Global Efficiency} & E_{\text{glob}}(G) = \frac{1}{n(n-1)} \sum_{u \neq v} \frac{1}{d(u,v)} & \text{Harmonic communication ease across disconnected graphs.} \\ \hline
\text{Algebraic Connectivity} & \lambda_2 \text{ of Graph Laplacian } L = D - A & \text{Spectral measure of overall graph robustness and synchrony.} \\ \hline
\text{Percolation / Random Breakdown} & p_c = 1 - \frac{1}{\langle k^2 \rangle / \langle k \rangle - 1} & \text{Random hardware failure tolerance of scale-free topologies.} \\ \hline
\text{Targeted Attack Vulnerability} & \text{Removal by order of degree } k_v \text{ or betweenness } C_B(v) & \text{Targeted cyber-attacks on core routing backbones.} \\ \hline
\end{array}$$

---

### 5. Architectural Principles

1. **Strict Separation of Concerns**: The analytical graph engine is completely decoupled from the web presentation layer. All mathematical computations run deterministically in the backend and expose their results via typed REST APIs.
2. **Deterministic Verification**: Every algorithmic function must be tested against mathematically proven graph theorems with zero empirical tolerance for errors.
3. **Interactive Visual Feedback**: Students and researchers must immediately observe the topological and mathematical consequences of any node or link failure in real time.
4. **Scope Realism**: Focus deeply on topological graph theory and computer network resilience without diluting engineering resources into kernel-level packet emulation or unrelated civil infrastructure domains.

