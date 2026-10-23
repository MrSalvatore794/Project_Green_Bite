"""Tests for Admin account provisioning and password reset (AuthService)."""

import pytest

from services.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)


def test_create_admin(auth_service, user_repo):
    admin = auth_service.create_admin(
        "Admin", "admin@example.com", "0211111111", "adminpass123"
    )
    assert admin.id is not None
    assert admin.role == "admin"

    loaded = user_repo.find_by_email("admin@example.com")
    assert loaded.role == "admin"


def test_create_admin_duplicate_email_rejected(auth_service):
    auth_service.create_admin("Admin", "admin@example.com", "0211111111", "adminpass123")
    with pytest.raises(UserAlreadyExistsError):
        auth_service.create_admin("Admin2", "admin@example.com", "0222222222", "otherpass123")


def test_create_admin_password_hashed(auth_service, user_repo):
    auth_service.create_admin("Admin", "admin@example.com", "0211111111", "adminpass123")
    stored = user_repo.find_by_email("admin@example.com")
    assert stored.password_hash != "adminpass123"
    assert "adminpass123" not in stored.password_hash


def test_admin_can_login_after_create(auth_service):
    auth_service.create_admin("Admin", "admin@example.com", "0211111111", "adminpass123")
    user = auth_service.authenticate("admin@example.com", "adminpass123")
    assert user.role == "admin"


def test_reset_admin_password(auth_service):
    auth_service.create_admin("Admin", "admin@example.com", "0211111111", "oldpass123")
    auth_service.reset_admin_password("admin@example.com", "newpass456")

    with pytest.raises(AuthenticationError):
        auth_service.authenticate("admin@example.com", "oldpass123")
    user = auth_service.authenticate("admin@example.com", "newpass456")
    assert user.role == "admin"


def test_reset_admin_password_rejects_customer(auth_service):
    auth_service.register("Richard", "cust@example.com", "0212345678", "Password123")
    with pytest.raises(ValidationError):
        auth_service.reset_admin_password("cust@example.com", "newpass456")


def test_reset_admin_password_nonexistent(auth_service):
    with pytest.raises(UserNotFoundError):
        auth_service.reset_admin_password("nobody@example.com", "newpass456")


def test_create_admin_missing_field(auth_service):
    with pytest.raises(ValidationError):
        auth_service.create_admin("", "admin@example.com", "0211111111", "adminpass123")
