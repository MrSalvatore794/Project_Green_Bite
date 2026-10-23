"""Tests for the Admin Product Management API."""

from tests.helpers import admin_token, auth, create_product, customer_token


# --- Authentication ---


def test_no_jwt_rejected(client):
    response = client.get("/api/v1/admin/products")
    assert response.status_code == 401


def test_invalid_jwt_rejected(client):
    response = client.get("/api/v1/admin/products", headers=auth("invalid.token"))
    assert response.status_code == 401


def test_customer_jwt_rejected(client):
    token = customer_token(client)
    response = client.get("/api/v1/admin/products", headers=auth(token))
    assert response.status_code == 403


def test_admin_jwt_allowed(client, app):
    token = admin_token(client, app)
    response = client.get("/api/v1/admin/products", headers=auth(token))
    assert response.status_code == 200


# --- List ---


def test_admin_lists_all_products(client, app):
    token = admin_token(client, app)
    create_product(app, name="Active", price=11.0, stock=8, active=True)
    create_product(app, name="Inactive", price=12.0, stock=4, active=False)
    create_product(app, name="ZeroStock", price=13.0, stock=0, active=True)

    response = client.get("/api/v1/admin/products", headers=auth(token))
    products = response.get_json()["products"]
    assert {p["name"] for p in products} == {"Active", "Inactive", "ZeroStock"}


def test_admin_list_includes_inactive(client, app):
    token = admin_token(client, app)
    create_product(app, name="Hidden", price=12.0, stock=4, active=False)

    response = client.get("/api/v1/admin/products", headers=auth(token))
    products = response.get_json()["products"]
    assert any(p["name"] == "Hidden" and p["is_active"] is False for p in products)


def test_admin_list_includes_zero_stock(client, app):
    token = admin_token(client, app)
    create_product(app, name="Empty", price=13.0, stock=0, active=True)

    response = client.get("/api/v1/admin/products", headers=auth(token))
    products = response.get_json()["products"]
    assert any(p["name"] == "Empty" and p["stock_quantity"] == 0 for p in products)


# --- Detail ---


def test_admin_views_active_product(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8, active=True)

    response = client.get(f"/api/v1/admin/products/{product.id}", headers=auth(token))
    assert response.status_code == 200
    assert response.get_json()["product"]["name"] == "Bread"


