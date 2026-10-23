"""Tests for the SQLite schema and database initialization."""

import sqlite3

import pytest

from database.database import Database


@pytest.fixture
def db(tmp_path):
    """A freshly initialised database stored in a temporary file."""
    database = Database(str(tmp_path / "greenbite_test.db"))
    database.initialize()
    return database


def test_fresh_database_can_be_initialised(tmp_path):
    path = str(tmp_path / "fresh.db")
    database = Database(path)
    database.initialize()

    connection = sqlite3.connect(path)
    try:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        connection.close()

    assert "users" in tables


def test_all_required_tables_exist(db):
    with db.connection() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

    names = {row["name"] for row in rows}
    expected = {"users", "products", "carts", "cart_items", "orders", "order_items"}
    assert expected <= names


def test_foreign_keys_are_enabled(db):
    connection = db.get_connection()
    try:
        enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]
    finally:
        connection.close()
    assert enabled == 1


def test_email_must_be_unique(db):
    with db.connection() as conn:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Richard", "richard@example.com", "hash"),
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Salin", "richard@example.com", "hash"),
            )


def test_negative_stock_is_rejected(db):
    with db.connection() as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO products (name, price, stock_quantity) VALUES (?, ?, ?)",
                ("Bread", 11.0, -1),
            )


def test_cart_item_quantity_must_be_positive(db):
    with db.connection() as conn:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Richard", "richard@example.com", "hash"),
        )
        conn.execute("INSERT INTO carts (user_id) VALUES (1)")
        conn.execute(
            "INSERT INTO products (name, price) VALUES (?, ?)", ("Bread", 11.0)
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)",
                (1, 1, 0),
            )


def test_foreign_key_violation_is_rejected(db):
    with db.connection() as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)",
                (999, 999, 1),
            )
