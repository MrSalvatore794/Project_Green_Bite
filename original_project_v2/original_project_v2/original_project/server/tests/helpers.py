"""Shared helpers for API-level tests."""


def register(client, name="Richard", email="richard@example.com", phone="0212345678", password="Password123"):
    """Register a customer via the API."""
    return client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "phone": phone, "password": password},
    )


def login(client, email, password):
    """Log in and return the full response."""
    return client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )


def token_for(client, email, password="Password123"):
    """Return the access token for a registered user."""
    response = login(client, email, password)
    assert response.status_code == 200
    return response.get_json()["access_token"]


def auth(token):
    """Build an Authorization header for a JWT."""
    return {"Authorization": f"Bearer {token}"}


def customer_token(client, email="richard@example.com", password="Password123"):
    """Register a customer and return their access token."""
    register(client, email=email, password=password)
    return token_for(client, email, password)


def create_product(app, name="Bread", price=11.0, stock=8, active=True):
    """Create (and optionally deactivate) a product via the admin service."""
    product_service = app.extensions["product_service"]
    product = product_service.create_product(name, price, stock_quantity=stock)
    if not active:
        return product_service.set_product_active(product.id, False)
    return product


def admin_token(client, app, email="admin@example.com", password="adminpass123"):
    """Create an Admin directly in the DB and return their access token."""
    from werkzeug.security import generate_password_hash

    from models import Admin

    admin = Admin(
        name="Admin",
        email=email,
        phone="0211111111",
        password_hash=generate_password_hash(password),
    )
    app.extensions["user_repository"].create_user(admin)
    return token_for(client, email, password)

