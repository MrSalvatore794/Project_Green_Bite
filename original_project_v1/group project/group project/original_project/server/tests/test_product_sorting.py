"""Focused tests for Phase 6B-Fix product sorting (customer + admin)."""

from tests.helpers import admin_token, auth, create_product


# --- Customer ordering (active only, star_level DESC, id ASC) ---


def test_customer_list_orders_by_star_level(client, app):
    low = create_product(app, name="Low", price=1.0, stock=5)
    mid = create_product(app, name="Mid", price=1.0, stock=5)
    high = create_product(app, name="High", price=1.0, stock=5)

    service = app.extensions["product_service"]
    service.update_product(high.id, star_level=5)
    service.update_product(mid.id, star_level=3)

    response = client.get("/api/v1/products")
    names = [p["name"] for p in response.get_json()["products"]]
    assert names == ["High", "Mid", "Low"]


def test_customer_list_same_star_uses_id_asc(client, app):
    a = create_product(app, name="A", price=1.0, stock=5)
    b = create_product(app, name="B", price=1.0, stock=5)

    response = client.get("/api/v1/products")
    names = [p["name"] for p in response.get_json()["products"]]
    assert names == ["A", "B"]


def test_customer_list_excludes_inactive_high_star(client, app):
    active = create_product(app, name="Active", price=1.0, stock=5)
    inactive = create_product(app, name="Inactive", price=1.0, stock=5, active=False)

    service = app.extensions["product_service"]
    service.update_product(inactive.id, star_level=5)

    response = client.get("/api/v1/products")
    names = [p["name"] for p in response.get_json()["products"]]
    assert "Inactive" not in names
    assert "Active" in names


# --- Admin ordering (active first, then star_level DESC, then id ASC) ---


def test_admin_orders_active_before_inactive(client, app):
    token = admin_token(client, app)
    inactive_high = create_product(app, name="InactiveHigh", price=1.0, stock=5, active=False)
    active_low = create_product(app, name="ActiveLow", price=1.0, stock=5)

    service = app.extensions["product_service"]
    service.update_product(inactive_high.id, star_level=5)
    service.update_product(active_low.id, star_level=0)

    response = client.get("/api/v1/admin/products", headers=auth(token))
    products = response.get_json()["products"]
    assert products[0]["name"] == "ActiveLow"
    assert any(p["name"] == "InactiveHigh" for p in products)


def test_admin_orders_active_by_star_then_id(client, app):
    token = admin_token(client, app)
    a = create_product(app, name="A", price=1.0, stock=5)
    b = create_product(app, name="B", price=1.0, stock=5)
    c = create_product(app, name="C", price=1.0, stock=5)

    service = app.extensions["product_service"]
    service.update_product(c.id, star_level=5)

    response = client.get("/api/v1/admin/products", headers=auth(token))
    names = [p["name"] for p in response.get_json()["products"]]
    assert names == ["C", "A", "B"]
