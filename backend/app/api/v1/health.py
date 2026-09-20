"""
Health check endpoints for Aegis Backend Service.
Provides liveness, readiness, and subsystem configuration inspection.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.config.settings import Settings, get_settings

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    region: str
    timestamp: str
    subsystems: Dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def get_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Primary health and readiness probe endpoint.
    Reports operational status and configured AWS resource references.
    Does not expose sensitive credentials.
    """
    subsystems = {
        "s3": {
            "documents_bucket": settings.s3_bucket_documents,
            "configured": bool(settings.s3_bucket_documents),
        },
        "dynamodb": {
            "documents_table": settings.dynamodb_documents_table,
            "conversations_table": settings.dynamodb_conversations_table,
            "evaluations_table": settings.dynamodb_evaluations_table,
            "configured": bool(settings.dynamodb_documents_table),
        },
        "bedrock": {
            "region": settings.bedrock_region,
            "embedding_model": settings.bedrock_embedding_model_id,
            "generation_model": settings.bedrock_generation_model_id,
            "configured": bool(settings.bedrock_embedding_model_id and settings.bedrock_generation_model_id),
        },
        "opensearch": {
            "endpoint_configured": bool(settings.opensearch_endpoint),
            "index": settings.opensearch_index,
        },
        "verification_engine": {
            "grounding_threshold": settings.grounding_threshold,
            "max_self_correction_attempts": settings.max_self_correction_attempts,
            "active": True,
        },
    }

    return HealthResponse(
        status="healthy",
        service="aegis-backend",
        version=settings.app_version,
        environment=settings.app_env,
        region=settings.aws_region,
        timestamp=datetime.now(timezone.utc).isoformat(),
        subsystems=subsystems,
    )
