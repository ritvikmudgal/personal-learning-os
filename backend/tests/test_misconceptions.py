"""Tests for misconception tracking and resolution workflow."""

import pytest
from app.db.models import Concept, LearnerProfile, MisconceptionStatus
from app.services.learner_state_service import LearnerStateService
from app.services.misconception_service import MisconceptionService


@pytest.mark.asyncio
async def test_record_and_observe_misconception(test_session):
    """Test recording a misconception and observing it again."""
    learner = LearnerProfile(name="Misconception Test Learner")
    concept = Concept(name="Pointers")
    test_session.add_all([learner, concept])
    await test_session.flush()

    service = MisconceptionService(test_session)

    m1 = await service.record_misconception(
        learner_id=learner.id,
        concept_id=concept.id,
        description="Confuses value with address",
        severity=0.6,
    )
    assert m1.id is not None
    assert m1.evidence_count == 1
    assert m1.status == MisconceptionStatus.ACTIVE

    # Observe again with same description
    m2 = await service.record_misconception(
        learner_id=learner.id,
        concept_id=concept.id,
        description="Confuses value with address",
        severity=0.7,
    )
    assert m2.id == m1.id
    assert m2.evidence_count == 2
    assert m2.severity == 0.7

    # KnowledgeState misconception_severity should equal max active severity
    state_service = LearnerStateService(test_session)
    state = await state_service.get_state(learner.id, concept.id)
    assert state.misconception_severity == 0.7


@pytest.mark.asyncio
async def test_resolve_misconception(test_session):
    """Test resolving a misconception."""
    learner = LearnerProfile(name="Resolve Test Learner")
    concept = Concept(name="References")
    test_session.add_all([learner, concept])
    await test_session.flush()

    service = MisconceptionService(test_session)
    m = await service.record_misconception(
        learner_id=learner.id,
        concept_id=concept.id,
        description="Thinks reference can be null",
        severity=0.8,
    )

    resolved = await service.resolve_misconception(
        misconception_id=m.id,
        resolution_notes="Learner demonstrated understanding in quiz",
    )
    assert resolved.resolved is True
    assert resolved.status == MisconceptionStatus.RESOLVED
    assert resolved.resolution_notes == "Learner demonstrated understanding in quiz"

    # Active misconceptions should be empty now
    active = await service.get_active_misconceptions(learner.id, concept.id)
    assert len(active) == 0

    # Knowledge state misconception_severity should be 0.0
    state_service = LearnerStateService(test_session)
    state = await state_service.get_state(learner.id, concept.id)
    assert state.misconception_severity == 0.0
