"""
Security and Request Sanitation Utilities.
Applies resource boundaries, upload limits, and input sanitization.
"""

from typing import Tuple
from app.core.config import settings
from app.core.exceptions import PayloadTooLargeError, BadRequestError


ALLOWED_EXTENSIONS = {".json", ".csv"}


def validate_payload_size(data: bytes) -> None:
    """Ensures input payload does not exceed MAX_UPLOAD_SIZE_BYTES."""
    if len(data) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise PayloadTooLargeError(
            message=f"Payload size ({len(data)} bytes) exceeds limit of {settings.MAX_UPLOAD_SIZE_BYTES} bytes."
        )


def validate_network_size(node_count: int, edge_count: int) -> None:
    """Enforces upper bounds on network graph order and size."""
    if node_count > settings.MAX_NETWORK_NODES:
        raise BadRequestError(
            message=f"Network node count ({node_count}) exceeds maximum allowed ({settings.MAX_NETWORK_NODES})."
        )
    if edge_count > settings.MAX_NETWORK_EDGES:
        raise BadRequestError(
            message=f"Network edge count ({edge_count}) exceeds maximum allowed ({settings.MAX_NETWORK_EDGES})."
        )


def validate_file_format(filename: str) -> str:
    """Validates filename extension and returns format ('json' or 'csv')."""
    lower = filename.lower()
    for ext in ALLOWED_EXTENSIONS:
        if lower.endswith(ext):
            return ext.lstrip(".")
    raise BadRequestError(
        message=f"Unsupported file format for '{filename}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
    )

