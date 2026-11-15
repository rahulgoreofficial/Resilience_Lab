# Phase 4: Algorithmic Complexity Analysis
## Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator

---

### 1. Master Algorithmic Complexity Table

| Algorithm | Module File | Time Complexity | Auxiliary Space Complexity | Governing Mathematical Mechanism | Empirical Runtime ($N=500, E=1500$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Breadth-First Search** | `app/algorithms/bfs.py` | $\Theta(V + E)$ | $\Theta(V)$ | FIFO Queue discovery | $< 1\text{ ms}$ |
| **Depth-First Search** | `app/algorithms/dfs.py` | $\Theta(V + E)$ | $\Theta(V)$ | Iterative stack backtracking | $< 1\text{ ms}$ |
| **Connected Components** | `app/algorithms/connected_components.py` | $\Theta(V + E)$ | $\Theta(V)$ | BFS component partition labeling | $< 2\text{ ms}$ |
| **Degree Analysis** | `app/algorithms/degree_analysis.py` | $\Theta(V + E)$ | $\Theta(V)$ | Neighbor counting & sum verification | $< 1\text{ ms}$ |
| **Tarjan Articulation Points** | `app/algorithms/articulation_points.py` | $\Theta(V + E)$ | $\Theta(V)$ | DFS tree low-link $\text{low}[v] \ge d[u]$ | $< 3\text{ ms}$ |
| **Tarjan Bridges** | `app/algorithms/bridges.py` | $\Theta(V + E)$ | $\Theta(V)$ | DFS tree low-link $\text{low}[v] > d[u]$ | $< 3\text{ ms}$ |
| **Dijkstra Shortest Path** | `app/algorithms/shortest_path.py` | $O((V + E) \log V)$ | $\Theta(V)$ | Binary min-heap relaxation | $< 4\text{ ms}$ |

---

### 2. Theoretical Complexity Proofs

#### 2.1 Tarjan's Linear Time vs. Naive Edge Removal
- **Naive Bridge Search**: Sequentially removes each edge $e \in E$ and runs BFS to check if component count increases:
  $$T_{\text{naive-bridge}} = |E| \times O(|V| + |E|) = O(|V||E| + |E|^2)$$
  For $V = 500, E = 1500$, naive bridge search requires $\approx 3,000,000$ operations.
- **Tarjan's Low-Link Algorithm**: Visits every vertex once and inspects every incident edge twice (tree edge traversal and backtrack):
  $$T_{\text{Tarjan}} = \Theta(|V| + |E|)$$
  For $V = 500, E = 1500$, Tarjan executes in $\approx 3,500$ operations.
  **Speedup**: $> 800\times$ faster than naive brute force.

#### 2.2 Dijkstra's Time Complexity Derivation
- Extract-Min: $|V|$ operations on binary min-heap $\implies O(|V| \log |V|)$.
- Edge Relaxations: At most $|E|$ edge inspections triggering `heappush` $\implies O(|E| \log |V|)$.
- Total Time:
  $$T_{\text{Dijkstra}} = O((|V| + |E|) \log |V|)$$

