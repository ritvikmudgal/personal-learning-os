"""Tests for LangGraph learning state graph workflow execution."""

import pytest
from app.engine.learning_graph import LearningGraphRunner, build_learning_graph
from app.engine.learning_state import LearningState
from app.db.repositories.concept_repo import ConceptRepository
from app.services.graph_service import GraphService
from app.domain.concept import ConceptCreate, ConceptRelationshipCreate
from app.db.models import RelationshipType


@pytest.mark.asyncio
async def test_langgraph_concept_resolution_and_execution(test_session, default_learner):
    """Test that LangGraph resolves concepts, loads context, plans teaching, and computes output."""
    concept_repo = ConceptRepository(test_session)
    c1 = await concept_repo.create(ConceptCreate(name="Arrays", description="Array data structure"))
    c2 = await concept_repo.create(ConceptCreate(name="Search", description="Search algorithms"))
    c3 = await concept_repo.create(ConceptCreate(name="Binary Search", description="Binary search algorithm"))

    graph_service = GraphService(test_session)
    await graph_service.create_relationship(
        ConceptRelationshipCreate(
            source_concept_id=c1.id,
            target_concept_id=c3.id,
            relationship_type=RelationshipType.PREREQUISITE,
        )
    )

    runner = LearningGraphRunner(test_session)
    graph = build_learning_graph(runner)

    init_state: LearningState = {
        "learner_id": default_learner.id,
        "user_goal": "Teach me binary search",
        "target_concept_id": None,
        "target_concept_name": None,
        "current_concept_id": None,
        "current_concept_name": None,
        "prerequisite_gaps": [],
        "relevant_known_concepts": [],
        "learner_state_snapshots": {},
        "misconceptions": [],
        "retrieved_material": [],
        "teaching_plan": [],
        "conversation_context": [],
        "evidence_candidates": [],
        "next_action": "teach_target",
        "session_id": None,
        "latest_response": "Teach me binary search",
        "explanation_output": "",
        "provenance": [],
        "step_count": 0,
    }

    final_state = await graph.ainvoke(init_state)

    assert final_state["target_concept_id"] is not None
    assert "Binary Search" in final_state["target_concept_name"]
    assert len(final_state["explanation_output"]) > 0
    assert final_state["step_count"] > 0
