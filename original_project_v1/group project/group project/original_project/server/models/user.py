"""User domain model and its role-specific subclasses."""


class User:
    """Common domain model for every user of the platform.

    ``Customer`` and ``Admin`` inherit the shared fields from this class and
    only differ by their role. Authentication and password hashing are added in
    a later task, so ``password_hash`` is stored here only as a future
    persistence field.
    """

    ROLE_CUSTOMER = "customer"
    ROLE_ADMIN = "admin"
    VALID_ROLES = (ROLE_CUSTOMER, ROLE_ADMIN)

    def __init__(
        self,
        name: str,
        email: str,
        phone: str | None = None,
        password_hash: str | None = None,
        role: str = ROLE_CUSTOMER,
        user_id: int | None = None,
    ) -> None:
        if role not in self.VALID_ROLES:
            raise ValueError(f"Invalid role: {role!r}")

        self.id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.password_hash = password_hash
        self.role = role
        self.created_at = None

    def get_permissions(self) -> set[str]:
        """Return the permissions for this role.

        A plain ``User`` has no permissions. ``Customer`` and ``Admin``
        override this method to return their own permission sets.
        """
        return set()


class Customer(User):
    """A user with the ``customer`` role."""

    def __init__(
        self,
        name: str,
        email: str,
        phone: str | None = None,
        password_hash: str | None = None,
        user_id: int | None = None,
    ) -> None:
        super().__init__(
            name=name,
            email=email,
            phone=phone,
            password_hash=password_hash,
            role=User.ROLE_CUSTOMER,
            user_id=user_id,
        )

    def get_permissions(self) -> set[str]:
        """Return the customer permission set."""
        return {
            "view_products",
            "manage_cart",
            "create_orders",
            "view_own_orders",
            "like_products",
        }


class Admin(User):
    """A user with the ``admin`` role."""

    def __init__(
        self,
        name: str,
        email: str,
        phone: str | None = None,
        password_hash: str | None = None,
        user_id: int | None = None,
    ) -> None:
        super().__init__(
            name=name,
            email=email,
            phone=phone,
            password_hash=password_hash,
            role=User.ROLE_ADMIN,
            user_id=user_id,
        )

    def get_permissions(self) -> set[str]:
        """Return the admin permission set."""
        return {
            "view_admin_dashboard",
            "view_products",
            "manage_products",
            "manage_stock",
            "view_users",
            "view_all_orders",
            "update_order_status",
            "manage_orders",
            "manage_users",
        }
