-- GreenBite database schema.
--
-- Foreign key enforcement is enabled per-connection by the Database helper in
-- database/database.py, so this file only contains the table definitions.

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE,
    phone         TEXT,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'customer'
                          CHECK (role IN ('customer', 'admin')),
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS products (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL,
    description    TEXT    NOT NULL DEFAULT '',
    price          REAL    NOT NULL CHECK (price >= 0),
    category       TEXT    NOT NULL DEFAULT '',
    vegetarian     INTEGER NOT NULL DEFAULT 0 CHECK (vegetarian IN (0, 1)),
    vegan          INTEGER NOT NULL DEFAULT 0 CHECK (vegan IN (0, 1)),
    ingredients    TEXT    NOT NULL DEFAULT '',
    allergens      TEXT    NOT NULL DEFAULT '',
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active      INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    image_url      TEXT    NOT NULL DEFAULT '',
    detail_image_url TEXT  NOT NULL DEFAULT '',
    star_level     INTEGER NOT NULL DEFAULT 0 CHECK (star_level BETWEEN 0 AND 5),
    created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS carts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL UNIQUE,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cart_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id    INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    UNIQUE (cart_id, product_id),
    FOREIGN KEY (cart_id)    REFERENCES carts (id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS orders (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                INTEGER NOT NULL,
    customer_name          TEXT    NOT NULL,
    phone                  TEXT    NOT NULL,
    pickup_date            TEXT    NOT NULL,
    pickup_time            TEXT    NOT NULL,
    payment_reference_type TEXT    NOT NULL,
    payment_reference      TEXT    NOT NULL,
    total_amount           REAL    NOT NULL CHECK (total_amount >= 0),
    status                 TEXT    NOT NULL DEFAULT 'pending'
                                  CHECK (status IN (
                                      'pending',
                                      'confirmed',
                                      'preparing',
                                      'ready_for_pickup',
                                      'collected'
                                  )),
    payment_status         TEXT    NOT NULL DEFAULT 'pending'
                                  CHECK (payment_status IN ('pending', 'completed', 'failed')),
    canceled_at            TEXT,
    created_at             TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id     INTEGER NOT NULL,
    product_id   INTEGER NOT NULL,
    product_name TEXT    NOT NULL,
    unit_price   REAL    NOT NULL CHECK (unit_price >= 0),
    quantity     INTEGER NOT NULL CHECK (quantity > 0),
    subtotal     REAL    NOT NULL CHECK (subtotal >= 0),
    FOREIGN KEY (order_id)   REFERENCES orders (id)   ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (id)
);

CREATE TABLE IF NOT EXISTS product_likes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (user_id, product_id),
    FOREIGN KEY (user_id)    REFERENCES users (id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);
