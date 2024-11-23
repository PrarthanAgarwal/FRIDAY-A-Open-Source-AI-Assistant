import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from src.core.llm import LLMHandler
from src.voice.recorder import InterruptibleRecorder
from src.voice.stt import VoiceProcessor
from src.core.conversation import ConversationHandler
from src.core.config import FridayConfig
from src.core.memory import ConversationMemory

async def main():
    try:
        # Initialize config
        config = FridayConfig()
        
        # Initialize components
        voice_processor = VoiceProcessor()
        llm = LLMHandler()
        recorder = InterruptibleRecorder(voice_processor)
        memory = ConversationMemory()
        
        # Create conversation handler (no need to pass TTS separately)
        conversation = ConversationHandler(
            llm=llm,
            recorder=recorder,
            memory=memory
        )
        
        # Start conversation
        await conversation.start_conversation()
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
