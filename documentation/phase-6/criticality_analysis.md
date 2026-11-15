# Phase 6: Criticality Analysis & Vulnerability Profiling

## 1. Single-Component Impact Analysis

Criticality analysis identifies the structurally and operationally most vital components in the infrastructure.

Rather than assuming all articulation points or hubs have equal severity, the system evaluates the **measured empirical impact** of removing each component individually:
$$G - v \quad \text{for each } v \in V, \qquad G - e \quad \text{for each } e \in E$$

---

## 2. Quantitative Criticality Metrics

For each node $v \in V$, the engine evaluates:
1. **Pairwise Connectivity Impact**:
   $$\Delta \text{PairConn}(v) = \text{PairConn}(G) - \text{PairConn}(G - v)$$
2. **LCC Size Reduction**:
   $$\Delta \text{LCC}(v) = |LCC(G)| - |LCC(G - v)|$$
3. **Component Increase**:
   $$\Delta \kappa(v) = \kappa(G - v) - \kappa(G)$$
4. **Service Reachability Loss**:
   $$\Delta \text{Service}(v) = \frac{|S_{\text{baseline}}| - |S_{G - v}|}{|S_{\text{baseline}}|}$$
5. **Articulation Point Classification**: Tarjan low-link cut-vertex status $\mathbb{I}(v \in \text{AP})$.

### Composite Criticality Formulation
$$\text{Score}(v) = 0.4 \cdot \Delta \text{PairConn} + 0.3 \cdot \Delta \text{Service} + 0.2 \cdot \frac{\Delta \text{LCC}}{|V|} + 0.1 \cdot \mathbb{I}(v \in \text{AP})$$

Deterministic tie-breaking is enforced by sorting alphabetically by `node_id`.

---

## 3. Communication Link (Edge) Criticality

For each communication link $e = \{u, v\} \in E$:
1. Evaluates $\Delta \text{PairConn}(e) = \text{PairConn}(G) - \text{PairConn}(G - e)$.
2. Identifies whether $e$ is a bridge via Tarjan's low-link algorithm: $\text{low}[v] > \text{discovery}[u]$.
3. Edge impact formula:
   $$\text{Score}(e) = 0.5 \cdot \Delta \text{PairConn} + 0.3 \cdot \Delta \text{Service} + 0.2 \cdot \mathbb{I}(e \in \text{Bridges})$$

### Bridge Impact Disambiguation
Not all bridges are equally critical:
* A bridge connected to an isolated leaf server disconnects 1 node ($|C_1| = |V| - 1, |C_2| = 1$), causing minor pairwise connectivity reduction.
* A central bisection bridge bisecting a network in half ($|C_1| = |V|/2, |C_2| = |V|/2$) destroys $\approx 50\%$ of all communication pairs.
The criticality engine correctly scores and differentiates these topologies.

---

## 4. Computational Complexity

* **Node Criticality**: Evaluates $|V|$ subgraphs via BFS connected components:
  $$O(|V| \cdot (|V| + |E|))$$
* **Edge Criticality**: Evaluates $|E|$ subgraphs:
  $$O(|E| \cdot (|V| + |E|))$$
* **Scalability Controls**: Central `max_components` parameter allows sampling top hubs for massive graphs.

