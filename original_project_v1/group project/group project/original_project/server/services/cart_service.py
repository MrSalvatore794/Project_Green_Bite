"""Cart business logic."""

from models import Cart, Product
from repositories.cart_repository import CartRepository
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository
from services.exceptions import (
    InsufficientStockError,
    ProductNotFoundError,
    ProductUnavailableError,
    UserNotFoundError,
    ValidationError,
)


class CartService:
    """Coordinate cart operations and validate product/quantity rules.

    The repository only persists data; this service decides whether an
    operation is allowed (product exists, active, has enough stock, etc.).
    """

    def __init__(
        self,
        cart_repository: CartRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository,
    ) -> None:
        self.cart_repository = cart_repository
        self.product_repository = product_repository
        self.user_repository = user_repository

    def get_cart(self, user_id: int) -> Cart:
        self._ensure_user_exists(user_id)
        cart = self.cart_repository.find_cart_by_user(user_id)
        if cart is None:
            cart = self.cart_repository.create_cart(user_id)
        return cart

    def add_item(self, user_id: int, product_id: int, quantity: int) -> Cart:
        self._validate_quantity(quantity)
        product = self._get_product(product_id)
        if not product.is_available():
            raise ProductUnavailableError(
                f"Product {product.name!r} is not available for purchase."
            )

        cart = self.get_cart(user_id)
        existing = self._find_item(cart, product_id)
        current_quantity = existing.quantity if existing else 0
        new_quantity = current_quantity + quantity

        if new_quantity > product.stock_quantity:
            raise InsufficientStockError(
                f"Only {product.stock_quantity} unit(s) of {product.name!r} available."
            )

        if existing is not None:
            self.cart_repository.update_cart_item_quantity(
                cart.id, product_id, new_quantity
            )
        else:
            self.cart_repository.add_cart_item(cart.id, product_id, quantity)

        return self.get_cart(user_id)

    def update_quantity(self, user_id: int, product_id: int, quantity: int) -> Cart:
        self._validate_quantity(quantity)
        product = self._get_product(product_id)

        cart = self.get_cart(user_id)
        if self._find_item(cart, product_id) is None:
            raise ProductNotFoundError("Product is not in the cart.")

        if quantity > product.stock_quantity:
            raise InsufficientStockError(
                f"Only {product.stock_quantity} unit(s) of {product.name!r} available."
            )

        self.cart_repository.update_cart_item_quantity(cart.id, product_id, quantity)
        return self.get_cart(user_id)

    def remove_item(self, user_id: int, product_id: int) -> Cart:
        cart = self.get_cart(user_id)
        self.cart_repository.remove_cart_item(cart.id, product_id)
        return self.get_cart(user_id)

    def clear_cart(self, user_id: int) -> Cart:
        cart = self.get_cart(user_id)
        self.cart_repository.clear_cart(cart.id)
        return self.get_cart(user_id)

    def calculate_total(self, user_id: int) -> float:
        return self.get_cart(user_id).calculate_total()

    # Internal helpers ------------------------------------------------------

    def _ensure_user_exists(self, user_id: int) -> None:
        if self.user_repository.find_by_id(user_id) is None:
            raise UserNotFoundError(f"User {user_id!r} does not exist.")

    def _get_product(self, product_id: int) -> Product:
        product = self.product_repository.find_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {product_id!r} does not exist.")
        return product

    def _validate_quantity(self, quantity) -> None:
        if quantity is None or quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")

    def _find_item(self, cart: Cart, product_id: int):
        for item in cart.items:
            if item.product_id == product_id:
                return item
        return None
