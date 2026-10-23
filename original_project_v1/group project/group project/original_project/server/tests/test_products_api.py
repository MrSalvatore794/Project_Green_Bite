"""Tests for the customer product API."""

from tests.helpers import auth, create_product, customer_token


def test_list_active_products(client, app):
    token = customer_token(client)
    create_product(app, name="Bread", price=11.0, stock=8)
    create_product(app, name="Cake", price=12.0, stock=4)

    response = client.get("/api/v1/products", headers=auth(token))
    assert response.status_code == 200
    names = [p["name"] for p in response.get_json()["products"]]
    assert names == ["Bread", "Cake"]


def test_products_list_is_public(client):
    response = client.get("/api/v1/products")
    assert response.status_code == 200


def test_product_detail_is_public(client, app):
    product = create_product(app, name="Bread", price=11.0, stock=8)

    response = client.get(f"/api/v1/products/{product.id}")
    assert response.status_code == 200
    assert response.get_json()["product"]["name"] == "Bread"


def test_inactive_product_detail_404(client, app):
    product = create_product(app, name="Hidden", price=12.0, stock=4, active=False)

    response = client.get(f"/api/v1/products/{product.id}")
    assert response.status_code == 404


def test_zero_stock_product_detail_404(client, app):
    product = create_product(app, name="Empty", price=13.0, stock=0, active=True)

    response = client.get(f"/api/v1/products/{product.id}")
    assert response.status_code == 404


def test_inactive_product_not_exposed(client, app):
    token = customer_token(client)
    create_product(app, name="Active Bread", price=11.0, stock=8, active=True)
    inactive = create_product(
        app, name="Inactive Cake", price=12.0, stock=4, active=False
    )

    response = client.get("/api/v1/products", headers=auth(token))
    assert [p["name"] for p in response.get_json()["products"]] == ["Active Bread"]

    detail = client.get(f"/api/v1/products/{inactive.id}", headers=auth(token))
    assert detail.status_code == 404


def test_product_detail(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    response = client.get(f"/api/v1/products/{product.id}", headers=auth(token))
    assert response.status_code == 200
    body = response.get_json()["product"]
    assert body["name"] == "Bread"
    assert body["price"] == 11.0


def test_nonexistent_product_404(client):
    token = customer_token(client)
    response = client.get("/api/v1/products/9999", headers=auth(token))
    assert response.status_code == 404
