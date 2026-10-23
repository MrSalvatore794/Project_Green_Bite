"""Admin order management routes."""

from flask import Blueprint, current_app, jsonify, request

from routes.serializers import order_summary_to_dict, order_to_dict
from services.exceptions import ValidationError
from utils.auth import require_auth, require_permission

admin_orders_bp = Blueprint(
    "admin_orders", __name__, url_prefix="/api/v1/admin/orders"
)


def _order_service():
    return current_app.extensions["order_service"]


@admin_orders_bp.get("")
@require_auth
@require_permission("manage_orders")
def list_orders():
    """List all orders for all customers."""
    orders = _order_service().get_all_orders()
    return jsonify({"orders": [order_summary_to_dict(o) for o in orders]}), 200


@admin_orders_bp.get("/<int:order_id>")
@require_auth
@require_permission("manage_orders")
def get_order(order_id):
    """Return any order by id (no ownership restriction)."""
    order = _order_service().get_order_admin(order_id)
    return jsonify({"order": order_to_dict(order)}), 200


@admin_orders_bp.patch("/<int:order_id>/status")
@require_auth
@require_permission("manage_orders")
def update_order_status(order_id):
    """Update the order status through the defined lifecycle."""
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        raise ValidationError("Invalid request body.")
    status = data.get("status")
    if status is None:
        raise ValidationError("Field 'status' is required.")
    order = _order_service().update_order_status(order_id, status)
    return jsonify({"order": order_to_dict(order)}), 200


@admin_orders_bp.patch("/<int:order_id>/payment-status")
@require_auth
@require_permission("manage_orders")
def update_payment_status(order_id):
    """Manually update an order's payment status (Admin verification)."""
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        raise ValidationError("Invalid request body.")
    status = data.get("payment_status")
    if status is None:
        raise ValidationError("Field 'payment_status' is required.")
    order = _order_service().update_payment_status(order_id, status)
    return jsonify({"order": order_to_dict(order)}), 200
