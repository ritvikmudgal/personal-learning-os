"""Tests for database schema and basic operations."""

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.db.models import (
    Concept,
    ConceptRelationship,
    DifficultyLevel,
    KnowledgeState,
    LearnerProfile,
    LearningEvent,
    AssessmentRecord,
    Misconception,
    MaterialMetadata,
    RelationshipType,
    EventType,
    AssessmentType,
)


@pytest.mark.asyncio
async def test_create_learner_profile(test_session):
    """Test creating a learner profile."""
    learner = LearnerProfile(name="Test User", email="test@example.com")
    test_session.add(learner)
    await test_session.flush()

    assert learner.id is not None
    assert learner.name == "Test User"
    assert learner.created_at is not None


@pytest.mark.asyncio
async def test_create_concept(test_session):
    """Test creating a concept."""
    concept = Concept(
        name="Linear Algebra",
        description="Study of vectors and matrices",
        domain="Mathematics",
        difficulty_level=DifficultyLevel.INTERMEDIATE,
    )
    test_session.add(concept)
    await test_session.flush()

    assert concept.id is not None
    assert concept.name == "Linear Algebra"
    assert concept.difficulty_level == DifficultyLevel.INTERMEDIATE


@pytest.mark.asyncio
async def test_concept_relationship(test_session):
    """Test creating prerequisite relationships between concepts."""
    algebra = Concept(name="Algebra", domain="Mathematics")
    calculus = Concept(name="Calculus", domain="Mathematics")
    test_session.add_all([algebra, calculus])
    await test_session.flush()

    relationship = ConceptRelationship(
        source_concept_id=algebra.id,
        target_concept_id=calculus.id,
        relationship_type=RelationshipType.PREREQUISITE,
        strength=1.0,
    )
    test_session.add(relationship)
    await test_session.flush()

    assert relationship.id is not None
    assert relationship.relationship_type == RelationshipType.PREREQUISITE


@pytest.mark.asyncio
async def test_knowledge_state(test_session):
    """Test creating a knowledge state entry."""
    learner = LearnerProfile(name="Test User")
    concept = Concept(name="Python Basics", domain="Programming")
    test_session.add_all([learner, concept])
    await test_session.flush()

    state = KnowledgeState(
        learner_id=learner.id,
        concept_id=concept.id,
        understanding_level=0.7,
        confidence=0.8,
        demonstrated_level=0.6,
    )
    test_session.add(state)
    await test_session.flush()

    assert state.understanding_level == 0.7
    assert state.confidence == 0.8
    assert state.demonstrated_level == 0.6


@pytest.mark.asyncio
async def test_learning_event(test_session):
    """Test recording a learning event."""
    learner = LearnerProfile(name="Test User")
    test_session.add(learner)
    await test_session.flush()

    event = LearningEvent(
        learner_id=learner.id,
        event_type=EventType.STUDY,
        source="textbook",
        duration_seconds=1800,
    )
    test_session.add(event)
    await test_session.flush()

    assert event.id is not None
    assert event.event_type == EventType.STUDY


@pytest.mark.asyncio
async def test_assessment_record(test_session):
    """Test recording an assessment."""
    learner = LearnerProfile(name="Test User")
    test_session.add(learner)
    await test_session.flush()

    assessment = AssessmentRecord(
        learner_id=learner.id,
        assessment_type=AssessmentType.QUIZ,
        score=8.0,
        max_score=10.0,
        passed=True,
        misconceptions_detected=["confused multiplication order"],
    )
    test_session.add(assessment)
    await test_session.flush()

    assert assessment.passed is True
    assert assessment.misconceptions_detected == ["confused multiplication order"]


@pytest.mark.asyncio
async def test_misconception(test_session):
    """Test recording a misconception."""
    learner = LearnerProfile(name="Test User")
    test_session.add(learner)
    await test_session.flush()

    misconception = Misconception(
        learner_id=learner.id,
        description="Believes division by zero is zero",
        related_prerequisite_ids=[1, 2],
    )
    test_session.add(misconception)
    await test_session.flush()

    assert misconception.resolved is False
    assert misconception.related_prerequisite_ids == [1, 2]


@pytest.mark.asyncio
async def test_material_metadata(test_session):
    """Test recording material metadata."""
    learner = LearnerProfile(name="Test User")
    test_session.add(learner)
    await test_session.flush()

    material = MaterialMetadata(
        learner_id=learner.id,
        title="Linear Algebra Textbook",
        content_type="application/pdf",
        file_size_bytes=1024000,
        associated_concept_ids=[1, 2, 3],
    )
    test_session.add(material)
    await test_session.flush()

    assert material.title == "Linear Algebra Textbook"
    assert material.associated_concept_ids == [1, 2, 3]
