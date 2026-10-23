"""Product business logic."""

from models import Product
from repositories.product_repository import ProductRepository
from services.exceptions import ProductNotFoundError, ValidationError


class ProductService:
    """Coordinate product operations and product business rules.

    Customer-facing methods only expose active, purchasable products. Admin
    methods (create/update/activate/deactivate/update stock) are separated so
    the route layer can enforce role checks before calling them.
    """

    def __init__(self, product_repository: ProductRepository) -> None:
        self.product_repository = product_repository

    # Customer-facing -------------------------------------------------------

    def get_active_products(self) -> list[Product]:
        """Return products that are available to customers (active and in stock)."""
        products = self.product_repository.list_active_products()
        return [product for product in products if product.is_available()]

    def get_product(self, product_id: int) -> Product:
        product = self.product_repository.find_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {product_id!r} does not exist.")
        return product

    def get_product_detail(self, product_id: int, current_user_id: int | None = None) -> Product:
        """Return a product with its like count and the current user's like state."""
        product = self.get_product(product_id)
        product.like_count = self.product_repository.count_likes(product_id)
        product.liked_by_current_user = (
            current_user_id is not None
            and self.product_repository.has_liked(current_user_id, product_id)
        )
        return product

    def like_product(self, user_id: int, product_id: int) -> tuple[bool, int]:
        """Like a product for a user (idempotent) and return ``(liked, count)``."""
        product = self.get_product(product_id)
        if not product.is_active:
            raise ProductNotFoundError(f"Product {product_id!r} does not exist.")
        self.product_repository.add_like(user_id, product_id)
        return True, self.product_repository.count_likes(product_id)

    def unlike_product(self, user_id: int, product_id: int) -> tuple[bool, int]:
        """Remove a user's like and return ``(liked, count)``."""
        self.get_product(product_id)
        self.product_repository.remove_like(user_id, product_id)
        return False, self.product_repository.count_likes(product_id)

    # Admin-facing ----------------------------------------------------------

    def get_all_products(self) -> list[Product]:
        """Return all products (including inactive and zero-stock ones)."""
        return self.product_repository.list_all_products()

    def create_product(
        self,
        name: str,
        price: float,
        stock_quantity: int = 0,
        description: str = "",
        category: str = "",
        vegetarian: bool = False,
        vegan: bool = False,
        ingredients: str = "",
        allergens: str = "",
        image_url: str = "",
        detail_image_url: str = "",
        star_level: int = 0,
    ) -> Product:
        if not name or not str(name).strip():
            raise ValidationError("Name is required.")
        if not isinstance(price, (int, float)) or isinstance(price, bool):
            raise ValidationError("Price must be a number.")
        if not isinstance(stock_quantity, int) or isinstance(stock_quantity, bool):
            raise ValidationError("Stock quantity must be an integer.")
        if isinstance(star_level, bool) or not isinstance(star_level, int):
            raise ValidationError("Star level must be an integer.")

        try:
            product = Product(
                name=name,
                price=price,
                stock_quantity=stock_quantity,
                is_active=True,
                description=description,
                category=category,
                vegetarian=vegetarian,
                vegan=vegan,
                ingredients=ingredients,
                allergens=allergens,
                image_url=image_url,
                detail_image_url=detail_image_url,
                star_level=star_level,
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return self.product_repository.create_product(product)

    def update_product(
        self,
        product_id: int,
        name: str | None = None,
        description: str | None = None,
        price: float | None = None,
        category: str | None = None,
        vegetarian: bool | None = None,
        vegan: bool | None = None,
        ingredients: str | None = None,
        allergens: str | None = None,
        image_url: str | None = None,
        detail_image_url: str | None = None,
        star_level: int | None = None,
    ) -> Product:
        """Update the given product fields (None means "leave unchanged")."""
        product = self.get_product(product_id)

        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price is not None:
            if not isinstance(price, (int, float)) or isinstance(price, bool):
                raise ValidationError("Price must be a number.")
            if price < 0:
                raise ValidationError("Price cannot be negative.")
            product.price = float(price)
        if category is not None:
            product.category = category
        if vegetarian is not None:
            product.vegetarian = vegetarian
        if vegan is not None:
            product.vegan = vegan
        if ingredients is not None:
            product.ingredients = ingredients
        if allergens is not None:
            product.allergens = allergens
        if image_url is not None:
            product.image_url = image_url
        if detail_image_url is not None:
            product.detail_image_url = detail_image_url
        if star_level is not None:
            try:
                product.set_star_level(star_level)
            except ValueError as exc:
                raise ValidationError(str(exc)) from exc

        return self.product_repository.update_product(product)

    def set_product_image(self, product_id: int, image_url: str, kind: str) -> Product:
        """Set the main (or detail) image URL for a product."""
        product = self.get_product(product_id)
        if kind == "detail":
            product.detail_image_url = image_url
        else:
            product.image_url = image_url
        return self.product_repository.update_product(product)

    def set_product_active(self, product_id: int, active: bool) -> Product:
        product = self.get_product(product_id)
        if not isinstance(active, bool):
            raise ValidationError("active must be a boolean.")
        product.is_active = active
        return self.product_repository.update_product(product)

    def update_stock(self, product_id: int, new_quantity: int) -> Product:
        product = self.get_product(product_id)
        if not isinstance(new_quantity, int) or isinstance(new_quantity, bool):
            raise ValidationError("Stock quantity must be an integer.")
        try:
            product.update_stock(new_quantity)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        self.product_repository.update_stock(product_id, new_quantity)
        return product
