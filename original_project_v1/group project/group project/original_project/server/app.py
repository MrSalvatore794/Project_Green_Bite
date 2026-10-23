"""Flask application factory for the GreenBite server."""

import os

from flask import Flask, request, send_from_directory

from config import config_by_name
from database.database import Database
from repositories.cart_repository import CartRepository
from repositories.order_repository import OrderRepository
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository
from routes.admin_orders import admin_orders_bp
from routes.admin_products import admin_products_bp
from routes.admin_users import admin_users_bp
from routes.auth import auth_bp
from routes.cart import cart_bp
from routes.health import health_bp
from routes.orders import orders_bp
from routes.products import products_bp
from routes.users import users_bp
from services.auth_service import AuthService
from services.cart_service import CartService
from services.image_storage import ImageStorage
from services.order_service import OrderService
from services.product_service import ProductService
from utils.error_handler import register_error_handlers


def create_app(
    config_name: str = "development", config_overrides: dict | None = None
) -> Flask:
    """Create and configure the Flask application.

    This is the single entry point shared by ``run.py`` and the tests. It loads
    configuration, wires up the database and services, registers routes, and
    registers error handlers.
    """
    app = Flask(__name__)

    config_class = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(config_class)
    if config_overrides:
        app.config.update(config_overrides)

    # Dependency wiring: database → repositories → services.
    db = Database(app.config["DATABASE_PATH"])
    db.initialize()

    user_repository = UserRepository(db)
    product_repository = ProductRepository(db)
    cart_repository = CartRepository(db)
    order_repository = OrderRepository(db)

    auth_service = AuthService(user_repository)
    product_service = ProductService(product_repository)
    cart_service = CartService(cart_repository, product_repository, user_repository)
    order_service = OrderService(order_repository, cart_repository, product_repository, db)

    app.extensions["db"] = db
    app.extensions["user_repository"] = user_repository
    app.extensions["product_repository"] = product_repository
    app.extensions["cart_repository"] = cart_repository
    app.extensions["order_repository"] = order_repository
    app.extensions["auth_service"] = auth_service
    app.extensions["product_service"] = product_service
    app.extensions["cart_service"] = cart_service
    app.extensions["order_service"] = order_service
    app.extensions["image_storage"] = ImageStorage(
        os.path.join(app.config["MEDIA_ROOT"], "products")
    )

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(admin_products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_orders_bp)
    app.register_blueprint(admin_users_bp)
    register_error_handlers(app)

    @app.route("/uploads/<path:filename>")
    def serve_media(filename):
        """Serve uploaded media files during local development."""
        return send_from_directory(app.config["MEDIA_ROOT"], filename)

    @app.after_request
    def add_cors_headers(response):
        """Allow known frontend origins to call the API cross-origin."""
        origin = request.headers.get("Origin")
        if origin and origin in app.config["CORS_ALLOWED_ORIGINS"]:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization"
            )
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            )
            response.headers["Access-Control-Max-Age"] = "3600"
        return response

    return app


