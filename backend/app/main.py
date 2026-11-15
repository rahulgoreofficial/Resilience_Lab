"""
FastAPI Application Entry Point.
Configures CORS, centralized exception handling, lifespan startup recovery,
v1 REST routes, and WebSocket endpoints.
"""

from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import AppException
from app.graph_engine.graph_validation import GraphException
from app.database.session import get_db_context
from app.database.init_db import recover_interrupted_simulations
from app.services.persistence_service import PersistenceService
from app.api.router import api_v1_router
from app.websockets.simulation_ws import ws_router

# Phase 2-7 legacy graph & algorithm routes for backward compatibility
from app.schemas.graph_schema import (
    HealthResponse,
    DatabaseHealthResponse,
    GraphDataSchema,
    BFSRequest,
    DijkstraRequest
)
from app.schemas.simulation_schema import (
    NodeFailureRequest,
    EdgeFailureRequest,
    MultipleFailureRequest,
    RandomFailureRequest,
    TargetedFailureRequest,
    CascadingFailureRequest
)
from app.schemas.resilience_schema import (
    ResilienceAnalysisRequest,
    CriticalityRequest,
    AlternativeRoutesRequest,
    ScenarioComparisonRequest
)
from app.graph_engine.graph_builder import NetworkGraph
from app.graph_engine.graph_representation import GraphRepresentation
from app.algorithms.bfs import breadth_first_search
from app.algorithms.dfs import depth_first_search
from app.algorithms.connected_components import find_connected_components
from app.algorithms.degree_analysis import analyze_degrees
from app.algorithms.articulation_points import find_articulation_points
from app.algorithms.bridges import find_bridges
from app.algorithms.shortest_path import dijkstra_shortest_path
from app.simulation import (
    simulation_manager,
    simulate_random_failure,
    simulate_targeted_failure,
    simulate_cascading_failure
)
from app.resilience import (
    analyze_network_connectivity,
    analyze_node_criticality,
    analyze_edge_criticality,
    analyze_alternative_routes,
    compare_failure_scenarios,
    generate_resilience_report
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: executes startup recovery and database seeding."""
    setup_logging()
    logger.info("Initializing application lifecycle...")

    # Ensure database tables exist (auto-create tables if missing)
    try:
        from app.database.init_db import init_db
        from app.database.session import engine
        init_db(engine)
        logger.info("Database schema initialized and verified.")
    except Exception as exc:
        logger.error(f"Database schema initialization failed: {exc}", exc_info=True)

    # Startup recovery: mark in-flight runs as interrupted and seed default network if empty
    try:
        with get_db_context() as db:
            recover_interrupted_simulations(db)
            PersistenceService.seed_sample_network(db)
    except Exception as exc:
        logger.warning(f"Database initialization deferred (service may be starting): {exc}")

    yield

    logger.info("Shutting down application lifecycle.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Discrete Mathematics Graph-Theoretic Resilience Simulator REST API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
# Centralized Error Handlers
# =====================================================================

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Standardized response for domain application exceptions."""
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


@app.exception_handler(GraphException)
async def graph_exception_handler(request: Request, exc: GraphException):
    """Translates graph structure/validation errors to 400 Bad Request."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "GRAPH_STRUCTURE_ERROR",
                "message": str(exc),
                "details": None
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Translates Pydantic validation errors to standardized 422 response."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed.",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Prevents unhandled stack trace leakage for unexpected internal errors."""
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "details": None
            }
        }
    )


# =====================================================================
# Mount Layered v1 Routers & WebSockets
# =====================================================================

app.include_router(api_v1_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)


# =====================================================================
# Backward-Compatible Direct Routes (/api/...)
# =====================================================================

@app.get(f"{settings.API_V1_STR}/health", response_model=HealthResponse, tags=["Legacy System"])
def get_health() -> Dict[str, Any]:
    return {"status": "healthy", "version": settings.VERSION, "project": settings.PROJECT_NAME}


@app.get(f"{settings.API_V1_STR}/version", tags=["Legacy System"])
def get_version() -> Dict[str, str]:
    return {"version": settings.VERSION, "project_name": settings.PROJECT_NAME, "phase": "Phase 8"}


