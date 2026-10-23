"""Tests for the repository layer."""

import pytest

from database.database import Database
from models import Admin, Order, OrderItem, Product, User
from repositories import (
    CartRepository,
    OrderRepository,
    ProductRepository,
    UserRepository,
)


@pytest.fixture
def db(tmp_path):
    database = Database(str(tmp_path / "repo_test.db"))
    database.initialize()
    return database


@pytest.fixture
def user_repo(db):
    return UserRepository(db)


@pytest.fixture
def product_repo(db):
    return ProductRepository(db)


@pytest.fixture
def cart_repo(db):
    return CartRepository(db)


@pytest.fixture
def order_repo(db):
    return OrderRepository(db)


def _user(name="Richard", email="richard@example.com"):
    return User(name=name, email=email, password_hash="hashed-password")


def _product(name="Bread", price=11.0, stock=8, active=True):
    return Product(name=name, price=price, stock_quantity=stock, is_active=active)


def _cart_for_user(cart_repo, user_repo, email="richard@example.com"):
    user = user_repo.create_user(_user(email=email))
    return cart_repo.create_cart(user.id)


def _order(user_id):
    return Order(
        user_id=user_id,
        customer_name="Richard",
        phone="0212345678",
        pickup_date="2026-10-10",
        pickup_time="15:00",
        payment_reference_type="bank_transfer",
        payment_reference="12345",
        total_amount=22.0,
    )


# --- UserRepository ---


def test_create_user(user_repo):
    created = user_repo.create_user(_user())
    assert created.id is not None


def test_find_user_by_id(user_repo):
    created = user_repo.create_user(_user())
    found = user_repo.find_by_id(created.id)
    assert found is not None
    assert found.name == "Richard"
    assert found.email == "richard@example.com"
    assert found.role == "customer"


def test_find_user_by_email(user_repo):
    user_repo.create_user(_user())
    found = user_repo.find_by_email("richard@example.com")
    assert found is not None
    assert found.name == "Richard"
    assert user_repo.find_by_email("missing@example.com") is None


def test_list_users(user_repo):
    user_repo.create_user(_user(email="richard@example.com"))
    user_repo.create_user(
        Admin(name="Ayush", email="ayush@example.com", password_hash="hashed-password")
    )
    users = user_repo.list_users()
    assert {u.email for u in users} == {"richard@example.com", "ayush@example.com"}


# --- ProductRepository ---


def test_create_product(product_repo):
    created = product_repo.create_product(_product())
    assert created.id is not None


def test_find_product(product_repo):
    created = product_repo.create_product(_product(name="Bread", price=11.0))
    found = product_repo.find_by_id(created.id)
    assert found is not None
    assert found.name == "Bread"
    assert found.price == 11.0


def test_list_active_products(product_repo):
    product_repo.create_product(_product(name="Active Bread", active=True))
    product_repo.create_product(_product(name="Inactive Cake", active=False))
    active = product_repo.list_active_products()
    assert [p.name for p in active] == ["Active Bread"]


def test_list_all_products(product_repo):
    product_repo.create_product(_product(name="Active Bread", active=True))
    product_repo.create_product(_product(name="Inactive Cake", active=False))
    assert len(product_repo.list_all_products()) == 2


def test_update_product(product_repo):
    product = product_repo.create_product(_product(name="Bread", price=11.0))
    product.name = "Sourdough"
    product.price = 13.0
    product_repo.update_product(product)
    found = product_repo.find_by_id(product.id)
    assert found.name == "Sourdough"
    assert found.price == 13.0


def test_update_stock(product_repo):
    product = product_repo.create_product(_product(stock=8))
    product_repo.update_stock(product.id, 15)
    assert product_repo.find_by_id(product.id).stock_quantity == 15


# --- CartRepository ---


def test_create_cart(cart_repo, user_repo):
    cart = _cart_for_user(cart_repo, user_repo)
    assert cart.id is not None
    assert cart.user_id is not None


def test_find_cart_by_user(cart_repo, user_repo):
    cart = _cart_for_user(cart_repo, user_repo)
    found = cart_repo.find_cart_by_user(cart.user_id)
    assert found is not None
    assert found.id == cart.id
    assert cart_repo.find_cart_by_user(9999) is None


def test_add_and_retrieve_cart_items(cart_repo, user_repo, product_repo):
    cart = _cart_for_user(cart_repo, user_repo)
    product = product_repo.create_product(_product(name="Bread", price=11.0))
    cart_repo.add_cart_item(cart.id, product.id, 2)

    items = cart_repo.get_cart_items(cart.id)
    assert len(items) == 1
    assert items[0].product_id == product.id
    assert items[0].product.name == "Bread"
    assert items[0].quantity == 2
    assert items[0].calculate_subtotal() == 22.0


