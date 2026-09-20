"""Regression and stabilization test suite for Layer 4 Tutor Engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.concept import ConceptCreate, ConceptRelationshipCreate
from app.domain.tutor_schemas import IntentClassificationSchema, TeachingPlanSchema
from app.engine.gap_analysis import find_learning_gaps
from app.engine.learning_graph import LearningGraphRunner
from app.engine.learning_state import LearningState
from app.llm.tutor_operations import TutorLLMOperations, parse_structured_llm_output
from app.services.graph_service import GraphService
from app.services.learner_state_service import LearnerStateService
from app.services.tutor_service import TutorService
from app.utils.query_cleaner import build_clean_search_query, clean_concept_name, strip_conversational_noise


# --- 1. Query Cleaner Tests ---

def test_query_cleaner_sanitizes_literal_null_and_none():
    """Verify 'null', 'None', 'undefined' are stripped completely from RAG queries."""
    res1 = build_clean_search_query("null", "I do not want to study this")
    assert "null" not in res1.lower()
    assert "none" not in res1.lower()
    assert len(res1) > 0

    res2 = build_clean_search_query("None", "explain calculus")
    assert "none" not in res2.lower()
    assert "calculus" in res2.lower()

    res3 = build_clean_search_query(None, "undefined Newton's Laws")
    assert "undefined" not in res3.lower()
    assert "newton" in res3.lower()


def test_query_cleaner_combines_concept_and_query():
    """Verify query cleaner combines concept and message cleanly without duplication."""
    query = build_clean_search_query("Vectors", "I want to study dot product of vectors")
    assert "Vectors" in query or "vectors" in query
    assert "dot product" in query
    assert "null" not in query.lower()


def test_clean_concept_name_and_noise_stripping():
    """Verify individual helper utility functions."""
    assert clean_concept_name("null") == ""
    assert clean_concept_name("None") == ""
    assert clean_concept_name("  Linear Algebra  ") == "Linear Algebra"

    stripped = strip_conversational_noise("I do not want to study this concept")
    assert stripped.lower() == "concept"


# --- 2. Structured LLM Output Parser Tests ---

def test_structured_parser_single_quoted_dict():
    """Verify single-quoted Python dict syntax is safely parsed via ast.literal_eval fallback."""
    raw_llm_output = "{'steps': ['Review Vectors', 'Explain Dot Product', 'Practice Exercises']}"
    parsed = parse_structured_llm_output(raw_llm_output, TeachingPlanSchema)
    assert len(parsed.steps) == 3
    assert parsed.steps[0] == "Review Vectors"


def test_structured_parser_markdown_codeblock():
    """Verify json inside markdown code blocks parses cleanly."""
    raw_llm_output = "```json\n{\"intent\": \"explain\", \"target_concept\": \"Quantum Mechanics\"}\n```"
    parsed = parse_structured_llm_output(raw_llm_output, IntentClassificationSchema)
    assert parsed.intent == "explain"
    assert parsed.target_concept == "Quantum Mechanics"


def test_structured_parser_invalid_json_uses_fallback():
    """Verify invalid or malformed output returns specified fallback instance without raising exceptions."""
    raw_llm_output = "Sorry, I cannot format this as JSON for you right now."
    fallback = IntentClassificationSchema(intent="teach", target_concept="Default Topic")
    parsed = parse_structured_llm_output(raw_llm_output, IntentClassificationSchema, fallback_instance=fallback)
    assert parsed.intent == "teach"
    assert parsed.target_concept == "Default Topic"


# --- 3. Prerequisite DAG Isolation & Intent Override Tests ---

@pytest.mark.asyncio
async def test_prerequisite_isolation_dag_only(test_session: AsyncSession, default_learner):
    """Verify gap analysis strictly reads directed PREREQUISITE edges in Concept Graph."""
    graph = GraphService(test_session)

    # Create concepts: C1 (Prerequisite) -> C2 (Target), and C3 (RELATED, not prerequisite)
    c1 = await graph.create_concept(ConceptCreate(name="Limits & Continuity", description="Foundation"))
    c2 = await graph.create_concept(ConceptCreate(name="Derivatives", description="Target"))
    c3 = await graph.create_concept(ConceptCreate(name="Physics Class XII", description="Related Metadata"))

    await graph.create_relationship(ConceptRelationshipCreate(
        source_concept_id=c1.id,
        target_concept_id=c2.id,
        relationship_type="prerequisite",
    ))
    await graph.create_relationship(ConceptRelationshipCreate(
        source_concept_id=c3.id,
        target_concept_id=c2.id,
        relationship_type="related",
    ))

    gap_res = await find_learning_gaps(test_session, default_learner.id, c2.id)

    prereq_ids = [p.concept_id for p in gap_res.prerequisites]
    assert c1.id in prereq_ids
    assert c3.id not in prereq_ids


@pytest.mark.asyncio
async def test_user_intent_override_bypasses_prereq_gaps(test_session: AsyncSession, default_learner):
    """Verify user override intent keeps current concept as target and does not force gap teaching turn."""
    runner = LearningGraphRunner(test_session)

    # Mock classify_learning_intent to return 'override'
    runner.tutor_ops.classify_learning_intent = AsyncMock(return_value={
        "intent": "override",
        "target_concept": "Dot Product",
    })
    runner.tutor_ops.resolve_concept_name = AsyncMock(return_value={
        "matched_id": 999,
        "matched_name": "Dot Product",
        "is_new": False,
    })

    state: LearningState = {
        "learner_id": default_learner.id,
        "user_goal": "I already know vectors, let me study dot product directly",
    }

    state = await runner.understand_goal(state)
    assert state.get("override_prerequisites") is True

    # Simulate weak gap present
    state["target_concept_id"] = 999
    state["target_concept_name"] = "Dot Product"
    
    state = await runner.analyze_prerequisites(state)
    assert state.get("current_concept_name") == "Dot Product"
    assert state.get("next_action") == "teach_target"


# --- 4. Graceful Error Handling & Fallback Tests ---

@pytest.mark.asyncio
async def test_graceful_tutor_error_handling_200_ok(test_session: AsyncSession, default_learner):
    """Verify TutorService handles engine exceptions gracefully and returns 200 OK payload."""
    service = TutorService(test_session)

    # Mock compiled_graph.ainvoke to raise an exception
    service.compiled_graph.ainvoke = AsyncMock(side_effect=RuntimeError("Ollama local connection timeout"))

    res = await service.handle_user_message(
        user_message="Teach me Organic Chemistry",
        learner_id=default_learner.id,
    )

    assert isinstance(res, dict)
    assert "session_id" in res
    assert "text" in res
    assert "temporary issue" in res["text"].lower() or "here to help" in res["text"].lower()
    assert res.get("next_action") == "teach_target"
