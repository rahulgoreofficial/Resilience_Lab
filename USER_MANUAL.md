# RESILIENCE LAB — User Manual & Operational Guide

**Product Title:** Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator  
**Software Version:** 1.0.0 (Production Release)  
**User Audience:** Network Engineers, System Architects, Discrete Mathematics Students, Researchers  

---

## 1. Introduction to the Platform

**RESILIENCE LAB** is an interactive network resilience analysis and infrastructure design platform that helps engineers model network topology, identify critical components, simulate hypothetical disruptions and evaluate network improvements through mathematical analysis.

Through graph-theoretic analysis, the platform transforms abstract discrete mathematics theorems into an actionable visual control plane.

### Core Interface Layout:
The workspace is organized into coordinated operational zones:
1. **Top Telemetry Bar:** Displays active network name, total vertex count $|V|$, total edge count $|E|$, component count $\kappa(G)$, Euler's Lemma verification status, and global connectivity state.
2. **Interactive Topology Canvas:** A hardware-accelerated Cytoscape.js canvas rendering network nodes, links, active shortest paths, highlighted articulation points, and failure states.
3. **Resilience Design Studio (`/design-studio`):** An isolated workspace for creating, editing, and evaluating candidate redundant links against bridge failures without mutating the original database snapshot.
4. **Interactive 3D Network Lab (`/interactive-guide`):** A guided 3D educational experience featuring the 12-node Campus Network demonstration, controlled cascading failure simulation, and 10-step Faculty Presentation Mode.
5. **Left Operations Drawer:** Contains topology management tools, component creation controls, and algorithm triggers.
6. **Right Resilience Analytics Panel:** Displays real-time resilience telemetry: Largest Connected Component (LCC) ratio, Normalized Pairwise Connectivity ($NPC$), fragmentation index, and degree distribution.
7. **Bottom Simulation Control Center:** Multi-tab console for configuring and executing Single-Node, Edge Severance, Monte Carlo Random, Adversarial Targeted, and Motter-Lai Cascading simulations.

---

## 2. Managing Network Topologies

### 2.1 Selecting Pre-Configured Benchmark Networks
The platform comes pre-loaded with three representative industrial topologies:
1. **Enterprise Tier-3 Datacenter:** Dual-core gateways, perimeter firewalls, distribution routers, access switches, and clustered database tiers.
2. **Campus Dual-Chord Ring Backbone:** Six metro routing hubs in a redundant ring supplemented with internal cross-chords for fault tolerance.
3. **Bridge-Vulnerable Hybrid Star-Mesh:** A multi-zone network featuring single points of failure (cut-vertices and inter-zone bridges) designed for immediate failure demonstration.

To switch topologies:
- Click the **Network Selector** in the top navigation bar.
- Choose any seeded topology from the dropdown. The canvas will instantaneously animate to the selected infrastructure.

### 2.2 Creating a Custom Infrastructure
1. Open the left sidebar and select **New Network**.
2. Specify the network name, administrative description, and category (e.g. `enterprise`, `campus`, `datacenter`).
3. Click **Create Infrastructure**. A fresh empty workspace canvas is initialized.

---

## 3. Adding and Configuring Infrastructure Elements

### 3.1 Adding Network Vertices (Nodes)
1. In the left panel, click **Add Node**.
2. Fill in the node properties:
   - **Node ID:** Unique identifier (e.g., `r_core_1`, `srv_db_primary`).
   - **Device Type:** Select from:
     - `router`: Core routing and packet forwarding;
     - `switch`: Access and distribution layer switching;
     - `server`: Compute and application workloads;
     - `database`: High-importance data tier;
     - `firewall`: Security boundary and perimeter inspection;
     - `gateway`: External ingress/egress peering point.
   - **Operational Capacity:** Maximum processing capacity in Mbps (default: `500.0`).
   - **Initial Load:** Baseline traffic load in Mbps (default: `50.0`).
   - **Importance Weight:** Administrative criticality between `0.1` (low) and `1.0` (mission-critical).
3. Click **Deploy Node**. The vertex appears immediately on the canvas.

### 3.2 Connecting Communication Links (Edges)
1. Click **Add Link** in the sidebar.
2. Configure edge parameters:
   - **Edge ID:** Optional custom identifier (or auto-generated).
   - **Source & Target Endpoints:** Select the two connected devices.
   - **Routing Weight / Cost:** Non-negative cost metric $w \ge 0$ used by Dijkstra shortest-path calculations.
   - **Bandwidth Capacity:** Physical transmission bandwidth in Mbps (default: `1000.0`).
   - **Propagation Latency:** Fiber/copper link delay in milliseconds.
