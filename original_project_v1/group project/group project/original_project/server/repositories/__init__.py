"""Repository layer.

Repositories hide SQLite persistence details from the Service layer. Each
repository maps database rows into domain model objects, so Services work with
``User``, ``Product``, ``Cart``, and ``Order`` objects instead of SQL rows.
"""

from .cart_repository import CartRepository
from .order_repository import OrderRepository
from .product_repository import ProductRepository
from .user_repository import UserRepository

__all__ = [
    "UserRepository",
    "ProductRepository",
    "CartRepository",
    "OrderRepository",
]

