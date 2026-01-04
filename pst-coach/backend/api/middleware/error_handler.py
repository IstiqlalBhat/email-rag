"""Global error handling middleware."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Centralized error handling middleware."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.exception(f"Unhandled exception: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
                }
            )
