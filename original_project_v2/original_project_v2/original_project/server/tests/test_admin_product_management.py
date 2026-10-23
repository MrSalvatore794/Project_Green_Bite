"""Focused tests for the Phase 6B Admin Product Management feature."""

import os
from io import BytesIO

from tests.helpers import admin_token, auth, create_product, customer_token


def _payload(**overrides):
    data = {
        "name": "Test Product",
        "description": "A test product.",
        "price": 12.5,
        "stock_quantity": 10,
        "star_level": 0,
    }
    data.update(overrides)
    return data


def _upload(client, token, url, content=b"fake-image", filename="photo.jpg"):
    return client.post(
        url,
        data={"image": (BytesIO(content), filename)},
        content_type="multipart/form-data",
        headers=auth(token),
    )


# --- Authorization ---


def test_guest_cannot_list_admin_products(client):
    assert client.get("/api/v1/admin/products").status_code == 401


def test_customer_cannot_list_admin_products(client):
    token = customer_token(client)
    assert client.get("/api/v1/admin/products", headers=auth(token)).status_code == 403


def test_admin_can_list_products(client, app):
    token = admin_token(client, app)
    create_product(app, name="Bread", price=11.0, stock=8)
    response = client.get("/api/v1/admin/products", headers=auth(token))
    assert response.status_code == 200
    assert len(response.get_json()["products"]) >= 1


# --- Create ---


def test_admin_can_create_product(client, app):
    token = admin_token(client, app)
    response = client.post("/api/v1/admin/products", json=_payload(), headers=auth(token))
    assert response.status_code == 201
    product = response.get_json()["product"]
    assert product["name"] == "Test Product"
    assert product["price"] == 12.5
    assert product["stock_quantity"] == 10
    assert product["star_level"] == 0
    assert product["is_active"] is True


def test_create_invalid_name_rejected(client, app):
    token = admin_token(client, app)
    response = client.post(
        "/api/v1/admin/products", json=_payload(name=""), headers=auth(token)
    )
    assert response.status_code == 400


def test_create_invalid_price_rejected(client, app):
    token = admin_token(client, app)
    response = client.post(
        "/api/v1/admin/products", json=_payload(price=-1), headers=auth(token)
    )
    assert response.status_code == 400


def test_create_negative_stock_rejected(client, app):
    token = admin_token(client, app)
    response = client.post(
        "/api/v1/admin/products", json=_payload(stock_quantity=-1), headers=auth(token)
    )
    assert response.status_code == 400


def test_create_invalid_star_level_rejected(client, app):
    token = admin_token(client, app)
    response = client.post(
        "/api/v1/admin/products", json=_payload(star_level="high"), headers=auth(token)
    )
    assert response.status_code == 400


def test_create_star_level_0_accepted(client, app):
    token = admin_token(client, app)
    response = client.post(
        "/api/v1/admin/products", json=_payload(star_level=0), headers=auth(token)
    )
    assert response.status_code == 201
    assert response.get_json()["product"]["star_level"] == 0


def test_create_star_level_5_accepted(client, app):
    token = admin_token(client, app)
    response = client.post(
        "/api/v1/admin/products", json=_payload(star_level=5), headers=auth(token)
    )
    assert response.status_code == 201
    assert response.get_json()["product"]["star_level"] == 5


def test_create_star_level_over_5_rejected(client, app):
    token = admin_token(client, app)
    response = client.post(
        "/api/v1/admin/products", json=_payload(star_level=6), headers=auth(token)
    )
    assert response.status_code == 400


# --- Edit / status / stock ---


