# Phase 6: Failure Scenario Comparison

## 1. Multi-Hypothesis Resilience Evaluation

The scenario comparison engine allows network architects to evaluate competing failure scenarios side-by-side against the common baseline graph.

```
                      +-----------------------------+
                      |      Baseline Network       |
                      |         G = (V, E)          |
                      +--------------+--------------+
                                     |
           +-------------------------+-------------------------+
           |                                                   |
           v                                                   v
+---------------------+                             +---------------------+
|     Scenario A      |                             |     Scenario B      |
|  Fail Router R1     |                             |  Fail Router R2     |
+----------+----------+                             +----------+----------+
           |                                                   |
           v                                                   v
+---------------------+                             +---------------------+
|  Post-Failure A     |                             |  Post-Failure B     |
| PairConn: 0.72      |                             | PairConn: 0.35      |
| Services: 100%      |                             | Services: 50%       |
+----------+----------+                             +----------+----------+
           |                                                   |
           +-------------------------+-------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |   Comparative Delta Matrix  |
                      |   & Recharts JSON Contract  |
                      +-----------------------------+
```

---

## 2. Structured Comparison Contract

Each comparison evaluation yields:
* **Baseline Profile**: Total vertices, edges, baseline pairwise connectivity, and baseline reachable services.
* **Per-Scenario Metrics**:
  * Active vertex count & edge count.
  * Disconnected components count and giant component size.
  * $\Delta \text{Pairwise Connectivity} = \text{PairConn}_{\text{baseline}} - \text{PairConn}_{\text{post}}$.
  * $\Delta \text{LCC Size}$.
  * Component increase $\Delta \kappa$.
  * Service Resilience Score $R$.

### JSON Response Structure
```json
{
  "baseline": {
    "total_vertices": 18,
    "total_edges": 18,
    "component_count": 3,
    "giant_component_size": 15,
    "lcc_ratio": 0.8333,
    "pairwise_connectivity": 0.6928,
    "reachable_critical_services": ["DB_PROD_1", "AUTH_SRV"],
    "critical_services_count": 2
  },
  "scenarios": [
    {
      "scenario_id": "scen_a",
      "name": "Core Switch SW_CORE_1 Failure",
      "failed_nodes": ["SW_CORE_1"],
      "failed_edges": ["e_r1_sw1", "e_sw1_r2"],
      "active_vertices": 17,
      "active_edges": 16,
      "component_count": 4,
      "giant_component_size": 12,
      "lcc_ratio": 0.7059,
      "pairwise_connectivity": 0.5074,
      "connectivity_loss": 0.4926,
      "delta_pairwise_connectivity": 0.1854,
      "delta_giant_component_size": 3,
      "component_increase": 1,
      "reachable_critical_services": ["AUTH_SRV"],
      "unreachable_critical_services": ["DB_PROD_1"],
      "service_resilience_score_R": 0.5
    }
  ]
}
```

This structure is directly consumable by frontend Recharts components for rendering comparative bar and radar charts.

