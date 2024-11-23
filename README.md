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

- **Advanced Voice Interface**
  - Real-time voice synthesis using StyleTTS2
  - Fast transcription with faster-whisper
  - Voice interrupt capability during responses
  
- **Intelligent Processing**
  - Local LLM processing via llama.cpp
  - Context-aware memory system
  - Natural language command parsing
  
- **System Integration**
  - Device control capabilities
  - Sensor data processing
  - Task automation
  - External service integration

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
  model: "llama2-7b-chat"
  quantization: "q4_K_M"
  
system:
  parallel_processing: true
  cache_enabled: true
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Special thanks to the open-source community and the creators of:
- StyleTTS2
- faster-whisper
- llama.cpp
- FastAPI
- Home Assistant

---

<p align="center">Made with ❤️ for the AI Assistant community</p>
