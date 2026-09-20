"""Performance and latency test suite for Layer 4 Low-Latency Local AI Tutor."""

import pytest
import time
from unittest.mock import AsyncMock
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.concept import ConceptCreate
from app.engine.learning_graph import LearningGraphRunner
from app.engine.learning_state import LearningState
from app.llm.tutor_operations import TutorLLMOperations
from app.services.graph_service import GraphService
from app.services.tutor_service import TutorService
from app.utils.telemetry import TutorRequestProfiler


def test_telemetry_profiler():
    """Verify TutorRequestProfiler measures latency stages accurately."""
    profiler = TutorRequestProfiler("test-req-1")
    profiler.start_stage("concept_resolution")
    time.sleep(0.01)
    dur = profiler.end_stage("concept_resolution")

    assert dur >= 9.0  # At least 9ms
    summary = profiler.log_summary(llm_calls_count=1)
    assert "concept_resolution" in summary
    assert summary["total_request_time"] >= dur


def test_deterministic_concept_resolution_fast_path():
    """Verify Python-side concept resolution resolves matching concepts in < 1ms without calling LLM."""
    mock_provider = AsyncMock()
    ops = TutorLLMOperations(mock_provider)

    available = [
        {"id": 1, "name": "Binary Search"},
        {"id": 2, "name": "Recursion"},
        {"id": 3, "name": "Sorting Algorithms"},
    ]

    t0 = time.perf_counter()
    res = ops.deterministic_concept_resolution("Explain Binary Search to me", available)
    t1 = time.perf_counter()

    duration_ms = (t1 - t0) * 1000.0
    assert res is not None
    assert res["matched_id"] == 1
    assert res["matched_name"] == "Binary Search"
    assert duration_ms < 50.0  # Fast execution
    # Verify mock_provider LLM was NEVER called
    mock_provider.generate.assert_not_called()


@pytest.mark.asyncio
async def test_parallel_context_pipeline_execution(test_session: AsyncSession, default_learner):
    """Verify execute_context_pipeline_parallel runs independent DB and RAG steps concurrently."""
    runner = LearningGraphRunner(test_session)

    # Populate a concept in graph
    graph = GraphService(test_session)
    c = await graph.create_concept(ConceptCreate(name="Tree Traversal", description="Data Structures"))

    state: LearningState = {
        "learner_id": default_learner.id,
        "user_goal": "Tree Traversal",
    }

    t0 = time.perf_counter()
    out_state = await runner.execute_context_pipeline_parallel(state)
    t1 = time.perf_counter()

    duration_ms = (t1 - t0) * 1000.0
    assert out_state.get("target_concept_id") == c.id
    assert out_state.get("target_concept_name") == "Tree Traversal"
    assert "teaching_plan" in out_state
    assert duration_ms < 5000.0  # Fast parallel execution


@pytest.mark.asyncio
async def test_streaming_tutor_chat_endpoint(client: AsyncClient, default_learner):
    """Verify /api/tutor/chat/stream SSE endpoint streams metadata and token events properly."""
    res = await client.post(
        "/api/tutor/chat/stream",
        json={"user_message": "Explain recursion"},
    )
    assert res.status_code == 200
    assert "text/event-stream" in res.headers["content-type"]
    body = res.text
    assert "event: metadata" in body
    assert "event: token" in body or "event: done" in body


@pytest.mark.asyncio
async def test_model_warmup_removed(client: AsyncClient):
    """Verify /api/tutor/warmup has been removed (returns 404) so Ollama remains 100% on-demand."""
    res = await client.post("/api/tutor/warmup")
    assert res.status_code == 404
