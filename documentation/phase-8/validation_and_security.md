# Phase 8: Validation, Security & Concurrency Controls

## 1. Optimistic Concurrency Control (OCC)

In a collaborative network modeling environment, multiple network engineers may attempt to modify the same network simultaneously. Without concurrency controls, the classic **lost update problem** occurs: User A's changes are quietly overwritten by User B's later save.

### 1.1. Mathematical Concurrency Model
Each network entity tracks an integer `version` counter:
$$\text{Network} = (V, E, \text{version})$$

When an update request is received:
1. The client supplies its `expected_version`.
2. The repository checks the condition:
   $$\text{current\_version} = \text{expected\_version}$$
3. If the condition holds:
   $$\text{version} \gets \text{version} + 1$$
   The update succeeds.
4. If the condition fails ($\text{current\_version} \ne \text{expected\_version}$):
   The repository aborts the transaction and raises `NetworkVersionConflictError` (HTTP 409 Conflict).

### 1.2. Implementation in Repository Layer
```python
if network.version != expected_version:
    raise NetworkVersionConflictError(
        f"Version conflict on network '{network_id}'. "
        f"Expected version {expected_version}, but database has version {network.version}."
    )
network.version += 1
```

The client receives an unambiguous HTTP 409 Conflict error with code `"VERSION_CONFLICT"`, prompting the UI to reload the latest topology before re-applying edits.

---

## 2. Standardized Error Response Envelope

To ensure API consistency, every exception across the entire backend produces a standardized, machine-readable JSON structure:

```json
{
  "error": {
    "code": "STRING_ERROR_CODE",
    "message": "Human-readable explanation of failure.",
    "details": null
  }
}
```

### Centralized Exception Code Taxonomy:

| HTTP Status | Exception Class | Error Code | Example Trigger |
| :--- | :--- | :--- | :--- |
| `400 Bad Request` | `BadRequestError` | `BAD_REQUEST` | Disallowed file extension (`.exe`), self-loop in edge. |
| `400 Bad Request` | `GraphStructureError` | `GRAPH_STRUCTURE_ERROR` | Non-existent endpoints or invalid graph syntax. |
| `404 Not Found` | `NetworkNotFoundError` | `NETWORK_NOT_FOUND` | Querying non-existent network UUID. |
| `404 Not Found` | `NodeNotFoundError` | `NODE_NOT_FOUND` | Deleting vertex that does not exist in network. |
| `404 Not Found` | `EdgeNotFoundError` | `EDGE_NOT_FOUND` | Link identifier does not exist. |
| `404 Not Found` | `SimulationNotFoundError` | `SIMULATION_NOT_FOUND` | Simulation execution UUID not found in database. |
| `409 Conflict` | `NetworkVersionConflictError` | `VERSION_CONFLICT` | Stale optimistic version submitted on network edit. |
| `409 Conflict` | `DuplicateEntityError` | `DUPLICATE_ENTITY` | Adding node with duplicate ID to same network. |
| `413 Payload Too Large`| `PayloadTooLargeError` | `PAYLOAD_TOO_LARGE` | JSON upload exceeds 10 MB limit. |
| `422 Unprocessable`| `RequestValidationError`| `VALIDATION_ERROR` | Negative capacity, missing required Pydantic field. |
| `500 Server Error` | `AppException` | `INTERNAL_SERVER_ERROR` | Uncaught internal runtime failure (stack trace withheld). |
| `503 Unavailable` | `DatabaseUnavailableError`| `DATABASE_UNAVAILABLE` | Database pool exhausted or unreachable. |

---

## 3. Resource Bounds & Security Guardrails

To prevent Denial of Service (DoS) attacks and memory exhaustion from excessively large inputs or infinite recursion, strict operational bounds are enforced in `app/core/security.py`:

### 3.1. Upload File Size Boundaries
- **Limit**: $10\text{ MB}$ (`MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024`).
- Any payload exceeding 10 MB is rejected before processing with `PayloadTooLargeError` (HTTP 413).

### 3.2. File Extension Whitelisting
- **Allowed Extensions**: strictly `.json` and `.csv`.
- Files with other extensions are rejected with `BadRequestError` (HTTP 400).

### 3.3. Graph Complexity Boundaries
- **Max Nodes**: $|V| \le 10,000$ (`MAX_NETWORK_NODES = 10000`).
- **Max Edges**: $|E| \le 50,000$ (`MAX_NETWORK_EDGES = 50000`).
- Networks exceeding these parameters are rejected with `BadRequestError` (HTTP 400).

### 3.4. Simulation Bounds
- **Stochastic Percolation Trials**: $N_{\text{trials}} \le 500$ (`MAX_SIMULATION_TRIALS = 500`).
- **Cascading Overload Max Rounds**: $R_{\text{cascade}} \le 100$ (`MAX_CASCADE_ROUNDS = 100`).
- Prevents runaway simulation loops and server lockups.

