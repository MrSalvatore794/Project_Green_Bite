"""Tests for ProductService."""

import pytest

from services.exceptions import ProductNotFoundError, ValidationError


def test_create_product(product_service):
    product = product_service.create_product("Walnut Bread", 11.0, stock_quantity=8)
    assert product.id is not None
    assert product.is_active is True


def test_get_product(product_service):
    created = product_service.create_product("Walnut Bread", 11.0, stock_quantity=8)
    found = product_service.get_product(created.id)
    assert found.name == "Walnut Bread"
    assert found.price == 11.0


def test_get_product_not_found(product_service):
    with pytest.raises(ProductNotFoundError):
        product_service.get_product(9999)


def test_list_active_products(product_service):
    product_service.create_product("Bread", 11.0, stock_quantity=8)
    product_service.create_product("Cake", 12.0, stock_quantity=4)
    inactive = product_service.create_product("Muffin", 5.0, stock_quantity=3)
    product_service.set_product_active(inactive.id, False)

    active = product_service.get_active_products()
    assert {p.name for p in active} == {"Bread", "Cake"}


def test_inactive_product_not_returned(product_service):
    product = product_service.create_product("Muffin", 5.0, stock_quantity=3)
    product_service.set_product_active(product.id, False)
    assert product_service.get_active_products() == []


def test_update_product(product_service):
    product = product_service.create_product("Bread", 11.0, stock_quantity=8)
    updated = product_service.update_product(product.id, name="Sourdough", price=13.0)
    assert updated.name == "Sourdough"
    assert updated.price == 13.0


def test_activate_and_deactivate(product_service):
    product = product_service.create_product("Bread", 11.0, stock_quantity=8)
    product_service.set_product_active(product.id, False)
    assert product_service.get_product(product.id).is_active is False
    product_service.set_product_active(product.id, True)
    assert product_service.get_product(product.id).is_active is True


def test_update_stock(product_service):
    product = product_service.create_product("Bread", 11.0, stock_quantity=8)
    updated = product_service.update_stock(product.id, 15)
    assert updated.stock_quantity == 15


def test_update_stock_negative_rejected(product_service):
    product = product_service.create_product("Bread", 11.0, stock_quantity=8)
    with pytest.raises(ValidationError):
        product_service.update_stock(product.id, -1)


def test_create_product_negative_price_rejected(product_service):
    with pytest.raises(ValidationError):
        product_service.create_product("Bad", -5.0, stock_quantity=8)
