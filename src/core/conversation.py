from loguru import logger
from pathlib import Path
from threading import Event
import asyncio
from colorama import init, Fore, Style

class ConversationHandler:
    def __init__(self, llm, recorder, memory):
        self.llm = llm
        self.recorder = recorder
        self.memory = memory
        self.stop_event = Event()
        
        # Import the TTS handler directly from testen.py
        from models.StyleTTS2.testen import tts_handler
        self.tts = tts_handler

    async def start_conversation(self):
        logger.info("Starting FRIDAY...\n", essential=True)
        
        while not self.stop_event.is_set():
            try:
                # Show listening status
                logger.info("🎤 Listening... (Press ESC to stop)", essential=True, status=True)
                
                user_input = await self.recorder.record()
                
                if user_input and user_input.lower() == "exit" or user_input == "interrupted":
                    logger.info("\nGoodbye!", essential=True)
                    break
                    
                if user_input:
                    # Log user input in green
                    logger.info(f"{user_input}", essential=True, speaker="user")
                
                    response = await self.llm.create_completion(user_input)
                    
                    if response:
                        # Log FRIDAY's response in pink/magenta
                        logger.info(f"{response}", essential=True, speaker="friday")
                        # Optional: Log generation time in yellow
                        if hasattr(self.llm, 'generation_time'):
                            logger.info(f"Generation time: {self.llm.generation_time:.2f}s", 
                                      essential=True, generation_time=True)
                        
                        await self.memory.save(user_input, response)
                        audio_file = await self.tts.generate_speech(response)
                        if audio_file:
                            await self.tts.play(audio_file)
                
            except Exception as e:
                logger.error(f"Error in conversation loop: {e}")
                await asyncio.sleep(0.1)
                continue 