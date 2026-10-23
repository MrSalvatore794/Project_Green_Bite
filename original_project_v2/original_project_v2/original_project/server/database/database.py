"""Small SQLite connection helper for the GreenBite server."""

import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


class Database:
    """Manage SQLite connections for a single database file.

    This class only knows how to open and close connections and how to create
    the schema. Table-specific SQL belongs in the repository layer, which is
    added in a later task.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._ensure_data_directory()

    def _ensure_data_directory(self) -> None:
        """Create the parent directory for the database file if needed."""
        directory = os.path.dirname(self.db_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Open a new connection with a dictionary-like row factory.

        Foreign key enforcement is enabled on every connection.
        """
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        """Create all tables by executing the schema file, then migrate.

        The schema uses ``CREATE TABLE IF NOT EXISTS``, so running this more
        than once is safe. A lightweight migration step adds any columns that
        were introduced after an existing database was first created.
        """
        with open(SCHEMA_PATH, encoding="utf-8") as schema_file:
            schema = schema_file.read()

        connection = self.get_connection()
        try:
            connection.executescript(schema)
            self._migrate(connection)
            connection.commit()
        finally:
            connection.close()

    def _migrate(self, connection: sqlite3.Connection) -> None:
        """Add columns introduced after the initial release."""
        self._ensure_column(
            connection, "products", "detail_image_url", "TEXT NOT NULL DEFAULT ''"
        )
        self._ensure_column(
            connection,
            "products",
            "star_level",
            "INTEGER NOT NULL DEFAULT 0 CHECK (star_level BETWEEN 0 AND 5)",
        )
        self._ensure_column(
            connection,
            "orders",
            "payment_status",
            "TEXT NOT NULL DEFAULT 'pending' "
            "CHECK (payment_status IN ('pending', 'completed', 'failed'))",
        )
        self._ensure_column(connection, "orders", "canceled_at", "TEXT")

    def _ensure_column(
        self, connection: sqlite3.Connection, table: str, column: str, definition: str
    ) -> None:
        columns = [
            row["name"] for row in connection.execute(f"PRAGMA table_info({table})")
        ]
        if column not in columns:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Provide a connection that commits on success and rolls back on error.

        The connection is always closed when the block exits.
        """
        connection = self.get_connection()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
