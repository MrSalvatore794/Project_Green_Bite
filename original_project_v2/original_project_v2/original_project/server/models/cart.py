"""Shopping cart domain model."""

from .cart_item import CartItem


class Cart:
    """The current shopping cart belonging to a single customer."""

    def __init__(self, user_id: int, cart_id: int | None = None) -> None:
        self.id = cart_id
        self.user_id = user_id
        self.items: list[CartItem] = []

    def _find_item(self, product_id: int) -> CartItem | None:
        for item in self.items:
            if item.product_id == product_id:
                return item
        return None

    def add_item(self, product, quantity: int = 1) -> None:
        """Add a product, merging the quantity if it is already in the cart."""
        new_item = CartItem(product, quantity)  # validates quantity > 0
        existing = self._find_item(product.id)
        if existing is not None:
            existing.quantity += new_item.quantity
        else:
            self.items.append(new_item)

    def update_item(self, product_id: int, quantity: int) -> None:
        """Set the quantity of an existing cart item."""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        item = self._find_item(product_id)
        if item is None:
            raise ValueError("Product is not in the cart.")
        item.quantity = quantity

    def remove_item(self, product_id: int) -> None:
        """Remove a product from the cart."""
        item = self._find_item(product_id)
        if item is None:
            raise ValueError("Product is not in the cart.")
        self.items.remove(item)

    def calculate_total(self) -> float:
        """Return the sum of all item subtotals, rounded to cents."""
        return round(sum(item.calculate_subtotal() for item in self.items), 2)

    def clear(self) -> None:
        """Remove all items from the cart."""
        self.items = []
