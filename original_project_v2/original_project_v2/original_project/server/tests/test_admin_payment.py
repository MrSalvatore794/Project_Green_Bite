"""Focused tests for Phase 6C manual payment verification."""

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


def _create_order(client, app, token):
    product = create_product(app, name="Bread", price=11.0, stock=8)
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product.id, "quantity": 1},
        headers=auth(token),
    )
    response = client.post("/api/v1/orders", json=_order_payload(), headers=auth(token))
    assert response.status_code == 201
    return response.get_json()["order"]


# --- Payment status lifecycle ---


def test_new_order_defaults_payment_pending(client, app):
    token = customer_token(client)
    order = _create_order(client, app, token)
    assert order["payment_status"] == "pending"


def test_admin_can_mark_payment_completed(client, app):
    admin = admin_token(client, app)
    customer = customer_token(client, email="cust@example.com")
    order = _create_order(client, app, customer)

    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/payment-status",
        json={"payment_status": "completed"},
        headers=auth(admin),
    )
    assert response.status_code == 200
    assert response.get_json()["order"]["payment_status"] == "completed"


def test_admin_can_mark_payment_failed(client, app):
    admin = admin_token(client, app)
    customer = customer_token(client, email="cust@example.com")
    order = _create_order(client, app, customer)

    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/payment-status",
        json={"payment_status": "failed"},
        headers=auth(admin),
    )
    assert response.status_code == 200
    assert response.get_json()["order"]["payment_status"] == "failed"


def test_failed_payment_can_become_completed(client, app):
    admin = admin_token(client, app)
    customer = customer_token(client, email="cust@example.com")
    order = _create_order(client, app, customer)

    client.patch(
        f"/api/v1/admin/orders/{order['id']}/payment-status",
        json={"payment_status": "failed"},
        headers=auth(admin),
    )
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/payment-status",
        json={"payment_status": "completed"},
        headers=auth(admin),
    )
    assert response.status_code == 200
    assert response.get_json()["order"]["payment_status"] == "completed"


def test_invalid_payment_status_rejected(client, app):
    admin = admin_token(client, app)
    customer = customer_token(client, email="cust@example.com")
    order = _create_order(client, app, customer)

    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/payment-status",
        json={"payment_status": "bogus"},
        headers=auth(admin),
    )
    assert response.status_code == 400


def test_completed_payment_cannot_revert(client, app):
    admin = admin_token(client, app)
    customer = customer_token(client, email="cust@example.com")
    order = _create_order(client, app, customer)

    client.patch(
        f"/api/v1/admin/orders/{order['id']}/payment-status",
        json={"payment_status": "completed"},
        headers=auth(admin),
    )
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/payment-status",
        json={"payment_status": "pending"},
        headers=auth(admin),
    )
    assert response.status_code == 400


# --- Authorization ---


def test_customer_cannot_modify_payment_status(client, app):
    customer = customer_token(client)
    order = _create_order(client, app, customer)
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/payment-status",
        json={"payment_status": "completed"},
        headers=auth(customer),
    )
    assert response.status_code == 403


def test_guest_cannot_modify_payment_status(client, app):
    customer = customer_token(client)
    order = _create_order(client, app, customer)
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/payment-status",
        json={"payment_status": "completed"},
    )
    assert response.status_code == 401


def test_customer_cannot_access_admin_orders(client):
    customer = customer_token(client)
    response = client.get("/api/v1/admin/orders", headers=auth(customer))
    assert response.status_code == 403


# --- Customer visibility ---


def test_customer_order_list_includes_payment_status(client, app):
    token = customer_token(client)
    _create_order(client, app, token)

    response = client.get("/api/v1/orders", headers=auth(token))
    orders = response.get_json()["orders"]
    assert orders[0]["payment_status"] == "pending"


def test_customer_order_detail_includes_payment_status(client, app):
    token = customer_token(client)
    order = _create_order(client, app, token)

    response = client.get(f"/api/v1/orders/{order['id']}", headers=auth(token))
    assert response.get_json()["order"]["payment_status"] == "pending"
