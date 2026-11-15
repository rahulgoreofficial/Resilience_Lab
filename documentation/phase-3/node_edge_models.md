# Phase 3: Node & Edge Mathematical Models
## Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator

---

### 1. Node Model (`app.graph_engine.graph_model.Node`)

The `Node` class models an infrastructure component $v \in V$:

$$v = \langle \text{node\_id}, \tau_v, I_v, C_v, L_v, p_v, \text{is\_critical}, \mathcal{M}_v \rangle$$

#### 1.1 Attribute Schema & Validation Rules

| Attribute | Type | Default Value | Validation Rule | Physical Role |
| :--- | :--- | :--- | :--- | :--- |
| `node_id` | `str` | Mandatory | Must be non-empty string; unique in $V$. | Component hostname or asset tag. |
| `node_type` | `str` | Mandatory | Must belong to: `router`, `switch`, `server`, `database`, `firewall`, `gateway`. | Architectural role archetype. |
| `importance` | `float` | `1.0` | Must be $\ge 0.0$. | Relative priority weight in service resilience scoring. |
| `capacity` | `float` | `100.0` | Must be strictly positive ($> 0.0$). | Maximum throughput capacity before overload in cascading failure. |
| `current_load` | `float` | `0.0` | Must be $\ge 0.0$. | Active traffic volume traversing the device. |
| `failure_probability` | `float` | `0.01` | Must be in range $[0.0, 1.0]$. | Baseline failure probability in Monte Carlo simulations. |
| `is_critical` | `bool` | `False` | Boolean flag. | Designates core infrastructure (e.g., primary gateway or DB). |
| `metadata` | `dict` | `{}` | Optional dictionary. | UI coordinates, IP subnet, vendor model. |

---

### 2. Edge Model (`app.graph_engine.graph_model.Edge`)

The `Edge` class models a communication link $e = \{u, v\} \in E$:

$$e = \langle \text{edge\_id}, u, v, w_e, \text{latency}_e, C_e, \mathcal{R}_e, \mathcal{M}_e \rangle$$

#### 2.1 Attribute Schema & Validation Rules

| Attribute | Type | Default Value | Validation Rule | Physical Meaning |
| :--- | :--- | :--- | :--- | :--- |
| `edge_id` | `str` | Generated | Non-empty unique string (e.g., `source--target`). | Transmission line identifier. |
| `source` | `str` | Mandatory | Must exist in $V$; cannot equal `target`. | First endpoint device. |
| `target` | `str` | Mandatory | Must exist in $V$; cannot equal `source`. | Second endpoint device. |
| `weight` | `float` | `1.0` | Must be $\ge 0.0$. | Primary cost metric for Dijkstra shortest paths. |
| `latency` | `float` | `1.0` | Must be $\ge 0.0$. | Physical propagation delay in milliseconds. |
| `capacity` | `float` | `10.0` | Must be strictly positive ($> 0.0$). | Physical transmission bandwidth (Gbps). |
| `reliability` | `float` | `0.99` | Must be in range $[0.0, 1.0]$. | Probability of error-free transmission. |
| `metadata` | `dict` | `{}` | Optional dictionary. | Cable type (fiber/copper), interface names. |

#### 2.2 Undirected Uniqueness Invariant
Because the network is an undirected simple graph, link $\{u, v\}$ is mathematically equivalent to $\{v, u\}$. The model implements:
```python
@property
def endpoints_key(self) -> frozenset:
  return frozenset([self.source, self.target])
```
The graph engine maps `frozenset({u, v}) -> edge_id`. Any attempt to insert an edge $\{v, u\}$ when $\{u, v\}$ already exists is detected and rejected with `DuplicateEdgeError`.

