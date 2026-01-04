"""Tenant isolation middleware."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    """Enforce multi-tenant isolation."""

    async def dispatch(self, request: Request, call_next):
        # Extract tenant from JWT or session
        # For now, just pass through
        # TODO: Implement tenant extraction and validation
        request.state.tenant_id = None

        response = await call_next(request)
        return response
