from uuid import uuid4
from typing import Dict, Optional
import asyncio
from datetime import datetime, timedelta
from loguru import logger

class Session:
    def __init__(self, id: str = None):
        self.id = id or str(uuid4())
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.context = []
        
    async def process_message(self, message: str) -> str:
        self.last_active = datetime.now()
        self.context.append({"role": "user", "content": message})
        # Process with LLM here
        return "Response placeholder"

class SessionManager:
    def __init__(self):
        self.sessions: Dict = {}
        self.cleanup_task = None
        logger.info("Session manager initialized")

    async def setup(self):
        """Initialize async components of the session manager"""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_old_sessions())
        return self

    async def _cleanup_old_sessions(self):
        while True:
            try:
                current_time = datetime.now()
                expired_sessions = [
                    session_id for session_id, session in self.sessions.items()
                    if current_time - session['last_active'] > timedelta(hours=1)
                ]
                
                for session_id in expired_sessions:
                    await self.end_session(session_id)
                    
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying

    async def start_session(self) -> str:
        # Implementation for starting a session
        pass

    async def end_session(self, session_id: str):
        # Implementation for ending a session
        pass

    async def get_session(self, session_id: Optional[str] = None) -> Session:
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            session.last_active = datetime.now()
            return session
            
        new_session = Session(session_id)
        self.sessions[new_session.id] = new_session
        return new_session
        
    async def end_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            
    async def _cleanup_old_sessions(self):
        while True:
            await asyncio.sleep(300)  # Check every 5 minutes
            now = datetime.now()
            expired = [
                sid for sid, session in self.sessions.items()
                if now - session.last_active > timedelta(hours=1)
            ]
            for sid in expired:
                await self.end_session(sid) 