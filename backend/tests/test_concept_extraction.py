"""Tests for LLM-based concept extractor."""

import pytest
from unittest.mock import AsyncMock

from app.ingestion.concept_extractor import ConceptExtractor


@pytest.mark.asyncio
async def test_concept_extractor_parses_json_response():
    """Test concept extractor correctly parses valid JSON array from LLM."""
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = """[
  {
    "name": "Eigenvalues",
    "description": "Scalars associated with linear systems of equations.",
    "domain": "Mathematics",
    "difficulty_level": "intermediate",
    "relevance_score": 0.9
  }
]"""

    extractor = ConceptExtractor(mock_llm)
    concepts = await extractor.extract_concepts_from_chunk(
        "Eigenvalues and eigenvectors are fundamental concepts in linear algebra and systems of equations."
    )

    assert len(concepts) == 1
    assert concepts[0].name == "Eigenvalues"
    assert concepts[0].domain == "Mathematics"
    assert concepts[0].relevance_score == 0.9


@pytest.mark.asyncio
async def test_concept_extractor_handles_empty_or_invalid_text():
    """Test extractor returns empty list for short text or invalid LLM response."""
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Not valid JSON response"

    extractor = ConceptExtractor(mock_llm)
    concepts = await extractor.extract_concepts_from_chunk("Short")
    assert len(concepts) == 0

    concepts2 = await extractor.extract_concepts_from_chunk("A" * 100)
    assert len(concepts2) == 0
