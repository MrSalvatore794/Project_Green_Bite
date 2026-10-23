# GreenBite Server

REST API backend for the GreenBite vegetarian & plant-based pre-order platform.
Built with **Python 3 + Flask + SQLite** using a layered architecture:

```text
Routes  →  Services  →  Repositories  →  SQLite
```

## Install dependencies

```bash
cd server
python3 -m pip install -r requirements.txt
```

## Run the server

```bash
cd server
python3 run.py
```

The server starts at <http://127.0.0.1:5006>.

## Run the tests

```bash
cd server
python3 -m pytest -q
```

## Health endpoint

```text
GET /api/v1/health
```

Response (`200 OK`):

```json
{
    "status": "ok",
    "service": "greenbite-server"
}
```

## Authentication

- `POST /api/v1/auth/register` — register a customer (always `customer` role)
- `POST /api/v1/auth/login` — login; returns a JWT `access_token`
- `GET /api/v1/users/me` — current user (requires `Authorization: Bearer <token>`)

Passwords are hashed with Werkzeug and never returned by the API. Public
registration always creates a `customer`; admin accounts are created through a
controlled mechanism.

## Public Product Browsing

Product browsing is public (no JWT required):

- `GET /api/v1/products` — list available products (active + in stock)
- `GET /api/v1/products/<id>` — product detail

Inactive and zero-stock products are hidden from public/customer browsing.

## Customer API (authenticated)

The following require a customer JWT:

- `GET /api/v1/cart` — current user's cart
- `POST /api/v1/cart/items` — add item
- `PUT /api/v1/cart/items/<product_id>` — update quantity
- `DELETE /api/v1/cart/items/<product_id>` — remove item
- `DELETE /api/v1/cart` — clear cart
- `POST /api/v1/orders` — create order (atomic transaction)
- `GET /api/v1/orders` — list own orders
- `GET /api/v1/orders/<id>` — order detail (ownership enforced)

## Admin Product API

Requires `manage_products` permission (Admin only):

- `GET /api/v1/admin/products` — list all products (incl. inactive / zero-stock)
- `GET /api/v1/admin/products/<id>` — product detail (incl. inactive)
- `POST /api/v1/admin/products` — create a product
- `PUT /api/v1/admin/products/<id>` — update a product
- `PATCH /api/v1/admin/products/<id>/status` — activate/deactivate
- `PATCH /api/v1/admin/products/<id>/stock` — update stock

Customer `GET /api/v1/products` returns only *available* products (active and
in stock). Admin `GET /api/v1/admin/products` returns all products.

## Admin Order API

Requires `manage_orders` permission (Admin only):

- `GET /api/v1/admin/orders` — list all orders (all customers)
- `GET /api/v1/admin/orders/<id>` — order detail (no ownership restriction)
- `PATCH /api/v1/admin/orders/<id>/status` — update status

Status lifecycle (sequential, `collected` is terminal):

```text
pending → confirmed → preparing → ready_for_pickup → collected
```

Example:

```json
PATCH /api/v1/admin/orders/123/status
{ "status": "confirmed" }
```

The customer `GET /api/v1/orders` returns only the current user's orders;
Admin `GET /api/v1/admin/orders` returns every order.

## Admin User API

Requires `manage_users` permission (Admin only):

- `GET /api/v1/admin/users` — list all users
- `GET /api/v1/admin/users/<id>` — view a single user

Safe fields returned: `id`, `name`, `email`, `phone`, `role`. Passwords are
one-way hashed, never stored in plaintext, and never returned by any API.

Admin accounts are **not** created through public registration. They are
provisioned (and their passwords reset) through the operational CLI:

```bash
python scripts/admin_account.py create --email admin@example.com
python scripts/admin_account.py reset-password --email admin@example.com
python scripts/admin_account.py list
```

Passwords are prompted via `getpass` and never echoed or printed.

## Initialize a fresh database

The schema lives in `database/schema.sql`. To create a fresh SQLite database:

```python
from config import Config
from database.database import Database

db = Database(Config.DATABASE_PATH)
db.initialize()
```

The database file is stored at `server/data/greenbite.db` (created automatically).

## Seed initial products

