"""FastAPI application for OpenCar."""

from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from opencar import __version__
from opencar.config.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    settings = get_settings()
    app.state.settings = settings

    # Initialize models
    await _initialize_models()

    yield

    # Shutdown
    await _cleanup_resources()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="OpenCar API",
        description="Advanced Autonomous Vehicle Perception System",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Add middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.debug else ["localhost", "*.opencar.ai"],
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add routes
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": __version__}

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "OpenCar API",
            "version": __version__,
            "status": "operational",
            "documentation": "/docs",
        }

    return app


async def _initialize_models() -> None:
    """Initialize ML models."""
    # Mock implementation
    pass


async def _cleanup_resources() -> None:
    """Cleanup resources on shutdown."""
    # Mock implementation
    pass


app = create_app() 