import os
import asyncio
import websockets
from fastapi import WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from .audio_processing import receive_audio, send_transcripts
from .websocket_utils import safe_send_json

# Load environment variables from .env file
load_dotenv()

try:
    from app.services.elevenlabs_service import elevenlabs_service
    ELEVENLABS_AVAILABLE = True
    print("✅ ElevenLabs service imported successfully")
except ImportError as e:
    ELEVENLABS_AVAILABLE = False
    print(f"⚠️ ElevenLabs service not available: {e}")

# Import OpenAI service
try:
    from app.services.openai_service import openai_service
    OPENAI_AVAILABLE = True
    print("✅ OpenAI service imported successfully")
except ImportError as e:
    OPENAI_AVAILABLE = False
    print(f"⚠️ OpenAI service not available: {e}")

# Deepgram configuration
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
if not DEEPGRAM_API_KEY:
    print("WARNING: DEEPGRAM_API_KEY not set. Please set it in .env file")

DEEPGRAM_URL = f"wss://api.deepgram.com/v1/listen?model=nova-2&encoding=linear16&sample_rate=16000&channels=1"


async def handle_websocket_connection(websocket: WebSocket):
    """Handle WebSocket connection with Deepgram"""
    await websocket.accept()
    print("Client connected to WebSocket")
    
    try:
        # Connect to Deepgram
        async with websockets.connect(
            DEEPGRAM_URL,
            extra_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
            ping_interval=20,
            ping_timeout=60
        ) as deepgram_ws:
            print("Connected to Deepgram")
            
            # Send initial connection success message
            await safe_send_json(websocket, {
                "type": "connection_status",
                "message": "Connected to speech processing services",
                "services": {
                    "deepgram": True,
                    "openai": OPENAI_AVAILABLE,
                    "elevenlabs": ELEVENLABS_AVAILABLE
                }
            })

            # Create task for receiving audio
            receive_task = asyncio.create_task(receive_audio(websocket, deepgram_ws))
            
            # Create task for sending transcripts with longer timeout
            try:
                await asyncio.wait_for(
                    send_transcripts(deepgram_ws, websocket),
                    timeout=300.0  # 5 minute timeout instead of immediate close
                )
            except asyncio.TimeoutError:
                print("WebSocket session completed naturally")
            
            # Cancel receive task
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
                       
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Clean up - close connection gracefully
        try:
            if websocket.client_state.name == 'CONNECTED':
                await websocket.close()
        except:
            pass  # Ignore if already closed
        print("WebSocket connection cleaned up")