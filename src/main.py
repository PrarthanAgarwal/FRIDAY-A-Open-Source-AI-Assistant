import asyncio
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from loguru import logger

from src.api.server import app as api_app
from src.core.config import config
from src.tts.styletts2_handler import StyleTTS2Handler

def setup_routes():
    app = FastAPI(title="FRIDAY MARK II")
    app.mount("/api", api_app)
    return app

async def startup():
    logger.info("Initializing FRIDAY MARK II...")
    required_paths = [
        config.models.WHISPER_PATH,
        config.models.STYLETTS2_PATH,
        config.models.LLAMA_PATH
    ]
    
    for path in required_paths:
        if not Path(path).exists():
            logger.error(f"Required model not found: {path}")
            raise FileNotFoundError(f"Missing model: {path}")
    
    logger.info("FRIDAY MARK II ready!")

def main():
    app = setup_routes()
    app.add_event_handler("startup", startup)
    
    logger.info("Starting FRIDAY MARK II server...")
    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
        log_level="info"
    )

if __name__ == "__main__":
    main() 