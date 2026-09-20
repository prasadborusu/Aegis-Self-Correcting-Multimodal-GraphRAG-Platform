"""
Tests for Aegis Health and System Endpoints.
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_health_endpoint():
    """Verify that the /health endpoint responds with 200 OK and expected structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "aegis-backend"
    assert "version" in data
    assert "region" in data
    assert "timestamp" in data
    assert "subsystems" in data
    assert "bedrock" in data["subsystems"]
    assert "s3" in data["subsystems"]
    assert "dynamodb" in data["subsystems"]


def test_v1_health_endpoint():
    """Verify that /api/v1/health functions identically."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "aegis-backend"
