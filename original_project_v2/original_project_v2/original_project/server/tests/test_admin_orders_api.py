"""Tests for the Admin Order Management API."""

import pytest

from tests.helpers import admin_token, auth, create_product, customer_token


def _order_payload():
    return {
        "customer_name": "Richard",
        "phone": "0212345678",
        "pickup_date": "2026-10-10",
        "pickup_time": "15:00",
        "payment_reference_type": "bank_transfer",
        "payment_reference": "12345",
    }


def _create_customer_order(client, app, token, name="Bread", price=11.0, stock=8, quantity=1):
    """Create an order for a customer via the customer API; return (order, product)."""
    product = create_product(app, name=name, price=price, stock=stock)
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product.id, "quantity": quantity},
        headers=auth(token),
    )
    response = client.post("/api/v1/orders", json=_order_payload(), headers=auth(token))
    assert response.status_code == 201
    return response.get_json()["order"], product


def _admin_and_order(client, app):
    """Return (admin_token, order) with one customer order in the DB."""
    admin = admin_token(client, app)
    customer = customer_token(client, email="cust@example.com")
    order, _ = _create_customer_order(client, app, customer)
    return admin, order


# --- Authentication ---


def test_no_jwt_rejected(client):
    response = client.get("/api/v1/admin/orders")
    assert response.status_code == 401


def test_invalid_jwt_rejected(client):
    response = client.get("/api/v1/admin/orders", headers=auth("invalid.token"))
    assert response.status_code == 401


def test_customer_jwt_rejected(client):
    token = customer_token(client)
    response = client.get("/api/v1/admin/orders", headers=auth(token))
    assert response.status_code == 403


def test_admin_jwt_allowed(client, app):
    admin = admin_token(client, app)
    response = client.get("/api/v1/admin/orders", headers=auth(admin))
    assert response.status_code == 200


# --- Admin list ---


def test_admin_lists_all_orders(client, app):
    admin = admin_token(client, app)
    cust1 = customer_token(client, email="cust1@example.com")
    cust2 = customer_token(client, email="cust2@example.com")
    _create_customer_order(client, app, cust1)
    _create_customer_order(client, app, cust2, name="Cake", price=12.0)

    response = client.get("/api/v1/admin/orders", headers=auth(admin))
    assert response.status_code == 200
    orders = response.get_json()["orders"]
    assert len(orders) == 2
    assert {o["status"] for o in orders} == {"pending"}


def test_admin_list_not_restricted_to_admin_user(client, app):
    admin = admin_token(client, app)
    customer = customer_token(client, email="cust@example.com")
    order, _ = _create_customer_order(client, app, customer)

    response = client.get("/api/v1/admin/orders", headers=auth(admin))
    orders = response.get_json()["orders"]
    assert [o["id"] for o in orders] == [order["id"]]


def test_empty_order_list(client, app):
    admin = admin_token(client, app)
    response = client.get("/api/v1/admin/orders", headers=auth(admin))
    assert response.status_code == 200
    assert response.get_json()["orders"] == []


# --- Admin detail ---


def test_admin_views_order(client, app):
    admin, order = _admin_and_order(client, app)

    response = client.get(f"/api/v1/admin/orders/{order['id']}", headers=auth(admin))
    assert response.status_code == 200
    body = response.get_json()["order"]
    assert body["id"] == order["id"]
    assert len(body["items"]) == 1


def test_admin_views_another_customers_order(client, app):
    admin = admin_token(client, app)
    customer = customer_token(client, email="other@example.com")
    order, _ = _create_customer_order(client, app, customer)

    response = client.get(f"/api/v1/admin/orders/{order['id']}", headers=auth(admin))
    assert response.status_code == 200
    assert response.get_json()["order"]["customer_name"] == "Richard"


def test_admin_detail_nonexistent_404(client, app):
    admin = admin_token(client, app)
    response = client.get("/api/v1/admin/orders/9999", headers=auth(admin))
    assert response.status_code == 404


# --- Customer security regression ---


def test_customer_views_own_order(client, app):
    customer = customer_token(client, email="cust@example.com")
    order, _ = _create_customer_order(client, app, customer)

    response = client.get(f"/api/v1/orders/{order['id']}", headers=auth(customer))
    assert response.status_code == 200


def test_customer_cannot_view_another_customers_order(client, app):
    cust1 = customer_token(client, email="cust1@example.com")
    cust2 = customer_token(client, email="cust2@example.com")
    order, _ = _create_customer_order(client, app, cust1)

    response = client.get(f"/api/v1/orders/{order['id']}", headers=auth(cust2))
    assert response.status_code == 404


def test_admin_views_order_customer_cannot(client, app):
    admin = admin_token(client, app)
    cust1 = customer_token(client, email="cust1@example.com")
    cust2 = customer_token(client, email="cust2@example.com")
    order, _ = _create_customer_order(client, app, cust1)

    # cust2 cannot see it...
    assert client.get(f"/api/v1/orders/{order['id']}", headers=auth(cust2)).status_code == 404
    # ...but admin can view it.
    assert client.get(f"/api/v1/admin/orders/{order['id']}", headers=auth(admin)).status_code == 200


