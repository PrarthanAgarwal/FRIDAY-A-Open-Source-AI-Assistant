from pathlib import Path
from typing import Dict, Optional, Any, Union
import os
from dataclasses import dataclass, field
import torch
import yaml
import json
import nltk
from loguru import logger
from colorama import init, Fore, Style
import sys

@dataclass
class ModelPaths:
    BASE_PATH: Path = Path("models")
    STYLETTS2_PATH: Path = BASE_PATH / "styletts2"
    WHISPER_PATH: Path = BASE_PATH / "faster-whisper-base"
    LLAMA_PATH: Path = BASE_PATH / "llama/Llama-3.2-3B-Instruct-uncensored-Q4_K_M.gguf"
    
    def __post_init__(self):
        """Ensure all paths are Path objects"""
        for field in self.__dataclass_fields__:
            value = getattr(self, field)
            if isinstance(value, str):
                setattr(self, field, Path(value))

@dataclass
class SystemConfig:
    # Hardware settings
    device: str = "cuda:0" if torch.cuda.is_available() else "cpu"
    gpu_layers: int = 35  # Adjust based on VRAM availability for LLaMA
    num_threads: int = 6  # Adjust based on your Ryzen 5 core count
    
    # Audio settings
    sample_rate: int = 16000
    chunk_size: int = 1024
    
    # Inference settings
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.95

@dataclass
class APIConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 60
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None

@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ttl: int = 3600  # Default cache TTL (1 hour)

@dataclass
class WhisperConfig:
    beam_size: int = 5
    word_timestamps: bool = True
    compute_type: str = "float16"  # or "int8" for CPU
    language: Optional[str] = None  # Auto-detect language
    task: str = "transcribe"

class ServerConfig:
    def __init__(self):
        self.host = "0.0.0.0"  # Default host
        self.port = 8000       # Default port

@dataclass
class FridayConfig:
    models: ModelPaths = field(default_factory=ModelPaths)
    system: SystemConfig = field(default_factory=SystemConfig)
    api: APIConfig = field(default_factory=APIConfig)
    server: ServerConfig = field(default_factory=ServerConfig)

    def __post_init__(self):
        """Verify models exist and paths are valid"""
        self._verify_models()
        setup_logging()
    
    def _verify_models(self):
        """Verify all model files exist"""
        required_files = [
            self.models.WHISPER_PATH,
            self.models.LLAMA_PATH,
            self.models.STYLETTS2_PATH
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                raise FileNotFoundError(f"Required model file not found: {file_path}")

class NLTKConfig:
    """NLTK configuration settings"""
    def __init__(self):
        self.data_path = Path("nltk_data")
        self.required_packages = ["punkt"]
        self.language = "english"
        
    def ensure_data(self):
        """Ensure required NLTK data is available"""
        for package in self.required_packages:
            try:
                nltk.data.find(f'tokenizers/{package}')
            except LookupError:
                nltk.download(package)

def setup_logging():
    # Initialize colorama for Windows compatibility
    init()
    
    # Remove default logger
    logger.remove()
    
    # Add file handler for debug/technical logs
    logger.add(
        "logs/debug.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {module}:{function}:{line} - {message}",
        rotation="1 day"
    )
    
    # Custom format function for console output
    def formatter(record):
        if record["extra"].get("speaker") == "user":
            return f"\n{Fore.GREEN}User: {record['message']}{Style.RESET_ALL}"
        elif record["extra"].get("speaker") == "friday":
            return f"\n{Fore.MAGENTA}FRIDAY: {record['message']}{Style.RESET_ALL}\n"
        elif record["extra"].get("status"):
            return f"\n{Fore.CYAN}{record['message']}{Style.RESET_ALL}\n"
        elif record["extra"].get("generation_time"):
            return f"{Fore.YELLOW}{record['message']}{Style.RESET_ALL}"
        return record["message"]
    
    # Add console handler for essential info only
    logger.add(
        sys.stdout,
        level="INFO",
        format=formatter,
        filter=lambda record: record["extra"].get("essential", False)
    )

# Create global config instance
config = FridayConfig() 