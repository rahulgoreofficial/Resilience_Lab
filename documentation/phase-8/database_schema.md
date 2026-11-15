# Phase 8: Normalized Database Schema Specification

## 1. Relational Design Philosophy

The database schema is normalized up to **Third Normal Form (3NF)** and optimized for high-performance graph infrastructure modeling. It is designed to run natively on **PostgreSQL 15+** with automatic zero-dependency fallback to **SQLite 3.35+** for local sandboxed development.

The schema comprises 6 core tables:
1. `networks`: Stores root network infrastructure metadata with optimistic version tracking.
2. `nodes`: Stores physical and logical component vertices $v \in V$.
3. `edges`: Stores bidirectional communication links $\{u, v\} \in E$ with canonical ordering.
4. `network_snapshots`: Stores immutable, serialized graph topology captures with SHA-256 fingerprints.
5. `simulations`: Records full execution lifecycles, configurations, and analytical outcomes.
6. `simulation_events`: Stores fine-grained, chronological execution events with monotonic sequence numbers.

---

## 2. Table Specifications

### 2.1. Table: `networks`
Stores top-level network entities and enforces optimistic concurrency control.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | UUIDv4 identifier string. |
| `name` | `VARCHAR(128)` | `NOT NULL, INDEX` | Human-readable network name. |
| `description` | `TEXT` | `NULLABLE` | Detailed architectural description. |
| `network_type` | `VARCHAR(64)` | `NOT NULL, DEFAULT 'COMMUNICATION_NETWORK'` | Domain classification (e.g. `ENTERPRISE_DATACENTER`). |
| `metadata` | `JSON` | `NOT NULL, DEFAULT '{}'` | Extensible key-value metadata attributes. |
| `version` | `INTEGER` | `NOT NULL, DEFAULT 1` | Optimistic lock counter incremented on every topology edit. |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL, DEFAULT NOW()` | UTC entity creation timestamp. |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL, DEFAULT NOW()` | UTC timestamp of last update. |

---

### 2.2. Table: `nodes`
Represents graph vertices $V$ modeling routers, switches, servers, databases, firewalls, and gateways.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY, AUTOINCREMENT` | Surrogate database row ID. |
| `network_id` | `VARCHAR(36)` | `NOT NULL, FK -> networks.id ON DELETE CASCADE, INDEX` | Parent network reference. |
| `node_id` | `VARCHAR(64)` | `NOT NULL` | Domain identifier within network (e.g. `R1_CORE`). |
| `node_type` | `VARCHAR(32)` | `NOT NULL` | Device category (`router`, `switch`, `server`, etc.). |
| `importance` | `DOUBLE PRECISION` | `NOT NULL, DEFAULT 1.0, CHECK (importance >= 0.0)` | Structural weight/criticality factor. |
| `capacity` | `DOUBLE PRECISION` | `NOT NULL, DEFAULT 100.0, CHECK (capacity > 0.0)` | Maximum throughput or processing bandwidth. |
| `current_load` | `DOUBLE PRECISION` | `NOT NULL, DEFAULT 0.0, CHECK (current_load >= 0.0)` | Active operational traffic demand. |
| `failure_probability`| `DOUBLE PRECISION` | `NOT NULL, DEFAULT 0.01, CHECK (p >= 0.0 AND p <= 1.0)` | Independent stochastic failure rate. |
| `is_critical` | `BOOLEAN` | `NOT NULL, DEFAULT FALSE` | Flag marking high-value critical assets. |
| `metadata` | `JSON` | `NOT NULL, DEFAULT '{}'` | Extended hardware specs (vendor, IP, rack ID). |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL, DEFAULT NOW()` | UTC creation timestamp. |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL, DEFAULT NOW()` | UTC last update timestamp. |

**Composite Constraints & Indexes:**
- `UNIQUE (network_id, node_id)` (`uq_network_node_id`): Prevents duplicate node IDs within the same network.
- `INDEX (network_id)`: Accelerates topology retrieval.

---

### 2.3. Table: `edges`
Represents undirected communication links $E = \{\{u, v\}\}$ between components.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY, AUTOINCREMENT` | Surrogate row ID. |
| `network_id` | `VARCHAR(36)` | `NOT NULL, FK -> networks.id ON DELETE CASCADE, INDEX` | Parent network reference. |
| `edge_id` | `VARCHAR(64)` | `NOT NULL` | Domain link ID (e.g. `e_r1_s1`). |
| `source_node_id` | `VARCHAR(64)` | `NOT NULL` | Directed API representation source vertex. |
| `target_node_id` | `VARCHAR(64)` | `NOT NULL` | Directed API representation target vertex. |
| `canonical_u` | `VARCHAR(64)` | `NOT NULL` | Lexicographically smaller endpoint ($\min(u, v)$). |
| `canonical_v` | `VARCHAR(64)` | `NOT NULL` | Lexicographically larger endpoint ($\max(u, v)$). |
| `weight` | `DOUBLE PRECISION` | `NOT NULL, DEFAULT 1.0, CHECK (weight >= 0.0)` | Dijkstra link routing cost. |
| `latency` | `DOUBLE PRECISION` | `NOT NULL, DEFAULT 1.0, CHECK (latency >= 0.0)` | Transmission delay in milliseconds. |
| `capacity` | `DOUBLE PRECISION` | `NOT NULL, DEFAULT 10.0, CHECK (capacity > 0.0)` | Bandwidth link saturation threshold. |
| `reliability` | `DOUBLE PRECISION` | `NOT NULL, DEFAULT 0.99, CHECK (r >= 0.0 AND r <= 1.0)` | Link survival probability. |
| `metadata` | `JSON` | `NOT NULL, DEFAULT '{}'` | Medium specs (fiber, copper, 10GbE). |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL, DEFAULT NOW()` | UTC creation timestamp. |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL, DEFAULT NOW()` | UTC last update timestamp. |

