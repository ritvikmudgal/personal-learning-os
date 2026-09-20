"""Test suite for AIRouter query classification, zero-LLM routes, and Settings API."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.ai_router import AIRouter, QueryCategory
from app.domain.concept import ConceptCreate


def test_ai_router_classification(test_session: AsyncSession):
    """Verify pattern matching rules for query categories."""
    router = AIRouter(test_session)

    # Normal conversation queries (0 LLM calls)
    assert router.classify_request("hello") == QueryCategory.NORMAL_CONVERSATION
    assert router.classify_request("thanks") == QueryCategory.NORMAL_CONVERSATION
    assert router.classify_request("what can you do?") == QueryCategory.NORMAL_CONVERSATION
    assert router.classify_request("how are you?") == QueryCategory.NORMAL_CONVERSATION
    assert router.classify_request("okay") == QueryCategory.NORMAL_CONVERSATION

    # Deterministic queries
    assert router.classify_request("Show my weak concepts") == QueryCategory.DETERMINISTIC
    assert router.classify_request("What are my prerequisites for DFS?") == QueryCategory.DETERMINISTIC
    assert router.classify_request("Show learner state") == QueryCategory.DETERMINISTIC
    assert router.classify_request("Show my active misconceptions") == QueryCategory.DETERMINISTIC

    # Retrieval queries
    assert router.classify_request("Find my notes on binary search") == QueryCategory.RETRIEVAL
    assert router.classify_request("What did I study about recursion?") == QueryCategory.RETRIEVAL

    # LLM required study queries
    assert router.classify_request("teach me binary search") == QueryCategory.LLM_REQUIRED
    assert router.classify_request("explain recursion") == QueryCategory.LLM_REQUIRED
    assert router.classify_request("I don't understand arithmetic microoperations") == QueryCategory.LLM_REQUIRED


@pytest.mark.asyncio
async def test_normal_conversation_route_zero_llm(test_session: AsyncSession, default_learner):
    """Verify AIRouter executes normal conversation route with 0 LLM calls."""
    router = AIRouter(test_session)

    for msg in ["hello", "thanks", "what can you do?", "how are you?", "okay"]:
        category = router.classify_request(msg)
        assert category == QueryCategory.NORMAL_CONVERSATION

        res = await router.execute_deterministic_route(
            category=category,
            user_message=msg,
            learner_id=default_learner.id,
        )

        assert res["llm_calls_count"] == 0
        assert res["target_concept_name"] is None
        assert res["teaching_plan"] == []
        assert res["provenance"] == []
        assert len(res["text"]) > 0


@pytest.mark.asyncio
async def test_deterministic_route_execution_zero_llm(test_session: AsyncSession, default_learner):
    """Verify AIRouter executes deterministic path with 0 LLM calls."""
    router = AIRouter(test_session)
    await router.graph_service.create_concept(ConceptCreate(name="Arrays", description="Data structures"))

    # Execute weak concepts query
    res = await router.execute_deterministic_route(
        category=QueryCategory.DETERMINISTIC,
        user_message="Show my weak concepts",
        learner_id=default_learner.id,
    )

    assert res["llm_calls_count"] == 0
    assert "text" in res
    assert len(res["text"]) > 0
    assert "Learner" in res["text"] or "Weak" in res["text"] or "Concepts" in res["text"]


@pytest.mark.asyncio
async def test_settings_api_get_and_post(client: AsyncClient):
    """Verify Settings API GET /api/settings and POST /api/settings."""
    # GET settings
    get_res = await client.get("/api/settings")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["local_ai_enabled"] is True
    assert data["ai_provider_preference"] == "auto"
    assert data["performance_mode"] == "cpu_friendly"

    # POST update settings
    post_res = await client.post(
        "/api/settings",
        json={
            "local_ai_enabled": False,
            "ai_provider_preference": "cloud",
            "performance_mode": "cpu_friendly",
        },
    )
    assert post_res.status_code == 200
    updated_data = post_res.json()
    assert updated_data["local_ai_enabled"] is False
    assert updated_data["ai_provider_preference"] == "cloud"


@pytest.mark.asyncio
async def test_chat_stream_hello_returns_instant_json(client: AsyncClient):
    """POST /api/tutor/chat/stream with 'hello' must return instant JSON, not SSE."""
    res = await client.post(
        "/api/tutor/chat/stream",
        json={"user_message": "hello"},
    )
    assert res.status_code == 200
    assert "application/json" in res.headers.get("content-type", "")
    data = res.json()
    assert data["type"] == "instant"
    assert len(data["text"]) > 0
    assert data["teaching_plan"] == []
    assert data["provenance"] == []


@pytest.mark.asyncio
async def test_chat_stream_hi_returns_instant_json(client: AsyncClient):
    """POST /api/tutor/chat/stream with 'hi' must return instant JSON."""
    res = await client.post(
        "/api/tutor/chat/stream",
        json={"user_message": "hi"},
    )
    assert res.status_code == 200
    assert "application/json" in res.headers.get("content-type", "")
    data = res.json()
    assert data["type"] == "instant"
    assert len(data["text"]) > 0


@pytest.mark.asyncio
async def test_chat_stream_what_can_you_do_returns_instant_json(client: AsyncClient):
    """POST /api/tutor/chat/stream with 'what can you do?' must return instant JSON."""
    res = await client.post(
        "/api/tutor/chat/stream",
        json={"user_message": "what can you do?"},
    )
    assert res.status_code == 200
    assert "application/json" in res.headers.get("content-type", "")
    data = res.json()
    assert data["type"] == "instant"
    assert len(data["text"]) > 0


@pytest.mark.asyncio
async def test_chat_stream_thanks_returns_instant_json(client: AsyncClient):
    """POST /api/tutor/chat/stream with 'thanks' must return instant JSON."""
    res = await client.post(
        "/api/tutor/chat/stream",
        json={"user_message": "thanks"},
    )
    assert res.status_code == 200
    assert "application/json" in res.headers.get("content-type", "")
    data = res.json()
    assert data["type"] == "instant"
    assert len(data["text"]) > 0
