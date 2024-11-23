import json
import pickle
from typing import Any, Optional
import redis.asyncio as redis
from loguru import logger

class RedisHandler:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self.binary_redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=False
        )
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        try:
            data = json.dumps(value)
            return await self.redis.set(key, data, ex=ttl)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def get_binary(self, key: str) -> Optional[bytes]:
        try:
            return await self.binary_redis.get(key)
        except Exception as e:
            logger.error(f"Redis binary get error: {e}")
            return None

    async def set_binary(self, key: str, value: bytes, ttl: int = 3600) -> bool:
        try:
            return await self.binary_redis.set(key, value, ex=ttl)
        except Exception as e:
            logger.error(f"Redis binary set error: {e}")
            return False 