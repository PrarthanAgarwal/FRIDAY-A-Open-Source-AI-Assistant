import json
import datetime
from pathlib import Path

class ConversationMemory:
    def __init__(self, memory_file="conversation_memory.json"):
        self.memory_file = Path(memory_file)
        self.conversations = self._load_memory()

    def _load_memory(self):
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return []

    def save_conversation(self, user_input, assistant_response):
        timestamp = datetime.datetime.now().isoformat()
        conversation = {
            "timestamp": timestamp,
            "user": user_input,
            "assistant": assistant_response
        }
        self.conversations.append(conversation)
        
        with open(self.memory_file, 'w') as f:
            json.dump(self.conversations, f, indent=2)

    def get_recent_conversations(self, limit=5):
        return self.conversations[-limit:] if self.conversations else [] 