import pytest
from fastapi.testclient import TestClient

from src.app.main import create_app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(create_app())


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
