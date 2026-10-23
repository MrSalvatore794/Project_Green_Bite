"""Operational CLI for managing Admin accounts (bootstrap + password reset).

Usage (run from the ``server`` directory):

    python scripts/admin_account.py create --email admin@example.com
    python scripts/admin_account.py reset-password --email admin@example.com
    python scripts/admin_account.py list

Passwords are prompted interactively via ``getpass`` (never echoed) and are
never printed. Admin accounts are provisioned here rather than through the
public registration API, so there is no role-escalation path for clients.
"""

import argparse
import getpass
import os
import sys

# Make the server package importable when run as a plain script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config  # noqa: E402
from database.database import Database  # noqa: E402
from repositories.user_repository import UserRepository  # noqa: E402
from services.auth_service import AuthService  # noqa: E402
from services.exceptions import (  # noqa: E402
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)


def _build_service() -> AuthService:
    db = Database(Config.DATABASE_PATH)
    db.initialize()
    return AuthService(UserRepository(db))


def _prompt_password() -> str:
    password = getpass.getpass("Password: ")
    if not password:
        print("Password cannot be empty.", file=sys.stderr)
        sys.exit(1)
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.", file=sys.stderr)
        sys.exit(1)
    return password


def cmd_create(args) -> None:
    service = _build_service()
    email = args.email or input("Admin email: ")
    name = args.name or input("Admin name: ")
    phone = args.phone or input("Admin phone: ")
    password = _prompt_password()
    try:
        admin = service.create_admin(name=name, email=email, phone=phone, password=password)
    except (UserAlreadyExistsError, ValidationError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Admin account created: id={admin.id} email={admin.email}")


def cmd_reset_password(args) -> None:
    service = _build_service()
    email = args.email or input("Admin email: ")
    password = _prompt_password()
    try:
        admin = service.reset_admin_password(email, password)
    except (UserNotFoundError, ValidationError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Password reset for Admin: email={admin.email}")


def cmd_list(args) -> None:
    service = _build_service()
    admins = [u for u in service.get_all_users() if u.role == "admin"]
    if not admins:
        print("No Admin accounts found.")
        return
    for admin in admins:
        print(f"id={admin.id} name={admin.name} email={admin.email}")


def main() -> None:
    parser = argparse.ArgumentParser(description="GreenBite Admin account management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create an Admin account")
    create_parser.add_argument("--email")
    create_parser.add_argument("--name")
    create_parser.add_argument("--phone")
    create_parser.set_defaults(func=cmd_create)

    reset_parser = subparsers.add_parser("reset-password", help="Reset an Admin password")
    reset_parser.add_argument("--email")
    reset_parser.set_defaults(func=cmd_reset_password)

    list_parser = subparsers.add_parser("list", help="List Admin accounts")
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
