"""Public product routes."""

from flask import Blueprint, current_app, jsonify

from routes.serializers import product_detail_to_dict, product_to_dict
from services.exceptions import ProductNotFoundError
from utils.auth import (
    get_current_user,
    get_optional_current_user,
    require_auth,
    require_permission,
)

products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")


@products_bp.get("")
def list_products():
    """List available products (public)."""
    product_service = current_app.extensions["product_service"]
    products = product_service.get_active_products()
    return jsonify({"products": [product_to_dict(p) for p in products]}), 200


@products_bp.get("/<int:product_id>")
def get_product(product_id):
    """Return a single available product (public, optionally personalised)."""
    product_service = current_app.extensions["product_service"]
    current_user = get_optional_current_user()
    product = product_service.get_product_detail(
        product_id, current_user.id if current_user else None
    )
    if not product.is_available():
        raise ProductNotFoundError(f"Product {product_id!r} does not exist.")
    return jsonify({"product": product_detail_to_dict(product)}), 200


@products_bp.post("/<int:product_id>/like")
@require_auth
@require_permission("like_products")
def like_product(product_id):
    """Like a product for the current customer."""
    product_service = current_app.extensions["product_service"]
    liked, like_count = product_service.like_product(get_current_user().id, product_id)
    return jsonify({"liked": liked, "like_count": like_count}), 200


@products_bp.delete("/<int:product_id>/like")
@require_auth
@require_permission("like_products")
def unlike_product(product_id):
    """Remove the current customer's like for a product."""
    product_service = current_app.extensions["product_service"]
    liked, like_count = product_service.unlike_product(get_current_user().id, product_id)
    return jsonify({"liked": liked, "like_count": like_count}), 200

