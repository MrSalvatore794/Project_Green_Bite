"""Admin product management routes."""

from flask import Blueprint, current_app, jsonify, request

from routes.serializers import product_to_dict
from services.exceptions import ValidationError
from utils.auth import require_auth, require_permission

admin_products_bp = Blueprint(
    "admin_products", __name__, url_prefix="/api/v1/admin/products"
)


def _product_service():
    return current_app.extensions["product_service"]


@admin_products_bp.get("")
@require_auth
@require_permission("manage_products")
def list_products():
    """List all products, including inactive and zero-stock ones."""
    products = _product_service().get_all_products()
    return jsonify({"products": [product_to_dict(p) for p in products]}), 200


@admin_products_bp.get("/<int:product_id>")
@require_auth
@require_permission("manage_products")
def get_product(product_id):
    """Return any product by id, including inactive products."""
    product = _product_service().get_product(product_id)
    return jsonify({"product": product_to_dict(product)}), 200


@admin_products_bp.post("")
@require_auth
@require_permission("manage_products")
def create_product():
    """Create a new product."""
    data = request.get_json(silent=True) or {}
    product = _product_service().create_product(
        name=data.get("name"),
        price=data.get("price"),
        stock_quantity=data.get("stock_quantity", data.get("stock", 0)),
        description=data.get("description", ""),
        category=data.get("category", ""),
        vegetarian=data.get("vegetarian", False),
        vegan=data.get("vegan", False),
        ingredients=data.get("ingredients", ""),
        allergens=data.get("allergens", ""),
        image_url=data.get("image_url", ""),
        detail_image_url=data.get("detail_image_url", ""),
        star_level=data.get("star_level", 0),
    )
    return jsonify({"product": product_to_dict(product)}), 201


@admin_products_bp.put("/<int:product_id>")
@require_auth
@require_permission("manage_products")
def update_product(product_id):
    """Update an existing product."""
    data = request.get_json(silent=True) or {}
    product = _product_service().update_product(
        product_id,
        name=data.get("name"),
        description=data.get("description"),
        price=data.get("price"),
        category=data.get("category"),
        vegetarian=data.get("vegetarian"),
        vegan=data.get("vegan"),
        ingredients=data.get("ingredients"),
        allergens=data.get("allergens"),
        image_url=data.get("image_url"),
        star_level=data.get("star_level"),
    )
    return jsonify({"product": product_to_dict(product)}), 200


@admin_products_bp.patch("/<int:product_id>/status")
@require_auth
@require_permission("manage_products")
def set_product_status(product_id):
    """Activate or deactivate a product."""
    data = request.get_json(silent=True) or {}
    active = data.get("is_active", data.get("active"))
    if active is None:
        raise ValidationError("Field 'is_active' is required.")
    product = _product_service().set_product_active(product_id, active)
    return jsonify({"product": product_to_dict(product)}), 200


@admin_products_bp.patch("/<int:product_id>/stock")
@require_auth
@require_permission("manage_products")
def update_product_stock(product_id):
    """Update product stock."""
    data = request.get_json(silent=True) or {}
    stock = data.get("stock_quantity", data.get("stock"))
    if stock is None:
        raise ValidationError("Field 'stock_quantity' is required.")
    product = _product_service().update_stock(product_id, stock)
    return jsonify({"product": product_to_dict(product)}), 200


@admin_products_bp.post("/<int:product_id>/image")
@require_auth
@require_permission("manage_products")
def upload_product_image(product_id):
    """Upload/replace the main product image."""
    file = request.files.get("image")
    if file is None or not file.filename:
        raise ValidationError("Image file is required.")
    image_storage = current_app.extensions["image_storage"]
    url = image_storage.save(file)
    product = _product_service().set_product_image(product_id, url, "main")
    return jsonify({"product": product_to_dict(product)}), 200


@admin_products_bp.post("/<int:product_id>/detail-image")
@require_auth
@require_permission("manage_products")
def upload_product_detail_image(product_id):
    """Upload/replace the product detail image."""
    file = request.files.get("image")
    if file is None or not file.filename:
        raise ValidationError("Image file is required.")
    image_storage = current_app.extensions["image_storage"]
    url = image_storage.save(file)
    product = _product_service().set_product_image(product_id, url, "detail")
    return jsonify({"product": product_to_dict(product)}), 200
