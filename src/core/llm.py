from llama_cpp import Llama
from .config import config
from ..utils.logger import get_logger
import os
import torch
import gc
from loguru import logger
from pathlib import Path
import sys
import contextlib

logger = get_logger()

class LLMHandler:
    def __init__(self):
        try:
            model_path = str(config.models.LLAMA_PATH)
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"LLaMA model not found at: {model_path}")
            
            if torch.cuda.is_available():
                logger.info(f"CUDA available: {torch.cuda.get_device_name()}")
                logger.info(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
                torch.cuda.empty_cache()
                gc.collect()
            
            logger.info("Initializing LLaMA with exact model specifications")
            
            # Redirect stdout temporarily to suppress llama.cpp debug output
            with self._suppress_output():
                # Settings exactly matching your model's metadata
                self.model = Llama(
                    model_path=model_path,
                    n_ctx=2048,
                    n_batch=8,
                    n_threads=4,
                    n_gpu_layers=1,
                    f16_kv=True,
                    vocab_only=False,
                    use_mmap=False,
                    use_mlock=False,
                    embedding=False,
                    n_gqa=3,
                    rms_norm_eps=0.000009999999747378752,
                    rope_freq_base=500000,
                    rope_freq_scale=1.0,
                    logits_all=False,
                    verbose=False  # Set to False to reduce output
                )
            
            logger.info("Model initialized, testing...")
            # Suppress output during test
            with self._suppress_output():
                test = self.model.create_completion("Test", max_tokens=1)
            logger.info("Model test successful")
            
            # Load personality file
            personality_path = Path("Personality.txt")
            with open(personality_path, 'r') as f:
                self.personality = f.read().strip()
            
        except Exception as e:
            import traceback
            detailed_error = f"Failed to initialize LLaMA: {str(e)}\n"
            detailed_error += f"Traceback: {traceback.format_exc()}"
            logger.error(detailed_error)
            raise RuntimeError(detailed_error)

    @contextlib.contextmanager
    def _suppress_output(self):
        """Context manager to temporarily suppress stdout and stderr"""
        # Save the current stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        # Create a dummy file-like object
        null = open(os.devnull, 'w')
        
        try:
            # Redirect stdout and stderr to the null device
            sys.stdout = null
            sys.stderr = null
            yield
        finally:
            # Restore stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            null.close()
    
    async def create_completion(self, prompt: str) -> str:
        """
        Create a completion for the given prompt using LLaMA
        """
        try:
            if not hasattr(self, 'personality'):
                personality_path = Path("Personality.txt")
                with open(personality_path, 'r') as f:
                    self.personality = f.read().strip()
            
            formatted_prompt = (
                f"{self.personality}\n\n"
                f"Human: {prompt}\n"
                "Assistant:"
            )
            
            # Suppress debug output during completion
            with self._suppress_output():
                response = self.model.create_completion(
                    formatted_prompt,
                    max_tokens=150,
                    temperature=0.7,
                    top_p=0.9,
                    stop=["Human:", "Assistant:", "\n\n"],
                    stream=False,
                    repeat_penalty=1.5
                )
            
            if isinstance(response, dict) and 'choices' in response:
                return response['choices'][0]['text'].strip()
            
            return str(response).strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""