"""Tests for health check endpoints."""

import pytest
import pytest_asyncio


@pytest.mark.asyncio
async def test_health_check(client):
    """Test the basic health check endpoint returns healthy status."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_ollama_status_endpoint(client):
    """Test the Ollama status endpoint returns structured response.

    Note: This test checks the response structure, not Ollama availability.
    Ollama may or may not be running during tests.
    """
    response = await client.get("/api/health/ollama")
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert "status" in data
    assert "configured_model" in data
    assert data["provider"] == "ollama"


@pytest.mark.asyncio
async def test_llm_provider_status(client):
    """Test the LLM provider status endpoint."""
    response = await client.get("/api/health/llm")
    assert response.status_code == 200
    data = response.json()
    assert "primary_provider" in data
    assert "primary_status" in data
