"""
API v1 Router Aggregator for Aegis.
"""

from fastapi import APIRouter
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.documents import router as documents_router

api_v1_router = APIRouter()

# Register sub-routers
api_v1_router.include_router(health_router, prefix="", tags=["Health"])
api_v1_router.include_router(documents_router)
