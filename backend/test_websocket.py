# test_websocket.py
import asyncio
import websockets

async def test_connection():
    try:
        async with websockets.connect('ws://localhost:8001/ws/transcribe') as ws:
            print("✅ WebSocket connection established successfully!")
            # Listen for a initial message
            message = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print(f"📥 Received message: {message}")
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

asyncio.run(test_connection())