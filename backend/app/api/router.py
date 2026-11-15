"""
Master API Router: Assembles v1 endpoints.
"""

from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.networks import router as networks_router
from app.api.v1.nodes import router as nodes_router
from app.api.v1.edges import router as edges_router
from app.api.v1.simulations import router as simulations_router
from app.api.v1.analytics import router as analytics_router

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(networks_router)
api_v1_router.include_router(nodes_router)
api_v1_router.include_router(edges_router)
api_v1_router.include_router(simulations_router)
api_v1_router.include_router(analytics_router)

__all__ = ["api_v1_router"]

