import redis.asyncio as redis
from typing import Any, Optional

class StateManager:
    def __init__(self, redis_url: str = "redis://localhost"):
        self.redis = redis.from_url(redis_url)
        
    async def set_state(self, key: str, value: Any):
        await self.redis.set(key, str(value))
        
    async def get_state(self, key: str) -> Optional[str]:
        return await self.redis.get(key) 