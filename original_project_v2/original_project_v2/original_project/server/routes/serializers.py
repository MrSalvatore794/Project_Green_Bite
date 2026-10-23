"""Serialization helpers for converting domain objects to JSON-safe dicts."""


def user_to_dict(user) -> dict:
    """Convert a User (Customer/Admin) to a dict, excluding password_hash."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "created_at": user.created_at,
    }


def product_to_dict(product) -> dict:
    """Convert a Product to a JSON-safe dict."""
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category": product.category,
        "vegetarian": product.vegetarian,
        "vegan": product.vegan,
        "ingredients": product.ingredients,
        "allergens": product.allergens,
        "stock_quantity": product.stock_quantity,
        "is_active": product.is_active,
        "image_url": product.image_url,
        "detail_image_url": product.detail_image_url,
        "star_level": product.star_level,
    }


def product_detail_to_dict(product) -> dict:
    """Convert a Product to a JSON-safe dict including like metadata."""
    data = product_to_dict(product)
    data["like_count"] = getattr(product, "like_count", 0)
    data["liked_by_current_user"] = getattr(product, "liked_by_current_user", False)
    return data


def cart_item_to_dict(item) -> dict:
    """Convert a CartItem to a JSON-safe dict using the live product price."""
    return {
        "product_id": item.product_id,
        "product_name": item.product.name,
        "unit_price": item.product.price,
        "quantity": item.quantity,
        "subtotal": item.calculate_subtotal(),
        "image_url": item.product.image_url,
        "stock_quantity": item.product.stock_quantity,
    }


def cart_to_dict(cart) -> dict:
    """Convert a Cart (with its items) to a JSON-safe dict."""
    return {
        "items": [cart_item_to_dict(item) for item in cart.items],
        "total": cart.calculate_total(),
    }


def order_item_to_dict(item) -> dict:
    """Convert an OrderItem to a JSON-safe dict using its stored snapshot."""
    return {
        "product_id": item.product_id,
        "product_name": item.product_name,
        "unit_price": item.unit_price,
        "quantity": item.quantity,
        "subtotal": item.subtotal,
    }


def order_to_dict(order) -> dict:
    """Convert an Order (with its items) to a JSON-safe dict."""
    return {
        "id": order.id,
        "customer_name": order.customer_name,
        "phone": order.phone,
        "pickup_date": order.pickup_date,
        "pickup_time": order.pickup_time,
        "payment_reference_type": order.payment_reference_type,
        "payment_reference": order.payment_reference,
        "total_amount": order.total_amount,
        "status": order.status,
        "payment_status": order.payment_status,
        "canceled_at": order.canceled_at,
        "items": [order_item_to_dict(item) for item in order.items],
    }


def order_summary_to_dict(order) -> dict:
    """Convert an Order to a short summary dict (includes a lightweight item list)."""
    return {
        "id": order.id,
        "user_id": order.user_id,
        "customer_name": order.customer_name,
        "phone": order.phone,
        "total_amount": order.total_amount,
        "pickup_date": order.pickup_date,
        "pickup_time": order.pickup_time,
        "payment_reference": order.payment_reference,
        "status": order.status,
        "payment_status": order.payment_status,
        "canceled_at": order.canceled_at,
        "created_at": order.created_at,
        "items": [order_item_to_dict(item) for item in order.items],
    }

