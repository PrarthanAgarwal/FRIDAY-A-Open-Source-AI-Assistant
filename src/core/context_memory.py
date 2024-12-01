from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path
from loguru import logger

@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime
    important: bool = False

class ContextMemory:
    def __init__(self, max_context: int = 10, conversation_timeout: int = 300):  # 5 minutes timeout
        self.max_context = max_context
        self.conversation_timeout = conversation_timeout  # seconds
        self.messages: List[Message] = []
        self.memory_file = Path("context_memory.json")
        self.last_interaction = datetime.now()
        
    def add_message(self, role: str, content: str, important: bool = False) -> None:
        """Add a message to context memory"""
        current_time = datetime.now()
        
        # Check if conversation has timed out
        if (current_time - self.last_interaction).seconds > self.conversation_timeout:
            logger.info("Conversation timed out, clearing context memory")
            self.clear_context()
        
        message = Message(
            role=role,
            content=content,
            timestamp=current_time,
            important=important
        )
        
        self.messages.append(message)
        self.last_interaction = current_time
        
        # Trim context while keeping important messages
        if len(self.messages) > self.max_context:
            important_msgs = [msg for msg in self.messages if msg.important]
            recent_msgs = [msg for msg in self.messages if not msg.important][-self.max_context + len(important_msgs):]
            self.messages = important_msgs + recent_msgs
            
        self._save_memory()
    
    def get_context(self) -> List[Dict]:
        """Get formatted context for LLM"""
        current_time = datetime.now()
        
        # Clear context if conversation has timed out
        if (current_time - self.last_interaction).seconds > self.conversation_timeout:
            self.clear_context()
            return []
            
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "important": msg.important
            }
            for msg in self.messages
        ]
    
    def clear_context(self) -> None:
        """Clear context memory except for important messages"""
        self.messages = [msg for msg in self.messages if msg.important]
        self._save_memory()
        logger.info("Context memory cleared")
    
    def _save_memory(self) -> None:
        """Save memory to file"""
        try:
            memory_data = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "important": msg.important
                }
                for msg in self.messages
            ]
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving context memory: {e}")
    
    def _load_memory(self) -> None:
        """Load memory from file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Only load messages from active conversations
                    current_time = datetime.now()
                    self.messages = [
                        Message(
                            role=msg["role"],
                            content=msg["content"],
                            timestamp=datetime.fromisoformat(msg["timestamp"]),
                            important=msg["important"]
                        )
                        for msg in data
                        if (current_time - datetime.fromisoformat(msg["timestamp"])).seconds <= self.conversation_timeout
                        or msg["important"]
                    ]
            except Exception as e:
                logger.error(f"Error loading context memory: {e}")
                self.messages = []