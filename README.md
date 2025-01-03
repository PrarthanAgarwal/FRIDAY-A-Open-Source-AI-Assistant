# F.R.I.D.A.Y MARK II
### Friendly, Reliable, Intelligent Digital Assistant for You

FRIDAY (MARK II) is a powerful, open-source AI assistant designed for real-time interaction and system integration. This next-generation release focuses on dramatic performance improvements and enhanced capabilities while maintaining a completely open-source architecture.

## ✨ What's New in MARK II

- **5x Faster Response Time**: Reduced from 15-20s to 2.5-5s
- **Parallel Processing**: Handle multiple operations simultaneously
- **Enhanced Voice Interaction**: Improved voice clarity and reduced latency
- **Real-time Processing**: Streaming responses and continuous interaction
- **Modular Architecture**: Plug-and-play capability for custom extensions

## 🚀 Core Features

<details>
<summary><b>Advanced Voice Interface</b></summary>

- Real-time voice synthesis using StyleTTS2
- Fast transcription with faster-whisper
- Voice interrupt capability during responses
</details>

<details>
<summary><b>Intelligent Processing</b></summary>

- Local LLM processing via llama.cpp
- Advanced memory systems:
  - Context-aware short-term memory
  - Long-term conversation storage
  - Automatic importance detection
  - Tag-based memory retrieval
- Natural language command parsing
</details>

<details>
<summary><b>Memory System</b></summary>

- Contextual conversation tracking
- Automatic importance detection
- Personal preference learning
- Tag-based memory organization:
  - Personal facts
  - Preferences
  - Temporal information
  - Tasks and reminders
- Conversation timeout management
- Memory persistence across sessions
</details>

<details>
<summary><b>System Integration</b></summary>

- Device control capabilities
- Sensor data processing
- Task automation
- External service integration
</details>

## 🏗️ Architecture

```
FRIDAY Core
├── Voice Interface
│   ├── StyleTTS2 (Speech Synthesis)
│   └── faster-whisper (Speech Recognition)
├── Brain
│   ├── LocalAI/llama.cpp
│   ├── Memory System
│   └── Command Parser
├── Skills System
│   ├── Core Skills
│   └── Custom Plugins
└── System Integration
    ├── Device Control
    ├── Sensor Processing
    ├── Task Automation
    └── External Services
```

## 🛠️ Tech Stack

- **FastAPI/gRPC**: Microservices communication
- **Redis**: Real-time state management
- **StyleTTS2**: Voice synthesis
- **faster-whisper**: Speech recognition
- **llama.cpp**: Local LLM inference
- **Home Assistant**: Device control integration

## ⚡ Performance Comparison

| Metric | MARK I | MARK II |
|--------|---------|----------|
| Response Time | 15-20s | 2.5-5s |
| Processing | Sequential | Parallel |
| Operations | Single | Multiple |
| Voice Quality | Good | Enhanced |

## 🚦 Getting Started

```bash
# Clone the repository
git clone https://github.com/your-username/friday-mark-ii.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start FRIDAY
python friday.py
```

## 📋 Requirements

- Python 3.8+
- CUDA-compatible GPU (recommended)
- 8GB+ RAM
- 20GB disk space

## 🔧 Configuration

Create a `config.yaml` file in the root directory:

```yaml
voice:
  engine: "styletts2"
  language: "en"
  
llm:
  model: "llama3.2-3b"
  quantization: "q4_K_M"
  
system:
  parallel_processing: true
  cache_enabled: true
  memory:
    context_size: 10
    conversation_timeout: 300
    persistence: true
    tags:
      - personal
      - preference
      - temporal
      - task
      - fact
```

## 🤝 Required Model Files

The following model files need to be downloaded and placed in the `models/` directory:

```
models/
├── faster-whisper-base/
│   ├── config.json
│   ├── model.bin
│   ├── tokenizer.json
│   └── vocabulary.txt
└── llama/
    └── llama-3.2-3B-instruct-uncensored.gguf
```

### Model Downloads
- **Faster Whisper**: Download the base model from [HuggingFace](https://huggingface.co/guillaumekln/faster-whisper-base)
- **Llama**: Download the quantized model from [HuggingFace](https://huggingface.co/TheBloke/Llama-2-3B-GGUF)

> Note: Due to size limitations, model files are not included in this repository. Please download them separately using the links above.

## 🙏 Acknowledgments

Special thanks to the open-source community and the creators of:
- StyleTTS2
- faster-whisper
- llama.cpp
- FastAPI
- Home Assistant

---

<p align="center">Made with a dream of matching Tony Stark </p>
