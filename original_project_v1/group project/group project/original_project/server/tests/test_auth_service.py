"""Tests for AuthService."""

import pytest

from models import Admin
from services.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)


def test_successful_registration(auth_service):
    user = auth_service.register(
        "Richard", "richard@example.com", "0212345678", "Password123"
    )
    assert user.id is not None
    assert user.role == "customer"
    assert user.email == "richard@example.com"


def test_registration_creates_customer_not_admin(auth_service):
    user = auth_service.register(
        "Richard", "richard@example.com", "0212345678", "Password123"
    )
    assert user.role == "customer"
    assert "manage_products" not in user.get_permissions()


def test_duplicate_email_rejected(auth_service):
    auth_service.register("Richard", "richard@example.com", "0212345678", "Password123")
    with pytest.raises(UserAlreadyExistsError):
        auth_service.register("Salin", "richard@example.com", "0223456789", "Password123")


def test_missing_fields_rejected(auth_service):
    with pytest.raises(ValidationError):
        auth_service.register("", "richard@example.com", "0212345678", "Password123")


def test_password_is_hashed(auth_service, user_repo):
    auth_service.register("Richard", "richard@example.com", "0212345678", "Password123")
    stored = user_repo.find_by_email("richard@example.com")
    assert stored.password_hash != "Password123"
    assert "Password123" not in stored.password_hash


def test_successful_authentication(auth_service):
    auth_service.register("Richard", "richard@example.com", "0212345678", "Password123")
    user = auth_service.authenticate("richard@example.com", "Password123")
    assert user is not None
    assert user.email == "richard@example.com"


def test_failed_authentication(auth_service):
    auth_service.register("Richard", "richard@example.com", "0212345678", "Password123")
    with pytest.raises(AuthenticationError):
        auth_service.authenticate("richard@example.com", "WrongPassword")
    with pytest.raises(AuthenticationError):
        auth_service.authenticate("unknown@example.com", "Password123")


def test_get_user(auth_service):
    created = auth_service.register(
        "Richard", "richard@example.com", "0212345678", "Password123"
    )
    assert auth_service.get_user(created.id).email == "richard@example.com"
    with pytest.raises(UserNotFoundError):
        auth_service.get_user(9999)


def test_customer_permissions_exclude_admin_operations(auth_service):
    customer = auth_service.register(
        "Richard", "richard@example.com", "0212345678", "Password123"
    )
    permissions = customer.get_permissions()
    assert "create_orders" in permissions
    assert "manage_products" not in permissions
    assert "update_order_status" not in permissions


def test_admin_permissions_include_admin_operations():
    admin = Admin(name="Ayush", email="ayush@example.com", password_hash="hash")
    permissions = admin.get_permissions()
    assert "manage_products" in permissions
    assert "update_order_status" in permissions
    assert "create_orders" not in permissions
