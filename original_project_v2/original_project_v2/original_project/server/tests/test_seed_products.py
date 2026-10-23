"""Tests for the product seed script."""

from scripts.seed_products import PRODUCTS, seed


def test_seed_creates_expected_products(product_service):
    created, skipped = seed(product_service)
    assert created == len(PRODUCTS)
    assert skipped == 0
    assert len(product_service.get_all_products()) == len(PRODUCTS)


def test_seed_is_idempotent(product_service):
    seed(product_service)
    created, skipped = seed(product_service)
    assert created == 0
    assert skipped == len(PRODUCTS)
    assert len(product_service.get_all_products()) == len(PRODUCTS)


def test_seeded_products_have_valid_prices(product_service):
    seed(product_service)
    for product in product_service.get_all_products():
        assert product.price >= 0


def test_seeded_products_have_valid_stock(product_service):
    seed(product_service)
    for product in product_service.get_all_products():
        assert isinstance(product.stock_quantity, int)
        assert product.stock_quantity >= 0


def test_seeded_products_are_active(product_service):
    seed(product_service)
    for product in product_service.get_all_products():
        assert product.is_active is True


def test_seeded_products_returned_by_customer_endpoint(client, app):
    seed(app.extensions["product_service"])
    response = client.get("/api/v1/products")  # public, no JWT
    assert response.status_code == 200
    assert len(response.get_json()["products"]) == len(PRODUCTS)
