"""Factory for creating EmbeddingProvider instances."""

from app.config import get_settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.ollama_embedding import OllamaEmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    """Instantiate and return the configured embedding provider."""
    settings = get_settings()
    provider_name = settings.embedding_provider.lower()

    if provider_name == "ollama":
        return OllamaEmbeddingProvider(
            base_url=settings.ollama_base_url,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
            timeout=settings.ollama_timeout,
        )
    else:
        raise ValueError(f"Unsupported embedding provider: '{provider_name}'")
