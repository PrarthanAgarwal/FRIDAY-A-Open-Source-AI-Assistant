import json
import datetime
from pathlib import Path
import re

class ConversationMemory:
    def __init__(self, memory_file="conversation_memory.json"):
        self.memory_file = Path(memory_file)
        self.conversations = self._load_memory()
        # Keywords that trigger memory storage
        self.memory_triggers = [
            "remember",
            "don't forget",
            "make a note",
            "save this",
            "store this",
            "memorize",
            "keep this in mind"
        ]

    def _load_memory(self):
        """Load memory from file, create new if doesn't exist or is corrupted"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r') as f:
                    try:
                        return json.load(f)
                    except json.JSONDecodeError:
                        print("Memory file corrupted, creating new memory file")
                        return []
            else:
                # Create new file with empty array
                with open(self.memory_file, 'w') as f:
                    json.dump([], f)
                return []
        except Exception as e:
            print(f"Error loading memory file: {e}")
            return []

    def should_remember(self, text):
        """Check if the conversation should be remembered based on triggers"""
        text = text.lower()
        return any(trigger in text for trigger in self.memory_triggers)

    def save_conversation(self, user_input, assistant_response):
        # Only save if there's a memory trigger in either input or response
        if self.should_remember(user_input) or self.should_remember(assistant_response):
            timestamp = datetime.datetime.now().isoformat()
            conversation = {
                "timestamp": timestamp,
                "user": user_input,
                "assistant": assistant_response,
                "tags": self._extract_tags(user_input, assistant_response)
            }
            self.conversations.append(conversation)
            
            with open(self.memory_file, 'w') as f:
                json.dump(self.conversations, f, indent=2)
            return True
        return False

    def _extract_tags(self, user_input, assistant_response):
        """Extract potential tags/topics from the conversation"""
        combined_text = f"{user_input} {assistant_response}".lower()
        # Add basic topic detection logic here
        tags = []
        
        # Common topics to track
        topic_keywords = {
            "personal": ["name", "age", "birthday", "family", "friend"],
            "task": ["reminder", "todo", "task", "schedule", "appointment"],
            "preference": ["like", "dislike", "prefer", "favorite"],
            "fact": ["fact", "information", "data", "detail"],
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                tags.append(topic)
                
        return list(set(tags))  # Remove duplicates

    def get_recent_conversations(self, limit=5, topic=None):
        """Get recent conversations, optionally filtered by topic"""
        if topic:
            filtered = [conv for conv in self.conversations if topic in conv.get("tags", [])]
            return filtered[-limit:] if filtered else []
        return self.conversations[-limit:] if self.conversations else []

    def search_memory(self, query):
        """Search through stored memories"""
        query = query.lower()
        results = []
        for conv in self.conversations:
            if (query in conv["user"].lower() or 
                query in conv["assistant"].lower() or 
                query in " ".join(conv.get("tags", []))):
                results.append(conv)
        return results