@app.get(f"{settings.API_V1_STR}/database-health", response_model=DatabaseHealthResponse, tags=["Legacy System"])
def get_database_health() -> Dict[str, Any]:
    from app.database.session import check_db_connection
    return check_db_connection()


@app.post(f"{settings.API_V1_STR}/graph/representations", tags=["Legacy Graph Engine"])
def get_graph_representations(payload: GraphDataSchema) -> Dict[str, Any]:
    graph = NetworkGraph.from_dict(payload.model_dump())
    rep = GraphRepresentation(graph)
    ordered_nodes, matrix_list, _ = rep.to_adjacency_matrix()
    return {
        "ordered_nodes": ordered_nodes,
        "adjacency_matrix": matrix_list,
        "adjacency_list": rep.to_adjacency_list(),
        "is_consistent": rep.verify_representation_consistency()
    }


@app.post(f"{settings.API_V1_STR}/algorithms/bfs", tags=["Legacy Algorithms"])
def run_bfs(payload: GraphDataSchema, req: BFSRequest) -> Dict[str, Any]:
    graph = NetworkGraph.from_dict(payload.model_dump())
    return breadth_first_search(graph, req.start_node)


@app.post(f"{settings.API_V1_STR}/algorithms/dfs", tags=["Legacy Algorithms"])
def run_dfs(payload: GraphDataSchema, req: BFSRequest) -> Dict[str, Any]:
    graph = NetworkGraph.from_dict(payload.model_dump())
    return depth_first_search(graph, req.start_node)


@app.post(f"{settings.API_V1_STR}/algorithms/connected-components", tags=["Legacy Algorithms"])
def run_connected_components(payload: GraphDataSchema) -> Dict[str, Any]:
    graph = NetworkGraph.from_dict(payload.model_dump())
    return find_connected_components(graph)


@app.post(f"{settings.API_V1_STR}/algorithms/degree-analysis", tags=["Legacy Algorithms"])
def run_degree_analysis(payload: GraphDataSchema) -> Dict[str, Any]:
    graph = NetworkGraph.from_dict(payload.model_dump())
    return analyze_degrees(graph)


@app.post(f"{settings.API_V1_STR}/algorithms/articulation-points", tags=["Legacy Algorithms"])
def run_articulation_points(payload: GraphDataSchema) -> Dict[str, Any]:
    graph = NetworkGraph.from_dict(payload.model_dump())
    return find_articulation_points(graph)


@app.post(f"{settings.API_V1_STR}/algorithms/bridges", tags=["Legacy Algorithms"])
def run_bridges(payload: GraphDataSchema) -> Dict[str, Any]:
    graph = NetworkGraph.from_dict(payload.model_dump())
    return find_bridges(graph)


@app.post(f"{settings.API_V1_STR}/algorithms/shortest-path", tags=["Legacy Algorithms"])
def run_shortest_path(payload: GraphDataSchema, req: DijkstraRequest) -> Dict[str, Any]:
    graph = NetworkGraph.from_dict(payload.model_dump())
    return dijkstra_shortest_path(graph, req.source, req.target, req.weight_attribute)


@app.post(f"{settings.API_V1_STR}/simulations/node-failure", tags=["Legacy Simulations"])
def api_simulate_node_failure(req: NodeFailureRequest) -> Dict[str, Any]:
    try:
        graph = NetworkGraph.from_dict(req.graph.model_dump())
        return simulation_manager.run_node_failure(graph, req.failed_node_ids, req.entry_points, req.critical_services).to_dict()
    except GraphException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.post(f"{settings.API_V1_STR}/simulations/edge-failure", tags=["Legacy Simulations"])
def api_simulate_edge_failure(req: EdgeFailureRequest) -> Dict[str, Any]:
    try:
        graph = NetworkGraph.from_dict(req.graph.model_dump())
        return simulation_manager.run_edge_failure(graph, req.failed_edges, req.entry_points, req.critical_services).to_dict()
    except GraphException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.post(f"{settings.API_V1_STR}/simulations/multiple-failure", tags=["Legacy Simulations"])
