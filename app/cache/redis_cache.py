from typing import Optional, Any
import json
import redis
from app.core.config import get_settings

settings = get_settings()


class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
        )
        self.ttl = settings.CACHE_TTL

    async def get(self, key: str) -> Optional[dict]:
        """Get value from cache"""
        data = self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any) -> None:
        """Set value in cache with TTL"""
        self.redis_client.setex(key, self.ttl, json.dumps(value))

    async def delete(self, key: str) -> None:
        """Delete key from cache"""
        self.redis_client.delete(key)
