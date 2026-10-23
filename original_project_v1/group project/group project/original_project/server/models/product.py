"""Product domain model."""


class Product:
    """A bakery product available for pre-order."""

    def __init__(
        self,
        name: str,
        price: float,
        stock_quantity: int = 0,
        is_active: bool = True,
        description: str = "",
        category: str = "",
        vegetarian: bool = False,
        vegan: bool = False,
        ingredients: str = "",
        allergens: str = "",
        image_url: str = "",
        detail_image_url: str = "",
        star_level: int = 0,
        product_id: int | None = None,
    ) -> None:
        if price < 0:
            raise ValueError("Price cannot be negative.")
        if stock_quantity < 0:
            raise ValueError("Stock quantity cannot be negative.")
        if not self._is_valid_star_level(star_level):
            raise ValueError("Star level must be an integer between 0 and 5.")

        self.id = product_id
        self.name = name
        self.description = description
        self.price = float(price)
        self.category = category
        self.vegetarian = vegetarian
        self.vegan = vegan
        self.ingredients = ingredients
        self.allergens = allergens
        self.stock_quantity = stock_quantity
        self.is_active = is_active
        self.image_url = image_url
        self.detail_image_url = detail_image_url
        self.star_level = star_level
        self.created_at = None
        self.like_count = 0
        self.liked_by_current_user = False

    @staticmethod
    def _is_valid_star_level(level) -> bool:
        """Return True when ``level`` is an integer in the 0-5 range."""
        return not isinstance(level, bool) and isinstance(level, int) and 0 <= level <= 5

    def is_available(self) -> bool:
        """Return True when the product is active and still has stock."""
        return self.is_active and self.stock_quantity > 0

    def update_stock(self, new_quantity: int) -> None:
        """Set the stock quantity to a new non-negative value."""
        if new_quantity < 0:
            raise ValueError("Stock quantity cannot be negative.")
        self.stock_quantity = new_quantity

    def set_star_level(self, level: int) -> None:
        """Set the recommendation star level (0-5)."""
        if not self._is_valid_star_level(level):
            raise ValueError("Star level must be an integer between 0 and 5.")
        self.star_level = level

    def reduce_stock(self, quantity: int) -> None:
        """Reduce stock by the given quantity (used when an order is placed)."""
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        if quantity > self.stock_quantity:
            raise ValueError("Not enough stock available.")
        self.stock_quantity -= quantity
