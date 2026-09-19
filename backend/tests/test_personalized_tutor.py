"""Tests for end-to-end TutorService behavior."""

import pytest
from app.services.tutor_service import TutorService
from app.services.graph_service import GraphService
from app.db.repositories.concept_repo import ConceptRepository
from app.domain.concept import ConceptCreate, ConceptRelationshipCreate
from app.db.models import RelationshipType


@pytest.mark.asyncio
async def test_tutor_service_prerequisite_aware_teaching(test_session, default_learner):
    """Test that TutorService identifies prerequisite graph and produces personalized teaching output."""
    concept_repo = ConceptRepository(test_session)
    arr = await concept_repo.create(ConceptCreate(name="Arrays", description="Basic arrays"))
    sort_arr = await concept_repo.create(ConceptCreate(name="Sorted Arrays", description="Sorted arrays"))

    graph_service = GraphService(test_session)
    await graph_service.create_relationship(
        ConceptRelationshipCreate(
            source_concept_id=arr.id,
            target_concept_id=sort_arr.id,
            relationship_type=RelationshipType.PREREQUISITE,
        )
    )

    tutor = TutorService(test_session)
    result = await tutor.handle_user_message(
        user_message="Teach me Sorted Arrays",
        learner_id=default_learner.id,
    )

    assert result["session_id"] is not None
    assert len(result["text"]) > 0
    assert len(result["teaching_plan"]) > 0
    assert result["target_concept_id"] == sort_arr.id
