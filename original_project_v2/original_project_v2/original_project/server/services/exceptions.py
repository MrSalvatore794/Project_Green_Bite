"""Service-level exceptions for business failures.

These are raised by Services so the API route layer can later map them to the
appropriate HTTP status codes. They do not depend on Flask.
"""


class ServiceError(Exception):
    """Base class for all service-layer business errors."""


class ValidationError(ServiceError):
    """The request data failed validation."""


class UserAlreadyExistsError(ServiceError):
    """A user with the given email already exists."""


class UserNotFoundError(ServiceError):
    """The requested user does not exist."""


class AuthenticationError(ServiceError):
    """Login credentials are invalid."""


class ProductNotFoundError(ServiceError):
    """The requested product does not exist."""


class ProductUnavailableError(ServiceError):
    """The product is inactive or out of stock, so it cannot be purchased."""


class InsufficientStockError(ServiceError):
    """The requested quantity exceeds the available stock."""


class CartEmptyError(ServiceError):
    """The cart has no items, so an order cannot be created."""


class OrderNotFoundError(ServiceError):
    """The requested order does not exist."""


class InvalidOrderStatusError(ServiceError):
    """The requested order status change is not allowed."""


class OrderNotCancelableError(ServiceError):
    """The order cannot be canceled (wrong status or already canceled)."""


class ForbiddenError(ServiceError):
    """The current user is not allowed to perform this action."""
