"""Tests for the liked-products list API."""

from tests.helpers import auth, create_product, customer_token


def _like(client, token, product_id):
    return client.post(f"/api/v1/products/{product_id}/like", headers=auth(token))


def _liked(client, token):
    return client.get("/api/v1/products/liked", headers=auth(token))


def test_liked_requires_auth(client):
    response = client.get("/api/v1/products/liked")
    assert response.status_code == 401


def test_liked_empty_by_default(client):
    token = customer_token(client)
    response = _liked(client, token)
    assert response.status_code == 200
    assert response.get_json()["products"] == []


def test_liked_returns_only_liked(client, app):
    token = customer_token(client)
    bread = create_product(app, name="Bread", price=11.0, stock=8)
    cake = create_product(app, name="Cake", price=12.0, stock=4)
    create_product(app, name="Bun", price=2.5, stock=20)
    _like(client, token, bread.id)
    _like(client, token, cake.id)

    names = [p["name"] for p in _liked(client, token).get_json()["products"]]
    assert names == ["Bread", "Cake"]


def test_liked_is_user_isolated(client, app):
    token_a = customer_token(client, email="a@example.com")
    token_b = customer_token(client, email="b@example.com")
    product = create_product(app, name="Bread", price=11.0, stock=8)
    _like(client, token_a, product.id)

    assert [p["name"] for p in _liked(client, token_a).get_json()["products"]] == ["Bread"]
    assert _liked(client, token_b).get_json()["products"] == []


def test_liked_excludes_unavailable(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    _like(client, token, product.id)
    app.extensions["product_service"].set_product_active(product.id, False)

    assert _liked(client, token).get_json()["products"] == []


def test_unlike_removes_from_liked(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    _like(client, token, product.id)
    client.delete(f"/api/v1/products/{product.id}/like", headers=auth(token))

    assert _liked(client, token).get_json()["products"] == []


def test_duplicate_like_lists_once(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    _like(client, token, product.id)
    _like(client, token, product.id)

    names = [p["name"] for p in _liked(client, token).get_json()["products"]]
    assert names == ["Bread"]
