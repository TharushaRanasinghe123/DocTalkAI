# quick_test.py
import asyncio
import websockets
import json

async def simple_test():
    uri = "ws://localhost:8001/ws/transcribe"
    
    async with websockets.connect(uri) as websocket:
        print("Connected - sending simple test tone...")
        
        # Create a very simple 1-second tone (16kHz, 16-bit, mono)
        sample_rate = 16000
        duration = 1.0  # 1 second
        samples = int(sample_rate * duration)
        
        # Generate a simple square wave
        audio_data = b''.join([
            (32767 if i % 100 < 50 else -32767).to_bytes(2, 'little', signed=True)
            for i in range(samples)
        ])
        
        # Send the audio
        await websocket.send(audio_data)
        print(f"Sent {len(audio_data)} bytes of test audio")
        
        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            print(f"✅ Got response: {response[:100]}...")
        except asyncio.TimeoutError:
            print("❌ No response within 10 seconds")

asyncio.run(simple_test())