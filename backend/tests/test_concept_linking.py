"""Tests for concept linking and graph integration."""

import pytest

from app.db.models import Concept, IngestionStatus, LearnerProfile, Material
from app.ingestion.concept_extractor import ExtractedConcept
from app.ingestion.concept_linker import ConceptLinker


@pytest.mark.asyncio
async def test_concept_linker_reuses_existing_or_creates_new(test_session):
    """Test concept linker matches existing concept or creates new node."""
    # Existing concept
    c_existing = Concept(name="Probability", description="Study of randomness", domain="Math")
    test_session.add(c_existing)
    await test_session.flush()

    learner = LearnerProfile(name="Linker User")
    test_session.add(learner)
    await test_session.flush()

    material = Material(
        learner_id=learner.id,
        title="Stats 101",
        original_filename="stats.txt",
        file_path="/data/stats.txt",
        file_type="txt",
        file_size_bytes=100,
        mime_type="text/plain",
        ingestion_status=IngestionStatus.PROCESSING,
    )
    test_session.add(material)
    await test_session.flush()

    extracted = [
        ExtractedConcept(name="Probability", description="Match existing", domain="Math"),
        ExtractedConcept(name="Bayes Theorem", description="New concept node", domain="Math"),
    ]

    linker = ConceptLinker(test_session)
    assocs = await linker.link_extracted_concepts(material.id, None, extracted)

    assert len(assocs) == 2
    # Verify Probability matched existing ID
    p_assoc = next(a for a in assocs if a.concept_id == c_existing.id)
    assert p_assoc is not None

    # Verify Bayes Theorem created new Concept node
    b_assoc = next(a for a in assocs if a.concept_id != c_existing.id)
    assert b_assoc is not None
