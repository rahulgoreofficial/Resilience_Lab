# Phase 6: Mathematical Resilience Metrics

## 1. Mathematical Metric Formulations

The Resilience Analysis Engine introduces four quantitative metrics to evaluate graph-theoretic and service availability degradation under infrastructure failures.

---

### 1.1 Largest Connected Component (LCC) Ratio
The LCC ratio quantifies the size of the surviving giant connected component relative to the active vertex population:

$$\text{LCC Ratio} = \frac{|V_{\text{giant}}|}{|V_{\text{active}}|}$$

* **Domain**: $[0.0, 1.0]$.
* **Interpretation**:
  * $\text{LCC Ratio} = 1.0 \implies$ All active components remain mutually connected in a single component.
  * $\text{LCC Ratio} \to 0.0 \implies$ The network has shattered into microscopic isolated fragments.
* **Edge Cases**:
  * $|V_{\text{active}}| = 0 \implies \text{LCC Ratio} = 0.0$.

---

### 1.2 Pairwise Connectivity
Pairwise Connectivity measures the fraction of all possible vertex pairs $\{u, v\} \subseteq V_{\text{active}}$ that can still communicate through active paths:

$$\text{Pairwise Connectivity} = \frac{\sum_{i=1}^k \binom{|C_i|}{2}}{\binom{|V_{\text{active}}|}{2}}$$

where $V / R = \{C_1, C_2, \dots, C_k\}$ is the partition of connected components.

* **Domain**: $[0.0, 1.0]$.
* **Interpretation**: Captures intra-component communication opportunities. Even if a giant component exists, severe fragmentation dramatically penalizes pairwise connectivity.
* **Edge Cases**:
  * $|V_{\text{active}}| = 0 \implies 0.0$.
  * $|V_{\text{active}}| = 1 \implies 1.0$ (no severed internal pairs).
  * $k = |V_{\text{active}}| \implies 0.0$ (all vertices completely isolated).

---

### 1.3 Connectivity Loss
Direct inverse of pairwise connectivity:

$$\text{Connectivity Loss} = 1.0 - \text{Pairwise Connectivity}$$

Represents the percentage of all communication flows severed by the failure.

---

### 1.4 Service Resilience Score ($R$)
Quantifies accessibility to designated critical application services (e.g. database servers, core DNS) from ingress entry points:

$$R = \frac{|S_{\text{post}}|}{|S_{\text{baseline}}|}$$

where $S$ is the set of critical services reachable from at least one active ingress entry point.

#### Weighted Service Resilience Score ($R_{\text{weighted}}$)
When services have distinct business importance weights $\omega(s) > 0$:

$$R_{\text{weighted}} = \frac{\sum_{s \in S_{\text{post}}} \omega(s)}{\sum_{s \in S_{\text{baseline}}} \omega(s)}$$

* **Undefined Denominator Safety**: If no critical services were reachable at baseline ($|S_{\text{baseline}}| = 0$ or not configured), the score safely returns `null` / `"NOT CONFIGURED"` rather than fabricating an arbitrary score.

