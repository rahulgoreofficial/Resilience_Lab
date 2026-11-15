# Phase 7: Cascading Overload Failure Model

## 1. Capacity-Based Failure Propagation Model

Cascading failures represent the most severe threat to critical infrastructure, where an initial minor disruption triggers rerouting, capacity overloads, and secondary failures across the network.

The simulator implements a discrete, multi-round, capacity-based traffic model inspired by the Motter-Lai formulation.

---

## 2. Mathematical Model & Routing Formulation

### 2.1 Component Capacity & Background Load
Each node $v \in V$ possesses:
* An initial background load $L_v^{(0)} \ge 0$.
* A maximum capacity $C_v > 0$.

Each edge $e \in E$ possesses:
* A maximum capacity $C_e > 0$.

### 2.2 Traffic Demand Rerouting
A set of traffic demands $D = \{ (s_i, t_i, A_i) \}$ represents communication flows of volume $A_i$ required between source $s_i$ and destination $t_i$.

At each simulation round $r$:
1. For each active demand $(s_i, t_i, A_i)$, compute the shortest path $P_i^*(r)$ in the active snapshot $G(r)$ using Dijkstra's algorithm.
2. If path $P_i^*(r)$ exists, add demand $A_i$ to the routed traffic load of all traversed nodes and links:
   $$L_v^{\text{routed}}(r) = \sum_{i : v \in P_i^*(r)} A_i, \qquad L_e^{\text{routed}}(r) = \sum_{i : e \in P_i^*(r)} A_i$$
3. Total node load:
   $$L_v(r) = L_v^{(0)} + L_v^{\text{routed}}(r)$$

### 2.3 Overload Criteria
A node or link fails synchronously if its aggregated load exceeds its capacity scaled by the user-configured overload threshold $\theta$:

$$\text{Overloaded Node}: \quad L_v(r) > C_v \times \theta$$
$$\text{Overloaded Edge}: \quad L_e^{\text{routed}}(r) > C_e \times \theta$$

---

## 3. Synchronous Propagation Rounds

```
[Round 0: Baseline Validation]
  Verify initial capacities & report pre-existing overloads
        |
        v
[Round 1: Trigger Failure]
  Disable user-specified initial nodes/edges
        |
        v
[Round 2..R_max: Dynamic Redistribution]
  Route traffic flows along active paths via Dijkstra
  Aggregate loads on active nodes & edges
  Identify newly overloaded components
        |
        +---> If NO new overloads occur  --> STOP ("STABLE - No further cascades")
        +---> If critical services lost --> STOP ("CRITICAL_SERVICES_EXHAUSTED")
        +---> If round >= R_max          --> STOP ("MAX_ROUNDS_REACHED")
        |
  Synchronously fail newly overloaded components
  Advance to round r + 1
```

Synchronous failure guarantees that cascade outcomes are completely deterministic and independent of arbitrary processing order.