def test_update_cart_item_quantity(cart_repo, user_repo, product_repo):
    cart = _cart_for_user(cart_repo, user_repo)
    product = product_repo.create_product(_product())
    cart_repo.add_cart_item(cart.id, product.id, 2)
    cart_repo.update_cart_item_quantity(cart.id, product.id, 5)
    assert cart_repo.get_cart_items(cart.id)[0].quantity == 5


def test_remove_cart_item(cart_repo, user_repo, product_repo):
    cart = _cart_for_user(cart_repo, user_repo)
    product = product_repo.create_product(_product())
    cart_repo.add_cart_item(cart.id, product.id, 2)
    cart_repo.remove_cart_item(cart.id, product.id)
    assert cart_repo.get_cart_items(cart.id) == []


def test_clear_cart(cart_repo, user_repo, product_repo):
    cart = _cart_for_user(cart_repo, user_repo)
    p1 = product_repo.create_product(_product(name="Bread"))
    p2 = product_repo.create_product(_product(name="Cake"))
    cart_repo.add_cart_item(cart.id, p1.id, 1)
    cart_repo.add_cart_item(cart.id, p2.id, 2)
    cart_repo.clear_cart(cart.id)
    assert cart_repo.get_cart_items(cart.id) == []


# --- OrderRepository ---


def test_create_order(order_repo, user_repo):
    user = user_repo.create_user(_user())
    created = order_repo.create_order(_order(user.id))
    assert created.id is not None


def test_create_order_items_and_retrieve(order_repo, user_repo, product_repo):
    user = user_repo.create_user(_user())
    product = product_repo.create_product(_product(name="Bread", price=11.0))
    order = order_repo.create_order(_order(user.id))

    item = OrderItem(
        product_id=product.id, product_name="Bread", unit_price=11.0, quantity=2
    )
    order_repo.create_order_items(order.id, [item])

    found = order_repo.find_by_id(order.id)
    assert len(found.items) == 1
    assert found.items[0].product_name == "Bread"
    assert found.items[0].unit_price == 11.0
    assert found.items[0].quantity == 2
    assert found.items[0].subtotal == 22.0


def test_retrieve_order(order_repo, user_repo):
    user = user_repo.create_user(_user())
    order = order_repo.create_order(_order(user.id))
    found = order_repo.find_by_id(order.id)
    assert found is not None
    assert found.total_amount == 22.0
    assert found.status == "pending"


def test_list_orders_for_user(order_repo, user_repo):
    u1 = user_repo.create_user(_user(email="r@example.com"))
    u2 = user_repo.create_user(_user(email="s@example.com"))
    order_repo.create_order(_order(u1.id))
    order_repo.create_order(_order(u2.id))
    orders = order_repo.list_orders_for_user(u1.id)
    assert len(orders) == 1
    assert orders[0].user_id == u1.id


def test_list_all_orders(order_repo, user_repo):
    u1 = user_repo.create_user(_user(email="r@example.com"))
    u2 = user_repo.create_user(_user(email="s@example.com"))
    order_repo.create_order(_order(u1.id))
    order_repo.create_order(_order(u2.id))
    assert len(order_repo.list_all_orders()) == 2


def test_update_order_status(order_repo, user_repo):
    user = user_repo.create_user(_user())
    order = order_repo.create_order(_order(user.id))
    order_repo.update_order_status(order.id, "confirmed")
    assert order_repo.find_by_id(order.id).status == "confirmed"


# --- Transaction support ---


def test_repositories_can_share_a_transaction(db, user_repo, product_repo, cart_repo, order_repo):
    user = user_repo.create_user(_user())
    cart = cart_repo.create_cart(user.id)
    product = product_repo.create_product(_product(stock=8))

    with db.connection() as conn:
        order = order_repo.create_order(_order(user.id), connection=conn)
        order_repo.create_order_items(
            order.id,
            [OrderItem(product.id, "Bread", 11.0, 2)],
            connection=conn,
        )
        product_repo.update_stock(product.id, 6, connection=conn)
        cart_repo.add_cart_item(cart.id, product.id, 2, connection=conn)

    found = order_repo.find_by_id(order.id)
    assert found.items[0].product_name == "Bread"
    assert product_repo.find_by_id(product.id).stock_quantity == 6
    assert cart_repo.get_cart_items(cart.id)[0].quantity == 2
