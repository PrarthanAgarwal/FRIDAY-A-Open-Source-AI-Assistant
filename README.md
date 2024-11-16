# F.R.I.D.A.Y - Friendly, Reliable, Intelligent Digital Assistant for You

FRIDAY is an advanced speech-to-speech AI assistant that offers natural voice interactions. Powered by OpenVoice for voice cloning, Whisper for speech recognition, and Ollama's language models for intelligent responses, FRIDAY provides a seamless conversational experience.

## Features

- **Natural Voice Interaction**: Speak naturally and get voice responses
- **Intelligent Conversations**: Context-aware responses with personality
- **Voice Interruption**: Interrupt FRIDAY's response by speaking
- **Memory System**: Remembers important conversations and context
- **Time Queries**: Get current time information
- **ESC to Stop**: Easy control with escape key to stop interactions

## Tech Stack

- **OpenVoice**: Voice cloning and synthesis
- **Whisper**: Speech-to-text transcription
- **Ollama**: Local LLM hosting (using llama3.2)
- **PyAudio**: Audio handling
- **WebRtcVadRecorder**: Voice activity detection
- **Python 3.10+**: Core programming language

## Project Structure

```plaintext
FRIDAY/
├── talk.py              # Main controller
├── audio_handler.py     # Audio playback management
├── chat_handler.py      # LLM interaction & response
├── memory.py            # Conversation memory
├── record.py            # Voice recording & transcription
├── tts_handler.py       # Text-to-speech processing
└── Personality.txt      # Assistant personality config
```

## Prerequisites

1. **Python Environment**
   - Create a virtual environment (pyenv/virtualenv)
   - Python 3.10+ recommended

2. **OpenVoice Setup**
   - Follow [OpenVoice installation](https://github.com/myshell-ai/OpenVoice)
   - Download required checkpoints

3. **Ollama Setup**
   - Install [Ollama](https://ollama.ai/)
   - Pull llama3.2 model: `ollama pull llama3.2`

4. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Activate your virtual environment
2. Start Ollama server
3. Run FRIDAY:
   ```bash
   python talk.py
   ```
4. Start speaking when prompted
5. Press ESC to stop recording or interrupt responses

## Voice Commands

- Speak naturally to interact
- Use "exit" to end conversation
- Press ESC to stop current interaction
- Speak during response to interrupt

## Memory System

FRIDAY remembers conversations when:
- Explicitly asked to remember
- Important information is shared
- Context needs to be maintained

## Contributing

Feel free to contribute to FRIDAY's development:
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
