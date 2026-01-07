"""
Rate limiting middleware for FastAPI.
Uses Redis sliding window rate limiting.
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from services.cache.redis_service import get_redis
from core.config import settings


# Rate limits by endpoint prefix
RATE_LIMITS = {
    "/api/chat": {"limit": 60, "window": 60},       # 60 req/min for chat
    "/api/analytics": {"limit": 120, "window": 60}, # 120 req/min for analytics
    "/api/uploads": {"limit": 30, "window": 60},    # 30 req/min for uploads
    "/api/graph": {"limit": 120, "window": 60},     # 120 req/min for graph (status polling)
}


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health checks and docs
        path = request.url.path
        if path in ["/", "/health", "/api/docs", "/api/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"
        
        # Find matching rate limit config
        limit_config = None
        for prefix, config in RATE_LIMITS.items():
            if path.startswith(prefix):
                limit_config = config
                break
        
        # Use default limits if no specific config
        if limit_config is None:
            limit_config = {
                "limit": settings.RATE_LIMIT_REQUESTS,
                "window": settings.RATE_LIMIT_WINDOW_SECONDS
            }
        
        # Check rate limit
        try:
            redis = await get_redis()
            identifier = f"{client_ip}:{path.split('/')[2]}"  # Group by IP:endpoint
            
            is_allowed, remaining = await redis.check_rate_limit(
                identifier,
                limit=limit_config["limit"],
                window_seconds=limit_config["window"]
            )
            
            # Add rate limit headers to response
            response = await call_next(request) if is_allowed else JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "detail": f"Rate limit exceeded. Try again in {limit_config['window']} seconds.",
                    "retry_after": limit_config["window"]
                }
            )
            
            response.headers["X-RateLimit-Limit"] = str(limit_config["limit"])
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Window"] = str(limit_config["window"])
            
            if not is_allowed:
                response.headers["Retry-After"] = str(limit_config["window"])
                logger.warning(f"Rate limit exceeded for {client_ip} on {path}")
            
            return response
            
        except Exception as e:
            # If rate limiting fails, allow the request (graceful degradation)
            logger.error(f"Rate limiter error: {e}")
            return await call_next(request)
