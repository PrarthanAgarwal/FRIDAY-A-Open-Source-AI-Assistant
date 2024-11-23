from faster_whisper import WhisperModel
from pathlib import Path
from typing import Optional
from loguru import logger
from ..core.config import FridayConfig

class WhisperHandler:
    def __init__(self, config: FridayConfig):
        self.config = config
        self.model = None
        self.initialize_model()

    def initialize_model(self):
        """Initialize the Faster Whisper model"""
        try:
            # Convert cuda:0 to cuda for faster-whisper compatibility
            device = "cuda" if "cuda" in self.config.system.device else "cpu"
            
            self.model = WhisperModel(
                model_size_or_path=str(self.config.models.WHISPER_PATH),
                device=device,
                compute_type="float16" if device == "cuda" else "int8",
                num_workers=self.config.system.num_threads
            )
            logger.info(f"Faster Whisper model initialized on {device}")
        except Exception as e:
            logger.error(f"Failed to initialize Whisper model: {e}")
            raise

    async def transcribe(self, audio_path: Path) -> Optional[str]:
        """
        Transcribe audio file to text using Faster Whisper
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            if not self.model:
                raise RuntimeError("Whisper model not initialized")

            # Perform transcription
            segments, _ = self.model.transcribe(
                str(audio_path),
                beam_size=5,
                word_timestamps=True
            )

            # Combine all segments
            text = " ".join([segment.text for segment in segments])
            
            # Clean up the text
            text = text.strip()
            logger.info(f"Transcribed: {text[:100]}...")
            
            return text

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None 