# Phase 2: Folder Structure & Repository Organization
## Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator

---

### 1. Repository Directory Tree

The project follows a clean, modular repository organization strictly conforming to the Phase 2 specification:

```
c:\DM\CP\
│
├── backend/                               # Python Backend Application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                        # FastAPI entry point & API route handlers
│   │   │
│   │   ├── core/                          # Configuration & Settings
│   │   │   ├── __init__.py
│   │   │   └── config.py                  # Pydantic Settings & environment variables
│   │   │
│   │   ├── graph_engine/                  # Pure Graph Engine Core
│   │   │   ├── __init__.py
│   │   │   ├── graph_model.py             # Node and Edge mathematical data classes
│   │   │   ├── graph_validation.py        # Custom exceptions and attribute validators
│   │   │   ├── graph_builder.py           # NetworkGraph 13 core graph operations
│   │   │   └── graph_representation.py   # Adjacency Matrix & Adjacency List generators
│   │   │
│   │   ├── algorithms/                    # Core Discrete Mathematics Graph Algorithms
│   │   │   ├── __init__.py
│   │   │   ├── bfs.py                     # Breadth-First Search traversal O(V+E)
│   │   │   ├── dfs.py                     # Iterative Depth-First Search O(V+E)
│   │   │   ├── connected_components.py    # Reachability equivalence classes O(V+E)
│   │   │   ├── degree_analysis.py         # Degrees & Euler Handshaking Lemma check
│   │   │   ├── articulation_points.py     # Tarjan Low-Link Cut-Vertex Detection O(V+E)
│   │   │   ├── bridges.py                 # Tarjan Low-Link Cut-Edge Detection O(V+E)
│   │   │   └── shortest_path.py           # Dijkstra Min-Heap Shortest Path O((V+E) log V)
│   │   │
│   │   ├── schemas/                       # Pydantic v2 Request/Response Schemas
│   │   │   ├── __init__.py
│   │   │   └── graph_schema.py            # API data models
│   │   │
│   │   └── database/                      # Persistence Layer
│   │       ├── __init__.py
│   │       ├── session.py                 # Non-blocking SQLAlchemy session manager
│   │       └── models.py                  # Topology SQLAlchemy ORM models
│   │
│   ├── tests/                             # Comprehensive Automated Unit Test Suite
│   │   ├── conftest.py                    # Reusable pytest fixtures (K1, P5, S5, C5, K5)
│   │   ├── test_graph_builder.py          # 11 tests: creation, mutation, deletion, JSON I/O
│   │   ├── test_graph_validation.py       # 11 tests: constraint checks, self-loops, duplicates
│   │   ├── test_graph_representation.py   # 7 tests: matrix symmetry, list isomorphism
│   │   ├── test_bfs.py                    # 5 tests: BFS ordering, distances, NetworkX check
│   │   ├── test_dfs.py                    # 5 tests: DFS order, cycles, NetworkX check
│   │   ├── test_connected_components.py   # 5 tests: partition disjointness, components
│   │   ├── test_degree_analysis.py        # 5 tests: Handshaking Lemma, regular graphs
│   │   ├── test_articulation_points.py    # 5 tests: Tarjan SPOFs, cut-vertex theorem
│   │   ├── test_bridges.py                # 4 tests: Tarjan bridges, cut-edge theorem
│   │   ├── test_shortest_path.py          # 5 tests: Dijkstra relaxation, unreachable pairs
│   │   └── test_api_endpoints.py          # 4 tests: health, version, db, and algorithm routes
│   │
│   ├── requirements.txt                   # Production and testing Python dependencies
│   ├── .env.example                       # Environment configuration template
│   └── Dockerfile                         # Container definition for Python backend
│
├── frontend/                              # React 19 + TypeScript Frontend Application
│   ├── src/
│   │   ├── components/                    # Reusable UI components
│   │   ├── pages/                         # View containers
│   │   ├── services/                      # Axios REST API client (api.ts)
│   │   ├── types/                         # TypeScript interfaces
│   │   ├── visualization/                 # Cytoscape graph canvas wrappers
│   │   ├── App.tsx                        # Master application shell & navigation
│   │   ├── main.tsx                       # React DOM entry point
│   │   └── index.css                      # Tailwind CSS v4 directives
│   │
│   ├── package.json                       # Node dependencies & build scripts
│   ├── vite.config.ts                     # Vite + Tailwind + Proxy configuration
│   └── index.html                         # Single-page application root HTML
│
├── datasets/                              # Benchmark Topologies
│   └── sample_network.json                # Calibrated 18-node, 18-link enterprise benchmark
│
├── documentation/                         # Project Documentation
│   ├── phase-0/                           # Planning, Architecture & Requirements (10 docs)
│   ├── phase-1/                           # Mathematical Foundations & Algorithms (9 docs)
│   ├── phase-2/                           # Environment Setup & Tooling (4 docs)
│   ├── phase-3/                           # Graph Engine Design & Models (3 docs)
│   └── phase-4/                           # Algorithm Specs, Complexity & Test Logs (3 docs)
│
├── docker-compose.yml                     # Multi-service composition (Postgres + Backend)
├── .gitignore                             # Git ignore rules for Python, Node, and IDEs
├── PROJECT_CHARTER.md                     # Executive project charter
├── MATHEMATICAL_DESIGN.md                 # Master mathematical design document
└── README.md                              # Master project overview & quickstart
```

