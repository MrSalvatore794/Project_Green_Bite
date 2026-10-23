"""Authentication routes (registration and login)."""

from flask import Blueprint, current_app, jsonify, request

from routes.serializers import user_to_dict
from services.exceptions import ValidationError
from utils.auth import generate_access_token

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.post("/register")
def register():
    """Register a new customer."""
    data = request.get_json(silent=True) or {}
    auth_service = current_app.extensions["auth_service"]

    user = auth_service.register(
        name=data.get("name"),
        email=data.get("email"),
        phone=data.get("phone"),
        password=data.get("password"),
    )

    return jsonify(
        {"message": "User registered successfully", "user": user_to_dict(user)}
    ), 201


@auth_bp.post("/login")
def login():
    """Authenticate a user and return a JWT access token."""
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise ValidationError("Email and password are required.")

    auth_service = current_app.extensions["auth_service"]
    user = auth_service.authenticate(email, password)
    token = generate_access_token(user.id, user.role)

    return jsonify(
        {
            "access_token": token,
            "token_type": "Bearer",
            "user": user_to_dict(user),
        }
    ), 200
