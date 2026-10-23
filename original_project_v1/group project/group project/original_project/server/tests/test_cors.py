"""Tests for the development CORS configuration."""


def test_cors_allows_known_origin(client):
    response = client.get(
        "/api/v1/products", headers={"Origin": "http://localhost:5174"}
    )
    assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:5174"


def test_cors_allows_customer_origin(client):
    response = client.get(
        "/api/v1/products", headers={"Origin": "http://localhost:5173"}
    )
    assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"


def test_cors_rejects_unknown_origin(client):
    response = client.get(
        "/api/v1/products", headers={"Origin": "http://evil.example.com"}
    )
    assert "Access-Control-Allow-Origin" not in response.headers


def test_cors_preflight_options(client):
    response = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "http://localhost:5174",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:5174"
    assert "POST" in response.headers.get("Access-Control-Allow-Methods", "")
