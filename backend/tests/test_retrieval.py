"""Tests for cosine similarity and RetrievalService semantic search."""

import pytest
from unittest.mock import AsyncMock

from app.db.models import DocumentChunk, IngestionStatus, LearnerProfile, Material
from app.services.retrieval_service import RetrievalService, cosine_similarity


def test_cosine_similarity():
    """Test cosine similarity vector math."""
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    v4 = [0.7071, 0.7071, 0.0]

    assert pytest.approx(cosine_similarity(v1, v2), 0.001) == 1.0
    assert pytest.approx(cosine_similarity(v1, v3), 0.001) == 0.0
    assert pytest.approx(cosine_similarity(v1, v4), 0.001) == 0.7071


@pytest.mark.asyncio
async def test_retrieval_service_search(test_session):
    """Test RetrievalService vector search over document chunks."""
    learner = LearnerProfile(name="Vector Learner")
    test_session.add(learner)
    await test_session.flush()

    material = Material(
        learner_id=learner.id,
        title="AI Foundations",
        original_filename="ai.txt",
        file_path="/data/ai.txt",
        file_type="txt",
        file_size_bytes=500,
        mime_type="text/plain",
        ingestion_status=IngestionStatus.COMPLETED,
    )
    test_session.add(material)
    await test_session.flush()

    # Chunk 1: vector pointing along X axis
    c1 = DocumentChunk(
        material_id=material.id,
        chunk_index=0,
        content="Neural Networks and Backpropagation.",
        clean_content="Neural Networks and Backpropagation.",
        start_char=0,
        end_char=35,
        page_number=1,
        token_count=5,
        embedding=[1.0, 0.0, 0.0],
        embedding_model="nomic-embed-text",
    )
    # Chunk 2: vector pointing along Y axis
    c2 = DocumentChunk(
        material_id=material.id,
        chunk_index=1,
        content="Calculus and Derivatives.",
        clean_content="Calculus and Derivatives.",
        start_char=36,
        end_char=60,
        page_number=1,
        token_count=4,
        embedding=[0.0, 1.0, 0.0],
        embedding_model="nomic-embed-text",
    )
    test_session.add_all([c1, c2])
    await test_session.flush()

    # Mock embedding provider to return [1.0, 0.0, 0.0] for query
    mock_provider = AsyncMock()
    mock_provider.embed_text.return_value = [1.0, 0.0, 0.0]

    service = RetrievalService(test_session, mock_provider)
    results = await service.search_semantic(query="Neural nets", learner_id=learner.id, top_k=2)

    assert len(results) == 2
    assert results[0].chunk_id == c1.id
    assert results[0].similarity_score == 1.0
    assert results[1].chunk_id == c2.id
    assert results[1].similarity_score == 0.0
