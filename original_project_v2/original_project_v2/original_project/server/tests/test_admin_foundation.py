"""Focused tests for the Phase 6A Admin foundation."""

from werkzeug.security import generate_password_hash

from models import Admin, Customer
from tests.helpers import admin_token, auth, customer_token


# --- Permissions (RBAC) ---


def test_admin_has_foundation_permissions():
    admin = Admin(name="A", email="a@example.com", phone="0211111111", password_hash="x")
    perms = admin.get_permissions()
    assert "view_admin_dashboard" in perms
    assert "manage_products" in perms
    assert "manage_orders" in perms
    assert "manage_users" in perms


def test_customer_lacks_admin_permissions():
    customer = Customer(
        name="C", email="c@example.com", phone="0212222222", password_hash="x"
    )
    perms = customer.get_permissions()
    assert "view_admin_dashboard" not in perms
    assert "manage_products" not in perms
    assert "manage_orders" not in perms
    assert "manage_users" not in perms


# --- Login ---


def test_admin_login_success(client, app):
    admin = Admin(
        name="Admin",
        email="admin@example.com",
        phone="0211111111",
        password_hash=generate_password_hash("adminpass123"),
    )
    app.extensions["user_repository"].create_user(admin)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["user"]["role"] == "admin"
    assert body["access_token"]


def test_admin_login_invalid_password(client, app):
    admin = Admin(
        name="Admin",
        email="admin@example.com",
        phone="0211111111",
        password_hash=generate_password_hash("adminpass123"),
    )
    app.extensions["user_repository"].create_user(admin)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_customer_login_role_is_customer(client):
    token = customer_token(client)
    response = client.get("/api/v1/users/me", headers=auth(token))
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "customer"


# --- Admin API authorization boundary ---


def test_guest_admin_api_unauthorized(client):
    assert client.get("/api/v1/admin/orders").status_code == 401
    assert client.get("/api/v1/admin/products").status_code == 401
    assert client.get("/api/v1/admin/users").status_code == 401


def test_customer_admin_api_forbidden(client):
    token = customer_token(client)
    assert client.get("/api/v1/admin/orders", headers=auth(token)).status_code == 403
    assert client.get("/api/v1/admin/products", headers=auth(token)).status_code == 403
    assert client.get("/api/v1/admin/users", headers=auth(token)).status_code == 403


def test_admin_admin_api_allowed(client, app):
    token = admin_token(client, app)
    assert client.get("/api/v1/admin/orders", headers=auth(token)).status_code == 200
    assert client.get("/api/v1/admin/products", headers=auth(token)).status_code == 200
    assert client.get("/api/v1/admin/users", headers=auth(token)).status_code == 200
