"""Shared test fixtures and configuration."""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base
from app.main import create_app
from app.db.database import get_db_session


# Use in-memory SQLite for tests
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_engine():
    """Create a test database engine with in-memory SQLite."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client with the FastAPI app."""
    app = create_app()

    # Override the database session dependency to use test DB
    factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def default_learner(test_session):
    """Create or get default learner profile for tests."""
    from app.db.repositories.learner_repo import LearnerRepository
    repo = LearnerRepository(test_session)
    learner = await repo.get_or_create_default()
    await test_session.commit()
    return learner


class MockLLMProvider:
    """Fast mock LLM provider for tests."""
    name = "mock_provider"

    async def health_check(self):
        from app.llm.provider import ProviderHealthResult, ProviderStatus
        return ProviderHealthResult(
            provider_name="mock_provider",
            status=ProviderStatus.AVAILABLE,
            message="Mock provider ready",
        )

    async def generate(self, prompt, system_prompt=None, options=None):
        from app.llm.provider import LLMResponse
        sys_p = (system_prompt or "").lower()

        if "intent classifier" in sys_p:
            concept_name = "Sorted Arrays"
            if "binary search" in prompt.lower():
                concept_name = "Binary Search"
            elif "recursion" in prompt.lower():
                concept_name = "Recursion"
            text = f'{{"intent": "teach", "target_concept": "{concept_name}"}}'
        elif "concept resolver" in sys_p:
            concept_name = "Sorted Arrays"
            if "binary search" in prompt.lower():
                concept_name = "Binary Search"
            elif "recursion" in prompt.lower():
                concept_name = "Recursion"
            
            matched_id = 1
            # Look for 'Concept Name' (id=X) in system_prompt/prompt
            import re
            m = re.search(rf"'{concept_name}'\s*\(id=(\d+)\)", sys_p + prompt, re.IGNORECASE)
            if m:
                matched_id = int(m.group(1))

            text = f'{{"matched_id": {matched_id}, "matched_name": "{concept_name}", "is_new": false}}'
        elif "pedagogical planner" in sys_p:
            text = '{"steps": ["Review Prerequisites", "Core Concept", "Practice"]}'
        elif "educational evaluator" in sys_p:
            text = '{"result_quality": 0.85, "is_sufficient": true, "feedback": "Great understanding"}'
        else:
            text = "Welcome to your personalized study session. Let's break down this concept together step-by-step."

        return LLMResponse(text=text, model="mock-qwen", provider="mock")

    async def generate_stream(self, prompt, system_prompt=None, options=None):
        yield "Mock response"


@pytest.fixture(autouse=True)
def mock_llm_provider(monkeypatch):
    """Autouse fixture to mock get_provider() across tests."""
    mock_inst = MockLLMProvider()
    monkeypatch.setattr("app.llm.factory.get_provider", lambda settings=None: mock_inst)
    monkeypatch.setattr("app.engine.learning_graph.get_provider", lambda settings=None: mock_inst)
    return mock_inst


