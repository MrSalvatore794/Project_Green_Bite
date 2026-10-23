"""Tests for the public / authenticated API boundary."""

from tests.helpers import create_product


def test_cart_requires_auth(client):
    response = client.get("/api/v1/cart")
    assert response.status_code == 401


def test_cart_add_requires_auth(client, app):
    product = create_product(app, name="Bread", price=11.0, stock=8)
    response = client.post(
        "/api/v1/cart/items", json={"product_id": product.id, "quantity": 1}
    )
    assert response.status_code == 401


def test_order_create_requires_auth(client):
    response = client.post(
        "/api/v1/orders",
        json={
            "customer_name": "Richard",
            "phone": "0212345678",
            "pickup_date": "2026-10-10",
            "pickup_time": "15:00",
            "payment_reference_type": "bank_transfer",
            "payment_reference": "12345",
        },
    )
    assert response.status_code == 401


def test_order_list_requires_auth(client):
    response = client.get("/api/v1/orders")
    assert response.status_code == 401


def test_order_detail_requires_auth(client):
    response = client.get("/api/v1/orders/1")
    assert response.status_code == 401
