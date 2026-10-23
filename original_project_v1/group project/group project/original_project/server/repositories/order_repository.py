"""Persistence for orders and order items."""

from database.database import Database
from models import Order, OrderItem
from repositories._connections import connection_scope


class OrderRepository:
    """Persist and retrieve Order and OrderItem data.

    Historical orders are preserved: each order item stores a snapshot of the
    product name and unit price, so later product changes never affect old
    orders.
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    def create_order(self, order: Order, connection=None) -> Order:
        with connection_scope(self.db, connection) as conn:
            cursor = conn.execute(
                "INSERT INTO orders (user_id, customer_name, phone, pickup_date, "
                "pickup_time, payment_reference_type, payment_reference, "
                "total_amount, status, payment_status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    order.user_id,
                    order.customer_name,
                    order.phone,
                    order.pickup_date,
                    order.pickup_time,
                    order.payment_reference_type,
                    order.payment_reference,
                    order.total_amount,
                    order.status,
                    order.payment_status,
                ),
            )
            order.id = cursor.lastrowid
        return order

    def create_order_items(
        self, order_id: int, items: list[OrderItem], connection=None
    ) -> None:
        with connection_scope(self.db, connection) as conn:
            for item in items:
                cursor = conn.execute(
                    "INSERT INTO order_items (order_id, product_id, product_name, "
                    "unit_price, quantity, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        order_id,
                        item.product_id,
                        item.product_name,
                        item.unit_price,
                        item.quantity,
                        item.subtotal,
                    ),
                )
                item.id = cursor.lastrowid
                item.order_id = order_id

    def find_by_id(self, order_id: int, connection=None) -> Order | None:
        with connection_scope(self.db, connection) as conn:
            row = conn.execute(
                "SELECT * FROM orders WHERE id = ?", (order_id,)
            ).fetchone()
            if row is None:
                return None
            order = self._row_to_order(row)
            item_rows = conn.execute(
                "SELECT * FROM order_items WHERE order_id = ? ORDER BY id",
                (order_id,),
            ).fetchall()
            order.items = [self._row_to_order_item(r) for r in item_rows]
        return order

    def list_orders_for_user(self, user_id: int, connection=None) -> list[Order]:
        with connection_scope(self.db, connection) as conn:
            rows = conn.execute(
                "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            ).fetchall()
            orders = [self._row_to_order(row) for row in rows]
            self._attach_items(conn, orders)
        return orders

    def list_all_orders(self, connection=None) -> list[Order]:
        with connection_scope(self.db, connection) as conn:
            rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
            orders = [self._row_to_order(row) for row in rows]
            self._attach_items(conn, orders)
        return orders

    def _attach_items(self, conn, orders: list[Order]) -> None:
        """Attach each order's items with a single query (avoids N+1)."""
        if not orders:
            return
        order_ids = [order.id for order in orders]
        placeholders = ",".join("?" for _ in order_ids)
        item_rows = conn.execute(
            f"SELECT * FROM order_items WHERE order_id IN ({placeholders}) ORDER BY id",
            order_ids,
        ).fetchall()
        grouped: dict = {}
        for row in item_rows:
            grouped.setdefault(row["order_id"], []).append(self._row_to_order_item(row))
        for order in orders:
            order.items = grouped.get(order.id, [])

    def update_order_status(
        self, order_id: int, new_status: str, connection=None
    ) -> None:
        with connection_scope(self.db, connection) as conn:
            conn.execute(
                "UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id)
            )

    def update_payment_status(
        self, order_id: int, new_status: str, connection=None
    ) -> None:
        with connection_scope(self.db, connection) as conn:
            conn.execute(
                "UPDATE orders SET payment_status = ? WHERE id = ?",
                (new_status, order_id),
            )

    def _row_to_order(self, row) -> Order:
        keys = set(row.keys())
        order = Order(
            user_id=row["user_id"],
            customer_name=row["customer_name"],
            phone=row["phone"],
            pickup_date=row["pickup_date"],
            pickup_time=row["pickup_time"],
            payment_reference_type=row["payment_reference_type"],
            payment_reference=row["payment_reference"],
            status=row["status"],
            payment_status=row["payment_status"] if "payment_status" in keys else "pending",
            order_id=row["id"],
            total_amount=row["total_amount"],
        )
        order.created_at = row["created_at"]
        return order

    def _row_to_order_item(self, row) -> OrderItem:
        return OrderItem(
            product_id=row["product_id"],
            product_name=row["product_name"],
            unit_price=row["unit_price"],
            quantity=row["quantity"],
            item_id=row["id"],
            order_id=row["order_id"],
        )
