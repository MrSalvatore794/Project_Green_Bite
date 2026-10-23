"""Authentication business logic."""

from werkzeug.security import check_password_hash, generate_password_hash

from models import Admin, Customer, User
from repositories.user_repository import UserRepository
from services.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)


class AuthService:
    """Coordinate registration, authentication, and user-management rules.

    Public registration always creates a ``Customer``. Admin accounts are
    provisioned through a controlled bootstrap mechanism (``create_admin``)
    and can never be created by a normal client request.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def register(self, name: str, email: str, phone: str, password: str) -> Customer:
        """Register a new customer and return the created user."""
        return self._create_user(Customer, name, email, phone, password)

    def create_admin(self, name: str, email: str, phone: str, password: str) -> Admin:
        """Provision a new Admin account (controlled bootstrap only)."""
        return self._create_user(Admin, name, email, phone, password)

    def authenticate(self, email: str, password: str) -> User:
        """Verify credentials and return the user, or raise AuthenticationError."""
        user = self.user_repository.find_by_email(email)
        if user is None or not check_password_hash(user.password_hash, password):
            raise AuthenticationError("Invalid email or password.")
        return user

    def get_user(self, user_id: int) -> User:
        """Return the user for the given id, or raise UserNotFoundError."""
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id!r} does not exist.")
        return user

    def get_all_users(self) -> list[User]:
        """Return all users (admin use)."""
        return self.user_repository.list_users()

    def search_users(self, search: str | None = None, role: str | None = None) -> list[User]:
        """Return users matching the optional search term and role (admin use)."""
        return self.user_repository.list_users(search=search, role=role)

    def reset_admin_password(self, email: str, new_password: str) -> Admin:
        """Reset an Admin's password. Rejects Customer accounts."""
        user = self.user_repository.find_by_email(email)
        if user is None:
            raise UserNotFoundError(f"User with email {email!r} does not exist.")
        if user.role != User.ROLE_ADMIN:
            raise ValidationError(
                "Only Admin accounts can have their password reset here."
            )
        if not new_password:
            raise ValidationError("New password is required.")
        user.password_hash = generate_password_hash(new_password)
        return self.user_repository.update_user(user)

    def _create_user(self, user_class, name, email, phone, password) -> User:
        self._validate_registration(name, email, phone, password)
        if self.user_repository.find_by_email(email) is not None:
            raise UserAlreadyExistsError(f"A user with email {email!r} already exists.")
        password_hash = generate_password_hash(password)
        user = user_class(name=name, email=email, phone=phone, password_hash=password_hash)
        return self.user_repository.create_user(user)

    def _validate_registration(self, name, email, phone, password) -> None:
        required = {"name": name, "email": email, "phone": phone, "password": password}
        missing = [field for field, value in required.items() if not value]
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))

