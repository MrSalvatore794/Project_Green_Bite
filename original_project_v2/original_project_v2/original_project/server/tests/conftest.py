"""Shared fixtures for the service-layer tests."""

import pytest

from database.database import Database
from repositories import (
    CartRepository,
    OrderRepository,
    ProductRepository,
    UserRepository,
)
from services import AuthService, CartService, OrderService, ProductService


@pytest.fixture
def db(tmp_path):
    database = Database(str(tmp_path / "service_test.db"))
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


@pytest.fixture
def auth_service(user_repo):
    return AuthService(user_repo)


@pytest.fixture
def product_service(product_repo):
    return ProductService(product_repo)


@pytest.fixture
def cart_service(cart_repo, product_repo, user_repo):
    return CartService(cart_repo, product_repo, user_repo)


@pytest.fixture
def order_service(order_repo, cart_repo, product_repo, db):
    return OrderService(order_repo, cart_repo, product_repo, db)


@pytest.fixture
def app(tmp_path):
    from app import create_app

    return create_app(
        "testing",
        {
            "DATABASE_PATH": str(tmp_path / "api_test.db"),
            "MEDIA_ROOT": str(tmp_path / "uploads"),
        },
    )


@pytest.fixture
def client(app):
    return app.test_client()