**Composite Constraints & Indexes:**
- `UNIQUE (network_id, edge_id)` (`uq_network_edge_id`): Guarantees edge identifier uniqueness.
- `UNIQUE (network_id, canonical_u, canonical_v)` (`uq_network_undirected_edge`): Prevents duplicate bidirectional links regardless of order.
- `CHECK (canonical_u != canonical_v)` (`chk_edge_no_self_loops`): Forbids invalid self-loops.

---

### 2.4. Table: `network_snapshots`
Freezes point-in-time network topologies used by simulations to guarantee historical reproducibility.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | UUIDv4 snapshot identifier. |
| `network_id` | `VARCHAR(36)` | `NOT NULL, FK -> networks.id ON DELETE CASCADE, INDEX` | Parent network ID. |
| `network_version` | `INTEGER` | `NOT NULL` | Incremental network version at capture time. |
| `graph_snapshot` | `JSON` | `NOT NULL` | Complete canonical serialized graph topology. |
| `snapshot_hash` | `VARCHAR(64)` | `NOT NULL, INDEX` | Deterministic SHA-256 hash fingerprint of graph data. |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL, DEFAULT NOW()` | UTC capture timestamp. |

---

### 2.5. Table: `simulations`
Tracks simulation jobs, execution configuration parameters, runtime status, and computed resilience metrics.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | UUIDv4 simulation identifier. |
| `network_id` | `VARCHAR(36)` | `NOT NULL, FK -> networks.id ON DELETE CASCADE, INDEX` | Target network reference. |
| `snapshot_id` | `VARCHAR(36)` | `NULLABLE, FK -> network_snapshots.id ON DELETE SET NULL, INDEX` | Point-in-time topology snapshot used. |
| `simulation_type` | `VARCHAR(32)` | `NOT NULL, INDEX` | Type: `node_failure`, `edge_failure`, `random`, `targeted`, `cascading`. |
| `status` | `VARCHAR(32)` | `NOT NULL, DEFAULT 'queued', INDEX` | State: `queued`, `running`, `completed`, `failed`, `interrupted`. |
| `configuration` | `JSON` | `NOT NULL, DEFAULT '{}'` | Inputs (failed elements, attack strategies, demands). |
| `random_seed` | `INTEGER` | `NULLABLE` | PRNG seed for reproducible stochastic percolation. |
| `results` | `JSON` | `NULLABLE` | Mathematical metrics output (LCC, connectivity, etc.). |
| `error_summary` | `TEXT` | `NULLABLE` | Detailed exception message if execution failed/interrupted. |
| `started_at` | `TIMESTAMP WITH TIME ZONE` | `NULLABLE` | UTC timestamp execution started. |
| `completed_at` | `TIMESTAMP WITH TIME ZONE` | `NULLABLE` | UTC timestamp execution finalized. |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL, DEFAULT NOW(), INDEX` | UTC simulation submission timestamp. |

---

### 2.6. Table: `simulation_events`
Stores chronological progress logs for real-time WebSocket streaming and offline audit replays.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY, AUTOINCREMENT` | Surrogate event ID. |
| `simulation_id` | `VARCHAR(36)` | `NOT NULL, FK -> simulations.id ON DELETE CASCADE, INDEX` | Parent simulation job reference. |
| `sequence_number` | `INTEGER` | `NOT NULL` | Monotonically increasing event index ($1, 2, 3, \dots$). |
| `event_type` | `VARCHAR(64)` | `NOT NULL` | Event tag (e.g. `simulation_started`, `failure_injected`). |
| `event_data` | `JSON` | `NOT NULL, DEFAULT '{}'` | Detailed payload (isolated nodes, load distributions). |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL, DEFAULT NOW()` | UTC emission timestamp. |

**Composite Constraints & Indexes:**
- `UNIQUE (simulation_id, sequence_number)` (`uq_simulation_event_sequence`): Enforces deterministic chronological sequence integrity.

