"""Tests for the domain models."""

import pytest

from models import Admin, Cart, CartItem, Customer, Order, OrderItem, Product, User


def _product(name="Walnut Raisin Bread", price=11.0, stock=8, is_active=True, product_id=None):
    return Product(
        name=name,
        price=price,
        stock_quantity=stock,
        is_active=is_active,
        product_id=product_id,
    )


# --- User / Customer / Admin ---


def test_user_can_be_instantiated():
    user = User("Richard", "richard@example.com", phone="0212345678", password_hash="hash")
    assert user.name == "Richard"
    assert user.email == "richard@example.com"
    assert user.phone == "0212345678"
    assert user.role == "customer"


def test_customer_and_admin_can_be_instantiated():
    customer = Customer("Richard", "richard@example.com")
    admin = Admin("Ayush", "ayush@example.com")
    assert customer.role == "customer"
    assert admin.role == "admin"


def test_customer_and_admin_inherit_common_user_data():
    customer = Customer("Richard", "richard@example.com", phone="0212345678")
    admin = Admin("Ayush", "ayush@example.com", phone="0223456789")
    assert isinstance(customer, User)
    assert isinstance(admin, User)
    assert customer.name == "Richard"
    assert customer.email == "richard@example.com"
    assert admin.phone == "0223456789"


# --- Product ---


def test_product_can_be_instantiated():
    product = _product()
    assert product.name == "Walnut Raisin Bread"
    assert product.price == 11.0
    assert product.stock_quantity == 8
    assert product.is_active is True


def test_product_availability():
    assert _product(stock=8, is_active=True).is_available() is True
    assert _product(stock=0, is_active=True).is_available() is False
    assert _product(stock=8, is_active=False).is_available() is False


def test_update_stock_works():
    product = _product(stock=8)
    product.update_stock(15)
    assert product.stock_quantity == 15


def test_update_stock_rejects_negative():
    product = _product(stock=8)
    with pytest.raises(ValueError):
        product.update_stock(-1)


def test_reduce_stock_works():
    product = _product(stock=8)
    product.reduce_stock(3)
    assert product.stock_quantity == 5


def test_reduce_stock_rejects_exceeding_stock():
    product = _product(stock=8)
    with pytest.raises(ValueError):
        product.reduce_stock(9)


# --- Cart / CartItem ---


def test_cart_can_contain_items():
    cart = Cart(user_id=1)
    cart.add_item(_product(), 2)
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 2


def test_cart_add_same_product_merges_quantity():
    cart = Cart(user_id=1)
    product = _product()
    cart.add_item(product, 2)
    cart.add_item(product, 3)
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 5


def test_cart_total_calculation():
    cart = Cart(user_id=1)
    cart.add_item(_product(product_id=1, name="Bread", price=11.0), 2)
    cart.add_item(_product(product_id=2, name="Cake", price=12.5), 1)
    assert cart.calculate_total() == 34.5


def test_cart_update_item_quantity():
    cart = Cart(user_id=1)
    product = _product()
    cart.add_item(product, 2)
    cart.update_item(product.id, 4)
    assert cart.items[0].quantity == 4


def test_cart_remove_item():
    cart = Cart(user_id=1)
    product = _product()
    cart.add_item(product, 2)
    cart.remove_item(product.id)
    assert len(cart.items) == 0


def test_cart_clear():
    cart = Cart(user_id=1)
    cart.add_item(_product(product_id=1), 2)
    cart.add_item(_product(product_id=2, name="Cake", price=12.5), 1)
    assert len(cart.items) == 2
    cart.clear()
    assert len(cart.items) == 0


def test_cart_item_quantity_must_be_positive():
    cart = Cart(user_id=1)
    with pytest.raises(ValueError):
        cart.add_item(_product(), 0)


def test_cart_item_subtotal():
    item = CartItem(_product(price=11.0), 2)
    assert item.calculate_subtotal() == 22.0


# --- Order / OrderItem ---


def test_order_can_contain_items():
    order = Order(user_id=1)
    order.add_item(OrderItem(1, "Bread", 11.0, 2))
    order.add_item(OrderItem(2, "Cake", 12.5, 1))
    assert len(order.items) == 2


def test_order_total_calculation():
    order = Order(user_id=1)
    order.add_item(OrderItem(1, "Bread", 11.0, 2))
    order.add_item(OrderItem(2, "Cake", 12.5, 1))
    assert order.calculate_total() == 34.5


def test_order_starts_pending():
    order = Order(user_id=1)
    assert order.status == "pending"


def test_valid_status_transition():
    order = Order(user_id=1)
    order.change_status("confirmed")
    assert order.status == "confirmed"


def test_order_follows_full_workflow():
    order = Order(user_id=1)
    for status in ["confirmed", "preparing", "ready_for_pickup", "collected"]:
        order.change_status(status)
    assert order.status == "collected"


def test_invalid_status_transition_is_rejected():
    order = Order(user_id=1)
    with pytest.raises(ValueError):
        order.change_status("preparing")  # skips "confirmed"


def test_status_cannot_go_backwards():
    order = Order(user_id=1)
    order.change_status("confirmed")
    with pytest.raises(ValueError):
        order.change_status("pending")


def test_order_item_subtotal():
    item = OrderItem(1, "Bread", 11.0, 2)
    assert item.calculate_subtotal() == 22.0
    assert item.subtotal == 22.0


def test_order_item_preserves_name_and_price_snapshot():
    item = OrderItem(1, "Walnut Raisin Bread", 11.0, 2)
    assert item.product_id == 1
    assert item.product_name == "Walnut Raisin Bread"
    assert item.unit_price == 11.0
    assert item.quantity == 2
