from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import asyncio
from loguru import logger

from ..core.session import SessionManager
from ..voice.tts import TTSHandler
from ..core.llm import LLMHandler
from ..voice.stt import VoiceProcessor
from ..voice.recorder import InterruptibleRecorder
from ..core.conversation import ConversationHandler
from ..core.config import FridayConfig

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    stream: bool = False

class ChatResponse(BaseModel):
    text: str
    audio: Optional[bytes] = None
    session_id: str

app = FastAPI(
    title="FRIDAY MARK II",
    description="AI Assistant with voice capabilities",
    version="2.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers
voice_processor = None
session_manager = None
conversation_handler = None

@app.on_event("startup")
async def startup_event():
    """Initialize all handlers during startup"""
    global voice_processor, session_manager, conversation_handler
    
    try:
        # Load config first
        config = FridayConfig()
        
        voice_processor = VoiceProcessor()
        session_manager = await SessionManager().setup()
        
        # Initialize conversation handler with necessary components
        conversation_handler = ConversationHandler(
            llm=LLMHandler(),
            recorder=InterruptibleRecorder(voice_processor),
            tts=TTSHandler(config),
            memory=session_manager.memory
        )
        
        logger.info("All handlers initialized successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = None
    
    try:
        while True:
            message = await websocket.receive_json()
            
            if message.get("type") == "start_conversation":
                # Start voice conversation mode
                await conversation_handler.start_conversation(
                    websocket=websocket,
                    session_id=message.get("session_id")
                )
            elif message.get("type") == "stop_conversation":
                conversation_handler.stop_event.set()
                await websocket.send_json({"status": "conversation_ended"})
            elif message.get("type") == "audio":
                # Handle regular audio processing
                audio_data = message.get("data")
                text, audio = await voice_processor.process_parallel(audio_data)
                
                response = {
                    "text": text,
                    "session_id": session_id
                }
                
                await websocket.send_json(response)
                if audio is not None:
                    await websocket.send_bytes(audio)
            
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
    finally:
        if session_id and session_manager:
            await session_manager.end_session(session_id)
        await websocket.close()

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        session = await session_manager.get_session(request.session_id)
        response = await session.process_message(request.message)
        
        audio = None
        if not request.stream:
            audio = await voice_processor.tts.generate_speech(response)
            
        return ChatResponse(
            text=response,
            audio=audio.cpu().numpy().tobytes() if audio is not None else None,
            session_id=session.id
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "voice_processor": voice_processor is not None,
            "session_manager": session_manager is not None
        }
    }

def start_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    start_server()
