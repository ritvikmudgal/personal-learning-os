"""Tests for API material upload, listing, details, search, and deletion."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from app.db.models import IngestionStatus, LearnerProfile, Material
from app.db.repositories.learner_repo import LearnerRepository
from app.domain.learner import LearnerCreate


@pytest.mark.asyncio
async def test_material_upload_api_flow(client: AsyncClient, test_session):
    """Test material file upload API, pipeline execution, listing, detail, and delete."""
    # Create learner
    learner_repo = LearnerRepository(test_session)
    learner = await learner_repo.create(LearnerCreate(name="Upload Tester"))

    # Mock embedding provider
    with patch("app.api.library.get_embedding_provider") as mock_emb_factory:
        mock_provider = AsyncMock()
        mock_provider.model_name = "nomic-embed-text"
        mock_provider.embed_batch.return_value = [[0.1] * 768]
        mock_emb_factory.return_value = mock_provider

        # 1. Upload TXT file
        files = {"file": ("algebra.txt", b"Linear algebra equations and matrix operations.", "text/plain")}
        data = {"learner_id": str(learner.id)}

        response = await client.post("/api/library/upload", files=files, data=data)
        assert response.status_code == 201
        m_data = response.json()
        assert m_data["title"] == "Algebra"
        assert m_data["file_type"] == "txt"
        assert m_data["ingestion_status"] == "COMPLETED"
        material_id = m_data["id"]

        # 2. List materials
        list_resp = await client.get(f"/api/library/materials?learner_id={learner.id}")
        assert list_resp.status_code == 200
        materials_list = list_resp.json()
        assert len(materials_list) == 1
        assert materials_list[0]["id"] == material_id

        # 3. Get material detail
        detail_resp = await client.get(f"/api/library/materials/{material_id}")
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()
        assert len(detail_data["chunks"]) >= 1

        # 4. Semantic Search
        search_payload = {"query": "matrix operations", "top_k": 5}
        search_resp = await client.post(
            f"/api/library/search?learner_id={learner.id}", json=search_payload
        )
        assert search_resp.status_code == 200
        results = search_resp.json()
        assert len(results) >= 1

        # 5. Delete material
        del_resp = await client.delete(f"/api/library/materials/{material_id}")
        assert del_resp.status_code == 204

        # Confirm deleted
        detail_resp_after = await client.get(f"/api/library/materials/{material_id}")
        assert detail_resp_after.status_code == 404
