"""Standard JSON error responses and framework-level error handlers."""

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from services.exceptions import (
    AuthenticationError,
    CartEmptyError,
    ForbiddenError,
    InsufficientStockError,
    InvalidOrderStatusError,
    OrderNotFoundError,
    ProductNotFoundError,
    ProductUnavailableError,
    ServiceError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)


def error_response(code: str, message: str, status_code: int) -> tuple:
    """Build the standard JSON error response used across the API."""
    return jsonify({"error": {"code": code, "message": message}}), status_code


# Maps each service exception to its HTTP error code and status.
_SERVICE_ERRORS = {
    ValidationError: ("INVALID_REQUEST", 400),
    AuthenticationError: ("UNAUTHORIZED", 401),
    ForbiddenError: ("FORBIDDEN", 403),
    UserNotFoundError: ("USER_NOT_FOUND", 404),
    ProductNotFoundError: ("PRODUCT_NOT_FOUND", 404),
    OrderNotFoundError: ("ORDER_NOT_FOUND", 404),
    UserAlreadyExistsError: ("USER_ALREADY_EXISTS", 409),
    ProductUnavailableError: ("PRODUCT_UNAVAILABLE", 409),
    InsufficientStockError: ("INSUFFICIENT_STOCK", 409),
    CartEmptyError: ("CART_EMPTY", 400),
    InvalidOrderStatusError: ("INVALID_ORDER_STATUS", 400),
}


def register_error_handlers(app: Flask) -> None:
    """Register framework-level handlers so every error is returned as JSON."""

    @app.errorhandler(404)
    def handle_not_found(error: HTTPException) -> tuple:
        return error_response("NOT_FOUND", "Resource not found", 404)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> tuple:
        code = error.name.upper().replace(" ", "_")
        return error_response(code, error.description, error.code)

    @app.errorhandler(ServiceError)
    def handle_service_error(error: ServiceError) -> tuple:
        code, status = _SERVICE_ERRORS.get(type(error), ("SERVICE_ERROR", 400))
        return error_response(code, str(error), status)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> tuple:
        app.logger.exception("Unhandled error: %s", error)
        return error_response("INTERNAL_ERROR", "An unexpected error occurred.", 500)

