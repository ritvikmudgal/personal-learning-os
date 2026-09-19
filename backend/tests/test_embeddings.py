"""Tests for embedding provider (Ollama / Mock)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.embeddings.ollama_embedding import OllamaEmbeddingProvider


@pytest.mark.asyncio
async def test_ollama_embedding_provider_mock():
    """Test Ollama embedding provider with mocked httpx post response."""
    provider = OllamaEmbeddingProvider(model="nomic-embed-text", dimension=4)

    fake_vector = [0.1, 0.2, 0.3, 0.4]

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"embedding": fake_vector}
        mock_post.return_value = mock_resp

        vec = await provider.embed_text("Machine learning vector test")
        assert vec == fake_vector
        assert provider.dimension == 4
        assert provider.model_name == "nomic-embed-text"


@pytest.mark.asyncio
async def test_ollama_embedding_batch():
    """Test batch embedding generation."""
    provider = OllamaEmbeddingProvider(dimension=3)

    with patch.object(provider, "embed_text", side_effect=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]):
        batch = await provider.embed_batch(["text1", "text2"])
        assert len(batch) == 2
        assert batch[0] == [1.0, 0.0, 0.0]
        assert batch[1] == [0.0, 1.0, 0.0]
