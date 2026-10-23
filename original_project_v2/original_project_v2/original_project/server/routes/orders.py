"""Customer order routes."""

from flask import Blueprint, current_app, jsonify, request

from routes.serializers import order_summary_to_dict, order_to_dict
from utils.auth import get_current_user, require_auth, require_permission

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")


@orders_bp.get("")
@require_auth
@require_permission("view_own_orders")
def list_orders():
    """List the current user's orders."""
    order_service = current_app.extensions["order_service"]
    orders = order_service.get_user_orders(get_current_user().id)
    return jsonify({"orders": [order_summary_to_dict(o) for o in orders]}), 200


@orders_bp.post("")
@require_auth
@require_permission("create_orders")
def create_order():
    """Create an order from the current user's cart."""
    data = request.get_json(silent=True) or {}
    order_service = current_app.extensions["order_service"]
    order = order_service.create_order(
        user_id=get_current_user().id,
        customer_name=data.get("customer_name"),
        phone=data.get("phone"),
        pickup_date=data.get("pickup_date"),
        pickup_time=data.get("pickup_time"),
        payment_reference_type=data.get("payment_reference_type"),
        payment_reference=data.get("payment_reference"),
    )
    return jsonify({"order": order_to_dict(order)}), 201


@orders_bp.get("/<int:order_id>")
@require_auth
@require_permission("view_own_orders")
def get_order(order_id):
    """Return a single order owned by the current user."""
    order_service = current_app.extensions["order_service"]
    order = order_service.get_order(order_id, get_current_user().id)
    return jsonify({"order": order_to_dict(order)}), 200


@orders_bp.post("/<int:order_id>/cancel")
@require_auth
@require_permission("cancel_orders")
def cancel_order(order_id):
    """Cancel the current user's own pending order."""
    order_service = current_app.extensions["order_service"]
    order = order_service.cancel_order(get_current_user().id, order_id)
    return jsonify({"order": order_to_dict(order)}), 200