Seed the initial 16 GreenBite products (idempotent):

```bash
python scripts/seed_products.py
```

The script skips products whose name already exists, so it is safe to re-run
without creating duplicates or overwriting admin edits.

## Database tables

| Table | Purpose |
|---|---|
| `users` | Common user accounts (role: `customer` or `admin`). |
| `products` | Bakery products, including price, stock, and availability. |
| `carts` | One cart per user. |
| `cart_items` | Products inside a cart (quantity). |
| `orders` | Submitted orders with contact / pickup / payment info. |
| `order_items` | Snapshot of each product purchased in an order. |

Main relationships:

- `users` 1 ─ 1 `carts`, `carts` 1 ─ many `cart_items`, `products` 1 ─ many `cart_items`
- `users` 1 ─ many `orders`, `orders` 1 ─ many `order_items`, `products` 1 ─ many `order_items`

`order_items` keeps a snapshot of `product_name` and `unit_price`, so later
product edits never change historical orders.

## Domain models

- `User` → `Customer`, `Admin`
- `Product`
- `Cart` → `CartItem`
- `Order` → `OrderItem`

## Project structure

```text
server/
├── app.py              # Flask application factory (create_app)
├── run.py              # Development entry point
├── config.py           # Configuration (dev / testing, DB path, secret key)
├── requirements.txt    # Minimal dependencies (Flask, PyJWT, pytest)
├── conftest.py         # Makes the server package importable in tests
├── database/
│   ├── database.py     # SQLite connection helper + schema initialization
│   └── schema.sql      # Table definitions
├── models/             # Domain models (User, Product, Cart, Order, ...)
├── repositories/       # Persistence layer (User/Product/Cart/Order repos)
├── services/           # Business-logic layer (Auth/Product/Cart/Order)
├── scripts/            # Operational CLI (Admin account + product seed)
├── routes/
│   ├── auth.py         # POST /auth/register, POST /auth/login
│   ├── users.py        # GET /users/me
│   ├── admin_products.py # Admin product management
│   ├── admin_orders.py   # Admin order management
│   ├── admin_users.py    # Admin user management
│   ├── products.py     # Public product browsing
│   ├── cart.py         # Customer cart
│   ├── orders.py       # Customer orders
│   ├── serializers.py  # Domain object → JSON dict (no password_hash)
│   └── health.py       # GET /api/v1/health
├── utils/
│   ├── auth.py         # JWT generation/decoding + require_auth/require_role
│   └── error_handler.py# Standard JSON error responses + handlers
└── tests/
    ├── conftest.py         # Shared fixtures (db + repositories + services)
    ├── test_health.py      # Foundation tests
    ├── test_database.py    # Schema tests
    ├── test_models.py      # Domain model tests
    ├── test_repositories.py# Repository tests
    ├── test_auth_service.py    # AuthService tests
    ├── test_product_service.py # ProductService tests
    ├── test_cart_service.py    # CartService tests
    ├── test_order_service.py   # OrderService tests
    ├── test_user_polymorphism.py # User/Customer/Admin polymorphism tests
    ├── test_auth_api.py        # Auth + JWT + user API tests
    ├── test_products_api.py    # Product API tests
    ├── test_public_access.py   # Public vs authenticated boundary tests
    ├── test_seed_products.py   # Product seed tests
    ├── test_cart_api.py        # Cart API tests
    ├── test_orders_api.py      # Order API tests
    ├── test_admin_products_api.py # Admin product API tests
    ├── test_admin_orders_api.py   # Admin order API tests
    ├── test_admin_users_api.py    # Admin user API tests
    └── test_admin_account.py      # Admin account (create/reset) tests
```

Generated `.db` files are ignored by git.

## API Contract (frozen)

The backend API is frozen for Vue development:

- Public: `GET /api/v1/products`, `GET /api/v1/products/<id>`
- Authenticated (customer JWT): cart + order endpoints
- Admin: JWT + `manage_*` permissions

Do not change this contract during Vue development unless a real bug is found.

## Not implemented yet

The following are intentionally left for later tasks:

- Vue Customer frontend
- Vue Admin frontend
- Online payment / delivery (future enhancements, out of MVP scope)
