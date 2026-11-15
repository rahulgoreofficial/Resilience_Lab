"""
Application Exception Hierarchy.
Provides standard, machine-readable error codes and status codes for clean API error responses.
"""

from typing import Any, Optional, Dict


class AppException(Exception):
    """Base application exception."""
    status_code: int = 500
    error_code: str = "INTERNAL_SERVER_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Any] = None
    ):
        self.message = message or self.message
        self.error_code = error_code or self.error_code
        self.status_code = status_code or self.status_code
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details
            }
        }


class EntityNotFoundError(AppException):
    status_code = 404
    error_code = "NOT_FOUND"
    message = "The requested resource was not found."


class NetworkNotFoundError(EntityNotFoundError):
    error_code = "NETWORK_NOT_FOUND"
    message = "The requested network does not exist."


class NodeNotFoundError(EntityNotFoundError):
    error_code = "NODE_NOT_FOUND"
    message = "The requested node does not exist in the network."


class EdgeNotFoundError(EntityNotFoundError):
    error_code = "EDGE_NOT_FOUND"
    message = "The requested edge does not exist in the network."


class SimulationNotFoundError(EntityNotFoundError):
    error_code = "SIMULATION_NOT_FOUND"
    message = "The requested simulation was not found."


class ConflictError(AppException):
    status_code = 409
    error_code = "CONFLICT"
    message = "A resource conflict occurred."


class NetworkVersionConflictError(ConflictError):
    error_code = "VERSION_CONFLICT"
    message = "The network has been modified by another process. Please reload and retry."


class DuplicateEntityError(ConflictError):
    error_code = "DUPLICATE_ENTITY"
    message = "An entity with the given identifier already exists."


class BadRequestError(AppException):
    status_code = 400
    error_code = "BAD_REQUEST"
    message = "Invalid request parameters."


class PayloadTooLargeError(AppException):
    status_code = 413
    error_code = "PAYLOAD_TOO_LARGE"
    message = "The submitted payload exceeds permissible size limits."


class DatabaseUnavailableError(AppException):
    status_code = 503
    error_code = "DATABASE_UNAVAILABLE"
    message = "The persistent storage service is temporarily unavailable."

