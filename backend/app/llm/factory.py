"""LLM provider factory — configuration-based provider selection.

Reads configuration to determine which LLM provider to use.
Supports fallback logic: if the primary provider is unavailable,
the system can attempt to use the fallback provider.
"""

from app.config import Settings, get_settings
from app.llm.cloud_provider import CloudProvider
from app.llm.ollama_provider import OllamaProvider
from app.llm.provider import LLMProvider, ProviderHealthResult, ProviderStatus
from app.utils.logging import get_logger

logger = get_logger("llm.factory")

# Module-level provider instances (initialized lazily)
_primary_provider: LLMProvider | None = None
_fallback_provider: LLMProvider | None = None


def _create_ollama_provider(settings: Settings) -> OllamaProvider:
    """Create an Ollama provider from settings."""
    return OllamaProvider(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout=settings.ollama_timeout,
    )


def _create_cloud_provider(settings: Settings) -> CloudProvider:
    """Create a cloud provider from settings."""
    return CloudProvider(
        provider_name=settings.cloud_llm_provider,
        api_key=settings.cloud_llm_api_key,
        model=settings.cloud_llm_model,
        base_url=settings.cloud_llm_base_url,
    )


def get_provider(settings: Settings | None = None) -> LLMProvider:
    """Get the primary LLM provider based on configuration.

    Provider selection:
    - LLM_PROVIDER=ollama → OllamaProvider (default)
    - LLM_PROVIDER=cloud  → CloudProvider

    Returns:
        The configured LLMProvider instance.
    """
    global _primary_provider

    if _primary_provider is not None:
        return _primary_provider

    settings = settings or get_settings()

    if settings.llm_provider == "cloud":
        _primary_provider = _create_cloud_provider(settings)
        logger.info("Primary LLM provider: cloud/%s", settings.cloud_llm_provider)
    else:
        _primary_provider = _create_ollama_provider(settings)
        logger.info(
            "Primary LLM provider: ollama (model=%s, url=%s)",
            settings.ollama_model,
            settings.ollama_base_url,
        )

    return _primary_provider


def get_fallback_provider(settings: Settings | None = None) -> LLMProvider | None:
    """Get the fallback LLM provider.

    If primary is Ollama, fallback is Cloud (and vice versa).
    Returns None if no meaningful fallback is available.
    """
    global _fallback_provider

    if _fallback_provider is not None:
        return _fallback_provider

    settings = settings or get_settings()

    if settings.llm_provider == "ollama":
        # Fallback to cloud if configured
        fallback = _create_cloud_provider(settings)
        if settings.cloud_llm_api_key:
            _fallback_provider = fallback
            logger.info("Fallback LLM provider: cloud/%s", settings.cloud_llm_provider)
            return _fallback_provider
    else:
        # Fallback to Ollama if available
        _fallback_provider = _create_ollama_provider(settings)
        logger.info("Fallback LLM provider: ollama")
        return _fallback_provider

    return None


async def get_healthy_provider(
    settings: Settings | None = None,
) -> tuple[LLMProvider, ProviderHealthResult]:
    """Get a healthy provider, falling back if the primary is unavailable.

    Tries the primary provider first. If it's unavailable and a fallback
    exists, tries the fallback.

    Returns:
        Tuple of (provider, health_result) for the first available provider.

    Raises:
        RuntimeError: If no provider is available.
    """
    primary = get_provider(settings)
    health = await primary.health_check()

    if health.status == ProviderStatus.AVAILABLE:
        return primary, health

    logger.warning(
        "Primary provider '%s' is %s: %s",
        primary.name,
        health.status,
        health.message,
    )

    # Try fallback
    fallback = get_fallback_provider(settings)
    if fallback is not None:
        fallback_health = await fallback.health_check()
        if fallback_health.status == ProviderStatus.AVAILABLE:
            logger.info("Using fallback provider: %s", fallback.name)
            return fallback, fallback_health

    # No provider available
    return primary, health


def reset_providers() -> None:
    """Reset provider instances. Useful for testing and reconfiguration."""
    global _primary_provider, _fallback_provider
    _primary_provider = None
    _fallback_provider = None