def api_simulate_multiple_failure(req: MultipleFailureRequest) -> Dict[str, Any]:
    try:
        graph = NetworkGraph.from_dict(req.graph.model_dump())
        return simulation_manager.run_multiple_failures(graph, req.failed_node_ids, req.failed_edges, req.entry_points, req.critical_services).to_dict()
    except GraphException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.post(f"{settings.API_V1_STR}/simulations/random", tags=["Legacy Simulations"])
def api_simulate_random_failure(req: RandomFailureRequest) -> Dict[str, Any]:
    try:
        graph = NetworkGraph.from_dict(req.graph.model_dump())
        return simulate_random_failure(graph, req.failure_target, req.failure_count, req.failure_percentage, req.num_trials, req.random_seed, req.selection_method, req.entry_points, req.critical_services)
    except GraphException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.post(f"{settings.API_V1_STR}/simulations/targeted", tags=["Legacy Simulations"])
def api_simulate_targeted_failure(req: TargetedFailureRequest) -> Dict[str, Any]:
    try:
        graph = NetworkGraph.from_dict(req.graph.model_dump())
        return simulate_targeted_failure(graph, req.strategy, req.failure_count, req.failure_percentage, req.adaptive, req.entry_points, req.critical_services)
    except GraphException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.post(f"{settings.API_V1_STR}/simulations/cascading", tags=["Legacy Simulations"])
def api_simulate_cascading_failure(req: CascadingFailureRequest) -> Dict[str, Any]:
    try:
        graph = NetworkGraph.from_dict(req.graph.model_dump())
        res = simulate_cascading_failure(graph, req.initial_failed_nodes, req.initial_failed_edges, req.traffic_demands, req.overload_threshold, req.max_simulation_rounds, req.entry_points, req.critical_services)
        simulation_manager.registry.register(res)
        return res.to_dict()
    except GraphException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.get(f"{settings.API_V1_STR}/simulations", tags=["Legacy Simulations"])
def api_list_simulations(limit: int = 100) -> List[Dict[str, Any]]:
    return simulation_manager.list_simulations(limit=limit)


