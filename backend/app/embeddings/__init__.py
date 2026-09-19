"""Embedding subsystem for vector generation."""

from app.embeddings.base import EmbeddingProvider
from app.embeddings.factory import get_embedding_provider
from app.embeddings.ollama_embedding import OllamaEmbeddingProvider

__all__ = ["EmbeddingProvider", "OllamaEmbeddingProvider", "get_embedding_provider"]
