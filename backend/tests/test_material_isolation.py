"""CRITICAL ISOLATION TEST: Verify material ingestion NEVER modifies Learner Knowledge State."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from app.db.models import Concept, KnowledgeState
from app.db.repositories.concept_repo import ConceptRepository
from app.db.repositories.learner_repo import LearnerRepository
from app.domain.concept import ConceptCreate
from app.domain.learner import LearnerCreate
from app.services.learner_state_service import LearnerStateService


@pytest.mark.asyncio
async def test_material_ingestion_preserves_learner_state_exactly(client: AsyncClient, test_session):
    """Verify material upload and ingestion leaves learner state 100% unchanged."""
    # 1. Setup learner and concept with baseline knowledge state
    learner_repo = LearnerRepository(test_session)
    learner = await learner_repo.create(LearnerCreate(name="Isolation Tester"))

    concept_repo = ConceptRepository(test_session)
    concept = await concept_repo.create(
        ConceptCreate(
            name="Linear Transformation",
            description="Mapping between vector spaces",
            domain="Linear Algebra",
        )
    )

    state_service = LearnerStateService(test_session)
    baseline_state = await state_service.get_or_create_state(learner.id, concept.id)
    baseline_state.mastery_probability = 0.45
    baseline_state.knowledge_strength = 0.60
    baseline_state.forgetting_state = 0.15
    baseline_state.confidence = 0.50
    baseline_state.evidence_reliability = 0.80
    baseline_state.misconception_severity = 0.00
    await test_session.flush()
    await test_session.commit()

    # Record snapshot values
    snapshot_mastery = baseline_state.mastery_probability
    snapshot_strength = baseline_state.knowledge_strength
    snapshot_forgetting = baseline_state.forgetting_state
    snapshot_confidence = baseline_state.confidence
    snapshot_reliability = baseline_state.evidence_reliability
    snapshot_misconception = baseline_state.misconception_severity

    # 2. Perform full material upload and ingestion pipeline
    with patch("app.api.library.get_embedding_provider") as mock_emb_factory:
        mock_provider = AsyncMock()
        mock_provider.model_name = "nomic-embed-text"
        mock_provider.embed_batch.return_value = [[0.2] * 768]
        mock_emb_factory.return_value = mock_provider

        files = {
            "file": (
                "linear_transformations.txt",
                b"Linear Transformation mappings from space V to space W preserve vector addition and scalar multiplication.",
                "text/plain",
            )
        }
        data = {"learner_id": str(learner.id)}

        upload_resp = await client.post("/api/library/upload", files=files, data=data)
        assert upload_resp.status_code == 201

    # 3. Re-query knowledge state from database
    current_state = await state_service.get_or_create_state(learner.id, concept.id)

    # 4. ASSERT ABSOLUTE ISOLATION
    assert current_state.mastery_probability == snapshot_mastery, "Mastery probability must NOT change during material ingestion!"
    assert current_state.knowledge_strength == snapshot_strength, "Knowledge strength must NOT change during material ingestion!"
    assert current_state.forgetting_state == snapshot_forgetting, "Forgetting state must NOT change during material ingestion!"
    assert current_state.confidence == snapshot_confidence, "Confidence must NOT change during material ingestion!"
    assert current_state.evidence_reliability == snapshot_reliability, "Evidence reliability must NOT change during material ingestion!"
    assert current_state.misconception_severity == snapshot_misconception, "Misconception severity must NOT change during material ingestion!"
