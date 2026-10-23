"""Persistence for users."""

from database.database import Database
from models import Admin, Customer, User
from repositories._connections import connection_scope


class UserRepository:
    """Persist and retrieve User data.

    This class only performs SQLite persistence. Authentication, password
    hashing, and authorization belong to AuthService.
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    def create_user(self, user: User, connection=None) -> User:
        with connection_scope(self.db, connection) as conn:
            cursor = conn.execute(
                "INSERT INTO users (name, email, phone, password_hash, role) "
                "VALUES (?, ?, ?, ?, ?)",
                (user.name, user.email, user.phone, user.password_hash, user.role),
            )
            user.id = cursor.lastrowid
        return user

    def find_by_id(self, user_id: int, connection=None) -> User | None:
        with connection_scope(self.db, connection) as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        return self._row_to_user(row) if row is not None else None

    def find_by_email(self, email: str, connection=None) -> User | None:
        with connection_scope(self.db, connection) as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
        return self._row_to_user(row) if row is not None else None

    def list_users(self, search=None, role=None, connection=None) -> list[User]:
        """List users, optionally filtered by a search term and role."""
        query = "SELECT * FROM users"
        conditions = []
        params = []
        if search:
            like = f"%{search}%"
            conditions.append("(name LIKE ? OR email LIKE ? OR phone LIKE ?)")
            params.extend([like, like, like])
        if role:
            conditions.append("role = ?")
            params.append(role)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id"

        with connection_scope(self.db, connection) as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_user(row) for row in rows]

    def update_user(self, user: User, connection=None) -> User:
        with connection_scope(self.db, connection) as conn:
            conn.execute(
                "UPDATE users SET name = ?, email = ?, phone = ?, "
                "password_hash = ?, role = ? WHERE id = ?",
                (
                    user.name,
                    user.email,
                    user.phone,
                    user.password_hash,
                    user.role,
                    user.id,
                ),
            )
        return user

    def _row_to_user(self, row) -> User:
        """Reconstruct the correct domain subtype from the stored role."""
        if row["role"] == User.ROLE_ADMIN:
            user = Admin(
                name=row["name"],
                email=row["email"],
                phone=row["phone"],
                password_hash=row["password_hash"],
                user_id=row["id"],
            )
        else:
            user = Customer(
                name=row["name"],
                email=row["email"],
                phone=row["phone"],
                password_hash=row["password_hash"],
                user_id=row["id"],
            )
        user.created_at = row["created_at"]
        return user
