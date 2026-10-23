"""Tests for customer-initiated order cancellation."""

from tests.helpers import admin_token, auth, create_product, customer_token


def _payload():
    return {
        "customer_name": "Richard",
        "phone": "0212345678",
        "pickup_date": "2026-10-10",
        "pickup_time": "15:00",
        "payment_reference_type": "bank_transfer",
        "payment_reference": "12345",
    }


def _add_to_cart(client, token, product_id, quantity):
    return client.post(
        "/api/v1/cart/items",
        json={"product_id": product_id, "quantity": quantity},
        headers=auth(token),
    )


def _create_order(client, token):
    return client.post("/api/v1/orders", json=_payload(), headers=auth(token))


def _cancel(client, token, order_id):
    return client.post(f"/api/v1/orders/{order_id}/cancel", headers=auth(token))


def _order(client, app, token, name="Bread", price=11.0, stock=8, quantity=1):
    product = create_product(app, name=name, price=price, stock=stock)
    _add_to_cart(client, token, product.id, quantity)
    order = _create_order(client, token).get_json()["order"]
    return order, product


def _set_payment_status(client, admin, order_id, status):
    response = client.patch(
        f"/api/v1/admin/orders/{order_id}/payment-status",
        json={"payment_status": status},
        headers=auth(admin),
    )
    assert response.status_code == 200


def _set_status(client, admin, order_id, status):
    response = client.patch(
        f"/api/v1/admin/orders/{order_id}/status",
        json={"status": status},
        headers=auth(admin),
    )
    assert response.status_code == 200


def test_cancel_pending_unpaid_order(client, app):
    token = customer_token(client)
    order, product = _order(client, app, token, stock=8, quantity=3)

    response = _cancel(client, token, order["id"])
    assert response.status_code == 200
    body = response.get_json()["order"]
    assert body["canceled_at"] is not None
    assert body["status"] == "pending"  # fulfillment status unchanged
    assert body["payment_status"] == "pending"

    assert app.extensions["product_service"].get_product(product.id).stock_quantity == 8


def test_cancel_paid_order_keeps_payment_completed(client, app):
    token = customer_token(client)
    admin = admin_token(client, app)
    order, product = _order(client, app, token, stock=8, quantity=2)
    _set_payment_status(client, admin, order["id"], "completed")

    response = _cancel(client, token, order["id"])
    assert response.status_code == 200
    body = response.get_json()["order"]
    assert body["canceled_at"] is not None
    assert body["payment_status"] == "completed"  # refund is NOT claimed complete


def test_cancel_failed_payment_order(client, app):
    token = customer_token(client)
    admin = admin_token(client, app)
    order, product = _order(client, app, token, stock=8, quantity=1)
    _set_payment_status(client, admin, order["id"], "failed")

    response = _cancel(client, token, order["id"])
    assert response.status_code == 200
    assert response.get_json()["order"]["canceled_at"] is not None


def test_guest_cannot_cancel(client, app):
    token = customer_token(client)
    order, _ = _order(client, app, token)
    response = client.post(f"/api/v1/orders/{order['id']}/cancel")
    assert response.status_code == 401


def test_customer_cannot_cancel_another_customers_order(client, app):
    token_a = customer_token(client, email="a@example.com")
    token_b = customer_token(client, email="b@example.com")
    order, _ = _order(client, app, token_a)
    response = _cancel(client, token_b, order["id"])
    assert response.status_code == 404


def test_non_pending_order_cannot_be_canceled(client, app):
    token = customer_token(client)
    admin = admin_token(client, app)
    order, product = _order(client, app, token, stock=8, quantity=2)
    _set_status(client, admin, order["id"], "confirmed")

    response = _cancel(client, token, order["id"])
    assert response.status_code == 409
    assert app.extensions["product_service"].get_product(product.id).stock_quantity == 6


def test_collected_order_cannot_be_canceled(client, app):
    token = customer_token(client)
    admin = admin_token(client, app)
    order, _ = _order(client, app, token, stock=8, quantity=1)
    for status in ("confirmed", "preparing", "ready_for_pickup", "collected"):
        _set_status(client, admin, order["id"], status)

    response = _cancel(client, token, order["id"])
    assert response.status_code == 409


def test_already_canceled_cannot_cancel_again(client, app):
    token = customer_token(client)
    order, product = _order(client, app, token, stock=8, quantity=2)
    _cancel(client, token, order["id"])

    response = _cancel(client, token, order["id"])
    assert response.status_code == 409
    assert app.extensions["product_service"].get_product(product.id).stock_quantity == 8


def test_cancel_restores_multiple_items(client, app):
    token = customer_token(client)
    p1 = create_product(app, name="Bread", price=11.0, stock=8)
    p2 = create_product(app, name="Cake", price=12.0, stock=10)
    _add_to_cart(client, token, p1.id, 2)
    _add_to_cart(client, token, p2.id, 3)
    order = _create_order(client, token).get_json()["order"]

    response = _cancel(client, token, order["id"])
    assert response.status_code == 200
    assert app.extensions["product_service"].get_product(p1.id).stock_quantity == 8
    assert app.extensions["product_service"].get_product(p2.id).stock_quantity == 10


def test_cancel_preserves_item_snapshots(client, app):
    token = customer_token(client)
    order, product = _order(
        client, app, token, name="Walnut Raisin Bread", price=11.0, stock=8, quantity=2
    )
    _cancel(client, token, order["id"])

    detail = client.get(f"/api/v1/orders/{order['id']}", headers=auth(token)).get_json()["order"]
    item = detail["items"][0]
    assert item["product_name"] == "Walnut Raisin Bread"
    assert item["unit_price"] == 11.0
    assert item["quantity"] == 2
    assert item["subtotal"] == 22.0


def test_canceled_order_cannot_be_advanced(client, app):
    token = customer_token(client)
    order, _ = _order(client, app, token)
    _cancel(client, token, order["id"])

    admin = admin_token(client, app)
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "confirmed"},
        headers=auth(admin),
    )
    assert response.status_code == 400
