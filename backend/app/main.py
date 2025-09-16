# # backend/app/main.py
# import os
# import json
# import asyncio
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# import websockets
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# app = FastAPI(
#     title="DocTalk A1 API",
#     description="Backend for real-time transcription",
#     version="1.0.0"
# )

# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Deepgram configuration
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
# if not DEEPGRAM_API_KEY:
#     print("WARNING: DEEPGRAM_API_KEY not set. Please set it in .env file")

# DEEPGRAM_URL = f"wss://api.deepgram.com/v1/listen?model=nova-2&encoding=linear16&sample_rate=16000&channels=1"

# @app.get("/")
# async def root():
#     return JSONResponse({
#         "message": "DocTalk A1 API is running",
#         "status": "success",
#         "endpoints": {
#             "root": "/",
#             "health": "/health",
#             "test": "/test",
#             "websocket": "/ws/transcribe"
#         }
#     })

# @app.get("/health")
# async def health_check():
#     return JSONResponse({
#         "status": "healthy",
#         "server": "running",
#         "port": 8001
#     })

# @app.get("/test")
# async def test_endpoint():
#     return JSONResponse({
#         "message": "Test endpoint is working!",
#         "status": "success"
#     })

# @app.websocket("/ws/transcribe")
# async def websocket_transcribe(websocket: WebSocket):
#     """
#     WebSocket endpoint for real-time audio transcription
#     """
#     await websocket.accept()
#     print("Client connected to WebSocket")
    
#     try:
#         # Connect to Deepgram
#         async with websockets.connect(
#             DEEPGRAM_URL,
#             extra_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}
#         ) as deepgram_ws:
#             print("Connected to Deepgram")
            
#             # Start bidirectional communication
#             await asyncio.gather(
#                 receive_audio(websocket, deepgram_ws),
#                 send_transcripts(deepgram_ws, websocket)
#             )
            
#     except WebSocketDisconnect:
#         print("Client disconnected")
#     except Exception as e:
#         print(f"WebSocket error: {e}")
#         await websocket.close(code=1011)

# async def receive_audio(client_ws: WebSocket, deepgram_ws):
#     """
#     Receive audio from client and forward to Deepgram
#     """
#     try:
#         print("🎤 Waiting for audio data from client...")
#         async for message in client_ws.iter_bytes():
#             print(f"📦 Received {len(message)} bytes from client")
#             # Forward audio data to Deepgram
#             await deepgram_ws.send(message)
#             print(f"📤 Forwarded {len(message)} bytes to Deepgram")
#     except Exception as e:
#         print(f"Error receiving audio: {e}")

# async def send_transcripts(deepgram_ws, client_ws: WebSocket):
#     """
#     Receive transcripts from Deepgram and send to client
#     """
#     try:
#         async for message in deepgram_ws:
#             try:
#                 data = json.loads(message)
#                 print(f"Received from Deepgram: {data}")
                
#                 # Extract transcript
#                 transcript = data.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
                
#                 # Only send if we have a transcript
#                 if transcript:
#                     await client_ws.send_json({
#                         "type": "transcript",
#                         "transcript": transcript,
#                         "is_final": data.get("is_final", False)
#                     })
#             except json.JSONDecodeError:
#                 print(f"Failed to parse JSON: {message}")
#     except Exception as e:
#         print(f"Error sending transcripts: {e}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.services import handle_websocket_connection
from app.services.mongodb_service import mongodb_service
from app.routes import appointments
from app.routes import auth

# For debugging WebSocket connections
from starlette.websockets import WebSocketState

# Load environment variables
load_dotenv()

app = FastAPI(
    title="DocTalk A1 API",
    description="Backend for real-time transcription",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "WEBSOCKET", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/")
async def root():
    return JSONResponse({
        "message": "DocTalk A1 API is running",
        "status": "success",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "test": "/test",
            "websocket": "/ws/transcribe"
        }
    })

@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "healthy",
        "server": "running",
        "port": 8001
    })

@app.get("/test")
async def test_endpoint():
    return JSONResponse({
        "message": "Test endpoint is working!",
        "status": "success"
    })

@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio transcription
    """
    print(f"New WebSocket connection request from {websocket.client}")
    try:
        await handle_websocket_connection(websocket)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected normally")
    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close(code=1000)
    finally:
        # Log final state
        print(f"WebSocket connection ended. Client state: {websocket.client_state}")

@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on application startup"""
    success = await mongodb_service.connect()
    if success:
        print("🎯 MongoDB connection established during startup")
    else:
        print("⚠️ MongoDB connection failed during startup")

@app.get("/test-db")
async def test_db_connection():
    """Test endpoint to check MongoDB connection"""
    if mongodb_service.client:
        return {
            "status": "connected", 
            "database": "doctalk_db",
            "message": "MongoDB Atlas connection is working!"
        }
    else:
        return {
            "status": "disconnected", 
            "error": "MongoDB not connected. Check your connection string."
        }

app.include_router(appointments.router, prefix="/api/v1", tags=["appointments"])

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")