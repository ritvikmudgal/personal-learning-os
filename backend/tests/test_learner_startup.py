"""Tests for startup default learner profile initialization and active learner resolution."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from app.db.models import LearnerProfile
from app.db.repositories.learner_repo import LearnerRepository
from app.main import init_default_learner


@pytest.mark.asyncio
async def test_startup_initialization_creates_default_learner(test_session):
    """Verify init_default_learner creates exactly one default learner profile on empty DB."""
    repo = LearnerRepository(test_session)
    learners_before = await repo.get_all()
    assert len(learners_before) == 0

    # Call repository get_or_create_default directly
    learner = await repo.get_or_create_default()
    await test_session.commit()

    assert learner is not None
    assert learner.name == "Local Learner"
    assert learner.email == "local@learning-os.internal"

    learners_after = await repo.get_all()
    assert len(learners_after) == 1
    assert learners_after[0].id == learner.id


@pytest.mark.asyncio
async def test_startup_initialization_reuses_existing_learner(test_session):
    """Verify running startup initialization twice does not create duplicate learners."""
    repo = LearnerRepository(test_session)

    # First init
    learner1 = await repo.get_or_create_default()
    await test_session.commit()

    # Second init
    learner2 = await repo.get_or_create_default()
    await test_session.commit()

    assert learner1.id == learner2.id
    assert learner1.name == learner2.name

    all_learners = await repo.get_all()
    assert len(all_learners) == 1


@pytest.mark.asyncio
async def test_active_learner_api_endpoint(client: AsyncClient):
    """Test GET /api/learner/active returns the active default local learner."""
    response = await client.get("/api/learner/active")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "Local Learner"

    # Alias /api/learner/me
    response_me = await client.get("/api/learner/me")
    assert response_me.status_code == 200
    assert response_me.json()["id"] == data["id"]


@pytest.mark.asyncio
async def test_library_upload_works_against_fresh_database(client: AsyncClient):
    """Test library upload works end-to-end on a fresh DB using active learner ID."""
    # 1. Fetch active learner
    active_resp = await client.get("/api/learner/active")
    assert active_resp.status_code == 200
    learner_id = active_resp.json()["id"]

    # 2. Upload library document using resolved learner_id
    with patch("app.api.library.get_embedding_provider") as mock_emb_factory:
        mock_provider = AsyncMock()
        mock_provider.model_name = "nomic-embed-text"
        mock_provider.embed_batch.return_value = [[0.1] * 768]
        mock_emb_factory.return_value = mock_provider

        files = {"file": ("calculus.txt", b"Derivatives and integration fundamental theorems.", "text/plain")}
        data = {"learner_id": str(learner_id)}

        upload_resp = await client.post("/api/library/upload", files=files, data=data)
        assert upload_resp.status_code == 201
        m_data = upload_resp.json()
        assert m_data["learner_id"] == learner_id
        assert m_data["title"] == "Calculus"
        assert m_data["ingestion_status"] == "COMPLETED"
