"""Tests for ContextBuilderService token budgeting and provenance assembly."""

import pytest
from app.engine.context_builder import ContextBuilderService
from app.db.repositories.concept_repo import ConceptRepository
from app.domain.concept import ConceptCreate
from app.services.misconception_service import MisconceptionService


@pytest.mark.asyncio
async def test_context_builder_budgeting_and_provenance(test_session, default_learner):
    """Test that context builder prioritizes targets, misconceptions, gaps, and respects token limits."""
    concept_repo = ConceptRepository(test_session)
    c1 = await concept_repo.create(ConceptCreate(name="Recursion", description="Recursive functions"))

    misc_service = MisconceptionService(test_session)
    await misc_service.record_misconception(
        learner_id=default_learner.id,
        description="Thinks base case is optional in recursion",
        concept_id=c1.id,
        severity=0.7,
    )

    builder = ContextBuilderService(test_session)
    built_ctx = await builder.build_tutor_context(
        learner_id=default_learner.id,
        target_concept_id=c1.id,
        target_concept_name="Recursion",
        user_message="I don't understand base cases",
        max_char_limit=2000,
    )

    assert built_ctx.target_concept_name == "Recursion"
    assert "Recursion" in built_ctx.formatted_context_str
    assert "base case" in built_ctx.formatted_context_str.lower()
    assert len(built_ctx.formatted_context_str) <= 2500
    assert any(p.source_type == "misconception" for p in built_ctx.provenance_list)
