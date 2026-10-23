"""Customer cart routes."""

from flask import Blueprint, current_app, jsonify, request

from routes.serializers import cart_to_dict
from utils.auth import get_current_user, require_auth, require_permission

cart_bp = Blueprint("cart", __name__, url_prefix="/api/v1/cart")


@cart_bp.get("")
@require_auth
@require_permission("manage_cart")
def get_cart():
    """Return the current user's cart."""
    cart_service = current_app.extensions["cart_service"]
    cart = cart_service.get_cart(get_current_user().id)
    return jsonify({"cart": cart_to_dict(cart)}), 200


@cart_bp.post("/items")
@require_auth
@require_permission("manage_cart")
def add_item():
    """Add a product to the cart."""
    data = request.get_json(silent=True) or {}
    cart_service = current_app.extensions["cart_service"]
    cart = cart_service.add_item(
        get_current_user().id, data.get("product_id"), data.get("quantity")
    )
    return jsonify({"cart": cart_to_dict(cart)}), 200


@cart_bp.put("/items/<int:product_id>")
@require_auth
@require_permission("manage_cart")
def update_item(product_id):
    """Update the quantity of a cart item."""
    data = request.get_json(silent=True) or {}
    cart_service = current_app.extensions["cart_service"]
    cart = cart_service.update_quantity(
        get_current_user().id, product_id, data.get("quantity")
    )
    return jsonify({"cart": cart_to_dict(cart)}), 200


@cart_bp.delete("/items/<int:product_id>")
@require_auth
@require_permission("manage_cart")
def remove_item(product_id):
    """Remove a product from the cart."""
    cart_service = current_app.extensions["cart_service"]
    cart = cart_service.remove_item(get_current_user().id, product_id)
    return jsonify({"cart": cart_to_dict(cart)}), 200


@cart_bp.delete("")
@require_auth
@require_permission("manage_cart")
def clear_cart():
    """Clear all items from the cart."""
    cart_service = current_app.extensions["cart_service"]
    cart = cart_service.clear_cart(get_current_user().id)
    return jsonify({"cart": cart_to_dict(cart)}), 200
