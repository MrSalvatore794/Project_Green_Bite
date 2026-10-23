"""Tests for the authentication / user HTTP API."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from flask import jsonify
from werkzeug.security import generate_password_hash

from app import create_app
from models import Admin
from utils.auth import generate_access_token, require_auth, require_role


@pytest.fixture
def app(tmp_path):
    app = create_app(
        "testing",
        {
            "DATABASE_PATH": str(tmp_path / "auth_test.db"),
            "JWT_SECRET_KEY": "test-jwt-secret-key-for-testing-only-0123456789",
        },
    )

    # A test-only admin route to verify the reusable role mechanism.
    @app.route("/api/v1/admin/test", methods=["GET"])
    @require_auth
    @require_role("admin")
    def admin_test():
        return jsonify({"message": "admin only"}), 200

    return app


@pytest.fixture
def client(app):
    return app.test_client()


def _register(
    client,
    name="Richard",
    email="richard@example.com",
    phone="0212345678",
    password="Password123",
):
    return client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "phone": phone, "password": password},
    )


def _login_token(client, email, password):
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200
    return response.get_json()["access_token"]


def _seed_admin(app):
    admin = Admin(
        name="Admin",
        email="admin@example.com",
        phone="0211111111",
        password_hash=generate_password_hash("adminpass123"),
    )
    app.extensions["user_repository"].create_user(admin)


# --- Registration ---


def test_register_success(client):
    response = _register(client)
    assert response.status_code == 201
    body = response.get_json()
    assert body["user"]["id"] is not None
    assert body["user"]["email"] == "richard@example.com"
    assert body["user"]["role"] == "customer"


@pytest.mark.parametrize("missing", ["name", "email", "phone", "password"])
def test_register_missing_field(client, missing):
    data = {
        "name": "Richard",
        "email": "richard@example.com",
        "phone": "0212345678",
        "password": "Password123",
    }
    del data[missing]
    response = client.post("/api/v1/auth/register", json=data)
    assert response.status_code == 400


def test_register_duplicate_email(client):
    _register(client)
    response = _register(client, name="Salin")
    assert response.status_code == 409


def test_register_cannot_create_admin(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Richard",
            "email": "richard@example.com",
            "phone": "0212345678",
            "password": "Password123",
            "role": "admin",
        },
    )
    assert response.status_code == 201
    assert response.get_json()["user"]["role"] == "customer"


def test_password_stored_hashed(client, app):
    _register(client)
    stored = app.extensions["user_repository"].find_by_email("richard@example.com")
    assert stored.password_hash != "Password123"
    assert "Password123" not in stored.password_hash


def test_register_response_does_not_expose_password_hash(client):
    response = _register(client)
    body = response.get_json()
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


# --- Login ---


def test_login_success(client):
    _register(client)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "richard@example.com", "password": "Password123"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["access_token"]
    assert body["token_type"] == "Bearer"
    assert body["user"]["email"] == "richard@example.com"
    assert "password_hash" not in body["user"]


def test_login_invalid_password(client):
    _register(client)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "richard@example.com", "password": "WrongPassword"},
    )
    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "unknown@example.com", "password": "Password123"},
    )
    assert response.status_code == 401


def test_login_admin(client, app):
    _seed_admin(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "admin"


# --- JWT ---


def test_jwt_generation(app):
    with app.app_context():
        token = generate_access_token(1, "customer")
    assert isinstance(token, str)
    payload = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
    assert payload["sub"] == "1"
    assert payload["role"] == "customer"


def test_valid_token_accepted(client):
    _register(client)
    token = _login_token(client, "richard@example.com", "Password123")
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_missing_token_rejected(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_malformed_token_rejected(client):
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": "Token abc"}
    )
    assert response.status_code == 401
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer"}
    )
    assert response.status_code == 401


def test_invalid_token_rejected(client):
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


def test_expired_token_rejected(client, app):
    expired = jwt.encode(
        {
            "sub": "1",
            "role": "customer",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {expired}"}
    )
    assert response.status_code == 401


# --- Current user ---


def test_users_me_returns_user(client):
    _register(client)
    token = _login_token(client, "richard@example.com", "Password123")
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    user = response.get_json()["user"]
    assert user["email"] == "richard@example.com"
    assert user["role"] == "customer"


def test_users_me_uses_token_identity(client):
    _register(client)
    token = _login_token(client, "richard@example.com", "Password123")
    response = client.get(
        "/api/v1/users/me?user_id=999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["email"] == "richard@example.com"


# --- Authorization (role mechanism) ---


def test_customer_cannot_access_admin_route(client):
    _register(client)
    token = _login_token(client, "richard@example.com", "Password123")
    response = client.get(
        "/api/v1/admin/test", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_admin_can_access_admin_route(client, app):
    _seed_admin(app)
    token = _login_token(client, "admin@example.com", "adminpass123")
    response = client.get(
        "/api/v1/admin/test", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_non_integer_sub_rejected(client, app):
    token = jwt.encode(
        {
            "sub": "abc",
            "role": "customer",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "UNAUTHORIZED"


def test_missing_sub_rejected(client, app):
    token = jwt.encode(
        {
            "role": "customer",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_valid_integer_sub_works(client, app):
    _register(client)
    user = app.extensions["user_repository"].find_by_email("richard@example.com")
    token = jwt.encode(
        {
            "sub": str(user.id),
            "role": "customer",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

