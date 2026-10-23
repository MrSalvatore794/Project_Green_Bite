"""Order business logic."""

from database.database import Database
from models import Order, OrderItem
from repositories.cart_repository import CartRepository
from repositories.order_repository import OrderRepository
from repositories.product_repository import ProductRepository
from services.exceptions import (
    CartEmptyError,
    InsufficientStockError,
    InvalidOrderStatusError,
    OrderNotFoundError,
    ProductUnavailableError,
    ValidationError,
)


class OrderService:
    """Coordinate order creation, stock validation, and order lifecycle."""

    def __init__(
        self,
        order_repository: OrderRepository,
        cart_repository: CartRepository,
        product_repository: ProductRepository,
        db: Database,
    ) -> None:
        self.order_repository = order_repository
        self.cart_repository = cart_repository
        self.product_repository = product_repository
        self.db = db

    def create_order(
        self,
        user_id: int,
        customer_name: str,
        phone: str,
        pickup_date: str,
        pickup_time: str,
        payment_reference_type: str,
        payment_reference: str,
    ) -> Order:
        """Create an order from the customer's cart in one transaction."""
        self._validate_checkout(
            customer_name, phone, pickup_date, pickup_time,
            payment_reference_type, payment_reference,
        )

        with self.db.connection() as conn:
            cart = self.cart_repository.find_cart_by_user(user_id, connection=conn)
            if cart is None or not cart.items:
                raise CartEmptyError("Cannot create an order from an empty cart.")

            order_items = []
            products = {}
            for item in cart.items:
                product = self.product_repository.find_by_id(
                    item.product_id, connection=conn
                )
                if product is None or not product.is_active:
                    raise ProductUnavailableError(
                        f"Product {item.product_id} is no longer available."
                    )
                if item.quantity > product.stock_quantity:
                    raise InsufficientStockError(
                        f"Not enough stock for {product.name!r}: "
                        f"requested {item.quantity}, available {product.stock_quantity}."
                    )

                products[product.id] = product
                order_items.append(
                    OrderItem(
                        product_id=product.id,
                        product_name=product.name,
                        unit_price=product.price,
                        quantity=item.quantity,
                    )
                )

            order = Order(
                user_id=user_id,
                customer_name=customer_name,
                phone=phone,
                pickup_date=pickup_date,
                pickup_time=pickup_time,
                payment_reference_type=payment_reference_type,
                payment_reference=payment_reference,
                status=Order.STATUS_PENDING,
            )
            for item in order_items:
                order.add_item(item)
            order.total_amount = order.calculate_total()

            self.order_repository.create_order(order, connection=conn)
            self.order_repository.create_order_items(order.id, order.items, connection=conn)

            for item in order.items:
                product = products[item.product_id]
                product.reduce_stock(item.quantity)
                self.product_repository.update_stock(
                    product.id, product.stock_quantity, connection=conn
                )

            self.cart_repository.clear_cart(cart.id, connection=conn)

        return order

    def get_user_orders(self, user_id: int) -> list[Order]:
        return self.order_repository.list_orders_for_user(user_id)

    def get_order(self, order_id: int, user_id: int) -> Order:
        """Return an order that belongs to the given user.

        Returns 404 (not 403) for another user's order so the order's
        existence is not revealed to unrelated customers.
        """
        order = self.order_repository.find_by_id(order_id)
        if order is None or order.user_id != user_id:
            raise OrderNotFoundError(f"Order {order_id!r} does not exist.")
        return order

    def get_order_admin(self, order_id: int) -> Order:
        """Return any order by id (admin use)."""
        order = self.order_repository.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id!r} does not exist.")
        return order

    def get_all_orders(self) -> list[Order]:
        return self.order_repository.list_all_orders()

    def update_order_status(self, order_id: int, new_status: str) -> Order:
        order = self.order_repository.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id!r} does not exist.")
        try:
            order.change_status(new_status)
        except ValueError as exc:
            raise InvalidOrderStatusError(str(exc)) from exc
        self.order_repository.update_order_status(order_id, new_status)
        return order

    def update_payment_status(self, order_id: int, new_status: str) -> Order:
        """Manually update an order's payment status (Admin action)."""
        order = self.order_repository.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id!r} does not exist.")
        try:
            order.change_payment_status(new_status)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        self.order_repository.update_payment_status(order_id, new_status)
        return order

    def _validate_checkout(
        self,
        customer_name,
        phone,
        pickup_date,
        pickup_time,
        payment_reference_type,
        payment_reference,
    ) -> None:
        required = {
            "customer_name": customer_name,
            "phone": phone,
            "pickup_date": pickup_date,
            "pickup_time": pickup_time,
            "payment_reference_type": payment_reference_type,
            "payment_reference": payment_reference,
        }
        missing = [
            field for field, value in required.items()
            if value is None or str(value).strip() == ""
        ]
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))
