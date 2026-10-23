"""Persistent image storage for uploaded product images."""

import os
import uuid

from services.exceptions import ValidationError

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class ImageStorage:
    """Validate and persist uploaded product images.

    Files are stored under a configured upload directory using a secure,
    server-generated filename (never the original client filename). The
    returned value is a logical URL path, independent of the filesystem.
    """

    def __init__(self, upload_dir: str, max_size: int = 5 * 1024 * 1024) -> None:
        self.upload_dir = upload_dir
        self.max_size = max_size

    def save(self, file_storage) -> str:
        """Validate ``file_storage`` and return its logical ``/uploads/...`` URL."""
        original = (file_storage.filename or "").strip()
        ext = os.path.splitext(original)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError("Unsupported image format. Use JPG, PNG or WEBP.")
        if file_storage.mimetype and not file_storage.mimetype.startswith("image/"):
            raise ValidationError("Unsupported image type.")

        data = file_storage.read()
        if not data:
            raise ValidationError("Image file is empty.")
        if len(data) > self.max_size:
            raise ValidationError("Image is too large (max 5MB).")

        secure_name = f"{uuid.uuid4().hex}{ext}"
        os.makedirs(self.upload_dir, exist_ok=True)
        with open(os.path.join(self.upload_dir, secure_name), "wb") as fh:
            fh.write(data)

        return f"/uploads/products/{secure_name}"