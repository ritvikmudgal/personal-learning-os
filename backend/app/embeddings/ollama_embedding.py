"""Ollama implementation of EmbeddingProvider using nomic-embed-text."""

import httpx

from app.embeddings.base import EmbeddingProvider
from app.utils.logging import get_logger

logger = get_logger("embeddings.ollama")


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Ollama local embedding provider."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "nomic-embed-text",
        dimension: int = 768,
        timeout: int = 60,
    ):
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._dimension = dimension
        self._timeout = timeout

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_name(self) -> str:
        return self._model

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding vector for a single text using Ollama /api/embeddings."""
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * self._dimension

        url = f"{self._base_url}/api/embeddings"
        payload = {
            "model": self._model,
            "prompt": text,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                embedding = data.get("embedding", [])
                if not embedding:
                    logger.warning("Ollama returned empty embedding for text prefix: %s...", text[:30])
                    return [0.0] * self._dimension
                return embedding
        except Exception as e:
            logger.error("Failed to generate embedding from Ollama: %s", str(e))
            raise RuntimeError(f"Ollama embedding error: {e}") from e

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a list of texts sequentially/concurrently."""
        results = []
        for text in texts:
            vec = await self.embed_text(text)
            results.append(vec)
        return results
