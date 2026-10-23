"""Persistence for products."""

from database.database import Database
from models import Product
from repositories._connections import connection_scope


def product_from_row(row) -> Product:
    """Map a products-table row (or an alias-matching row) to a Product."""
    keys = set(row.keys())
    product = Product(
        name=row["name"],
        price=row["price"],
        stock_quantity=row["stock_quantity"],
        is_active=bool(row["is_active"]),
        description=row["description"],
        category=row["category"],
        vegetarian=bool(row["vegetarian"]),
        vegan=bool(row["vegan"]),
        ingredients=row["ingredients"],
        allergens=row["allergens"],
        image_url=row["image_url"],
        detail_image_url=row["detail_image_url"] if "detail_image_url" in keys else "",
        star_level=row["star_level"] if "star_level" in keys else 0,
        product_id=row["id"],
    )
    product.created_at = row["created_at"]
    return product


class ProductRepository:
    """Persist and retrieve Product data.

    This class only performs SQLite persistence. Product business rules
    (availability, stock validation) belong to ProductService.
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    def create_product(self, product: Product, connection=None) -> Product:
        with connection_scope(self.db, connection) as conn:
            cursor = conn.execute(
                "INSERT INTO products (name, description, price, category, "
                "vegetarian, vegan, ingredients, allergens, stock_quantity, "
                "is_active, image_url, detail_image_url, star_level) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    product.name,
                    product.description,
                    product.price,
                    product.category,
                    int(product.vegetarian),
                    int(product.vegan),
                    product.ingredients,
                    product.allergens,
                    product.stock_quantity,
                    int(product.is_active),
                    product.image_url,
                    product.detail_image_url,
                    product.star_level,
                ),
            )
            product.id = cursor.lastrowid
        return product

    def find_by_id(self, product_id: int, connection=None) -> Product | None:
        with connection_scope(self.db, connection) as conn:
            row = conn.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()
        return product_from_row(row) if row is not None else None

    def list_active_products(self, connection=None) -> list[Product]:
        with connection_scope(self.db, connection) as conn:
            rows = conn.execute(
                "SELECT * FROM products WHERE is_active = 1 "
                "ORDER BY star_level DESC, id"
            ).fetchall()
        return [product_from_row(row) for row in rows]

    def list_all_products(self, connection=None) -> list[Product]:
        with connection_scope(self.db, connection) as conn:
            rows = conn.execute(
                "SELECT * FROM products "
                "ORDER BY is_active DESC, star_level DESC, id"
            ).fetchall()
        return [product_from_row(row) for row in rows]

    def update_product(self, product: Product, connection=None) -> Product:
        with connection_scope(self.db, connection) as conn:
            conn.execute(
                "UPDATE products SET name = ?, description = ?, price = ?, "
                "category = ?, vegetarian = ?, vegan = ?, ingredients = ?, "
                "allergens = ?, stock_quantity = ?, is_active = ?, image_url = ?, "
                "detail_image_url = ?, star_level = ? "
                "WHERE id = ?",
                (
                    product.name,
                    product.description,
                    product.price,
                    product.category,
                    int(product.vegetarian),
                    int(product.vegan),
                    product.ingredients,
                    product.allergens,
                    product.stock_quantity,
                    int(product.is_active),
                    product.image_url,
                    product.detail_image_url,
                    product.star_level,
                    product.id,
                ),
            )
        return product

    def update_stock(
        self, product_id: int, new_quantity: int, connection=None
    ) -> None:
        with connection_scope(self.db, connection) as conn:
            conn.execute(
                "UPDATE products SET stock_quantity = ? WHERE id = ?",
                (new_quantity, product_id),
            )

    # Likes ----------------------------------------------------------------

    def add_like(self, user_id: int, product_id: int, connection=None) -> None:
        """Record a like; the UNIQUE constraint makes this idempotent."""
        with connection_scope(self.db, connection) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO product_likes (user_id, product_id) "
                "VALUES (?, ?)",
                (user_id, product_id),
            )

    def remove_like(self, user_id: int, product_id: int, connection=None) -> None:
        with connection_scope(self.db, connection) as conn:
            conn.execute(
                "DELETE FROM product_likes WHERE user_id = ? AND product_id = ?",
                (user_id, product_id),
            )

    def count_likes(self, product_id: int, connection=None) -> int:
        with connection_scope(self.db, connection) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM product_likes WHERE product_id = ?",
                (product_id,),
            ).fetchone()
        return int(row[0]) if row is not None else 0

    def has_liked(self, user_id: int, product_id: int, connection=None) -> bool:
        with connection_scope(self.db, connection) as conn:
            row = conn.execute(
                "SELECT 1 FROM product_likes WHERE user_id = ? AND product_id = ?",
                (user_id, product_id),
            ).fetchone()
        return row is not None
