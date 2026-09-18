"""Tests for learner API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_create_learner(client):
    """Test creating a learner via the API."""
    response = await client.post(
        "/api/learner",
        json={"name": "Test User", "email": "test@example.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_learner(client):
    """Test getting a learner by ID."""
    # Create first
    create_resp = await client.post(
        "/api/learner",
        json={"name": "Get Test User"},
    )
    learner_id = create_resp.json()["id"]

    # Get
    response = await client.get(f"/api/learner/{learner_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Get Test User"


@pytest.mark.asyncio
async def test_get_nonexistent_learner(client):
    """Test getting a learner that doesn't exist."""
    response = await client.get("/api/learner/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_learners(client):
    """Test listing all learners."""
    # Create a couple
    await client.post("/api/learner", json={"name": "User 1"})
    await client.post("/api/learner", json={"name": "User 2"})

    response = await client.get("/api/learner")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_update_learner(client):
    """Test updating a learner profile."""
    create_resp = await client.post(
        "/api/learner",
        json={"name": "Original Name"},
    )
    learner_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/learner/{learner_id}",
        json={"name": "Updated Name"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_learner(client):
    """Test deleting a learner profile."""
    create_resp = await client.post(
        "/api/learner",
        json={"name": "Delete Me"},
    )
    learner_id = create_resp.json()["id"]

    response = await client.delete(f"/api/learner/{learner_id}")
    assert response.status_code == 204

    # Verify deleted
    get_resp = await client.get(f"/api/learner/{learner_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_learner_knowledge_empty(client):
    """Test getting knowledge summary for a learner with no study history."""
    create_resp = await client.post(
        "/api/learner",
        json={"name": "New Learner"},
    )
    learner_id = create_resp.json()["id"]

    response = await client.get(f"/api/learner/{learner_id}/knowledge")
    assert response.status_code == 200
    data = response.json()
    assert data["learner_id"] == learner_id
    assert data["total_concepts_studied"] == 0
    assert data["states"] == []
