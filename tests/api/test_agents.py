"""Tests for individual agent API endpoints."""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.app.core.agents import ArchitectOutput


def test_architect_endpoint(client: TestClient, mock_provider):
    """Test the architect endpoint."""
    with patch("src.app.api.agents.architect.ProviderFactory.create", return_value=mock_provider):
        response = client.post(
            "/api/agents/architect",
            json={
                "requirements": "Build a REST API for user management",
                "context": "Use Python and FastAPI",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "architect"
        assert "result" in data
        assert "tech_stack" in data["result"]


def test_architect_with_provider(client: TestClient, mock_provider):
    """Test the architect endpoint with provider selection."""
    with patch("src.app.api.agents.architect.ProviderFactory.create", return_value=mock_provider):
        response = client.post(
            "/api/agents/architect",
            json={
                "requirements": "Build a REST API",
                "provider": "anthropic",
                "temperature": 0.5,
                "max_tokens": 2000,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "architect"


def test_architect_missing_requirements(client: TestClient):
    """Test the architect endpoint with missing requirements."""
    response = client.post(
        "/api/agents/architect",
        json={},
    )

    assert response.status_code == 422  # Validation error


def test_implement_endpoint(client: TestClient, mock_provider, mock_architect_output):
    """Test the implement endpoint."""
    with patch("src.app.api.agents.implement.ProviderFactory.create", return_value=mock_provider):
        response = client.post(
            "/api/agents/implement",
            json={
                "architecture": mock_architect_output.model_dump(),
                "requirements": "Build a REST API for user management",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "implement"
        assert "result" in data
        assert "files" in data["result"]


def test_reviewer_endpoint(client: TestClient, mock_provider, mock_implement_output):
    """Test the reviewer endpoint."""
    with patch("src.app.api.agents.reviewer.ProviderFactory.create", return_value=mock_provider):
        response = client.post(
            "/api/agents/reviewer",
            json={
                "implementation": mock_implement_output.model_dump(),
                "requirements": "Build a REST API for user management",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "reviewer"
        assert "result" in data
        assert "overall_assessment" in data["result"]


def test_tester_endpoint(client: TestClient, mock_provider, mock_implement_output):
    """Test the tester endpoint."""
    with patch("src.app.api.agents.tester.ProviderFactory.create", return_value=mock_provider):
        response = client.post(
            "/api/agents/tester",
            json={
                "implementation": mock_implement_output.model_dump(),
                "requirements": "Build a REST API for user management",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "tester"
        assert "result" in data
        assert "test_cases" in data["result"]


def test_agent_error_handling(client: TestClient):
    """Test agent error handling."""
    with patch("src.app.api.agents.architect.ProviderFactory.create", side_effect=Exception("API error")):
        response = client.post(
            "/api/agents/architect",
            json={"requirements": "Build a REST API"},
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


def test_invalid_provider(client: TestClient):
    """Test with invalid provider."""
    with patch(
        "src.app.api.agents.architect.ProviderFactory.create",
        side_effect=ValueError("Unknown provider: invalid"),
    ):
        response = client.post(
            "/api/agents/architect",
            json={"requirements": "Build a REST API", "provider": "invalid"},
        )

        assert response.status_code == 400
