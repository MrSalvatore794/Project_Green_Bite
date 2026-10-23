"""Tests for OrderService."""

import pytest

from models import Product, User
from services import OrderService
from services.exceptions import (
    CartEmptyError,
    InsufficientStockError,
    InvalidOrderStatusError,
    OrderNotFoundError,
    ProductUnavailableError,
    ValidationError,
)


def _register(auth_service, email="richard@example.com"):
    return auth_service.register("Richard", email, "0212345678", "Password123")


def _product(product_service, name="Bread", price=11.0, stock=8):
    return product_service.create_product(name, price, stock_quantity=stock)


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


def _create_order(order_service, user_id):
    return order_service.create_order(**_checkout(user_id))


def test_empty_cart_rejected(order_service, auth_service):
    user = _register(auth_service)
    with pytest.raises(CartEmptyError):
        _create_order(order_service, user.id)


def test_unavailable_product_rejected(order_service, auth_service, product_service, cart_service):
    user = _register(auth_service)
    product = _product(product_service)
    cart_service.add_item(user.id, product.id, 1)
    product_service.set_product_active(product.id, False)
    with pytest.raises(ProductUnavailableError):
        _create_order(order_service, user.id)


def test_insufficient_stock_rejected(order_service, auth_service, product_service, cart_service):
    user = _register(auth_service)
    product = _product(product_service, stock=5)
    cart_service.add_item(user.id, product.id, 3)
    product_service.update_stock(product.id, 2)
    with pytest.raises(InsufficientStockError):
        _create_order(order_service, user.id)


def test_successful_order_creation(order_service, auth_service, product_service, cart_service):
    user = _register(auth_service)
    bread = _product(product_service, name="Bread", price=11.0, stock=8)
    cake = _product(product_service, name="Cake", price=12.5, stock=10)
    cart_service.add_item(user.id, bread.id, 2)  # 22.0
    cart_service.add_item(user.id, cake.id, 1)   # 12.5

    order = _create_order(order_service, user.id)

    assert order.id is not None
    assert order.total_amount == 34.5
    assert order.status == "pending"
    assert len(order.items) == 2


def test_order_items_snapshot_preserved(order_service, auth_service, product_service, cart_service):
    user = _register(auth_service)
    bread = _product(product_service, name="Walnut Raisin Bread", price=11.0, stock=8)
    cart_service.add_item(user.id, bread.id, 2)
    order = _create_order(order_service, user.id)

    item = order.items[0]
    assert item.product_name == "Walnut Raisin Bread"
    assert item.unit_price == 11.0
    assert item.quantity == 2
    assert item.subtotal == 22.0


def test_stock_reduced_after_order(order_service, auth_service, product_service, cart_service):
    user = _register(auth_service)
    bread = _product(product_service, stock=8)
    cart_service.add_item(user.id, bread.id, 3)
    _create_order(order_service, user.id)
    assert product_service.get_product(bread.id).stock_quantity == 5


def test_cart_cleared_after_order(order_service, auth_service, product_service, cart_service):
    user = _register(auth_service)
    bread = _product(product_service, stock=8)
    cart_service.add_item(user.id, bread.id, 3)
    _create_order(order_service, user.id)
    assert cart_service.get_cart(user.id).items == []


def test_historical_price_preserved(order_service, auth_service, product_service, cart_service):
    user = _register(auth_service)
    bread = _product(product_service, name="Bread", price=11.0, stock=8)
    cart_service.add_item(user.id, bread.id, 2)
    order = _create_order(order_service, user.id)

    product_service.update_product(bread.id, price=99.0)

    reloaded = order_service.get_order(order.id, user.id)
    assert reloaded.items[0].unit_price == 11.0


def test_missing_checkout_fields_rejected(order_service, auth_service, product_service, cart_service):
    user = _register(auth_service)
    product = _product(product_service)
    cart_service.add_item(user.id, product.id, 1)
    with pytest.raises(ValidationError):
        order_service.create_order(
            user.id, "", "0212345678", "2026-10-10", "15:00", "bank_transfer", "12345"
        )


def test_customer_retrieves_own_orders(order_service, auth_service, product_service, cart_service):
    user = _register(auth_service)
    product = _product(product_service)
    cart_service.add_item(user.id, product.id, 1)
    _create_order(order_service, user.id)
    orders = order_service.get_user_orders(user.id)
    assert len(orders) == 1
    assert orders[0].user_id == user.id


def test_customer_cannot_access_another_customers_order(
    order_service, auth_service, product_service, cart_service
):
    user1 = _register(auth_service, "richard@example.com")
    user2 = _register(auth_service, "salin@example.com")
    product = _product(product_service)
    cart_service.add_item(user1.id, product.id, 1)
    order = _create_order(order_service, user1.id)

    with pytest.raises(OrderNotFoundError):
        order_service.get_order(order.id, user2.id)


def test_order_status_transition(order_service, auth_service, product_service, cart_service):
    user = _register(auth_service)
    product = _product(product_service)
    cart_service.add_item(user.id, product.id, 1)
    order = _create_order(order_service, user.id)

    assert order_service.update_order_status(order.id, "confirmed").status == "confirmed"


def test_invalid_status_transition_rejected(order_service, auth_service, product_service, cart_service):
    user = _register(auth_service)
    product = _product(product_service)
    cart_service.add_item(user.id, product.id, 1)
    order = _create_order(order_service, user.id)

    with pytest.raises(InvalidOrderStatusError):
        order_service.update_order_status(order.id, "collected")


def test_admin_retrieves_all_orders(order_service, auth_service, product_service, cart_service):
    user = _register(auth_service)
    product = _product(product_service)
    cart_service.add_item(user.id, product.id, 1)
    _create_order(order_service, user.id)
    assert len(order_service.get_all_orders()) == 1


def test_transaction_rollback_on_failure(order_repo, cart_repo, product_repo, user_repo, db):
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

    service = OrderService(FailingOrderRepository(order_repo), cart_repo, product_repo, db)

    with pytest.raises(RuntimeError):
        service.create_order(
            user.id, "Richard", "0212345678", "2026-10-10", "15:00",
            "bank_transfer", "12345",
        )

    # Nothing was committed: no order, stock unchanged, cart not cleared.
    assert order_repo.list_all_orders() == []
    assert product_repo.find_by_id(product.id).stock_quantity == 8
    assert cart_repo.get_cart_items(cart.id)[0].quantity == 2
