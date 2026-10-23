"""Tests for the product like API and like persistence."""

from tests.helpers import auth, create_product, customer_token


def _like(client, token, product_id):
    return client.post(f"/api/v1/products/{product_id}/like", headers=auth(token))


def _unlike(client, token, product_id):
    return client.delete(f"/api/v1/products/{product_id}/like", headers=auth(token))


def test_like_increases_count(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    response = _like(client, token, product.id)
    assert response.status_code == 200
    body = response.get_json()
    assert body["liked"] is True
    assert body["like_count"] == 1


def test_duplicate_like_increments_once(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    _like(client, token, product.id)
    response = _like(client, token, product.id)
    assert response.status_code == 200
    assert response.get_json()["like_count"] == 1


def test_unlike_decreases_count(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    _like(client, token, product.id)

    response = _unlike(client, token, product.id)
    assert response.status_code == 200
    body = response.get_json()
    assert body["liked"] is False
    assert body["like_count"] == 0


def test_repeated_unlike_not_negative(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    _unlike(client, token, product.id)
    response = _unlike(client, token, product.id)
    assert response.status_code == 200
    assert response.get_json()["like_count"] == 0


def test_user_isolation(client, app):
    token_a = customer_token(client, email="a@example.com")
    token_b = customer_token(client, email="b@example.com")
    product = create_product(app, name="Bread", price=11.0, stock=8)
    _like(client, token_a, product.id)

    detail_a = client.get(f"/api/v1/products/{product.id}", headers=auth(token_a))
    body_a = detail_a.get_json()["product"]
    assert body_a["like_count"] == 1
    assert body_a["liked_by_current_user"] is True

    detail_b = client.get(f"/api/v1/products/{product.id}", headers=auth(token_b))
    body_b = detail_b.get_json()["product"]
    assert body_b["like_count"] == 1
    assert body_b["liked_by_current_user"] is False


def test_guest_cannot_like(client, app):
    product = create_product(app, name="Bread", price=11.0, stock=8)
    response = client.post(f"/api/v1/products/{product.id}/like")
    assert response.status_code == 401


def test_detail_like_count_for_guest(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    _like(client, token, product.id)

    response = client.get(f"/api/v1/products/{product.id}")
    body = response.get_json()["product"]
    assert body["like_count"] == 1
    assert body["liked_by_current_user"] is False


def test_like_persists(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    _like(client, token, product.id)

    response = client.get(f"/api/v1/products/{product.id}", headers=auth(token))
    body = response.get_json()["product"]
    assert body["like_count"] == 1
    assert body["liked_by_current_user"] is True


def test_database_uniqueness(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    _like(client, token, product.id)
    _like(client, token, product.id)

    db = app.extensions["db"]
    with db.connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM product_likes WHERE product_id = ?",
            (product.id,),
        ).fetchone()
    assert row[0] == 1
