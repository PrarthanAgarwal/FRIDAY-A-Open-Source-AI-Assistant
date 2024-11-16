import torch
from threading import Event

# Local imports for handlers
from record import InterruptibleRecorder
from memory import ConversationMemory
from audio_handler import AudioHandler
from tts_handler import TTSHandler
from chat_handler import ChatHandler

# ANSI escape codes for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# Global variables for checkpoints and device
EN_CKPT_BASE = "checkpoints/base_speakers/EN"
CKPT_CONVERTER = "checkpoints/converter"
DEVICE = 'cuda:0' if torch.cuda.is_available() else 'cpu'

# Events for audio control
stop_audio = Event()
current_conversation_active = Event()
voice_detected = Event()

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def user_chatbot_conversation(audio_handler, tts_handler, chat_handler, memory):
    conversation_history = []
    system_message = open_file("Personality.txt")
    recorder = InterruptibleRecorder()
    
    print("\nStarting conversation...")
    
    while True:
        try:
            print("\nListening... (Press ESC to stop)")
            user_input = recorder.speech_to_text()
            
            if user_input.lower() == "exit" or user_input == "interrupted":
                print("\nEnding conversation...")
                break
                
            print(CYAN + "You:", user_input + RESET_COLOR)
            
            # Check for time-related queries first
            if any(word in user_input.lower() for word in ["time", "what time"]):
                response = chat_handler.get_time_info(user_input)
            else:
                print(PINK + "Friday: " + RESET_COLOR, end='')
                response = chat_handler.query_ollama(user_input)
            
            if response:
                # Save to memory if needed
                memory.save_conversation(user_input, response)
                
                # Process and play audio response
                tts_handler.process_and_play(response, "default", 
                                          "resources/example_reference.mp3",
                                          audio_handler)
                
                # Save to conversation history
                conversation_history.append({"role": "user", "content": user_input})
                conversation_history.append({"role": "assistant", "content": response})
                
                # Manage conversation history size
                if len(conversation_history) > 20:
                    conversation_history = conversation_history[-20:]
            
        except Exception as e:
            print(f"\nError in conversation loop: {e}")
            print("Continuing conversation...")
            continue

def main():
    # Initialize handlers
    audio_handler = AudioHandler()
    tts_handler = TTSHandler(EN_CKPT_BASE, CKPT_CONVERTER, DEVICE)
    memory = ConversationMemory()
    chat_handler = ChatHandler(memory)
    
    # Start conversation
    user_chatbot_conversation(
        audio_handler, 
        tts_handler, 
        chat_handler, 
        memory
    )

if __name__ == "__main__":
    main()
