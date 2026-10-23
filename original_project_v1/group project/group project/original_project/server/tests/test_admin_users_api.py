"""Tests for the Admin User Management API."""

from models import Admin, Customer
from tests.helpers import admin_token, auth, customer_token


# --- Authentication ---


def test_no_jwt_rejected(client):
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401


def test_invalid_jwt_rejected(client):
    response = client.get("/api/v1/admin/users", headers=auth("invalid.token"))
    assert response.status_code == 401


def test_customer_jwt_rejected(client):
    token = customer_token(client)
    response = client.get("/api/v1/admin/users", headers=auth(token))
    assert response.status_code == 403


def test_admin_jwt_allowed(client, app):
    admin = admin_token(client, app)
    response = client.get("/api/v1/admin/users", headers=auth(admin))
    assert response.status_code == 200


# --- List ---


def test_admin_lists_users(client, app):
    admin = admin_token(client, app)
    customer_token(client, email="cust@example.com")

    response = client.get("/api/v1/admin/users", headers=auth(admin))
    users = response.get_json()["users"]
    emails = {u["email"] for u in users}
    assert "admin@example.com" in emails
    assert "cust@example.com" in emails


def test_customer_role_represented(client, app):
    admin = admin_token(client, app)
    customer_token(client, email="cust@example.com")

    users = client.get("/api/v1/admin/users", headers=auth(admin)).get_json()["users"]
    customer = next(u for u in users if u["email"] == "cust@example.com")
    assert customer["role"] == "customer"


def test_admin_role_represented(client, app):
    admin = admin_token(client, app)

    users = client.get("/api/v1/admin/users", headers=auth(admin)).get_json()["users"]
    admin_user = next(u for u in users if u["email"] == "admin@example.com")
    assert admin_user["role"] == "admin"


# --- Detail ---


def test_admin_views_customer(client, app):
    admin = admin_token(client, app)
    customer_token(client, email="cust@example.com")
    users = client.get("/api/v1/admin/users", headers=auth(admin)).get_json()["users"]
    customer_id = next(u for u in users if u["email"] == "cust@example.com")["id"]

    response = client.get(f"/api/v1/admin/users/{customer_id}", headers=auth(admin))
    assert response.status_code == 200
    assert response.get_json()["user"]["email"] == "cust@example.com"


def test_admin_views_admin(client, app):
    admin = admin_token(client, app)
    users = client.get("/api/v1/admin/users", headers=auth(admin)).get_json()["users"]
    admin_id = next(u for u in users if u["email"] == "admin@example.com")["id"]

    response = client.get(f"/api/v1/admin/users/{admin_id}", headers=auth(admin))
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "admin"


def test_nonexistent_user_404(client, app):
    admin = admin_token(client, app)
    response = client.get("/api/v1/admin/users/9999", headers=auth(admin))
    assert response.status_code == 404


# --- Security: no password_hash / plaintext password ---


def test_user_list_no_password_hash(client, app):
    admin = admin_token(client, app)
    customer_token(client, email="cust@example.com")

    users = client.get("/api/v1/admin/users", headers=auth(admin)).get_json()["users"]
    for user in users:
        assert "password_hash" not in user
        assert "password" not in user


def test_user_detail_no_password_hash(client, app):
    admin = admin_token(client, app)
    customer_token(client, email="cust@example.com")
    users = client.get("/api/v1/admin/users", headers=auth(admin)).get_json()["users"]
    customer_id = next(u for u in users if u["email"] == "cust@example.com")["id"]

    detail = client.get(f"/api/v1/admin/users/{customer_id}", headers=auth(admin)).get_json()["user"]
    assert "password_hash" not in detail
    assert "password" not in detail


# --- Permissions ---


def test_manage_users_permission_model():
    admin_perms = Admin(name="A", email="a@example.com", password_hash="h").get_permissions()
    customer_perms = Customer(name="C", email="c@example.com", password_hash="h").get_permissions()
    assert "manage_users" in admin_perms
    assert "manage_users" not in customer_perms


def test_manage_products_still_works(client, app):
    admin = admin_token(client, app)
    response = client.get("/api/v1/admin/products", headers=auth(admin))
    assert response.status_code == 200


def test_manage_orders_still_works(client, app):
    admin = admin_token(client, app)
    response = client.get("/api/v1/admin/orders", headers=auth(admin))
    assert response.status_code == 200


# --- Regression ---


def test_customer_registration_still_works(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Richard",
            "email": "richard@example.com",
            "phone": "0212345678",
            "password": "Password123",
        },
    )
    assert response.status_code == 201
