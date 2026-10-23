"""Tests for the optional WxPusher new-order notification service."""

import json
import urllib.error

import pytest

from models import Order, OrderItem, Product, User
from services.notifications import WxPusherNotificationService
from services.order_service import OrderService
from services.exceptions import CartEmptyError


class FakeResponse:
    def __init__(self, status=200, body='{"code": 1000}'):
        self.status = status
        self._body = body.encode("utf-8")

    def read(self):
        return self._body

    def getcode(self):
        return self.status


def _service(app_token="AT_token", uids="UID_a, UID_b", http_post=None):
    return WxPusherNotificationService(
        app_token=app_token, uids=uids, http_post=http_post
    )


def _make_order():
    order = Order(user_id=1, order_id=7, total_amount=34.5)
    order.pickup_date = "2026-10-10"
    order.pickup_time = "15:00"
    order.payment_status = "pending"
    order.add_item(
        OrderItem(product_id=1, product_name="Bread", unit_price=11.0, quantity=2)
    )
    order.add_item(
        OrderItem(product_id=2, product_name="Cake", unit_price=12.5, quantity=1)
    )
    return order


# --- Configuration ---

def test_not_configured_without_token():
    assert not _service(app_token="", uids="UID_a").is_configured()


def test_not_configured_without_uids():
    assert not _service(app_token="AT_token", uids="").is_configured()


def test_not_configured_with_blank_uids():
    assert not _service(app_token="AT_token", uids="  , ").is_configured()


def test_configured_with_token_and_uids():
    assert _service().is_configured()


def test_parse_uids_comma_separated():
    assert _service(uids="UID_a, UID_b ,UID_c").uids == ["UID_a", "UID_b", "UID_c"]


# --- Payload ---

def test_payload_contains_operational_fields():
    payload = _service()._build_payload(_make_order())

    assert payload["appToken"] == "AT_token"
    assert payload["uids"] == ["UID_a", "UID_b"]
    assert payload["contentType"] == 1
    assert "New order #7" in payload["content"]
    assert "$34.50" in payload["content"]
    assert "2026-10-10 15:00" in payload["content"]
    assert "Bread x2" in payload["content"]
    assert "Cake x1" in payload["content"]


def test_payload_excludes_customer_secrets():
    order = _make_order()
    order.payment_reference = "secret-reference-value"

    payload = _service()._build_payload(order)
    assert "secret-reference-value" not in json.dumps(payload)


# --- Sending (mocked HTTP) ---

def test_send_success():
    sent = []

    def post(data):
        sent.append(json.loads(data.decode("utf-8")))
        return FakeResponse(200, '{"code": 1000}')

    service = _service(http_post=post)
    assert service.send_new_order_notification(_make_order()) is True
    assert len(sent) == 1
    assert sent[0]["appToken"] == "AT_token"


def test_send_provider_failure_returns_false():
    def post(data):
        return FakeResponse(200, '{"code": 1001, "msg": "bad"}')

    assert _service(http_post=post).send_new_order_notification(_make_order()) is False


def test_send_http_error_returns_false():
    def post(data):
        raise urllib.error.HTTPError("url", 500, "err", None, None)

    assert _service(http_post=post).send_new_order_notification(_make_order()) is False


def test_send_network_error_returns_false():
    def post(data):
        raise urllib.error.URLError("boom")

    assert _service(http_post=post).send_new_order_notification(_make_order()) is False


def test_send_timeout_returns_false():
    def post(data):
        raise TimeoutError("timed out")

    assert _service(http_post=post).send_new_order_notification(_make_order()) is False


def test_send_malformed_response_returns_false():
    def post(data):
        return FakeResponse(200, "not json")

    assert _service(http_post=post).send_new_order_notification(_make_order()) is False


def test_disabled_service_does_not_send():
    calls = []

    def post(data):
        calls.append(data)

    service = _service(app_token="", uids="UID_a", http_post=post)
    assert service.send_new_order_notification(_make_order()) is False
    assert calls == []


# --- Integration with OrderService ---

class RecordingNotifier:
    def __init__(self):
        self.calls = []

    def send_new_order_notification(self, order):
        self.calls.append(order.id)
        return True