def test_admin_views_inactive_product(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Cake", price=12.0, stock=4, active=False)

    response = client.get(f"/api/v1/admin/products/{product.id}", headers=auth(token))
    assert response.status_code == 200
    assert response.get_json()["product"]["is_active"] is False


def test_admin_detail_nonexistent_404(client, app):
    token = admin_token(client, app)
    response = client.get("/api/v1/admin/products/9999", headers=auth(token))
    assert response.status_code == 404


# --- Create ---


def test_admin_creates_product(client, app):
    token = admin_token(client, app)
    response = client.post(
        "/api/v1/admin/products",
        json={"name": "Pumpkin Cake", "price": 12.0, "stock_quantity": 10},
        headers=auth(token),
    )
    assert response.status_code == 201
    body = response.get_json()["product"]
    assert body["name"] == "Pumpkin Cake"
    assert body["is_active"] is True


def test_created_product_is_persisted(client, app):
    token = admin_token(client, app)
    response = client.post(
        "/api/v1/admin/products",
        json={"name": "Bread", "price": 11.0, "stock_quantity": 8},
        headers=auth(token),
    )
    product_id = response.get_json()["product"]["id"]

    detail = client.get(f"/api/v1/admin/products/{product_id}", headers=auth(token))
    assert detail.status_code == 200
    assert detail.get_json()["product"]["name"] == "Bread"


def test_create_missing_name_400(client, app):
    token = admin_token(client, app)
    response = client.post(
        "/api/v1/admin/products",
        json={"price": 11.0, "stock_quantity": 8},
        headers=auth(token),
    )
    assert response.status_code == 400


def test_create_negative_price_400(client, app):
    token = admin_token(client, app)
    response = client.post(
        "/api/v1/admin/products",
        json={"name": "Bad", "price": -5.0, "stock_quantity": 8},
        headers=auth(token),
    )
    assert response.status_code == 400


def test_create_negative_stock_400(client, app):
    token = admin_token(client, app)
    response = client.post(
        "/api/v1/admin/products",
        json={"name": "Bad", "price": 11.0, "stock_quantity": -1},
        headers=auth(token),
    )
    assert response.status_code == 400


# --- Update ---


def test_admin_updates_product(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    response = client.put(
        f"/api/v1/admin/products/{product.id}",
        json={"name": "Sourdough", "price": 13.0},
        headers=auth(token),
    )
    assert response.status_code == 200
    body = response.get_json()["product"]
    assert body["name"] == "Sourdough"
    assert body["price"] == 13.0


def test_update_nonexistent_404(client, app):
    token = admin_token(client, app)
    response = client.put(
        "/api/v1/admin/products/9999",
        json={"name": "Ghost", "price": 11.0},
        headers=auth(token),
    )
    assert response.status_code == 404


def test_update_invalid_data_400(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    response = client.put(
        f"/api/v1/admin/products/{product.id}",
        json={"price": -5.0},
        headers=auth(token),
    )
    assert response.status_code == 400


# --- Status ---


def test_admin_deactivates_product(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    response = client.patch(
        f"/api/v1/admin/products/{product.id}/status",
        json={"is_active": False},
        headers=auth(token),
    )
    assert response.status_code == 200
    assert response.get_json()["product"]["is_active"] is False


def test_deactivated_disappears_from_customer_list(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    client.patch(
        f"/api/v1/admin/products/{product.id}/status",
        json={"is_active": False},
        headers=auth(token),
    )

    customer = customer_token(client, email="c@example.com")
    response = client.get("/api/v1/products", headers=auth(customer))
    assert response.get_json()["products"] == []


def test_admin_still_views_deactivated(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    client.patch(
        f"/api/v1/admin/products/{product.id}/status",
        json={"is_active": False},
        headers=auth(token),
    )

    detail = client.get(f"/api/v1/admin/products/{product.id}", headers=auth(token))
    assert detail.status_code == 200
    assert detail.get_json()["product"]["is_active"] is False


def test_admin_reactivates_product(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8, active=False)

    response = client.patch(
        f"/api/v1/admin/products/{product.id}/status",
        json={"is_active": True},
        headers=auth(token),
    )
    assert response.status_code == 200
    assert response.get_json()["product"]["is_active"] is True


# --- Stock ---


def test_admin_updates_stock(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    response = client.patch(
        f"/api/v1/admin/products/{product.id}/stock",
        json={"stock_quantity": 20},
        headers=auth(token),
    )
    assert response.status_code == 200
    assert response.get_json()["product"]["stock_quantity"] == 20


def test_zero_stock_allowed(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    response = client.patch(
        f"/api/v1/admin/products/{product.id}/stock",
        json={"stock_quantity": 0},
        headers=auth(token),
    )
    assert response.status_code == 200
    assert response.get_json()["product"]["stock_quantity"] == 0


def test_negative_stock_400(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    response = client.patch(
        f"/api/v1/admin/products/{product.id}/stock",
        json={"stock_quantity": -1},
        headers=auth(token),
    )
    assert response.status_code == 400


def test_non_integer_stock_400(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)

    response = client.patch(
        f"/api/v1/admin/products/{product.id}/stock",
        json={"stock_quantity": "abc"},
        headers=auth(token),
    )
    assert response.status_code == 400


def test_stock_nonexistent_404(client, app):
    token = admin_token(client, app)
    response = client.patch(
        "/api/v1/admin/products/9999/stock",
        json={"stock_quantity": 20},
        headers=auth(token),
    )
    assert response.status_code == 404


# --- Regression: customer/admin visibility distinction ---


def test_customer_vs_admin_visibility(client, app):
    admin = admin_token(client, app)
    create_product(app, name="Visible", price=11.0, stock=10, active=True)
    create_product(app, name="HiddenInactive", price=12.0, stock=10, active=False)
    create_product(app, name="HiddenZeroStock", price=13.0, stock=0, active=True)

    customer = customer_token(client, email="cust@example.com")
    customer_products = client.get("/api/v1/products", headers=auth(customer)).get_json()["products"]
    assert [p["name"] for p in customer_products] == ["Visible"]

    admin_products = client.get("/api/v1/admin/products", headers=auth(admin)).get_json()["products"]
    assert {p["name"] for p in admin_products} == {"Visible", "HiddenInactive", "HiddenZeroStock"}


