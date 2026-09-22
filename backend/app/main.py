"""
Aegis - Self-Correcting Multimodal RAG Backend
Main FastAPI Application Entrypoint
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config.settings import get_settings
from backend.app.api.v1.router import api_v1_router
from backend.app.api.v1.health import get_health, HealthResponse

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"Starting Aegis Knowledge Intelligence Engine v{settings.app_version} "
        f"[Env: {settings.app_env}, Region: {settings.aws_region}]"
    )
    yield
    logger.info("Shutting down Aegis Service")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-oriented evidence-first knowledge intelligence platform with self-correcting RAG.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root level health endpoint for load balancers & direct container probes
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def root_health():
    return await get_health(settings)


# Register API v1 routes
app.include_router(api_v1_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=(settings.app_env == "development"),
    )
