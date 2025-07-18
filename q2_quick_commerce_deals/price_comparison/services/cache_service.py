"""Cache service for the price comparison platform."""

import json
import hashlib
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """Redis-based cache service with multi-level caching strategy."""
    
    def __init__(self):
        """Initialize cache service."""
        self.redis_client = redis.from_url(
            settings.redis.url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        self.default_ttl = 300  # 5 minutes
        self.schema_ttl = 3600  # 1 hour
        self.query_ttl = 300  # 5 minutes
        self.result_ttl = 600  # 10 minutes
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.redis_client.get(key)
            if value:
                logger.debug("Cache hit", key=key)
                return json.loads(value)
            logger.debug("Cache miss", key=key)
            return None
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL."""
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            await self.redis_client.setex(key, ttl, serialized_value)
            logger.debug("Cache set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            result = await self.redis_client.delete(key)
            logger.debug("Cache delete", key=key, deleted=bool(result))
            return bool(result)
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(await self.redis_client.exists(key))
        except Exception as e:
            logger.error("Cache exists error", key=key, error=str(e))
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key."""
        try:
            return bool(await self.redis_client.expire(key, ttl))
        except Exception as e:
            logger.error("Cache expire error", key=key, error=str(e))
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache."""
        try:
            return await self.redis_client.incr(key, amount)
        except Exception as e:
            logger.error("Cache increment error", key=key, error=str(e))
            return None
    
    async def get_or_set(self, key: str, default_func, ttl: Optional[int] = None) -> Any:
        """Get from cache or set default value."""
        value = await self.get(key)
        if value is not None:
            return value
        
        # Generate default value
        if callable(default_func):
            value = await default_func() if hasattr(default_func, '__await__') else default_func()
        else:
            value = default_func
        
        # Cache the value
        await self.set(key, value, ttl)
        return value
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments."""
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            key_parts.append(str(arg))
        
        # Add keyword arguments (sorted for consistency)
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        return ":".join(key_parts)
    
    def generate_query_key(self, query: str, max_results: int = 100) -> str:
        """Generate cache key for query results."""
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        return f"query:{query_hash}:{max_results}"
    
    def generate_schema_key(self, table_name: str) -> str:
        """Generate cache key for schema information."""
        return f"schema:{table_name}"
    
    async def get_query_cache(self, query: str, max_results: int = 100) -> Optional[Dict[str, Any]]:
        """Get cached query result."""
        key = self.generate_query_key(query, max_results)
        return await self.get(key)
    
    async def set_query_cache(self, query: str, result: Dict[str, Any], max_results: int = 100) -> bool:
        """Cache query result."""
        key = self.generate_query_key(query, max_results)
        return await self.set(key, result, self.query_ttl)
    
    async def invalidate_query_cache(self, pattern: str = "query:*") -> int:
        """Invalidate query cache by pattern."""
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info("Invalidated query cache", pattern=pattern, deleted=deleted)
                return deleted
            return 0
        except Exception as e:
            logger.error("Cache invalidation error", pattern=pattern, error=str(e))
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            info = await self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            }
        except Exception as e:
            logger.error("Failed to get cache stats", error=str(e))
            return {}
    
    async def health_check(self) -> bool:
        """Check cache health."""
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error("Cache health check failed", error=str(e))
            return False
    
    async def close(self):
        """Close Redis connection."""
        try:
            await self.redis_client.close()
            logger.info("Cache service closed")
        except Exception as e:
            logger.error("Error closing cache service", error=str(e)) 