# --- Status transitions (valid) ---


def test_status_pending_to_confirmed(client, app):
    admin, order = _admin_and_order(client, app)
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "confirmed"},
        headers=auth(admin),
    )
    assert response.status_code == 200
    assert response.get_json()["order"]["status"] == "confirmed"


def test_status_confirmed_to_preparing(client, app):
    admin, order = _admin_and_order(client, app)
    client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "confirmed"},
        headers=auth(admin),
    )
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "preparing"},
        headers=auth(admin),
    )
    assert response.status_code == 200
    assert response.get_json()["order"]["status"] == "preparing"


def test_status_preparing_to_ready_for_pickup(client, app):
    admin, order = _admin_and_order(client, app)
    for status in ("confirmed", "preparing"):
        client.patch(
            f"/api/v1/admin/orders/{order['id']}/status",
            json={"status": status},
            headers=auth(admin),
        )
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "ready_for_pickup"},
        headers=auth(admin),
    )
    assert response.status_code == 200
    assert response.get_json()["order"]["status"] == "ready_for_pickup"


def test_status_ready_for_pickup_to_collected(client, app):
    admin, order = _admin_and_order(client, app)
    for status in ("confirmed", "preparing", "ready_for_pickup"):
        client.patch(
            f"/api/v1/admin/orders/{order['id']}/status",
            json={"status": status},
            headers=auth(admin),
        )
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "collected"},
        headers=auth(admin),
    )
    assert response.status_code == 200
    assert response.get_json()["order"]["status"] == "collected"


# --- Status transitions (invalid) ---


@pytest.mark.parametrize("target", ["preparing", "ready_for_pickup", "collected"])
def test_pending_skip_rejected(client, app, target):
    admin, order = _admin_and_order(client, app)
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": target},
        headers=auth(admin),
    )
    assert response.status_code == 400


def test_confirmed_to_collected_rejected(client, app):
    admin, order = _admin_and_order(client, app)
    client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "confirmed"},
        headers=auth(admin),
    )
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "collected"},
        headers=auth(admin),
    )
    assert response.status_code == 400


def test_preparing_to_collected_rejected(client, app):
    admin, order = _admin_and_order(client, app)
    for status in ("confirmed", "preparing"):
        client.patch(
            f"/api/v1/admin/orders/{order['id']}/status",
            json={"status": status},
            headers=auth(admin),
        )
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "collected"},
        headers=auth(admin),
    )
    assert response.status_code == 400


def test_collected_is_terminal(client, app):
    admin, order = _admin_and_order(client, app)
    for status in ("confirmed", "preparing", "ready_for_pickup", "collected"):
        client.patch(
            f"/api/v1/admin/orders/{order['id']}/status",
            json={"status": status},
            headers=auth(admin),
        )
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "confirmed"},
        headers=auth(admin),
    )
    assert response.status_code == 400


# --- Invalid status / request ---


def test_unknown_status_rejected(client, app):
    admin, order = _admin_and_order(client, app)
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "shipped"},
        headers=auth(admin),
    )
    assert response.status_code == 400


def test_missing_status_rejected(client, app):
    admin, order = _admin_and_order(client, app)
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={},
        headers=auth(admin),
    )
    assert response.status_code == 400


def test_invalid_body_rejected(client, app):
    admin, order = _admin_and_order(client, app)
    response = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json=["not", "a", "dict"],
        headers=auth(admin),
    )
    assert response.status_code == 400


# --- Data integrity ---


def test_status_change_keeps_total(client, app):
    admin, order = _admin_and_order(client, app)

    client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "confirmed"},
        headers=auth(admin),
    )
    detail = client.get(f"/api/v1/admin/orders/{order['id']}", headers=auth(admin)).get_json()["order"]
    assert detail["total_amount"] == order["total_amount"]
    assert detail["total_amount"] == 11.0


def test_status_change_keeps_item_snapshot(client, app):
    admin, order = _admin_and_order(client, app)
    client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "confirmed"},
        headers=auth(admin),
    )

    item = client.get(f"/api/v1/admin/orders/{order['id']}", headers=auth(admin)).get_json()["order"]["items"][0]
    assert item["unit_price"] == 11.0
    assert item["quantity"] == 1
    assert item["subtotal"] == 11.0


def test_status_change_keeps_quantity(client, app):
    admin, order = _admin_and_order(client, app)
    client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"status": "preparing"},
        headers=auth(admin),
    )

    item = client.get(f"/api/v1/admin/orders/{order['id']}", headers=auth(admin)).get_json()["order"]["items"][0]
    assert item["quantity"] == 1


def test_product_price_change_keeps_historical_price(client, app):
    admin, order = _admin_and_order(client, app)
    product_id = order["items"][0]["product_id"]

    # Admin changes the product price after the order was placed.
    client.put(
        f"/api/v1/admin/products/{product_id}",
        json={"price": 99.0},
        headers=auth(admin),
    )

    item = client.get(f"/api/v1/admin/orders/{order['id']}", headers=auth(admin)).get_json()["order"]["items"][0]
    assert item["unit_price"] == 11.0
    assert item["subtotal"] == 11.0


