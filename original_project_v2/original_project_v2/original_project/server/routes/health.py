"""Health-check route for the GreenBite server."""

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__, url_prefix="/api/v1")


@health_bp.get("/health")
def health() -> tuple:
    """Return a simple service status response."""
    return jsonify({"status": "ok", "service": "greenbite-server"}), 200
