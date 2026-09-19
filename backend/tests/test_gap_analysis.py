"""Tests for prerequisite weakness gap analysis."""

import pytest
from app.db.models import EvidenceType, LearnerProfile
from app.domain.concept import ConceptCreate, ConceptRelationshipCreate
from app.engine.gap_analysis import find_learning_gaps
from app.services.evidence_service import EvidenceService
from app.services.graph_service import GraphService


@pytest.mark.asyncio
async def test_gap_analysis_detects_weak_prerequisites(test_session):
    """Test that gap analysis detects unstudied or low-mastery prerequisites."""
    graph_service = GraphService(test_session)
    learner = LearnerProfile(name="Gap Test Learner")
    test_session.add(learner)
    await test_session.flush()

    # Build chain: Basic Math -> Fractions -> Ratios -> Probability
    c1 = await graph_service.create_concept(ConceptCreate(name="Basic Math"))
    c2 = await graph_service.create_concept(ConceptCreate(name="Fractions"))
    c3 = await graph_service.create_concept(ConceptCreate(name="Ratios"))
    c4 = await graph_service.create_concept(ConceptCreate(name="Probability"))

    for src, tgt in [(c1.id, c2.id), (c2.id, c3.id), (c3.id, c4.id)]:
        await graph_service.create_relationship(
            ConceptRelationshipCreate(
                source_concept_id=src,
                target_concept_id=tgt,
                relationship_type="prerequisite",
            )
        )

    # Learner studied Basic Math (strong performance)
    evidence_service = EvidenceService(test_session)
    for _ in range(12):
        await evidence_service.record_evidence(
            learner_id=learner.id,
            concept_id=c1.id,
            evidence_type=EvidenceType.SOLVED_PROBLEM,
            result_quality=1.0,
            difficulty=0.8,
        )


    # Run gap analysis on Probability (c4)
    result = await find_learning_gaps(test_session, learner.id, c4.id)

    assert result.target_concept_id == c4.id
    assert result.has_gaps is True
    # Fractions and Ratios have no knowledge states -> classified as "unknown" (which counts as weak)
    weak_names = [w.concept_name for w in result.weak_prerequisites]
    assert "Fractions" in weak_names
    assert "Ratios" in weak_names
    # Basic Math was studied heavily -> classified as "strong"
    prereq_dict = {p.concept_name: p.classification for p in result.prerequisites}
    assert prereq_dict["Basic Math"] == "strong"


@pytest.mark.asyncio
async def test_gap_analysis_no_prerequisites(test_session):
    """Test gap analysis on a concept with no prerequisites."""
    graph_service = GraphService(test_session)
    learner = LearnerProfile(name="No Prereq Learner")
    test_session.add(learner)
    await test_session.flush()

    c = await graph_service.create_concept(ConceptCreate(name="Standalone Concept"))

    result = await find_learning_gaps(test_session, learner.id, c.id)

    assert result.target_concept_id == c.id
    assert result.has_gaps is False
    assert len(result.prerequisites) == 0
    assert len(result.weak_prerequisites) == 0
