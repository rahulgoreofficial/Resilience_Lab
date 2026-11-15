# Phase 0: Academic & Industry References
## Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator

---

### 1. Foundational Discrete Mathematics & Graph Theory Literature

1. **Tarjan, R. E. (1972)**. *Depth-first search and linear graph algorithms*. SIAM Journal on Computing, 1(2), 146-160.
   - DOI: [10.1137/0201010](https://doi.org/10.1137/0201010)
   - *Relevance*: Mathematical foundation for linear-time $O(|V| + |E|)$ articulation point (cut-vertex) and bridge (cut-edge) detection using DFS discovery and low-link numbers.

2. **Hopcroft, J., & Tarjan, R. (1973)**. *Algorithm 447: efficient algorithms for graph manipulation*. Communications of the ACM, 16(6), 372-378.
   - DOI: [10.1145/362248.362272](https://doi.org/10.1145/362248.362272)
   - *Relevance*: Formal derivation of biconnected component decomposition and linear-time connectivity validation.

3. **West, D. B. (2001)**. *Introduction to Graph Theory* (2nd ed.). Prentice Hall, Upper Saddle River, NJ.
   - ISBN: 978-0130144003
   - *Relevance*: Standard undergraduate academic reference for graph connectivity, cut-sets, trees, adjacency matrices, and connectivity bounds ($\kappa(G) \le \lambda(G) \le \delta(G)$).

4. **Brandes, U. (2001)**. *A faster algorithm for betweenness centrality*. Journal of Mathematical Sociology, 25(2), 163-177.
   - DOI: [10.1080/0022250X.2001.9990249](https://doi.org/10.1080/0022250X.2001.9990249)
   - *Relevance*: Provides the $O(|V||E|)$ algorithm used in our Centrality Engine to rank network transit chokepoints without computing the full $O(|V|^3)$ all-pairs shortest paths matrix.

---

### 2. Complex Networks, Percolation & Cascading Failure Literature

5. **Albert, R., Jeong, H., & Barabási, A. L. (2000)**. *Error and attack tolerance of complex networks*. Nature, 406(6794), 378-382.
   - DOI: [10.1038/35019019](https://doi.org/10.1038/35019019)
   - *Relevance*: Theoretical basis for our Random vs. Targeted failure simulation engine; demonstrates the resilience of scale-free topologies against random breakdowns and extreme vulnerability to degree-based hub attacks.

6. **Motter, A. E., & Lai, Y. C. (2002)**. *Cascade-based attacks on complex networks*. Physical Review E, 66(6), 065102.
   - DOI: [10.1103/PhysRevE.66.065102](https://doi.org/10.1103/PhysRevE.66.065102)
   - *Relevance*: The mathematical load-capacity formulation ($C_i = (1 + \alpha) L_i$) implemented in our Cascading Failure Engine to model traffic redirection overloads.

7. **Latora, V., & Marchiori, M. (2001)**. *Efficient behavior of small-world networks*. Physical Review Letters, 87(19), 198701.
   - DOI: [10.1103/PhysRevLett.87.198701](https://doi.org/10.1103/PhysRevLett.87.198701)
   - *Relevance*: Formulates Global Network Efficiency $E_{\text{glob}}(G)$, eliminating mathematical singularities when networks fragment into disconnected components.

8. **Fiedler, M. (1973)**. *Algebraic connectivity of graphs*. Czechoslovak Mathematical Journal, 23(2), 298-305.
   - Handle: [http://hdl.handle.net/10338.dmlcz/101168](http://hdl.handle.net/10338.dmlcz/101168)
   - *Relevance*: Mathematical foundation for using the second smallest eigenvalue ($\lambda_2$) of the graph Laplacian matrix as a global metric of structural network resilience.

---

### 3. Existing Commercial & Open-Source Systems (Verified Official Documentation)

9. **SolarWinds Network Topology Mapper (NTM)**
   - Official Product Portal: [https://www.solarwinds.com/network-topology-mapper](https://www.solarwinds.com/network-topology-mapper)
   - Official Documentation: [https://documentation.solarwinds.com/en/success_center/ntm/content/ntm_documentation.htm](https://documentation.solarwinds.com/en/success_center/ntm/content/ntm_documentation.htm)
   - *Description*: Commercial Layer-2/Layer-3 network discovery and diagramming tool.

10. **Cisco Modeling Labs (CML)**
    - Official Product Portal: [https://www.cisco.com/c/en/us/products/cloud-systems-management/modeling-labs/index.html](https://www.cisco.com/c/en/us/products/cloud-systems-management/modeling-labs/index.html)
    - Official Developer & API Guide: [https://developer.cisco.com/docs/modeling-labs/](https://developer.cisco.com/docs/modeling-labs/)
    - *Description*: Virtualized network emulation platform running authentic Cisco IOS/NX-OS operating system images.

11. **AWS Fault Injection Service (AWS FIS)**
    - Official Product Portal: [https://aws.amazon.com/fis/](https://aws.amazon.com/fis/)
    - Official User Guide: [https://docs.aws.amazon.com/fis/latest/userguide/](https://docs.aws.amazon.com/fis/latest/userguide/)
    - *Description*: Managed chaos engineering and fault injection service for AWS cloud infrastructure.

12. **Chaos Mesh**
    - Official Website: [https://chaos-mesh.org/](https://chaos-mesh.org/)
    - Official Technical Documentation: [https://chaos-mesh.org/docs/](https://chaos-mesh.org/docs/)
    - *Description*: Cloud Native Computing Foundation (CNCF) chaos engineering platform for Kubernetes container environments.

---

### 4. Software Libraries, Frameworks & Engineering Tools

13. **NetworkX (Python Complex Network Analysis)**
    - Official Portal & Documentation: [https://networkx.org/documentation/stable/](https://networkx.org/documentation/stable/)
    - Citation: Hagberg, A., Swart, P., & S Chult, D. (2008). *Exploring network structure, dynamics, and function using NetworkX*. Los Alamos National Laboratory (LANL).

14. **FastAPI (High-Performance Python Web Framework)**
    - Official Portal: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
    - *Description*: Modern, asynchronous REST API framework leveraging Python type annotations and Pydantic schema validation.

15. **Cytoscape.js (Graph Theory & Network Visualization)**
    - Official Portal: [https://js.cytoscape.org/](https://js.cytoscape.org/)
    - Citation: Franz, M., Lopes, C. T., Huck, G., Dong, Y., Sumer, O., & Bader, G. D. (2016). *Cytoscape.js: a graph theory library for visualisation and analysis*. Bioinformatics, 32(2), 309-311. DOI: [10.1093/bioinformatics/btv557](https://doi.org/10.1093/bioinformatics/btv557)

16. **Recharts (Composable Charting for React)**
    - Official Portal: [https://recharts.org/en-US/](https://recharts.org/en-US/)
    - *Description*: Declarative charting library for React and D3 used for real-time resilience degradation curves.

17. **PostgreSQL & SQLAlchemy**
    - PostgreSQL Official Documentation: [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)
    - SQLAlchemy 2.0 Unified Documentation: [https://docs.sqlalchemy.org/en/20/](https://docs.sqlalchemy.org/en/20/)

18. **Pytest (Python Testing Framework)**
    - Official Documentation: [https://docs.pytest.org/en/stable/](https://docs.pytest.org/en/stable/)
    - *Description*: Scalable testing framework for unit and property-based verification of graph algorithms.

