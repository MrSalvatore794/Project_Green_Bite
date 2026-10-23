"""Order domain model."""

from .order_item import OrderItem


class Order:
    """A submitted customer order."""

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_PREPARING = "preparing"
    STATUS_READY_FOR_PICKUP = "ready_for_pickup"
    STATUS_COLLECTED = "collected"

    VALID_STATUSES = (
        STATUS_PENDING,
        STATUS_CONFIRMED,
        STATUS_PREPARING,
        STATUS_READY_FOR_PICKUP,
        STATUS_COLLECTED,
    )

    # Each status maps to the only status it is allowed to move to next.
    NEXT_STATUS = {
        STATUS_PENDING: STATUS_CONFIRMED,
        STATUS_CONFIRMED: STATUS_PREPARING,
        STATUS_PREPARING: STATUS_READY_FOR_PICKUP,
        STATUS_READY_FOR_PICKUP: STATUS_COLLECTED,
        STATUS_COLLECTED: None,
    }

    PAYMENT_PENDING = "pending"
    PAYMENT_COMPLETED = "completed"
    PAYMENT_FAILED = "failed"

    VALID_PAYMENT_STATUSES = (
        PAYMENT_PENDING,
        PAYMENT_COMPLETED,
        PAYMENT_FAILED,
    )

    # Each payment status maps to the set of statuses it may move to next.
    PAYMENT_NEXT = {
        PAYMENT_PENDING: (PAYMENT_COMPLETED, PAYMENT_FAILED),
        PAYMENT_FAILED: (PAYMENT_COMPLETED,),
        PAYMENT_COMPLETED: (),
    }

    def __init__(
        self,
        user_id: int,
        customer_name: str = "",
        phone: str = "",
        pickup_date: str = "",
        pickup_time: str = "",
        payment_reference_type: str = "",
        payment_reference: str = "",
        status: str = STATUS_PENDING,
        payment_status: str = PAYMENT_PENDING,
        order_id: int | None = None,
        total_amount: float | None = None,
    ) -> None:
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Unknown order status: {status!r}")
        if payment_status not in self.VALID_PAYMENT_STATUSES:
            raise ValueError(f"Unknown payment status: {payment_status!r}")

        self.id = order_id
        self.user_id = user_id
        self.customer_name = customer_name
        self.phone = phone
        self.pickup_date = pickup_date
        self.pickup_time = pickup_time
        self.payment_reference_type = payment_reference_type
        self.payment_reference = payment_reference
        self.status = status
        self.payment_status = payment_status
        self.total_amount = total_amount
        self.items: list[OrderItem] = []
        self.created_at = None

    def add_item(self, item: OrderItem) -> None:
        """Add an order item to the order."""
        self.items.append(item)

    def calculate_total(self) -> float:
        """Return the sum of all order item subtotals, rounded to cents."""
        return round(sum(item.subtotal for item in self.items), 2)

    def change_status(self, new_status: str) -> None:
        """Move the order to the next allowed status in the workflow."""
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Unknown order status: {new_status!r}")

        allowed_next = self.NEXT_STATUS[self.status]
        if new_status != allowed_next:
            raise ValueError(
                f"Invalid status transition: {self.status} -> {new_status}"
            )
        self.status = new_status

    def change_payment_status(self, new_status: str) -> None:
        """Move the order to an allowed payment status (manual Admin action)."""
        if new_status not in self.VALID_PAYMENT_STATUSES:
            raise ValueError(f"Unknown payment status: {new_status!r}")

        if new_status not in self.PAYMENT_NEXT[self.payment_status]:
            raise ValueError(
                f"Invalid payment status transition: "
                f"{self.payment_status} -> {new_status}"
            )
        self.payment_status = new_status
