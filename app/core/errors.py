from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle standard HTTP exceptions.

    Args:
        request (Request): The incoming request.
        exc (StarletteHTTPException): The raised HTTP exception.

    Returns:
        JSONResponse: A structured error response with code and message.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.detail}},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors from Pydantic/FastAPI.

    Args:
        request (Request): The incoming request.
        exc (RequestValidationError): The raised validation error.

    Returns:
        JSONResponse: A 422 error response containing validation details.
    """
    errors = []
    for err in exc.errors():
        errors.append(
            {
                "loc": err["loc"],
                "msg": err["msg"],
                "type": err["type"],
            }
        )
    return JSONResponse(
        status_code=422,
        content={"error": {"code": 422, "message": errors}},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected server-side exceptions.

    Args:
        request (Request): The incoming request.
        exc (Exception): The raised generic exception.

    Returns:
        JSONResponse: A 500 error response with a generic message.
    """
    return JSONResponse(
        status_code=500,
        content={"error": {"code": 500, "message": "Internal server error"}},
    )


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handle requests exceeding the configured rate limits.

    Args:
        request (Request): The incoming request.
        exc (RateLimitExceeded): The raised rate limit exception.

    Returns:
        JSONResponse: A 429 error response indicating too many requests.
    """
    return JSONResponse(
        status_code=429,
        content={"error": {"code": 429, "message": "Too many requests"}},
    )
