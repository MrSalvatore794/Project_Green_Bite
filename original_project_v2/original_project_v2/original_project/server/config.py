"""Application configuration for the GreenBite server."""

import os


class Config:
    """Base configuration shared by all environments."""

    # Flask settings
    DEBUG = False
    TESTING = False

    # Development-only placeholder secret key.
    # A real production deployment MUST provide a secure value through the
    # FLASK_SECRET_KEY environment variable instead of this fallback.
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-only-secret-key-change-me")

    # JWT settings. JWT_SECRET_KEY is a clearly-marked development fallback;
    # production MUST provide a secure value via the JWT_SECRET_KEY env var.
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-jwt-secret-key-change-me-0123456789")
    JWT_EXPIRATION_MINUTES = int(os.environ.get("JWT_EXPIRATION_MINUTES", "60"))

    # SQLite database location. The database file lives inside the server
    # project so the whole application stays self-contained during the MVP.
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DATABASE_PATH = os.environ.get(
        "GREENBITE_DB_PATH", os.path.join(DATA_DIR, "greenbite.db")
    )

    # Persistent runtime media (uploaded product images). Stored outside the app
    # packages so it is never part of Vite build output. In production this can
    # be served by Nginx; in development Flask serves it under /uploads/.
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    MEDIA_ROOT = os.environ.get(
        "GREENBITE_MEDIA_ROOT", os.path.join(PROJECT_ROOT, "uploads")
    )

    # CORS: known development frontend origins. The Customer web app proxies
    # /api through Vite, but the independent Admin app calls the API directly,
    # so its origin must be allowed here. Never set to "*".
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]

    # WxPusher merchant notifications (optional, best-effort). Leave either
    # value empty to disable notifications. UIDs are comma-separated.
    WXPUSHER_APP_TOKEN = os.environ.get("WXPUSHER_APP_TOKEN", "")
    WXPUSHER_UIDS = os.environ.get("WXPUSHER_UIDS", "")


class DevelopmentConfig(Config):
    """Configuration used while developing locally."""

    DEBUG = True


class TestingConfig(Config):
    """Configuration used by the pytest test suite."""

    TESTING = True
    DATABASE_PATH = os.path.join(Config.DATA_DIR, "test_greenbite.db")
    JWT_SECRET_KEY = "test-jwt-secret-key-for-testing-only-0123456789"


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}
