"""Order item domain model."""


class OrderItem:
    """A snapshot of one product line purchased in an order.

    Unlike ``CartItem``, this stores copies of the product name and unit price
    at the time of purchase, so later Product changes never affect old orders.
    """

    def __init__(
        self,
        product_id: int,
        product_name: str,
        unit_price: float,
        quantity: int,
        item_id: int | None = None,
        order_id: int | None = None,
    ) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if unit_price < 0:
            raise ValueError("Unit price cannot be negative.")

        self.id = item_id
        self.order_id = order_id
        self.product_id = product_id
        self.product_name = product_name
        self.unit_price = float(unit_price)
        self.quantity = quantity
        self.subtotal = self.calculate_subtotal()

    def calculate_subtotal(self) -> float:
        """Return unit price multiplied by quantity, rounded to cents."""
        return round(self.unit_price * self.quantity, 2)
