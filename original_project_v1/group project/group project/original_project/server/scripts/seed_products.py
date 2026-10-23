"""Seed the initial GreenBite product catalog (idempotent).

Usage (run from the ``server`` directory):

    python scripts/seed_products.py

The script detects existing products by name and skips them, so it is safe to
run multiple times without creating duplicates or overwriting admin edits.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config  # noqa: E402
from database.database import Database  # noqa: E402
from repositories.product_repository import ProductRepository  # noqa: E402
from services.product_service import ProductService  # noqa: E402

PRODUCTS = [
    {
        "name": "Matcha Mousse Cake — 8-inch",
        "price": 50.00,
        "stock_quantity": 8,
        "description": "8-inch vegan matcha mousse cake.",
        "category": "cake",
        "ingredients": "biscuit, oat milk, coconut oil, cashew, coconut milk, sugar, salt, matcha",
        "allergens": "cashew",
        "image_url": "/images/products/matcha-mousse-cake.jpg",
    },
    {
        "name": "Matcha Mousse Cake — 8-inch with Cake Box Set",
        "price": 55.00,
        "stock_quantity": 5,
        "description": "8-inch vegan matcha mousse cake with a cake box set.",
        "category": "cake",
        "ingredients": "biscuit, oat milk, coconut oil, cashew, coconut milk, sugar, salt, matcha",
        "allergens": "cashew",
        "image_url": "/images/products/matcha-mousse-cake.jpg",
    },
    {
        "name": "Fresh Toast — 250g",
        "price": 5.50,
        "stock_quantity": 20,
        "description": "Vegan fresh toast, 250g.",
        "category": "bread",
        "ingredients": "",
        "allergens": "",
        "image_url": "/images/products/fresh-toast.jpg",
    },
    {
        "name": "Fresh Toast — 500g",
        "price": 11.00,
        "stock_quantity": 15,
        "description": "Vegan fresh toast, 500g.",
        "category": "bread",
        "ingredients": "",
        "allergens": "",
        "image_url": "/images/products/fresh-toast.jpg",
    },
    {
        "name": "Vegan Meat Floss Bun",
        "price": 2.50,
        "stock_quantity": 25,
        "description": "Vegan bun topped with meat floss.",
        "category": "bun",
        "ingredients": "",
        "allergens": "",
        "image_url": "/images/products/meat-floss-bun.jpg",
    },
    {
        "name": "Chocolate Toast — 250g",
        "price": 7.50,
        "stock_quantity": 20,
        "description": "Chocolate toast, 250g. Room temperature 3-5 days; frozen 30 days.",
        "category": "bread",
        "ingredients": "wheat flour, yeast, fine sugar, coconut powder, soy milk powder, vegan butter, salt, cocoa, chocolate chips",
        "allergens": "wheat, soy",
        "image_url": "/images/products/chocolate-toast.jpg",
    },
    {
        "name": "Chocolate Toast — 500g",
        "price": 15.00,
        "stock_quantity": 15,
        "description": "Chocolate toast, 500g. Room temperature 3-5 days; frozen 30 days.",
        "category": "bread",
        "ingredients": "wheat flour, yeast, fine sugar, coconut powder, soy milk powder, vegan butter, salt, cocoa, chocolate chips",
        "allergens": "wheat, soy",
        "image_url": "/images/products/chocolate-toast.jpg",
    },
    {
        "name": "Chestnut Toast — 250g",
        "price": 7.50,
        "stock_quantity": 20,
        "description": "Chestnut toast, 250g.",
        "category": "bread",
        "ingredients": "",
        "allergens": "",
        "image_url": "/images/products/chestnut-toast.jpg",
    },
    {
        "name": "Chestnut Toast — 500g",
        "price": 15.00,
        "stock_quantity": 15,
        "description": "Chestnut toast, 500g.",
        "category": "bread",
        "ingredients": "",
        "allergens": "",
        "image_url": "/images/products/chestnut-toast.jpg",
    },
    {
        "name": "Cranberry Cookies — 200g",
        "price": 8.00,
        "stock_quantity": 20,
        "description": "Cranberry cookies, approximately 200g (approximately 16 pieces). Room temperature 30 days.",
        "category": "cookie",
        "ingredients": "",
        "allergens": "",
        "image_url": "/images/products/cranberry-cookie.jpg",
    },
    {
        "name": "Chinese Mantou — 4 pieces",
        "price": 5.00,
        "stock_quantity": 25,
        "description": "Chinese steamed mantou, 4 pieces.",
        "category": "bun",
        "ingredients": "",
        "allergens": "",
        "image_url": "/images/products/steamed-bun.jpg",
    },
    {
        "name": "Vegan Meat Bun — 3 pieces",
        "price": 5.00,
        "stock_quantity": 25,
        "description": "Vegan meat bun, 3 pieces.",
        "category": "bun",
        "ingredients": "",
        "allergens": "",
        "image_url": "/images/products/vegetarian-meat-bun.jpg",
    },
    {
        "name": "Sea Salt Roll",
        "price": 2.50,
        "stock_quantity": 30,
        "description": "Sea salt roll.",
        "category": "bread",
        "ingredients": "",
        "allergens": "",
        "image_url": "/images/products/sea-salt-roll.jpg",
    },
    {
        "name": "Palmier — 200g",
        "price": 8.00,
        "stock_quantity": 20,
        "description": "Palmier, 200g.",
        "category": "pastry",
        "ingredients": "",
        "allergens": "",
        "image_url": "/images/products/palmier.jpg",
    },
    {
        "name": "Walnut Raisin Country Bread",
        "price": 4.50,
        "stock_quantity": 15,
        "description": "Walnut raisin country bread. Pre-bake approximately 180g; post-bake approximately 170g.",
        "category": "bread",
        "ingredients": "",
        "allergens": "walnut",
        "image_url": "/images/products/walnut-raisin-bread.jpg",
    },
    {
        "name": "Red Bean Pineapple Bun",
        "price": 2.50,
        "stock_quantity": 25,
        "description": "Red bean pineapple bun.",
        "category": "bun",
        "ingredients": "",
        "allergens": "",
        "image_url": "/images/products/red-bean-pineapple-bun.jpg",
    },
]


def seed(service: ProductService) -> tuple[int, int]:
    """Seed products, skipping any whose name already exists.

    Returns ``(created, skipped)``.
    """
    existing = {product.name for product in service.get_all_products()}
    created = 0
    skipped = 0
    for data in PRODUCTS:
        if data["name"] in existing:
            skipped += 1
            continue
        service.create_product(
            name=data["name"],
            price=data["price"],
            stock_quantity=data["stock_quantity"],
            description=data["description"],
            category=data["category"],
            vegetarian=True,
            vegan=True,
            ingredients=data["ingredients"],
            allergens=data["allergens"],
            image_url=data["image_url"],
        )
        created += 1
    return created, skipped


def main() -> None:
    db = Database(Config.DATABASE_PATH)
    db.initialize()
    service = ProductService(ProductRepository(db))
    created, skipped = seed(service)
    print(f"Seed complete: {created} created, {skipped} skipped.")


if __name__ == "__main__":
    main()

