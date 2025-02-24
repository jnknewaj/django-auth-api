from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    PermissionDenied,
    NotAuthenticated,
    ValidationError,
)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Default error structure
        custom_response = {
            "status_code": response.status_code,
            "message": response.data.get("detail", "An error occurred."),
            "error": str(exc),
        }

        # Handle specific exception cases
        if isinstance(exc, PermissionDenied):
            custom_response["message"] = (
                "You do not have permission to perform this action."
            )
        elif isinstance(exc, NotAuthenticated):
            custom_response["message"] = (
                "Authentication credentials were nottt provided."
            )
        elif isinstance(exc, ValidationError):
            custom_response["message"] = "Invalid input provided."
            custom_response["errors"] = response.data  # Show detailed validation errors

        response.data = custom_response

    return response
