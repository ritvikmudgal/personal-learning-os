"""Base interface for embedding providers."""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Generate an embedding vector for a single string.

        Args:
            text: Input text string.

        Returns:
            List of floats representing the embedding vector.
        """
        pass

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a batch of strings.

        Args:
            texts: List of input text strings.

        Returns:
            List of embedding vectors.
        """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the vector dimension size (e.g. 768)."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model name."""
        pass
