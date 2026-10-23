"""Focused tests for Phase 6D Admin User Management."""

from tests.helpers import admin_token, auth, create_product, customer_token


def _order_payload():
    return {
        "customer_name": "Richard",
        "phone": "0212345678",
        "pickup_date": "2026-10-10",
        "pickup_time": "15:00",
        "payment_reference_type": "bank_transfer",
        "payment_reference": "12345",
    }


def _create_order(client, app, token, name="Bread", price=11.0, stock=8):
    product = create_product(app, name=name, price=price, stock=stock)
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product.id, "quantity": 1},
        headers=auth(token),
    )
    return client.post("/api/v1/orders", json=_order_payload(), headers=auth(token))


def _register_user(client, name, email, phone="0211111111"):
    return client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "phone": phone, "password": "Password123"},
    )


# --- Authorization ---


def test_guest_cannot_list_users(client):
    assert client.get("/api/v1/admin/users").status_code == 401


def test_customer_cannot_list_users(client):
    token = customer_token(client)
    assert client.get("/api/v1/admin/users", headers=auth(token)).status_code == 403


def test_admin_can_list_users(client, app):
    token = admin_token(client, app)
    customer_token(client, email="cust@example.com")
    response = client.get("/api/v1/admin/users", headers=auth(token))
    assert response.status_code == 200
    emails = {u["email"] for u in response.get_json()["users"]}
    assert "admin@example.com" in emails
    assert "cust@example.com" in emails


def test_guest_cannot_get_user(client):
    assert client.get("/api/v1/admin/users/1").status_code == 401


def test_customer_cannot_get_user(client, app):
    admin_token(client, app)
    customer = customer_token(client, email="cust@example.com")
    assert client.get("/api/v1/admin/users/1", headers=auth(customer)).status_code == 403


def test_admin_can_get_user(client, app):
    admin = admin_token(client, app)
    customer_token(client, email="cust@example.com")
    users = client.get("/api/v1/admin/users", headers=auth(admin)).get_json()["users"]
    cust = next(u for u in users if u["email"] == "cust@example.com")

    response = client.get(f"/api/v1/admin/users/{cust['id']}", headers=auth(admin))
    assert response.status_code == 200
    assert response.get_json()["user"]["email"] == "cust@example.com"


def test_user_detail_never_exposes_password_hash(client, app):
    admin = admin_token(client, app)
    customer_token(client, email="cust@example.com")
    users = client.get("/api/v1/admin/users", headers=auth(admin)).get_json()["users"]
    cust = next(u for u in users if u["email"] == "cust@example.com")

    response = client.get(f"/api/v1/admin/users/{cust['id']}", headers=auth(admin))
    body = response.get_json()
    assert "password_hash" not in body["user"]
    assert "password" not in body["user"]


# --- Search ---


def test_search_by_name(client, app):
    admin = admin_token(client, app)
    _register_user(client, "Alice Smith", "alice@example.com")
    _register_user(client, "Bob Jones", "bob@example.com")

    response = client.get("/api/v1/admin/users?search=Alice", headers=auth(admin))
    emails = {u["email"] for u in response.get_json()["users"]}
    assert "alice@example.com" in emails
    assert "bob@example.com" not in emails


def test_search_by_email(client, app):
    admin = admin_token(client, app)
    _register_user(client, "Alice", "alice@example.com")
    _register_user(client, "Bob", "bob@example.com")

    response = client.get("/api/v1/admin/users?search=bob@example", headers=auth(admin))
    emails = {u["email"] for u in response.get_json()["users"]}
    assert "bob@example.com" in emails
    assert "alice@example.com" not in emails


def test_search_by_phone(client, app):
    admin = admin_token(client, app)
    _register_user(client, "Alice", "alice@example.com", phone="0211111111")
    _register_user(client, "Bob", "bob@example.com", phone="0212222222")

    response = client.get("/api/v1/admin/users?search=0211111", headers=auth(admin))
    emails = {u["email"] for u in response.get_json()["users"]}
    assert "alice@example.com" in emails
    assert "bob@example.com" not in emails


# --- Role filter ---


def test_role_filter_admin(client, app):
    admin = admin_token(client, app)
    customer_token(client, email="cust@example.com")

    response = client.get("/api/v1/admin/users?role=admin", headers=auth(admin))
    users = response.get_json()["users"]
    assert all(u["role"] == "admin" for u in users)
    assert any(u["email"] == "admin@example.com" for u in users)


def test_role_filter_customer(client, app):
    admin = admin_token(client, app)
    customer_token(client, email="cust@example.com")

    response = client.get("/api/v1/admin/users?role=customer", headers=auth(admin))
    users = response.get_json()["users"]
    assert all(u["role"] == "customer" for u in users)
    assert any(u["email"] == "cust@example.com" for u in users)


# --- Order association ---


def test_user_order_association(client, app):
    admin = admin_token(client, app)
    customer = customer_token(client, email="cust@example.com")
    _create_order(client, app, customer, name="Bread")

    users = client.get("/api/v1/admin/users", headers=auth(admin)).get_json()["users"]
    cust = next(u for u in users if u["email"] == "cust@example.com")
    response = client.get(f"/api/v1/admin/users/{cust['id']}", headers=auth(admin))
    body = response.get_json()
    assert len(body["orders"]) == 1
    assert body["orders"][0]["payment_status"] == "pending"
    assert body["orders"][0]["status"] == "pending"


def test_user_with_no_orders(client, app):
    admin = admin_token(client, app)
    customer_token(client, email="cust@example.com")

    users = client.get("/api/v1/admin/users", headers=auth(admin)).get_json()["users"]
    cust = next(u for u in users if u["email"] == "cust@example.com")
    response = client.get(f"/api/v1/admin/users/{cust['id']}", headers=auth(admin))
    assert response.get_json()["orders"] == []


def test_user_with_multiple_orders(client, app):
    admin = admin_token(client, app)
    customer = customer_token(client, email="cust@example.com")
    _create_order(client, app, customer, name="Bread")
    _create_order(client, app, customer, name="Cake", price=12.0)

    users = client.get("/api/v1/admin/users", headers=auth(admin)).get_json()["users"]
    cust = next(u for u in users if u["email"] == "cust@example.com")
    response = client.get(f"/api/v1/admin/users/{cust['id']}", headers=auth(admin))
    assert len(response.get_json()["orders"]) == 2


# --- Unknown user ---


def test_unknown_user_404(client, app):
    admin = admin_token(client, app)
    response = client.get("/api/v1/admin/users/9999", headers=auth(admin))
    assert response.status_code == 404

