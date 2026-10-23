"""Cart item domain model."""

from .product import Product


class CartItem:
    """A single product line inside a shopping cart.

    Holds a live ``Product`` reference so the subtotal always reflects the
    product's current price while it is still in the cart.
    """

    def __init__(
        self,
        product: Product,
        quantity: int,
        item_id: int | None = None,
        cart_id: int | None = None,
    ) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        self.id = item_id
        self.cart_id = cart_id
        self.product = product
        self.quantity = quantity

    @property
    def product_id(self) -> int | None:
        return self.product.id

    def calculate_subtotal(self) -> float:
        """Return unit price multiplied by quantity, rounded to cents."""
        return round(self.product.price * self.quantity, 2)
