import torch
from typing import Optional
import hashlib
from ..core.redis_handler import RedisHandler

class TTSCache:
    def __init__(self):
        self.redis = RedisHandler()
        
    def _get_cache_key(self, text: str) -> str:
        """Generate a consistent cache key for the text"""
        return f"tts:{hashlib.md5(text.encode()).hexdigest()}"
    
    async def get(self, text: str) -> Optional[torch.Tensor]:
        """Retrieve cached audio"""
        key = self._get_cache_key(text)
        data = await self.redis.get_binary(key)
        
        if data:
            # Deserialize to torch tensor
            return torch.frombuffer(data, dtype=torch.float32)
        return None
    
    async def put(self, text: str, audio: torch.Tensor):
        """Cache audio data"""
        key = self._get_cache_key(text)
        # Convert tensor to bytes
        data = audio.cpu().numpy().tobytes()
        await self.redis.set_binary(key, data) 