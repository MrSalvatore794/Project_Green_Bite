"""Persistence for carts and cart items."""

from database.database import Database
from models import Cart, CartItem
from repositories._connections import connection_scope
from repositories.product_repository import product_from_row


class CartRepository:
    """Persist and retrieve Cart and CartItem data.

    This class only performs SQLite persistence. Deciding whether a product is
    available (or how many can be added) belongs to CartService / ProductService.
    """

    _ITEM_SELECT = """
        SELECT
            ci.id             AS item_id,
            ci.cart_id        AS cart_id,
            ci.quantity       AS quantity,
            p.id              AS id,
            p.name            AS name,
            p.description     AS description,
            p.price           AS price,
            p.category        AS category,
            p.vegetarian      AS vegetarian,
            p.vegan           AS vegan,
            p.ingredients     AS ingredients,
            p.allergens       AS allergens,
            p.stock_quantity  AS stock_quantity,
            p.is_active       AS is_active,
            p.image_url       AS image_url,
            p.created_at      AS created_at
        FROM cart_items ci
        JOIN products p ON p.id = ci.product_id
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    def create_cart(self, user_id: int, connection=None) -> Cart:
        with connection_scope(self.db, connection) as conn:
            cursor = conn.execute(
                "INSERT INTO carts (user_id) VALUES (?)", (user_id,)
            )
            cart_id = cursor.lastrowid
        return Cart(user_id=user_id, cart_id=cart_id)

    def find_cart_by_user(self, user_id: int, connection=None) -> Cart | None:
        with connection_scope(self.db, connection) as conn:
            row = conn.execute(
                "SELECT id, user_id FROM carts WHERE user_id = ?", (user_id,)
            ).fetchone()
            if row is None:
                return None
            cart = Cart(user_id=row["user_id"], cart_id=row["id"])
            cart.items = self._get_cart_items(conn, row["id"])
        return cart

    def get_cart_items(self, cart_id: int, connection=None) -> list[CartItem]:
        with connection_scope(self.db, connection) as conn:
            return self._get_cart_items(conn, cart_id)

    def add_cart_item(
        self, cart_id: int, product_id: int, quantity: int, connection=None
    ) -> None:
        with connection_scope(self.db, connection) as conn:
            conn.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) "
                "VALUES (?, ?, ?)",
                (cart_id, product_id, quantity),
            )

    def update_cart_item_quantity(
        self, cart_id: int, product_id: int, quantity: int, connection=None
    ) -> None:
        with connection_scope(self.db, connection) as conn:
            conn.execute(
                "UPDATE cart_items SET quantity = ? "
                "WHERE cart_id = ? AND product_id = ?",
                (quantity, cart_id, product_id),
            )

    def remove_cart_item(
        self, cart_id: int, product_id: int, connection=None
    ) -> None:
        with connection_scope(self.db, connection) as conn:
            conn.execute(
                "DELETE FROM cart_items WHERE cart_id = ? AND product_id = ?",
                (cart_id, product_id),
            )

    def clear_cart(self, cart_id: int, connection=None) -> None:
        with connection_scope(self.db, connection) as conn:
            conn.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))

    def _get_cart_items(self, conn, cart_id: int) -> list[CartItem]:
        rows = conn.execute(
            self._ITEM_SELECT + " WHERE ci.cart_id = ? ORDER BY ci.id",
            (cart_id,),
        ).fetchall()
        return [self._row_to_cart_item(row) for row in rows]

    def _row_to_cart_item(self, row) -> CartItem:
        return CartItem(
            product=product_from_row(row),
            quantity=row["quantity"],
            item_id=row["item_id"],
            cart_id=row["cart_id"],
        )