3. Click **Connect Link**. The bi-directional edge is drawn with automatic curved collision avoidance.

---

## 4. Analyzing Structural Vulnerabilities

RESILIENCE LAB analyzes graph structure without mutating or deleting elements.

### 4.1 Detecting Cut-Vertices (Articulation Points)
- In the analytics panel, click **Detect Articulation Points**.
- The backend executes **Tarjan's Linear-Time Algorithm** in $O(|V| + |E|)$ time.
- Cut-vertices are immediately highlighted on the canvas with **bright amber glowing halos** and marked in the vulnerability register.
- *Interpretation:* If any of these highlighted nodes fail, the network will partition into disconnected components.

### 4.2 Detecting Critical Bridges (Cut-Edges)
- Click **Detect Critical Bridges**.
- All cut-edges are rendered with **pulsing orange dashed strokes**.
- *Interpretation:* These links represent single-conduit physical paths with zero alternate bypasses.

### 4.3 Optimal Routing & Shortest Paths
- Under the **Path Routing** tab, select a Source Node and Target Node.
- Click **Compute Shortest Path**.
- The optimal route calculated via Dijkstra's algorithm illuminates in **neon cyan**, and total cumulative metric and hop sequence are printed in the telemetry drawer.

---

## 5. Executing Failure Simulations

Navigate to the bottom **Simulation Control Center** to trigger failure scenarios.

### 5.1 Single / Multi-Node Failure
1. Select the **Node Failure** tab.
2. Select one or more target nodes from the multiselect checklist (or click directly on nodes on the canvas).
3. Click **Execute Node Failure**.
4. **Visual Result:**
   - Target nodes turn translucent gray with red strikeout badges.
   - Incident links vanish from active routing.
   - The topology dynamically re-partitions, updating the LCC ratio and component count in real time.

### 5.2 Physical Link Severance
1. Select the **Edge Failure** tab.
2. Pick the target link ID.
3. Click **Sever Link**.
4. The link turns red and is severed, demonstrating whether rerouting paths exist or if an entire branch becomes isolated.

### 5.3 Monte Carlo Stochastic Random Failure
1. Select the **Random Failure** tab.
2. Set **Failure Count** (or percentage of nodes to remove) and **Number of Trials** (e.g., 5 or 10).
3. Set optional **Random Seed** for deterministic academic reproduction.
4. Click **Run Monte Carlo Simulation**.
5. The platform plots the expected degradation curve, showing mean, median, and standard deviation of LCC retention.

### 5.4 Adversarial Targeted Attack
1. Select the **Targeted Attack** tab.
2. Choose an attack strategy:
   - **Degree Centrality:** Attacks the highest-degree hubs first.
   - **Articulation Points:** Attacks critical cut-vertices first to maximize fragmentation.
   - **Multi-Criteria Impact:** Attacks nodes with highest composite criticality score.
3. Toggle **Adaptive Targeting** (recalculates rankings after each removal) vs. **Static Targeting**.
4. Click **Launch Attack**. Observe how rapidly the network disintegrates under targeted strikes compared to random failure.

### 5.5 Motter-Lai Cascading Overload Simulation
1. Select the **Cascading Overload** tab.
2. Select initial failure triggers (e.g. remove a core distribution router `r_dist_1`).
3. Set **Overload Threshold Multiplier** $\theta$ (default `1.0` or `1.2`).
4. Set **Maximum Simulation Rounds** (default `5` to `10`).
5. Click **Start Overload Cascade**.
6. **Live Cascade Playback:**
   - The simulation plays back round by round.
   - Overloaded nodes illuminate in bright red before failing simultaneously at the end of each round.
   - The event log displays exact excess load values (e.g., `Node r_dist_2 load 750 Mbps exceeds capacity 600 Mbps (125%)`).
   - The cascade halts automatically when equilibrium is reached.

---

## 6. Interpreting Quantitative Resilience Metrics

