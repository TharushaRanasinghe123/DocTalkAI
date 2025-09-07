# # backend/app/services/elevenlabs_service.py
# import os
# from elevenlabs.client import ElevenLabs
# from elevenlabs import Voice, VoiceSettings
# from dotenv import load_dotenv

# load_dotenv()

# class ElevenLabsService:
#     def __init__(self):
#         self.api_key = os.getenv("ELEVENLABS_API_KEY")
#         if not self.api_key:
#             raise ValueError("ELEVENLABS_API_KEY not set in environment variables")
        
#         self.client = ElevenLabs(api_key=self.api_key)
#         self.voice_id = "Rachel"  # or your preferred voice ID
#         self.model = "eleven_flash_v2"  # Fastest model for real-time
    
#     async def generate_speech(self, text: str):
#         """Generate speech audio from text"""
#         try:
#             # Generate audio stream - NEW SYNTAX
#             audio = self.client.text_to_speech.convert(
#                 text=text,
#                 voice=Voice(
#                     voice_id=self.voice_id,
#                     settings=VoiceSettings(
#                         stability=0.7,
#                         similarity_boost=0.8,
#                         style=0.2,
#                         use_speaker_boost=True
#                     )
#                 ),
#                 model_id=self.model,
#                 output_format="mp3_44100_128"  # Add output format
#             )
            
#             return audio
            
#         except Exception as e:
#             print(f"Error generating speech: {e}")
#             return None
    
#     async def stream_speech_to_client(self, text: str, websocket):
#         """Stream speech audio directly to WebSocket client"""
#         try:
#             audio = await self.generate_speech(text)
#             if audio:
#                 # Convert generator to bytes and send
#                 audio_bytes = b''.join([chunk for chunk in audio])
#                 await websocket.send_bytes(audio_bytes)
#                 print(f"🎵 Sent audio: {len(audio_bytes)} bytes")
#                 print("✅ Speech streaming completed")
#             else:
#                 print("❌ Failed to generate speech")
                
#         except Exception as e:
#             print(f"Error streaming speech: {e}")

# # Global instance
# elevenlabs_service = ElevenLabsService()

# backend/app/services/elevenlabs_service.py
import os
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings
from dotenv import load_dotenv

load_dotenv()

class ElevenLabsService:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not set in environment variables")
        
        self.client = ElevenLabs(api_key=self.api_key)
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # or your preferred voice ID
        self.model = "eleven_flash_v2"  # Fastest model for real-time
    
    async def generate_speech(self, text: str):
        """Generate speech audio from text"""
        try:
            # Fixed syntax - voice settings should be passed differently
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,  # Pass voice_id directly
                model_id=self.model,
                voice_settings=VoiceSettings(  # Pass settings separately
                    stability=0.7,
                    similarity_boost=0.8,
                    style=0.2,
                    use_speaker_boost=True
                ),
                output_format="mp3_44100_128"
            )
            
            return audio
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            print(f"Text attempted: {text}")
            return None
    
    async def stream_speech_to_client(self, text: str, websocket):
        """Stream speech audio directly to WebSocket client"""
        try:
            # Check if websocket is still connected
            if websocket.client_state.name != 'CONNECTED':
                print("❌ WebSocket not connected, skipping speech generation")
                return
                
            print(f"🎵 Generating speech for: {text[:50]}...")
            audio = await self.generate_speech(text)
            
            if audio and websocket.client_state.name == 'CONNECTED':
                # Convert generator to bytes and send
                try:
                    audio_bytes = b''.join([chunk for chunk in audio])
                    await websocket.send_bytes(audio_bytes)
                    print(f"🎵 Sent audio: {len(audio_bytes)} bytes")
                    print("✅ Speech streaming completed")
                except Exception as send_error:
                    print(f"Error sending audio bytes: {send_error}")
            else:
                print("❌ Failed to generate speech or WebSocket disconnected")
                
        except Exception as e:
            print(f"Error streaming speech: {e}")
            print(f"WebSocket state: {websocket.client_state.name if hasattr(websocket, 'client_state') else 'Unknown'}")

# Global instance
elevenlabs_service = ElevenLabsService()