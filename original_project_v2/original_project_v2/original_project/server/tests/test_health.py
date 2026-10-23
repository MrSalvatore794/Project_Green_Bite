"""Foundation tests for the GreenBite server."""

import pytest

from app import create_app


@pytest.fixture
def client():
    """Create a test client backed by a fresh testing-configured app."""
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_app_can_be_created():
    app = create_app("testing")
    assert app is not None


def test_health_returns_200(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_is_json(client):
    response = client.get("/api/v1/health")
    assert response.is_json
    assert response.get_json() == {
        "status": "ok",
        "service": "greenbite-server",
    }


def test_health_status_is_ok(client):
    response = client.get("/api/v1/health")
    assert response.get_json()["status"] == "ok"


def test_unknown_route_returns_json_error(client):
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    assert response.is_json
    body = response.get_json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert "message" in body["error"]
