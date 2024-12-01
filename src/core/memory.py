import json
import datetime
from pathlib import Path
import re
from typing import List, Dict, Optional
from loguru import logger

class ConversationMemory:
    def __init__(self, memory_file: str = "conversation_memory.json"):
        """
        Initialize conversation memory system
        
        Args:
            memory_file: Path to the memory storage file
        """
        self.memory_file = Path(memory_file)
        self.conversations: List[Dict] = self._load_memory()
        
        # Enhanced memory triggers with more natural language patterns
        self.memory_triggers = {
            'explicit': [
                "remember",
                "don't forget",
                "make a note",
                "save this",
                "store this",
                "memorize",
                "keep this in mind",
                "important",
                "note this",
                "write this down"
            ],
            'personal': [
                "my name is",
                "i am",
                "i'm",
                "my birthday",
                "my address",
                "my phone",
                "my email",
                "call me"
            ],
            'preference': [
                "i like",
                "i love",
                "i hate",
                "i prefer",
                "favorite",
                "don't like"
            ],
            'temporal': [
                "remind me",
                "schedule",
                "appointment",
                "meeting",
                "deadline"
            ]
        }
        
        # Enhanced topic detection
        self.topic_keywords = {
            "personal": [
                "name", "age", "birthday", "family", "friend",
                "address", "phone", "email", "contact"
            ],
            "task": [
                "reminder", "todo", "task", "schedule", "appointment",
                "deadline", "meeting", "project"
            ],
            "preference": [
                "like", "dislike", "prefer", "favorite", "hate",
                "love", "enjoy", "interest"
            ],
            "fact": [
                "fact", "information", "data", "detail", "knowledge",
                "remember", "note"
            ],
            "temporal": [
                "time", "date", "schedule", "when", "appointment",
                "deadline", "reminder"
            ]
        }

    def _load_memory(self) -> List[Dict]:
        """Load memory from file, create new if doesn't exist or is corrupted"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    try:
                        return json.load(f)
                    except json.JSONDecodeError:
                        logger.error("Memory file corrupted, creating new memory file")
                        return []
            else:
                logger.info("Creating new memory file")
                self.memory_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.memory_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                return []
        except Exception as e:
            logger.error(f"Error loading memory file: {e}")
            return []

    def should_remember(self, text: str) -> bool:
        """
        Check if the conversation should be remembered based on triggers
        
        Args:
            text: Input text to check
            
        Returns:
            bool: True if text contains any memory triggers
        """
        text = text.lower()
        
        # Check all trigger categories
        for category, triggers in self.memory_triggers.items():
            if any(trigger in text for trigger in triggers):
                return True
                
        return False

    async def save(self, user_input: str, assistant_response: str) -> bool:
        """
        Save conversation if it contains important information
        
        Args:
            user_input: User's message
            assistant_response: Assistant's response
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if self.should_remember(user_input) or self.should_remember(assistant_response):
                timestamp = datetime.datetime.now().isoformat()
                tags = self._extract_tags(user_input, assistant_response)
                
                conversation = {
                    "timestamp": timestamp,
                    "user": user_input,
                    "assistant": assistant_response,
                    "tags": tags,
                    "category": self._determine_category(tags)
                }
                
                self.conversations.append(conversation)
                
                # Save with proper formatting and encoding
                with open(self.memory_file, 'w', encoding='utf-8') as f:
                    json.dump(self.conversations, f, indent=2, ensure_ascii=False)
                    
                logger.info(f"Saved memory with tags: {tags}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
            
        return False

    def _extract_tags(self, user_input: str, assistant_response: str) -> List[str]:
        """Extract relevant tags from conversation"""
        combined_text = f"{user_input} {assistant_response}".lower()
        tags = set()
        
        # Check each topic category
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                tags.add(topic)
        
        # Extract potential dates
        date_patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',  # DD/MM/YYYY
            r'\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)',  # 23rd October
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                tags.add("date")
                
        return list(tags)

    def _determine_category(self, tags: List[str]) -> str:
        """Determine primary category based on tags"""
        priority_order = ["personal", "temporal", "task", "preference", "fact"]
        for category in priority_order:
            if category in tags:
                return category
        return "general"

    def search_memory(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search through stored memories
        
        Args:
            query: Search term
            limit: Maximum number of results
            
        Returns:
            List of matching conversations
        """
        query = query.lower()
        results = []
        
        for conv in self.conversations:
            relevance_score = 0
            
            # Check content
            if query in conv["user"].lower():
                relevance_score += 2
            if query in conv["assistant"].lower():
                relevance_score += 1
            if query in " ".join(conv.get("tags", [])):
                relevance_score += 3
                
            if relevance_score > 0:
                results.append((relevance_score, conv))
                
        # Sort by relevance and return top results
        results.sort(key=lambda x: (-x[0], x[1]["timestamp"]), reverse=True)
        return [conv for _, conv in results[:limit]]

    def get_recent_conversations(self, limit=5, topic=None):
        """Get recent conversations, optionally filtered by topic"""
        if topic:
            filtered = [conv for conv in self.conversations if topic in conv.get("tags", [])]
            return filtered[-limit:] if filtered else []
        return self.conversations[-limit:] if self.conversations else []

    def _load_conversations(self):
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return []