"""Validation errors for schema and request normalization."""


class RequestValidationError(ValueError):
    """Raised when a CLI request payload fails validation."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def to_error_payload(code: str, message: str) -> dict:
    """Build a compact JSON error payload."""
    return {"error": code, "message": message}
