"""Admin user management routes."""

from flask import Blueprint, current_app, jsonify, request

from routes.serializers import order_summary_to_dict, user_to_dict
from utils.auth import require_auth, require_permission

admin_users_bp = Blueprint("admin_users", __name__, url_prefix="/api/v1/admin/users")


def _auth_service():
    return current_app.extensions["auth_service"]


def _order_service():
    return current_app.extensions["order_service"]


@admin_users_bp.get("")
@require_auth
@require_permission("manage_users")
def list_users():
    """List users, optionally filtered by search and role."""
    search = request.args.get("search")
    role = request.args.get("role")
    users = _auth_service().search_users(search=search, role=role)
    return jsonify({"users": [user_to_dict(u) for u in users]}), 200


@admin_users_bp.get("/<int:user_id>")
@require_auth
@require_permission("manage_users")
def get_user(user_id):
    """Return a single user with their order history."""
    user = _auth_service().get_user(user_id)
    orders = _order_service().get_user_orders(user_id)
    return jsonify(
        {
            "user": user_to_dict(user),
            "orders": [order_summary_to_dict(o) for o in orders],
        }
    ), 200
