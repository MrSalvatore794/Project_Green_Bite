"""Tests for the customer cart API."""

from tests.helpers import auth, create_product, customer_token


def test_get_empty_cart(client):
    token = customer_token(client)
    response = client.get("/api/v1/cart", headers=auth(token))
    assert response.status_code == 200
    body = response.get_json()["cart"]
    assert body["items"] == []
    assert body["total"] == 0.0


def test_add_product(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    response = client.post(
        "/api/v1/cart/items",
        json={"product_id": product.id, "quantity": 2},
        headers=auth(token),
    )
    assert response.status_code == 200
    items = response.get_json()["cart"]["items"]
    assert len(items) == 1
    assert items[0]["product_id"] == product.id
    assert items[0]["quantity"] == 2
    assert items[0]["subtotal"] == 22.0


def test_add_same_product_merges_quantity(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    client.post(
        "/api/v1/cart/items",
        json={"product_id": product.id, "quantity": 2},
        headers=auth(token),
    )
    response = client.post(
        "/api/v1/cart/items",
        json={"product_id": product.id, "quantity": 3},
        headers=auth(token),
    )

    items = response.get_json()["cart"]["items"]
    assert len(items) == 1
    assert items[0]["quantity"] == 5


def test_invalid_product_rejected(client):
    token = customer_token(client)
    response = client.post(
        "/api/v1/cart/items",
        json={"product_id": 9999, "quantity": 1},
        headers=auth(token),
    )
    assert response.status_code == 404


def test_inactive_product_rejected(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8, active=False)
    response = client.post(
        "/api/v1/cart/items",
        json={"product_id": product.id, "quantity": 1},
        headers=auth(token),
    )
    assert response.status_code == 409


def test_insufficient_stock_rejected(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=5)
    response = client.post(
        "/api/v1/cart/items",
        json={"product_id": product.id, "quantity": 6},
        headers=auth(token),
    )
    assert response.status_code == 409


def test_non_positive_quantity_rejected(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    for quantity in (0, -1):
        response = client.post(
            "/api/v1/cart/items",
            json={"product_id": product.id, "quantity": quantity},
            headers=auth(token),
        )
        assert response.status_code == 400


def test_update_quantity(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=10)
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product.id, "quantity": 2},
        headers=auth(token),
    )

    response = client.put(
        f"/api/v1/cart/items/{product.id}",
        json={"quantity": 4},
        headers=auth(token),
    )
    assert response.status_code == 200
    assert response.get_json()["cart"]["items"][0]["quantity"] == 4


def test_remove_item(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product.id, "quantity": 2},
        headers=auth(token),
    )

    response = client.delete(f"/api/v1/cart/items/{product.id}", headers=auth(token))
    assert response.status_code == 200
    assert response.get_json()["cart"]["items"] == []


def test_clear_cart(client, app):
    token = customer_token(client)
    p1 = create_product(app, name="Bread", price=11.0, stock=8)
    p2 = create_product(app, name="Cake", price=12.0, stock=8)
    client.post(
        "/api/v1/cart/items",
        json={"product_id": p1.id, "quantity": 1},
        headers=auth(token),
    )
    client.post(
        "/api/v1/cart/items",
        json={"product_id": p2.id, "quantity": 2},
        headers=auth(token),
    )

    response = client.delete("/api/v1/cart", headers=auth(token))
    assert response.status_code == 200
    assert response.get_json()["cart"]["items"] == []


def test_customer_cannot_access_another_users_cart(client, app):
    token1 = customer_token(client, email="u1@example.com")
    token2 = customer_token(client, email="u2@example.com")
    product = create_product(app, name="Bread", price=11.0, stock=8)
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product.id, "quantity": 2},
        headers=auth(token1),
    )

    response = client.get("/api/v1/cart", headers=auth(token2))
    assert response.get_json()["cart"]["items"] == []
