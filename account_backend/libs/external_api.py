import re
import sys
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppInvokeQuotaExceededError(ValueError):
    """
    Custom exception raised when the quota for an app has been exceeded.
    """

    description = "App Invoke Quota Exceeded"


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    headers = {}
    if exc.headers:
        headers = exc.headers

    status_code = exc.status_code
    default_data = {
        "code": re.sub(r"(?<!^)(?=[A-Z])", "_", type(exc).__name__).lower(),
        "message": getattr(exc, "detail", "Internal Server Error"),
        "status": status_code,
    }

    if (
        default_data["message"]
        and default_data["message"] == "Failed to decode JSON object: Expecting value: line 1 column 1 (char 0)"
    ):
        default_data["message"] = "Invalid JSON payload received or JSON payload is empty."

    if "code" not in default_data:
        default_data["code"] = "unknown"

    return JSONResponse(
        status_code=status_code,
        content=default_data,
        headers=headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions"""
    status_code = 400
    default_data = {
        "code": "invalid_param",
        "message": str(exc),
        "status": status_code,
    }
    
    # Format validation errors
    if exc.errors():
        error_detail = exc.errors()[0]
        if "loc" in error_detail and "msg" in error_detail:
            param_key = ".".join(str(x) for x in error_detail["loc"] if x != "body")
            default_data = {
                "code": "invalid_param",
                "message": error_detail["msg"],
                "params": param_key,
                "status": status_code,
            }
    
    return JSONResponse(
        status_code=status_code,
        content=default_data
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    status_code = 500
    default_data = {
        "message": "Internal Server Error",
        "code": "internal_error",
        "status": status_code,
    }

    # Record the exception in the logs when we have a server error of status code: 500
    exc_info: Any = sys.exc_info()
    if exc_info[1] is None:
        exc_info = None
    # In FastAPI, logging is handled differently
    import logging
    logging.exception("Unhandled exception")

    return JSONResponse(
        status_code=status_code,
        content=default_data
    )


async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions"""
    status_code = 400
    default_data = {
        "code": "invalid_param",
        "message": str(exc),
        "status": status_code,
    }
    return JSONResponse(
        status_code=status_code,
        content=default_data
    )


async def quota_exceeded_handler(request: Request, exc: AppInvokeQuotaExceededError):
    """Handle AppInvokeQuotaExceededError exceptions"""
    status_code = 429
    default_data = {
        "code": "too_many_requests",
        "message": str(exc),
        "status": status_code,
    }
    return JSONResponse(
        status_code=status_code,
        content=default_data
    )
