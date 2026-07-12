"""
Custom exception handler for consistent API error responses.

All errors follow a uniform structure:
{
    "error": {
        "code": "validation_error",
        "message": "Human-readable message",
        "details": { ... }  // optional
    }
}
"""

from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Override DRF's default exception handler for consistent error formatting.

    Returns structured error responses with no stack traces (§20).
    """
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception — return generic 500
        from rest_framework.response import Response

        return Response(
            {
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred.",
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Map known exceptions to error codes
    error_code = _get_error_code(exc)
    error_message = _get_error_message(exc, response)

    error_body = {
        "error": {
            "code": error_code,
            "message": error_message,
        }
    }

    # Include field-level details for validation errors
    if isinstance(exc, ValidationError) and isinstance(response.data, dict):
        error_body["error"]["details"] = response.data

    response.data = error_body
    return response


def _get_error_code(exc):
    """Map exception type to a machine-readable error code."""
    code_map = {
        ValidationError: "validation_error",
        NotAuthenticated: "not_authenticated",
        AuthenticationFailed: "authentication_failed",
        PermissionDenied: "permission_denied",
    }
    for exc_class, code in code_map.items():
        if isinstance(exc, exc_class):
            return code
    return "error"


def _get_error_message(exc, response):
    """Extract a human-readable message from the exception."""
    if isinstance(exc, ValidationError):
        return "Validation failed."
    if hasattr(exc, "detail"):
        detail = exc.detail
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list) and detail:
            return str(detail[0])
    status_messages = {
        401: "Authentication credentials were not provided or are invalid.",
        403: "You do not have permission to perform this action.",
        404: "The requested resource was not found.",
        405: "Method not allowed.",
    }
    return status_messages.get(response.status_code, "An error occurred.")
