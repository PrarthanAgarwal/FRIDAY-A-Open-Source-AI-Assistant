from faster_whisper import WhisperModel
import torch
from loguru import logger
from pathlib import Path
from ..core.config import config
from typing import Optional

class STTHandler:
    def __init__(self):
        # Check CUDA availability and compute capability
        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "float16"
        else:
            device = "cpu"
            compute_type = "int8"

        logger.info(f"Initializing Whisper model on {device} with compute type {compute_type}")
        
        # Convert Path to string if it's a Path object
        model_path = str(getattr(config.models, 'WHISPER_PATH', "medium"))
        
        try:
            self.model = WhisperModel(
                model_size_or_path=model_path,
                device=device,
                compute_type=compute_type,
                device_index=0,
                cpu_threads=4
            )
            logger.info("Whisper model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Whisper model: {e}")
            # Fallback to medium model if local model fails
            logger.info("Attempting to fall back to medium model...")
            self.model = WhisperModel(
                model_size_or_path="medium",
                device=device,
                compute_type=compute_type,
                device_index=0,
                cpu_threads=4
            )

    async def transcribe(self, audio_data):
        try:
            segments, _ = self.model.transcribe(audio_data, beam_size=5)
            return " ".join([segment.text for segment in segments])
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise

class VoiceProcessor:
    def __init__(self):
        self.stt = STTHandler()
        logger.info("Voice processor initialized")

    async def transcribe(self, audio_path: Path) -> Optional[str]:
        """
        Transcribe audio file to text using the STT handler
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            # Delegate transcription to STT handler
            return await self.stt.transcribe(audio_path)
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None