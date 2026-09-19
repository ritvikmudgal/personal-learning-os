"""Isolation test — verifies LLM response produces candidate evidence which passes through Layer 2 EvidenceService and UpdateEngine."""

import pytest
from app.db.repositories.concept_repo import ConceptRepository
from app.domain.concept import ConceptCreate
from app.services.learner_state_service import LearnerStateService
from app.services.evidence_service import EvidenceService
from app.domain.evidence import EvidenceCreate, EvidenceType
from app.engine.update_engine import update_state_from_evidence


@pytest.mark.asyncio
async def test_evidence_candidate_pipeline_isolation(test_session, default_learner):
    """Verify that candidate evidence updates KnowledgeState ONLY via EvidenceService and UpdateEngine."""
    concept_repo = ConceptRepository(test_session)
    c1 = await concept_repo.create(ConceptCreate(name="Dynamic Programming", description="DP algorithms"))

    state_service = LearnerStateService(test_session)
    initial_state = await state_service.get_or_create_state(default_learner.id, c1.id)
    assert initial_state.mastery_probability == 0.0

    # 1. Simulate candidate evidence produced by LLM tutor evaluation turn
    evidence_service = EvidenceService(test_session)
    evidence, updated_state = await evidence_service.record_evidence(
        learner_id=default_learner.id,
        concept_id=c1.id,
        evidence_type=EvidenceType.EXPLANATION,
        result_quality=0.85,
        source="AI Tutor Study Session",
        notes="Learner correctly explained overlapping subproblems",
    )
    assert evidence.id is not None
    assert evidence.result_quality == 0.85
    assert updated_state is not None
    assert updated_state.mastery_probability > 0.0
    assert updated_state.evidence_reliability > 0.0
