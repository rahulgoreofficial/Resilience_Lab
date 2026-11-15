"""
Analytics and Resilience Endpoints.
Exposes topological metrics, criticality rankings, and scenario evaluations.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.dependencies import get_database
from app.services.analytics_service import AnalyticsService
from app.schemas.resilience_schema import (
    AlternativeRoutesRequest,
    ScenarioComparisonRequest
)

router = APIRouter(prefix="/networks/{network_id}", tags=["Analytics"])


@router.api_route("/analysis", methods=["GET", "POST"])
def get_network_analysis(
    network_id: str,
    entry_points: Optional[List[str]] = Query(default=None),
    critical_services: Optional[List[str]] = Query(default=None),
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Computes full topological connectivity and critical service accessibility profile."""
    return AnalyticsService.analyze_resilience(
        db=db,
        network_id=network_id,
        entry_points=entry_points,
        critical_services=critical_services
    )


@router.api_route("/criticality", methods=["GET", "POST"])
def get_network_criticality(
    network_id: str,
    entry_points: Optional[List[str]] = Query(default=None),
    critical_services: Optional[List[str]] = Query(default=None),
    max_components: Optional[int] = Query(default=None),
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Computes measured node and edge criticality rankings."""
    return AnalyticsService.analyze_criticality(
        db=db,
        network_id=network_id,
        entry_points=entry_points,
        critical_services=critical_services,
        max_components=max_components
    )


@router.api_route("/connectivity", methods=["GET", "POST"])
def get_network_connectivity(
    network_id: str,
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Computes connected components, giant component, LCC ratio, and pairwise connectivity."""
    full_analysis = AnalyticsService.analyze_resilience(db=db, network_id=network_id)
    return {
        "active_vertices": full_analysis["active_vertices"],
        "active_edges": full_analysis["active_edges"],
        "component_count": full_analysis["component_count"],
        "giant_component_size": full_analysis["giant_component_size"],
        "lcc_ratio": full_analysis["lcc_ratio"],
        "pairwise_connectivity": full_analysis["pairwise_connectivity"],
        "connectivity_loss": full_analysis["connectivity_loss"],
        "isolated_nodes": full_analysis["isolated_nodes"]
    }


@router.api_route("/resilience", methods=["GET", "POST"])
def get_network_resilience(
    network_id: str,
    entry_points: Optional[List[str]] = Query(default=None),
    critical_services: Optional[List[str]] = Query(default=None),
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Computes service reachability and resilience scores."""
    full = AnalyticsService.analyze_resilience(
        db=db,
        network_id=network_id,
        entry_points=entry_points,
        critical_services=critical_services
    )
    return {
        "critical_services_status": full["critical_services_status"],
        "critical_services": full["critical_services"],
        "reachable_critical_services": full["reachable_critical_services"],
        "unreachable_critical_services": full["unreachable_critical_services"],
        "pairwise_connectivity": full["pairwise_connectivity"],
        "lcc_ratio": full["lcc_ratio"]
    }


@router.post("/comparisons")
def compare_scenarios(
    network_id: str,
    payload: ScenarioComparisonRequest,
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Compares baseline network resilience against multiple hypothetical failure scenarios."""
    return AnalyticsService.compare_scenarios(
        db=db,
        network_id=network_id,
        scenarios=payload.scenarios,
        entry_points=payload.entry_points,
        critical_services=payload.critical_services
    )


@router.api_route("/report", methods=["GET", "POST"])
def get_resilience_report(
    network_id: str,
    entry_points: Optional[List[str]] = Query(default=None),
    critical_services: Optional[List[str]] = Query(default=None),
    top_k: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """Generates an executive structural health audit and mitigation recommendations."""
    return AnalyticsService.generate_report(
        db=db,
        network_id=network_id,
        entry_points=entry_points,
        critical_services=critical_services,
        top_k=top_k
    )


@router.api_route("/candidate-links", methods=["GET", "POST"])
def evaluate_candidate_links(
    network_id: str,
    target_bridge_id: Optional[str] = Query(default=None),
    target_failure_source: Optional[str] = Query(default=None),
    target_failure_target: Optional[str] = Query(default=None),
    max_recommendations: int = Query(default=10, ge=1, le=50),
    payload: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """
    Evaluates candidate redundant backup links (u, v) not in E to mitigate bridge failures.
    Ranks suggestions by Delta LCC, Delta Pairwise, eliminated bridges, and cost-benefit ratio.
    """
    graph_dict = payload.get("graph") if payload else None
    t_bridge = (payload.get("target_bridge_id") if payload else None) or target_bridge_id
    t_nodes = payload.get("target_failure_nodes") if payload else None
    if not t_nodes and target_failure_source and target_failure_target:
        t_nodes = [target_failure_source, target_failure_target]
    entry_pts = payload.get("entry_points") if payload else None
    crit_svcs = payload.get("critical_services") if payload else None
    max_rec = (payload.get("max_recommendations") if payload else None) or max_recommendations

    return AnalyticsService.evaluate_candidate_backup_links(
        db=db,
        network_id=network_id,
        graph_data=graph_dict,
        target_bridge_id=t_bridge,
        target_failure_nodes=t_nodes,
        entry_points=entry_pts,
        critical_services=crit_svcs,
        max_recommendations=max_rec
    )


@router.post("/alternative-routes")
def get_alternative_routes(
    network_id: str,
    payload: AlternativeRoutesRequest,
    db: Session = Depends(get_database)
) -> List[Dict[str, Any]]:
    """Evaluates primary vs alternative routes under component disruptions."""
    flow_tuples = [(pair[0], pair[1]) for pair in payload.flow_pairs if len(pair) == 2]
    return AnalyticsService.analyze_alternative_routes(
        db=db,
        network_id=network_id,
        flow_pairs=flow_tuples,
        failed_node_ids=payload.failed_node_ids,
        failed_edge_ids=payload.failed_edge_ids,
        weight_attribute=payload.weight_attribute
    )



