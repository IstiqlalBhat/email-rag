"""
Example unit tests.
"""
import pytest


def test_example():
    """Example test case."""
    assert 1 + 1 == 2


def test_api_health(client):
    """Test API health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