def _register(auth_service, email="richard@example.com"):
    return auth_service.register("Richard", email, "0212345678", "Password123")


def _checkout(user_id):
    return dict(
        user_id=user_id,
        customer_name="Richard",
        phone="0212345678",
        pickup_date="2026-10-10",
        pickup_time="15:00",
        payment_reference_type="bank_transfer",
        payment_reference="12345",
    )


def test_notification_sent_after_successful_order(
    order_repo, cart_repo, product_repo, user_repo, db,
    auth_service, product_service, cart_service,
):
    user = _register(auth_service)
    product = product_service.create_product("Bread", 11.0, stock_quantity=8)
    cart_service.add_item(user.id, product.id, 2)

    notifier = RecordingNotifier()
    service = OrderService(order_repo, cart_repo, product_repo, db, notifier)
    order = service.create_order(**_checkout(user.id))

    assert notifier.calls == [order.id]


def test_no_notification_when_not_configured(
    order_repo, cart_repo, product_repo, user_repo, db,
    auth_service, product_service, cart_service,
):
    user = _register(auth_service)
    product = product_service.create_product("Bread", 11.0, stock_quantity=8)
    cart_service.add_item(user.id, product.id, 1)

    calls = []
    notifier = WxPusherNotificationService(
        app_token="", uids="", http_post=lambda data: calls.append(data)
    )
    service = OrderService(order_repo, cart_repo, product_repo, db, notifier)
    order = service.create_order(**_checkout(user.id))

    assert order.id is not None
    assert calls == []


def test_no_notification_on_empty_cart(order_repo, cart_repo, product_repo, db, auth_service):
    user = _register(auth_service)
    notifier = RecordingNotifier()
    service = OrderService(order_repo, cart_repo, product_repo, db, notifier)

    with pytest.raises(CartEmptyError):
        service.create_order(**_checkout(user.id))
    assert notifier.calls == []


def test_notification_failure_does_not_affect_order(
    order_repo, cart_repo, product_repo, user_repo, db,
    auth_service, product_service, cart_service,
):
    user = _register(auth_service)
    product = product_service.create_product("Bread", 11.0, stock_quantity=8)
    cart_service.add_item(user.id, product.id, 2)

    def fail(data):
        raise TimeoutError("timeout")

    notifier = WxPusherNotificationService(
        app_token="AT_token", uids="UID_a", http_post=fail
    )
    service = OrderService(order_repo, cart_repo, product_repo, db, notifier)
    order = service.create_order(**_checkout(user.id))

    assert order.id is not None
    assert product_service.get_product(product.id).stock_quantity == 6


def test_no_notification_on_rollback(order_repo, cart_repo, product_repo, user_repo, db):
    user = user_repo.create_user(
        User(name="Richard", email="richard@example.com", password_hash="hash")
    )
    product = product_repo.create_product(
        Product(name="Bread", price=11.0, stock_quantity=8)
    )
    cart = cart_repo.create_cart(user.id)
    cart_repo.add_cart_item(cart.id, product.id, 2)

    class FailingOrderRepository:
        def __init__(self, real):
            self.real = real

        def create_order(self, order, connection=None):
            return self.real.create_order(order, connection=connection)

        def create_order_items(self, order_id, items, connection=None):
            raise RuntimeError("simulated failure")

        def find_by_id(self, order_id, connection=None):
            return self.real.find_by_id(order_id, connection=connection)

        def list_orders_for_user(self, user_id, connection=None):
            return self.real.list_orders_for_user(user_id, connection=connection)

        def list_all_orders(self, connection=None):
            return self.real.list_all_orders(connection=connection)

        def update_order_status(self, order_id, new_status, connection=None):
            return self.real.update_order_status(order_id, new_status, connection=connection)

    notifier = RecordingNotifier()
    service = OrderService(
        FailingOrderRepository(order_repo), cart_repo, product_repo, db, notifier
    )

    with pytest.raises(RuntimeError):
        service.create_order(
            user.id, "Richard", "0212345678", "2026-10-10", "15:00",
            "bank_transfer", "12345",
        )
    assert notifier.calls == []
    assert product_repo.find_by_id(product.id).stock_quantity == 8
