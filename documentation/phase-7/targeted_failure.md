# Phase 7: Targeted Adversarial Attacks

## 1. Adversarial Attack Strategies

Unlike random failures, targeted adversarial attacks simulate intentional disruption directed against the network's most influential components.

The simulator implements three discrete targeting strategies:

### Strategy A: Degree-Based (Hub Attack)
Targets nodes with the maximum vertex degree $\deg(v) = |N(v)|$:
$$v^* = \arg\max_{v \in V} \deg(v)$$
Highly effective against scale-free or hub-and-spoke topologies.

### Strategy B: Articulation-Point-Based (SPOF Attack)
Prioritizes cut-vertices identified by Tarjan's low-link algorithm:
$$v^* \in \{ v \in V \mid \kappa(G - v) > \kappa(G) \}$$
Guarantees immediate network partition whenever an active articulation point exists.

### Strategy C: Impact-Based (Empirical Vulnerability Attack)
Ranks nodes by their actual evaluated single-node failure impact $\Delta \text{Pairwise Connectivity}$.

---

## 2. Static vs. Adaptive Targeting

* **Static Targeting (`adaptive=False`)**: Ranks all nodes once based on the initial baseline graph $G_0$ and removes the top $k$ nodes in sequence.
* **Adaptive Targeting (`adaptive=True`)**: Recomputes topological rankings (degrees, cut-vertices, and impacts) dynamically after each removal step $k \to k + 1$, adapting to the evolving graph structure.

### Deterministic Tie-Breaking
When two candidates share identical degrees or impact scores, ties are resolved deterministically by lexicographical order of `node_id`.

---

## 3. Resilience Degradation Percolation Curve

For an attack budget of $K$ steps, the engine records the complete degradation trajectory:
$$\{ (k, \text{LCC}(k), \text{PairConn}(k), \kappa(k), \text{Services}(k)) \}_{k=0}^K$$

This produces the classic Albert-Barabási comparison curve: targeted attacks collapse scale-free networks exponentially faster than random failures.