| Metric | Formula | Range | Interpretation |
|---|---|---|---|
| **LCC Ratio** ($R_{\text{LCC}}$) | $|V_{\text{LCC}}| / |V_{\text{initial}}|$ | $0.0 \dots 1.0$ | Fraction of initial network remaining in largest connected cluster. $1.0$ is ideal; $< 0.5$ indicates catastrophic collapse. |
| **Pairwise Connectivity** ($NPC$) | $\frac{\sum |V_i|(|V_i|-1)}{|V|(|V|-1)}$ | $0.0 \dots 1.0$ | Probability that two arbitrarily chosen surviving devices can communicate. |
| **Fragmentation Index** ($F$) | $1 - NPC$ | $0.0 \dots 1.0$ | Likelihood of communication disruption between random endpoints. |
| **Graph Diameter** | $\max_{u, v} dist(u, v)$ | $1 \dots |V|-1$ | Maximum shortest-path hop latency across the active connected component. |
| **Node Criticality Index** | Multi-factor weighted sum | $0.0 \dots 1.0$ | Higher values indicate higher priority for hardware hardening and link redundancy. |

---

## 7. Exporting Topologies & Simulation Reports

- **Export Topology (JSON):** Downloads standard schema containing all nodes, edges, and capacities for archival or cross-system import.
- **Export Cytoscape Elements:** Exports raw canvas elements for integration into external visualization tools.
- **Export Simulation Report (PDF / Markdown):** Generates full event histories, pre/post metrics, and component breakdowns for executive reporting.

---

## 8. Resilience Design Studio & Candidate-Link Analysis

Accessible via **Resilience Design Studio** in the primary navigation:
1. **Isolated Working Copy (`draftNetwork`):**
   - Allows network engineers to test topological improvements in a sandboxed buffer without altering the saved database model.
   - Insert new transmission links, delete existing connections, and tune device capacities.
2. **Automated Candidate-Link Evaluation:**
   - Evaluates all candidate non-existent links $(u, v) \notin E$ against simulated bridge failures.
   - Computes $\Delta\text{LCC}$ and $\Delta\text{Pairwise Connectivity}$ gains for every candidate.
   - Provides architectural classification (Inter-Switch Trunk, Router Uplink, Host Direct Link) and cost-benefit ratios.
   - **One-Click Application:** Clicking `+ Add to Draft` immediately injects the selected candidate into the working copy.
3. **Side-by-Side Disruption Tester:**
   - Simulates identical link disruptions (e.g. `C1-L1` severance) on both Baseline and Working Copy concurrently.
   - Proves dynamic rerouting and displays alternative paths (e.g., `G1 → R1 → C1 → B1 → L1 → LS1`).
4. **Design Persistence:**
   - `Save Design to Database`: Commits the modified working copy as an engineered network variant.
   - `Discard Changes`: Reverts working copy to the pristine network state.
   - `Reset Campus Baseline`: Restores the 12-node campus demonstration benchmark.

---

## 9. Guided Demonstrations & Faculty Presentation Mode

Accessible via **Interactive 3D Guide** (`/interactive-guide`):
1. **Campus Laboratory Connectivity Failure (Steps A - F):**
   - Step A: Baseline analysis (12 nodes, 11 edges, 1 component, 4/4 services reachable).
   - Step B: Bridge vulnerability detection (`C1-L1` identified via Tarjan's algorithm).
   - Step C: Live failure simulation (splits into 2 components sizes 10 & 2; LCC = 83.33%, Pairwise = 69.70%, Services = 75%).
   - Step D: Network improvement (adding backup link `L1-B1`).
   - Step E: Repeated disruption test (100% LCC, 100% Pairwise, 100% Services).
   - Step F: Before/after side-by-side comparison with dynamic rerouting.
2. **Controlled Cascading Overload Demonstration:**
   - 5-node topology (`CL1`, `PR1`, `BR1`, `CS1`, `SRV_APP`) carrying 300 Mbps demand.
   - Primary Router `PR1` failure shifts load onto Backup Router `BR1` ($100 + 300 = 400 > 350$).
   - `BR1` trips in Round 2, causing total service disconnection.
3. **Faculty Presentation Mode:**
   - 10-step presenter-controlled walkthrough with Step Captions, Next/Previous/Pause/Reset, auto-camera focus, and discrete mathematics syllabus tags.

---

## 10. Engineering Deployment Caveats & Disclaimers
> **IMPORTANT:** Topological improvements calculated on an abstract graph represent mathematical upper bounds. Physical deployment requires:
> 1. Configuring 802.1Q VLAN trunks and Rapid Spanning Tree Protocol (RSTP / 802.1w) to prevent broadcast loops during normal operation.
> 2. Verifying physical intra-building conduit and fiber pathway routing.
> 3. Synchronizing firewall ACL security policies for rerouted transit flows.


