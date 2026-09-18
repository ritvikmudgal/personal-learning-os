"""FastAPI application entry point.

Configures:
- CORS for Tauri frontend
- Application lifespan (startup/shutdown)
- Root API router
- Logging
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.db.database import close_db, init_db
from app.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager — handles startup and shutdown."""
    settings = get_settings()

    # Setup logging
    logger = setup_logging(level=settings.log_level)
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Log LLM provider configuration
    logger.info("LLM provider: %s", settings.llm_provider)
    if settings.llm_provider == "ollama":
        logger.info(
            "Ollama: url=%s model=%s",
            settings.ollama_base_url,
            settings.ollama_model,
        )

    yield

    # Shutdown
    await close_db()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Personal Learning OS — Backend API",
        lifespan=lifespan,
    )

    # CORS middleware for Tauri frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router)

    return app


# Application instance used by uvicorn
app = create_app()
