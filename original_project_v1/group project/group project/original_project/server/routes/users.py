"""Current-user routes."""

from flask import Blueprint, jsonify

from routes.serializers import user_to_dict
from utils.auth import get_current_user, require_auth

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


@users_bp.get("/me")
@require_auth
def get_current_user_info():
    """Return the authenticated user identified by the JWT."""
    return jsonify({"user": user_to_dict(get_current_user())}), 200
