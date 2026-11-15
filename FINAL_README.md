# RESILIENCE LAB
## Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg)](https://react.dev/)
[![Cytoscape](https://img.shields.io/badge/Cytoscape.js-3.34-E65100.svg)](https://js.cytoscape.org/)
[![Tests](https://img.shields.io/badge/Tests-152%20Passed%20(100%25)-success.svg)](backend/tests/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Executive Overview

**RESILIENCE LAB** is an interactive, mathematically rigorous simulation platform designed to model computer and communication network infrastructure as finite undirected graphs $G=(V, E)$. Developed for a second-year Computer Engineering course in **Discrete Mathematics and Graph Theory**, the project demonstrates how fundamental mathematical theorems solve modern engineering challenges in critical infrastructure protection, cloud datacenter reliability, and telecommunications survivability.

### Key Capabilities:
- **Graph Engine from First Principles:** Custom in-memory adjacency list graph representation with $O(1)$ edge existence checks, duplicate guards, and snapshot immutability.
- **Structural Vulnerability Detection:** Linear-time $O(|V| + |E|)$ identification of **Articulation Points (Cut-Vertices)** and **Bridges (Cut-Edges)** via Tarjan's low-link algorithm.
- **Optimal Routing & Alternatives:** Dijkstra shortest-path calculations via a binary min-heap priority queue ($O((|V|+|E|)\log|V|)$) and redundant path diversity.
- **Multi-Regime Failure Simulation:**
  - Deterministic single and multi-node failure modeling;
  - Physical link severance;
  - Monte Carlo stochastic percolation (random node failures across repeated trials);
  - Adversarial targeted attacks (Degree, Articulation Point, and Multi-Criteria Impact);
  - **Motter-Lai capacity-based cascading overload propagation** across discrete rounds.
- **Objective Resilience Quantification:** Real-time calculation of Largest Connected Component (LCC) retention ratio, Normalized Pairwise Connectivity ($NPC$), network fragmentation index, and composite node criticality rankings.
- **Cybersecurity Control Plane UI:** Professional dark-mode interface built with React 19, TypeScript, Tailwind CSS, and hardware-accelerated Cytoscape.js canvas rendering.
- **Dual Persistence:** Zero-configuration local SQLite 3.39+ with foreign key enforcement and production PostgreSQL 14–16 support via SQLAlchemy 2.0 ORM.
- **One-Click Automation:** Native Windows installers (`Install_Resilience_Lab.bat`) and launchers (`Run_Resilience_Lab.bat`, `Stop_Resilience_Lab.bat`).

---

## 2. Mathematical Rigor & Academic Validation

The platform strictly verifies foundational theorems of Discrete Mathematics:

| Mathematical Concept | Theoretical Complexity | System Verification |
|---|---|---|
| **Euler's Handshaking Lemma** | $\sum_{v \in V} \deg(v) = 2|E|$ | Verified on $K_6$, $S_8$, $C_{10}$, and random graphs up to 2,500 nodes |
| **Adjacency Matrix Symmetry** | $A = A^T$, $\text{diag}(A) = 0$ | Verified across all network topologies |
| **Tarjan's Cut-Vertices** | $O(|V| + |E|)$ | 100% parity against `networkx.articulation_points` |
| **Tarjan's Cut-Edges (Bridges)**| $O(|V| + |E|)$ | 100% parity against `networkx.bridges` |
| **Dijkstra Shortest Path** | $O((|V| + |E|) \log |V|)$ | 100% parity against `networkx.shortest_path` |
| **Motter-Lai Cascades** | $O(R \cdot (|V| + |E|) \log |V|)$ | Discrete overload propagation across synchronous rounds |

---

## 3. Empirical Performance Benchmarks

Measured on standard workstation hardware across 5 distinct topological scales (mean execution latency in milliseconds):

| Operation | Small (20 / 30) | Medium (100 / 150) | Large (500 / 800) | V. Large (1k / 1.5k) | Extended (2.5k / 4k) |
|---|---|---|---|---|---|
| **BFS Traversal** | 0.017 ms | 0.097 ms | 0.482 ms | 0.974 ms | 2.683 ms |
| **DFS Traversal** | 0.018 ms | 0.100 ms | 0.597 ms | 1.302 ms | 3.235 ms |
| **Connected Components** | 0.018 ms | 0.134 ms | 0.566 ms | 1.176 ms | 2.630 ms |
| **Tarjan Cut-Vertices** | 0.026 ms | 0.139 ms | 0.842 ms | 1.523 ms | 4.498 ms |
| **Tarjan Bridges** | 0.023 ms | 0.139 ms | 0.814 ms | 1.840 ms | 4.521 ms |
| **Dijkstra Shortest Path** | 0.032 ms | 0.171 ms | 1.112 ms | 1.823 ms | 2.297 ms |
| **Motter-Lai Cascade** | 0.316 ms | 1.345 ms | 7.160 ms | 12.972 ms | 36.678 ms |

Full charts, CSV datasets, and methodologies are published in [`documentation/phase-10/benchmark_results/`](documentation/phase-10/benchmark_results/).

---

## 4. Quickstart Guide (One-Click Launch)

### Prerequisites:
- **Windows 10 / 11 x64** (or Linux/macOS)
- **Python 3.10+** (added to system PATH)
- **Node.js 18+** & **npm** (added to system PATH)

### One-Click Installation (Windows):
1. Double-click `Install_Resilience_Lab.bat`.
   - Automatically sets up `backend/venv`, installs pip packages, compiles frontend assets, and seeds benchmark topologies.
2. Double-click `Run_Resilience_Lab.bat`.
   - Starts backend and frontend services, verifies health, and opens your browser automatically to `http://localhost:5173`.
3. To stop all services cleanly, double-click `Stop_Resilience_Lab.bat`.

### Manual Cross-Platform Launch:
```bash
# 1. Setup Backend:
python -m venv backend/venv
source backend/venv/bin/activate  # or backend\venv\Scripts\activate on Windows
pip install -r backend/requirements.txt
export PYTHONPATH=backend
python tools/seed_database.py

# 2. Setup Frontend:
cd frontend
npm install
npm run build
cd ..

# 3. Launch via Process Manager:
python tools/launcher.py
```

---

## 5. Repository Architecture

```
CP/
├── backend/                        # FastAPI Backend & Graph Engine
│   ├── app/
│   │   ├── algorithms/             # BFS, DFS, Tarjan AP/Bridges, Dijkstra
│   │   ├── api/                    # v1 REST API Controllers
│   │   ├── database/               # SQLAlchemy Session & Base
│   │   ├── graph_engine/           # NetworkGraph, Node, Edge, Validation
│   │   ├── models/                 # Relational Database Models
│   │   ├── repositories/           # Data Access Layer & Concurrency Locks
│   │   ├── resilience/             # LCC, Pairwise Connectivity, Criticality
│   │   ├── schemas/                # Pydantic v2 Request/Response Contracts
│   │   ├── services/               # Transactional Business Logic
│   │   └── simulation/             # Motter-Lai, Monte Carlo, Attack Engines
│   ├── tests/                      # 152 Automated Pytest Unit & Invariant Tests
│   └── requirements.txt            # Python Dependencies
├── frontend/                       # React 19 + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/             # Cytoscape Canvas, Metrics, Sim Controls
│   │   ├── services/               # Axios API Client & WebSocket Handlers
│   │   └── types/                  # TypeScript Interfaces
│   └── dist/                       # Compiled Production Bundle
├── documentation/
│   ├── final_report/
│   │   ├── PROJECT_REPORT.md       # Master Academic Project Report (Chapters 1-18)
│   │   └── PROJECT_REPORT.pdf      # Publication-Ready Formal Academic PDF
│   └── phase-10/
│       ├── benchmark_results/      # High-Res Charts & Raw Benchmark CSV
│       ├── quality_assurance_report.md
│       ├── bug_and_fix_log.md
│       └── dynamic_behaviour_testing.md
├── tools/
│   ├── launcher.py                 # Multi-Service Application Manager
│   ├── stop_launcher.py            # Process Cleaner & Port Reclaimer
│   ├── run_benchmarks.py           # Empirical Benchmarking Script
│   ├── generate_pdf_report.py      # ReportLab PDF Compiler
│   ├── seed_database.py            # Database Initialization & Seeding
│   └── verify_dynamic_behaviour.py # Live Dynamic Mutation Verifier
├── Install_Resilience_Lab.bat      # Windows One-Click Installer
├── Run_Resilience_Lab.bat          # Windows One-Click Launcher
├── Stop_Resilience_Lab.bat         # Windows One-Click Terminator
├── INSTALLATION_GUIDE.md           # Installation Guide
├── USER_MANUAL.md                  # User Manual
├── API_REFERENCE.md                # OpenAPI REST & WebSocket Documentation
├── DEVELOPER_GUIDE.md              # Engineering Architecture Guide
├── TESTING_REPORT.md               # QA Verification & Invariant Proofs
├── DEPLOYMENT_GUIDE.md             # Production Docker & Cloud Deployment
└── TROUBLESHOOTING.md              # Operational Diagnosis & FAQs
```

---

## 6. Running the Test Suite

```bash
# Execute full backend test suite (152 tests):
backend/venv/Scripts/pytest backend/tests/ -v

# Run mathematical invariant verification:
backend/venv/Scripts/pytest backend/tests/test_mathematical_invariants.py -v

# Run live dynamic database mutation test:
backend/venv/Scripts/python tools/verify_dynamic_behaviour.py
```

---

## 7. Documentation Index

- **Master Academic Project Report (PDF):** [`documentation/final_report/PROJECT_REPORT.pdf`](documentation/final_report/PROJECT_REPORT.pdf)
- **Master Academic Project Report (MD):** [`documentation/final_report/PROJECT_REPORT.md`](documentation/final_report/PROJECT_REPORT.md)
- **User Manual & Interactive Guide:** [`USER_MANUAL.md`](USER_MANUAL.md)
- **REST & WebSocket API Reference:** [`API_REFERENCE.md`](API_REFERENCE.md)
- **Developer Guide & Codebase Architecture:** [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md)
- **QA & Verification Report:** [`TESTING_REPORT.md`](TESTING_REPORT.md)
- **Production Deployment Guide:** [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)
- **Troubleshooting Guide:** [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)

---

## 8. License & Academic Attribution
Developed as an academic course project for **Discrete Mathematics & Graph Theory (Second-Year Computer Engineering)**. Released under the **MIT License**.