def test_admin_can_edit_product(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Old", price=11.0, stock=8)
    response = client.put(
        f"/api/v1/admin/products/{product.id}",
        json={"name": "New", "price": 20.0, "star_level": 3},
        headers=auth(token),
    )
    assert response.status_code == 200
    body = response.get_json()["product"]
    assert body["name"] == "New"
    assert body["price"] == 20.0
    assert body["star_level"] == 3


def test_admin_can_activate_product(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8, active=False)
    response = client.patch(
        f"/api/v1/admin/products/{product.id}/status",
        json={"is_active": True},
        headers=auth(token),
    )
    assert response.status_code == 200
    assert response.get_json()["product"]["is_active"] is True


def test_admin_can_deactivate_product(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    response = client.patch(
        f"/api/v1/admin/products/{product.id}/status",
        json={"is_active": False},
        headers=auth(token),
    )
    assert response.status_code == 200
    assert response.get_json()["product"]["is_active"] is False


def test_admin_can_update_stock(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    response = client.patch(
        f"/api/v1/admin/products/{product.id}/stock",
        json={"stock_quantity": 20},
        headers=auth(token),
    )
    assert response.status_code == 200
    assert response.get_json()["product"]["stock_quantity"] == 20


def test_negative_stock_rejected(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    response = client.patch(
        f"/api/v1/admin/products/{product.id}/stock",
        json={"stock_quantity": -5},
        headers=auth(token),
    )
    assert response.status_code == 400


# --- Ordering ---


def test_list_ordering_by_star_level(client, app):
    token = admin_token(client, app)
    low = create_product(app, name="Low", price=1.0, stock=1)
    mid = create_product(app, name="Mid", price=1.0, stock=1)
    high = create_product(app, name="High", price=1.0, stock=1)

    service = app.extensions["product_service"]
    service.update_product(high.id, star_level=5)
    service.update_product(mid.id, star_level=3)

    response = client.get("/api/v1/admin/products", headers=auth(token))
    products = response.get_json()["products"]
    ids = [p["id"] for p in products]
    assert ids[0] == high.id
    assert ids.index(mid.id) < ids.index(low.id)


def test_stable_ordering_within_same_star_level(client, app):
    token = admin_token(client, app)
    a = create_product(app, name="A", price=1.0, stock=1)
    b = create_product(app, name="B", price=1.0, stock=1)

    response = client.get("/api/v1/admin/products", headers=auth(token))
    products = response.get_json()["products"]
    ids = [p["id"] for p in products if p["id"] in (a.id, b.id)]
    assert ids == [a.id, b.id]


# --- Image upload ---


def test_image_upload_requires_admin(client, app):
    product = create_product(app, name="Bread", price=11.0, stock=8)
    response = _upload(client, None, f"/api/v1/admin/products/{product.id}/image")
    assert response.status_code == 401


def test_invalid_image_type_rejected(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    response = client.post(
        f"/api/v1/admin/products/{product.id}/image",
        data={"image": (BytesIO(b"fake"), "script.py")},
        content_type="multipart/form-data",
        headers=auth(token),
    )
    assert response.status_code == 400


def test_oversized_image_rejected(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    big = b"x" * (5 * 1024 * 1024 + 1)
    response = _upload(client, token, f"/api/v1/admin/products/{product.id}/image", content=big)
    assert response.status_code == 400


def test_uploaded_image_stored_and_url_correct(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    response = _upload(
        client, token, f"/api/v1/admin/products/{product.id}/image", content=b"fake-image"
    )
    assert response.status_code == 200
    url = response.get_json()["product"]["image_url"]
    assert url.startswith("/uploads/products/")
    assert url.endswith(".jpg")

    filename = url.rsplit("/", 1)[1]
    upload_dir = os.path.join(app.config["MEDIA_ROOT"], "products")
    assert os.path.exists(os.path.join(upload_dir, filename))


def test_detail_image_upload(client, app):
    token = admin_token(client, app)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    response = client.post(
        f"/api/v1/admin/products/{product.id}/detail-image",
        data={"image": (BytesIO(b"fake-detail"), "detail.png")},
        content_type="multipart/form-data",
        headers=auth(token),
    )
    assert response.status_code == 200
    assert response.get_json()["product"]["detail_image_url"].startswith("/uploads/products/")


# --- Customer compatibility ---


def test_customer_product_api_compatible(client, app):
    token = admin_token(client, app)
    create_product(app, name="Bread", price=11.0, stock=8)
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    names = [p["name"] for p in response.get_json()["products"]]
    assert "Bread" in names


def test_like_functionality_still_works(client, app):
    token = customer_token(client)
    product = create_product(app, name="Bread", price=11.0, stock=8)
    response = client.post(f"/api/v1/products/{product.id}/like", headers=auth(token))
    assert response.status_code == 200
    assert response.get_json()["like_count"] == 1

    detail = client.get(f"/api/v1/products/{product.id}", headers=auth(token))
    body = detail.get_json()["product"]
    assert body["like_count"] == 1
    assert body["liked_by_current_user"] is True
