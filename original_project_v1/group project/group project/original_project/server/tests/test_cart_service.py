"""Tests for CartService."""

import pytest

from services.exceptions import (
    InsufficientStockError,
    ProductNotFoundError,
    ProductUnavailableError,
    UserNotFoundError,
    ValidationError,
)


def _register(auth_service, email="richard@example.com"):
    return auth_service.register("Richard", email, "0212345678", "Password123")


def _create_product(product_service, name="Bread", price=11.0, stock=8, active=True):
    product = product_service.create_product(name, price, stock_quantity=stock)
    if not active:
        product_service.set_product_active(product.id, False)
    return product


def test_get_or_create_cart(cart_service, auth_service):
    user = _register(auth_service)
    cart = cart_service.get_cart(user.id)
    assert cart.id is not None
    assert cart.user_id == user.id
    # A second call returns the same cart rather than creating a duplicate.
    assert cart_service.get_cart(user.id).id == cart.id


def test_customer_must_exist(cart_service):
    with pytest.raises(UserNotFoundError):
        cart_service.get_cart(9999)


def test_add_product(cart_service, auth_service, product_service):
    user = _register(auth_service)
    product = _create_product(product_service)
    cart = cart_service.add_item(user.id, product.id, 2)
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 2


def test_add_same_product_twice(cart_service, auth_service, product_service):
    user = _register(auth_service)
    product = _create_product(product_service)
    cart_service.add_item(user.id, product.id, 2)
    cart = cart_service.add_item(user.id, product.id, 3)
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 5


def test_quantity_must_be_positive(cart_service, auth_service, product_service):
    user = _register(auth_service)
    product = _create_product(product_service)
    with pytest.raises(ValidationError):
        cart_service.add_item(user.id, product.id, 0)


def test_unavailable_product_rejected(cart_service, auth_service, product_service):
    user = _register(auth_service)
    product = _create_product(product_service, active=False)
    with pytest.raises(ProductUnavailableError):
        cart_service.add_item(user.id, product.id, 1)


def test_product_not_found(cart_service, auth_service):
    user = _register(auth_service)
    with pytest.raises(ProductNotFoundError):
        cart_service.add_item(user.id, 9999, 1)


def test_insufficient_stock_rejected(cart_service, auth_service, product_service):
    user = _register(auth_service)
    product = _create_product(product_service, stock=5)
    with pytest.raises(InsufficientStockError):
        cart_service.add_item(user.id, product.id, 6)


def test_update_quantity(cart_service, auth_service, product_service):
    user = _register(auth_service)
    product = _create_product(product_service, stock=10)
    cart_service.add_item(user.id, product.id, 2)
    cart = cart_service.update_quantity(user.id, product.id, 4)
    assert cart.items[0].quantity == 4


def test_remove_item(cart_service, auth_service, product_service):
    user = _register(auth_service)
    product = _create_product(product_service)
    cart_service.add_item(user.id, product.id, 2)
    cart = cart_service.remove_item(user.id, product.id)
    assert cart.items == []


def test_clear_cart(cart_service, auth_service, product_service):
    user = _register(auth_service)
    p1 = _create_product(product_service, name="Bread")
    p2 = _create_product(product_service, name="Cake", price=12.0)
    cart_service.add_item(user.id, p1.id, 1)
    cart_service.add_item(user.id, p2.id, 2)
    cart = cart_service.clear_cart(user.id)
    assert cart.items == []


def test_calculate_total(cart_service, auth_service, product_service):
    user = _register(auth_service)
    p1 = _create_product(product_service, name="Bread", price=11.0)
    p2 = _create_product(product_service, name="Cake", price=12.5)
    cart_service.add_item(user.id, p1.id, 2)  # 22.0
    cart_service.add_item(user.id, p2.id, 1)  # 12.5
    assert cart_service.calculate_total(user.id) == 34.5


def test_carts_are_isolated_per_customer(cart_service, auth_service, product_service):
    user1 = _register(auth_service, "richard@example.com")
    user2 = _register(auth_service, "salin@example.com")
    product = _create_product(product_service)
    cart_service.add_item(user1.id, product.id, 2)
    assert cart_service.get_cart(user2.id).items == []
