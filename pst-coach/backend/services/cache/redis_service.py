"""
Redis caching service for PST Coach.
Provides caching utilities, rate limiting, and connection management.
"""
import hashlib
import json
from typing import Any, Optional
from datetime import timedelta

import redis.asyncio as redis
from loguru import logger

from core.config import settings


class RedisService:
    """Redis service for caching and rate limiting."""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Initialize Redis connection."""
        if self._client is not None:
            return self._connected
        
        try:
            self._client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self._client.ping()
            self._connected = True
            logger.info("Redis connected successfully")
            return True
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching will be disabled.")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            self._connected = False
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._connected and self._client is not None
    
    async def health_check(self) -> dict:
        """Check Redis health status."""
        if not self.is_connected:
            return {"status": "disconnected", "message": "Redis not connected"}
        
        try:
            await self._client.ping()
            info = await self._client.info("memory")
            return {
                "status": "healthy",
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def generate_cache_key(*args, **kwargs) -> str:
        """Generate a consistent cache key from arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]
    
    async def get_cached(self, key: str) -> Optional[Any]:
        """Get a cached value."""
        if not self.is_connected:
            return None
        
        try:
            value = await self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set_cached(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """Set a cached value with optional TTL."""
        if not self.is_connected:
            return False
        
        try:
            ttl = ttl_seconds or settings.CACHE_TTL_SECONDS
            serialized = json.dumps(value)
            await self._client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def delete_cached(self, pattern: str) -> int:
        """Delete cached values matching a pattern."""
        if not self.is_connected:
            return 0
        
        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return 0
    
    async def invalidate_upload_cache(self, upload_id: str) -> int:
        """Invalidate all caches for a specific upload."""
        count = 0
        count += await self.delete_cached(f"chat:{upload_id}:*")
        count += await self.delete_cached(f"analytics:*:{upload_id}")
        logger.info(f"Invalidated {count} cache keys for upload {upload_id}")
        return count
    
    async def check_rate_limit(
        self, 
        identifier: str, 
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None
    ) -> tuple[bool, int]:
        """
        Check rate limit using sliding window.
        Returns (is_allowed, remaining_requests).
        """
        if not self.is_connected:
            # If Redis is down, allow requests (graceful degradation)
            return True, limit or settings.RATE_LIMIT_REQUESTS
        
        limit = limit or settings.RATE_LIMIT_REQUESTS
        window = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
        key = f"ratelimit:{identifier}"
        
        try:
            # Increment counter
            current = await self._client.incr(key)
            
            # Set expiry on first request
            if current == 1:
                await self._client.expire(key, window)
            
            remaining = max(0, limit - current)
            is_allowed = current <= limit
            
            return is_allowed, remaining
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True, limit


# Singleton instance
redis_service = RedisService()


async def get_redis() -> RedisService:
    """Get the Redis service instance, connecting if needed."""
    if not redis_service.is_connected:
        await redis_service.connect()
    return redis_service
