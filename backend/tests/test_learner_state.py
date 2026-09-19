"""Tests for learner knowledge state and evidence updates."""

import pytest
from app.db.models import EvidenceType, LearnerProfile, Concept
from app.services.evidence_service import EvidenceService
from app.services.learner_state_service import LearnerStateService


@pytest.mark.asyncio
async def test_initial_state_defaults(test_session):
    """Test creating a default 6-dimension knowledge state."""
    learner = LearnerProfile(name="State Test Learner")
    concept = Concept(name="Functions")
    test_session.add_all([learner, concept])
    await test_session.flush()

    service = LearnerStateService(test_session)
    state = await service.get_or_create_state(learner.id, concept.id)

    assert state.mastery_probability == 0.0
    assert state.knowledge_strength == 0.0
    assert state.forgetting_state == 0.0
    assert state.confidence == 0.0
    assert state.evidence_reliability == 0.0
    assert state.misconception_severity == 0.0


@pytest.mark.asyncio
async def test_evidence_updates_mastery_and_reliability(test_session):
    """Test that evidence updates mastery and reliability independently."""
    learner = LearnerProfile(name="Evidence Test")
    concept = Concept(name="Loops")
    test_session.add_all([learner, concept])
    await test_session.flush()

    evidence_service = EvidenceService(test_session)

    # Record good evidence without confidence
    evidence, state = await evidence_service.record_evidence(
        learner_id=learner.id,
        concept_id=concept.id,
        evidence_type=EvidenceType.SOLVED_PROBLEM,
        result_quality=0.9,
        difficulty=0.7,
        confidence=None,  # No confidence provided
    )

    assert state is not None
    assert state.mastery_probability > 0.0
    assert state.confidence == 0.0  # Confidence untouched when None provided!
    assert state.evidence_reliability > 0.0
    assert state.knowledge_strength > 0.0



@pytest.mark.asyncio
async def test_confidence_only_updates_when_provided(test_session):
    """Test that confidence updates only when explicit confidence is provided."""
    learner = LearnerProfile(name="Confidence Test")
    concept = Concept(name="Recursion")
    test_session.add_all([learner, concept])
    await test_session.flush()

    evidence_service = EvidenceService(test_session)

    # High quality performance, but learner self-reports low confidence (0.2)
    _, state = await evidence_service.record_evidence(
        learner_id=learner.id,
        concept_id=concept.id,
        evidence_type=EvidenceType.ASSESSMENT_ANSWER,
        result_quality=1.0,
        confidence=0.2,
    )

    assert state.mastery_probability > 0.0
    # Confidence moved toward 0.2 from default 0.5 (0.7*0.5 + 0.3*0.2 = 0.41)
    assert state.confidence < 0.5
