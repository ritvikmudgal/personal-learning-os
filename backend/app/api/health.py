"""Health check endpoints.

Provides status information about:
- The application itself
- Ollama connectivity and model availability
- The active LLM provider
"""

from dataclasses import asdict

from fastapi import APIRouter

from app.config import get_settings
from app.llm.factory import get_fallback_provider, get_provider
from app.utils.logging import get_logger

logger = get_logger("api.health")

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Basic application health check."""
    settings = get_settings()
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/ollama")
async def ollama_status():
    """Check Ollama connectivity and available models.

    This endpoint directly checks the Ollama instance regardless
    of which provider is configured as primary.
    """
    from app.llm.ollama_provider import OllamaProvider

    settings = get_settings()
    ollama = OllamaProvider(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )
    result = await ollama.health_check()

    return {
        "provider": result.provider_name,
        "status": result.status.value,
        "message": result.message,
        "configured_model": settings.ollama_model,
        "active_model": result.active_model,
        "available_models": [
            {
                "name": m.name,
                "size": m.size,
            }
            for m in result.available_models
        ],
    }


@router.get("/llm")
async def llm_provider_status():
    """Check the active LLM provider status and fallback availability."""
    settings = get_settings()
    provider = get_provider(settings)
    primary_health = await provider.health_check()

    response = {
        "primary_provider": provider.name,
        "primary_status": primary_health.status.value,
        "primary_message": primary_health.message,
        "active_model": primary_health.active_model,
        "fallback_provider": None,
        "fallback_status": None,
    }

    # Check fallback
    fallback = get_fallback_provider(settings)
    if fallback is not None:
        fallback_health = await fallback.health_check()
        response["fallback_provider"] = fallback.name
        response["fallback_status"] = fallback_health.status.value

    return response
