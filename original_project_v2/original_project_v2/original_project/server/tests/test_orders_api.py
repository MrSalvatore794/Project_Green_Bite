"""Tests for the customer order API."""

from tests.helpers import auth, create_product, customer_token


def _order_payload():
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
    return client.post("/api/v1/orders", json=_order_payload(), headers=auth(token))


def test_create_order_successfully(client, app):
    token = customer_token(client)
    bread = create_product(app, name="Bread", price=11.0, stock=8)
    cake = create_product(app, name="Cake", price=12.5, stock=10)
    _add_to_cart(client, token, bread.id, 2)
    _add_to_cart(client, token, cake.id, 1)

    response = _create_order(client, token)
    assert response.status_code == 201
    order = response.get_json()["order"]
    assert order["total_amount"] == 34.5
    assert order["status"] == "pending"
    assert len(order["items"]) == 2


def test_empty_cart_cannot_create_order(client):
    token = customer_token(client)
    response = _create_order(client, token)
    assert response.status_code == 400


def test_insufficient_stock_cannot_create_order(client, app):
    token = customer_token(client)
    bread = create_product(app, name="Bread", price=11.0, stock=5)
    _add_to_cart(client, token, bread.id, 3)
    app.extensions["product_service"].update_stock(bread.id, 2)

    response = _create_order(client, token)
    assert response.status_code == 409


def test_order_reduces_stock(client, app):
    token = customer_token(client)
    bread = create_product(app, name="Bread", price=11.0, stock=8)
    _add_to_cart(client, token, bread.id, 3)

    _create_order(client, token)
    assert app.extensions["product_service"].get_product(bread.id).stock_quantity == 5


def test_order_clears_cart(client, app):
    token = customer_token(client)
    bread = create_product(app, name="Bread", price=11.0, stock=8)
    _add_to_cart(client, token, bread.id, 3)

    _create_order(client, token)
    cart = client.get("/api/v1/cart", headers=auth(token)).get_json()["cart"]
    assert cart["items"] == []


def test_order_total_is_correct(client, app):
    token = customer_token(client)
    bread = create_product(app, name="Bread", price=11.0, stock=8)
    cake = create_product(app, name="Cake", price=12.5, stock=10)
    _add_to_cart(client, token, bread.id, 2)
    _add_to_cart(client, token, cake.id, 1)

    response = _create_order(client, token)
    assert response.get_json()["order"]["total_amount"] == 34.5


def test_order_item_snapshots(client, app):
    token = customer_token(client)
    bread = create_product(app, name="Walnut Raisin Bread", price=11.0, stock=8)
    _add_to_cart(client, token, bread.id, 2)

    order = _create_order(client, token).get_json()["order"]

    # Change the product price after ordering.
    app.extensions["product_service"].update_product(bread.id, price=99.0)

    detail = client.get(f"/api/v1/orders/{order['id']}", headers=auth(token))
    item = detail.get_json()["order"]["items"][0]
    assert item["product_name"] == "Walnut Raisin Bread"
    assert item["unit_price"] == 11.0
    assert item["subtotal"] == 22.0


def test_customer_lists_own_orders(client, app):
    token = customer_token(client)
    bread = create_product(app, name="Bread", price=11.0, stock=8)
    _add_to_cart(client, token, bread.id, 1)
    _create_order(client, token)

    response = client.get("/api/v1/orders", headers=auth(token))
    assert response.status_code == 200
    orders = response.get_json()["orders"]
    assert len(orders) == 1
    assert orders[0]["total_amount"] == 11.0


def test_customer_retrieves_own_order(client, app):
    token = customer_token(client)
    bread = create_product(app, name="Bread", price=11.0, stock=8)
    _add_to_cart(client, token, bread.id, 1)
    order = _create_order(client, token).get_json()["order"]

    response = client.get(f"/api/v1/orders/{order['id']}", headers=auth(token))
    assert response.status_code == 200
    assert response.get_json()["order"]["id"] == order["id"]


def test_customer_cannot_retrieve_another_users_order(client, app):
    token1 = customer_token(client, email="u1@example.com")
    token2 = customer_token(client, email="u2@example.com")
    bread = create_product(app, name="Bread", price=11.0, stock=8)
    _add_to_cart(client, token1, bread.id, 1)
    order = _create_order(client, token1).get_json()["order"]

    response = client.get(f"/api/v1/orders/{order['id']}", headers=auth(token2))
    assert response.status_code == 404


def test_nonexistent_order_404(client):
    token = customer_token(client)
    response = client.get("/api/v1/orders/9999", headers=auth(token))
    assert response.status_code == 404
