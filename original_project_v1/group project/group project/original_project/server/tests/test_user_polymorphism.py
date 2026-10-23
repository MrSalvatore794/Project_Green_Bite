"""Tests for User/Customer/Admin polymorphism in the repository layer."""

from models import Admin, Customer, User


def test_repository_returns_customer_for_customer_role(user_repo):
    customer = user_repo.create_user(
        Customer(name="Richard", email="richard@example.com", password_hash="hash")
    )
    loaded = user_repo.find_by_id(customer.id)
    assert isinstance(loaded, Customer)
    assert loaded.role == "customer"


def test_repository_returns_admin_for_admin_role(user_repo):
    admin = user_repo.create_user(
        Admin(name="Ayush", email="ayush@example.com", password_hash="hash")
    )
    loaded = user_repo.find_by_id(admin.id)
    assert isinstance(loaded, Admin)
    assert loaded.role == "admin"


def test_customer_permissions(user_repo):
    customer = user_repo.create_user(
        Customer(name="Richard", email="richard@example.com", password_hash="hash")
    )
    permissions = user_repo.find_by_id(customer.id).get_permissions()
    assert "create_orders" in permissions
    assert "manage_products" not in permissions


def test_admin_permissions(user_repo):
    admin = user_repo.create_user(
        Admin(name="Ayush", email="ayush@example.com", password_hash="hash")
    )
    permissions = user_repo.find_by_id(admin.id).get_permissions()
    assert "manage_products" in permissions
    assert "create_orders" not in permissions


def test_get_permissions_is_overridden_per_subclass():
    assert Customer.get_permissions is not User.get_permissions
    assert Admin.get_permissions is not User.get_permissions
    assert Customer.get_permissions is not Admin.get_permissions