@app.get(f"{settings.API_V1_STR}/simulations/{{simulation_id}}", tags=["Legacy Simulations"])
def api_get_simulation(simulation_id: str) -> Dict[str, Any]:
    res = simulation_manager.get_simulation(simulation_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation '{simulation_id}' not found.")
    return res.to_dict()


@app.get(f"{settings.API_V1_STR}/simulations/{{simulation_id}}/results", tags=["Legacy Simulations"])
def api_get_simulation_results(simulation_id: str) -> Dict[str, Any]:
    res = simulation_manager.get_simulation(simulation_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation '{simulation_id}' not found.")
    data = res.to_dict()
    return {"simulation_id": data["simulation_id"], "status": data["status"], "metrics": data["metrics"], "connected_components": data["connected_components"], "failed_nodes": data["failed_nodes"], "failed_edges": data["failed_edges"]}


@app.get(f"{settings.API_V1_STR}/simulations/{{simulation_id}}/events", tags=["Legacy Simulations"])
def api_get_simulation_events(simulation_id: str) -> Dict[str, Any]:
    res = simulation_manager.get_simulation(simulation_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation '{simulation_id}' not found.")
    return {"simulation_id": res.simulation_id, "events": res.events}


@app.post(f"{settings.API_V1_STR}/resilience/analyze", tags=["Legacy Resilience"])
def api_analyze_resilience(req: ResilienceAnalysisRequest) -> Dict[str, Any]:
    graph = NetworkGraph.from_dict(req.graph.model_dump())
    return analyze_network_connectivity(graph, req.entry_points, req.critical_services)


@app.post(f"{settings.API_V1_STR}/resilience/criticality/nodes", tags=["Legacy Resilience"])
def api_node_criticality(req: CriticalityRequest) -> List[Dict[str, Any]]:
    graph = NetworkGraph.from_dict(req.graph.model_dump())
    return analyze_node_criticality(graph, req.entry_points, req.critical_services, req.max_components)


@app.post(f"{settings.API_V1_STR}/resilience/criticality/edges", tags=["Legacy Resilience"])
def api_edge_criticality(req: CriticalityRequest) -> List[Dict[str, Any]]:
    graph = NetworkGraph.from_dict(req.graph.model_dump())
    return analyze_edge_criticality(graph, req.entry_points, req.critical_services, req.max_components)


@app.post(f"{settings.API_V1_STR}/resilience/alternative-routes", tags=["Legacy Resilience"])
def api_alternative_routes(req: AlternativeRoutesRequest) -> List[Dict[str, Any]]:
    graph = NetworkGraph.from_dict(req.graph.model_dump())
    flow_tuples = [(pair[0], pair[1]) for pair in req.flow_pairs if len(pair) == 2]
    return analyze_alternative_routes(graph, flow_tuples, req.failed_node_ids, req.failed_edge_ids, req.weight_attribute)


@app.post(f"{settings.API_V1_STR}/resilience/compare-scenarios", tags=["Legacy Resilience"])
def api_compare_scenarios(req: ScenarioComparisonRequest) -> Dict[str, Any]:
    graph = NetworkGraph.from_dict(req.graph.model_dump())
    return compare_failure_scenarios(graph, req.scenarios, req.entry_points, req.critical_services)


@app.post(f"{settings.API_V1_STR}/resilience/report", tags=["Legacy Resilience"])
def api_generate_report(req: ResilienceAnalysisRequest) -> Dict[str, Any]:
    graph = NetworkGraph.from_dict(req.graph.model_dump())
    return generate_resilience_report(graph, req.entry_points, req.critical_services)


# =====================================================================
# System Management & Production Static Frontend Serving
# =====================================================================

@app.post(f"{settings.API_V1_STR}/system/shutdown", tags=["System Management"])
def api_system_shutdown(request: Request) -> Dict[str, str]:
    """
    Gracefully shuts down the backend process.
    Strictly restricted to localhost/loopback requests to prevent unauthorized external access.
    """
    client_host = request.client.host if request.client else ""
    if client_host not in ("127.0.0.1", "::1", "localhost", "testclient"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Shutdown endpoint is restricted to localhost only."
        )

    import os
    import signal
    import threading
    def _delayed_shutdown():
        import time
        time.sleep(0.5)
        try:
            os.kill(os.getpid(), signal.SIGTERM)
        except Exception:
            os._exit(0)

    threading.Thread(target=_delayed_shutdown, daemon=True).start()
    return {"status": "shutting_down", "message": "Backend server is terminating cleanly."}


# Mount production frontend if distribution directory is present
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sys
from pathlib import Path


def find_frontend_dist() -> Optional[Path]:
    """Resolves production frontend build directory across development and frozen PyInstaller package."""
    import os
    if "FRONTEND_DIST" in os.environ:
        p = Path(os.environ["FRONTEND_DIST"]).resolve()
        if p.is_dir() and (p / "index.html").is_file():
            return p

    # Frozen PyInstaller directory inspection
    if getattr(sys, "frozen", False):
        base_dir = Path(getattr(sys, "_MEIPASS", sys.executable)).resolve()
        if not base_dir.is_dir():
            base_dir = base_dir.parent
        for candidate in [base_dir / "frontend_dist", base_dir / "static", base_dir / "frontend" / "dist"]:
            if candidate.is_dir() and (candidate / "index.html").is_file():
                return candidate

    # Development repository directory structure
    repo_root = Path(__file__).resolve().parents[2]
    dev_candidate = repo_root / "frontend" / "dist"
    if dev_candidate.is_dir() and (dev_candidate / "index.html").is_file():
        return dev_candidate
    return None


frontend_dist_dir = find_frontend_dist()
if frontend_dist_dir:
    assets_dir = frontend_dist_dir / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa_frontend(full_path: str):
        """Serves compiled frontend assets and falls back to index.html for client-side routing."""
        if full_path.startswith("api") or full_path.startswith("ws"):
            raise HTTPException(status_code=404, detail="API route not found.")
        target_file = frontend_dist_dir / full_path
        if full_path and target_file.is_file():
            return FileResponse(str(target_file))
        return FileResponse(str(frontend_dist_dir / "index.html"))

