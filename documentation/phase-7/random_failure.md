# Phase 7: Random Failure & Stochastic Percolation

## 1. Theoretical Basis: Random Node & Edge Percolation

Random failure models stochastic, uncoordinated component outages (e.g. hardware faults, power supply dropouts, environmental cable cuts).

In statistical physics and network science, removing a fraction $f$ of nodes uniformly at random corresponds to **site percolation**:
$$f = \frac{k}{|V|}, \qquad k \text{ components removed without replacement}$$

As $f$ increases, the network experiences a percolation transition: the giant component undergoes continuous dissolution until it disintegrates into small clusters at the critical threshold $f_c$.

---

## 2. Dynamic Configuration & Reproducibility

Users configure:
1. **Failure Target**: `"NODES"`, `"EDGES"`, or `"BOTH"`.
2. **Failure Budget**: Explicit count $k$ or percentage $f \in [0, 100]$.
3. **Number of Trials**: $M \in [1, 500]$ Monte Carlo runs.
4. **Deterministic PRNG Seed**: Seeds an isolated `random.Random(seed)` instance, avoiding global state contamination.
5. **Selection Method**:
   * **`UNIFORM`**: Every component has equal probability $P(v) = 1 / |V|$.
   * **`WEIGHTED_PROBABILITY`**: Components are sampled according to their configured `failure_probability` attribute without replacement.

---

## 3. Statistical Distribution Computation

Across $M$ stochastic trials, the engine computes summary statistics:
$$\bar{X} = \frac{1}{M} \sum_{i=1}^M X_i, \qquad \sigma_X = \sqrt{\frac{1}{M - 1} \sum_{i=1}^M (X_i - \bar{X})^2}$$

Metrics summarized:
* Mean, Median, Min, Max, and Std Dev of **Pairwise Connectivity**.
* Mean, Median, Min, Max, and Std Dev of **LCC Ratio**.
* Mean, Median, Min, Max, and Std Dev of **Component Count** $\kappa$.
* Mean, Median, Min, Max, and Std Dev of **Reachable Critical Services**.

