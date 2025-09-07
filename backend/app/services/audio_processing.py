# app/services/audio_processing.py
import json
import asyncio
from fastapi import WebSocket

from app.services import conversation_service
from .transcript_buffer import TranscriptBuffer
from .websocket_utils import safe_send_json
from app.models.conversation import ConversationState


try:
    from app.services.elevenlabs_service import elevenlabs_service
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

try:
    from app.services.openai_service import openai_service
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

conversation_states = {}


async def receive_audio(client_ws: WebSocket, deepgram_ws):
    """Receive audio from client and forward to Deepgram"""
    try:
        print("🎤 Waiting for audio data from client...")
        async for message in client_ws.iter_bytes():
            try:
                print(f"📦 Received {len(message)} bytes from client")
                # Forward audio data to Deepgram
                await deepgram_ws.send(message)
                print(f"📤 Forwarded {len(message)} bytes to Deepgram")
            except Exception as e:
                print(f"Error forwarding audio: {e}")
                break
    except Exception as e:
        print(f"Error receiving audio: {e}")


async def process_complete_sentence(client_ws, transcript):
    """Process a complete sentence with OpenAI and convert response to speech"""
    try:
        # Check if WebSocket is still connected before processing
        if client_ws.client_state.name != 'CONNECTED':
            print(f"⚠️ WebSocket not connected, skipping processing for: {transcript}")
            return
            
        print(f"🔄 Processing complete sentence: {transcript}")
        intent_response = await openai_service.analyze_intent(transcript)

        if client_ws not in conversation_states:
            conversation_states[client_ws] = ConversationState()
        current_state = conversation_states[client_ws]

        response_text, updated_state = await conversation_service.process_intent(intent_response, current_state)
        conversation_states[client_ws] = updated_state # Update the state
        
        intent_response.processed_response = response_text

        print(f"✅ Intent: {intent_response.intent}")
        print(f"📋 Entities: {intent_response.entities}")
        print(f"🎯 Confidence: {intent_response.confidence}")
        print(f"💬 Response: {intent_response.processed_response}")
        
        # Send intent response first (always works)
        success = await safe_send_json(client_ws, {
            "type": "intent",
            "transcript": transcript,
            "intent": intent_response.intent,
            "entities": intent_response.entities,
            "confidence": intent_response.confidence,
            "processed_response": intent_response.processed_response,
            "is_final": True
        })
        
        if not success:
            print("❌ Failed to send intent response - client disconnected")
            return

        # Try speech generation (may fail, but don't break the flow)
        if (ELEVENLABS_AVAILABLE and 
            intent_response.processed_response and 
            client_ws.client_state.name == 'CONNECTED'):
            
            try:
                print(f"🎵 Generating speech: {intent_response.processed_response}")
                
                # Send speech start signal
                await safe_send_json(client_ws, {
                    "type": "speech_start",
                    "message": "AI is responding..."
                })

                audio = await elevenlabs_service.generate_speech(intent_response.processed_response)

                
                # CHECK CONNECTION AGAIN before sending audio
                if client_ws.client_state.name == 'CONNECTED' and audio:
                    # Convert to bytes and send
                    audio_bytes = b''.join([chunk for chunk in audio])
                    await client_ws.send_bytes(audio_bytes)
                    print(f"✅ Sent audio: {len(audio_bytes)} bytes")
                    
                    # Send speech end signal
                    await safe_send_json(client_ws, {
                        "type": "speech_end", 
                        "message": "AI finished speaking"
                    })
                else:
                    print("❌ Connection closed during audio generation")
                
            except Exception as speech_error:
                print(f"🔊 Speech generation failed (continuing without audio): {speech_error}")
                # Send speech error signal to frontend
                await safe_send_json(client_ws, {
                    "type": "speech_error",
                    "message": "Text-to-speech unavailable, continuing with text only",
                    "error": str(speech_error)
                })
        else:
            print("🔇 Speech generation skipped (service unavailable or no response text)")
        
    except Exception as e:
        print(f"❌ Error in intent processing: {e}")
        # Fallback: send just the transcript if connection is still active
        await safe_send_json(client_ws, {
            "type": "transcript",
            "transcript": transcript,
            "is_final": True,
            "error": "Intent processing failed"
        })


async def send_transcripts(deepgram_ws, client_ws: WebSocket):
    """Receive transcripts from Deepgram, buffer sentences, and send complete ones to OpenAI"""
    transcript_buffer = TranscriptBuffer()
    
    try:
        print("🎧 Starting to listen for Deepgram responses...")
        async for message in deepgram_ws:
            try:
                # Check if client is still connected
                if client_ws.client_state.name != 'CONNECTED':
                    print("Client disconnected, stopping transcript processing")
                    break

                print(f"📨 Raw message from Deepgram: {message[:100]}...")   
                data = json.loads(message)
                print(f"📊 Parsed Deepgram data: {data}")
                
                # Extract transcript
                transcript = data.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
                is_final = data.get("is_final", False)
                
                # Only process if we have a transcript
                if transcript:
                    # Check for complete sentence
                    complete_sentence = transcript_buffer.add_transcript(transcript, is_final)
                    
                    if complete_sentence:
                        print(f"🎯 Complete sentence detected: {complete_sentence}")
                        # Process in background to avoid blocking
                        await process_complete_sentence(client_ws, complete_sentence)
                                            
                    # Send interim transcripts for real-time display (only if connected)
                    await safe_send_json(client_ws, {
                        "type": "transcript",
                        "transcript": transcript,
                        "is_final": is_final,
                        "is_interim": not is_final
                    })
                        
            except json.JSONDecodeError:
                print(f"Failed to parse JSON: {message}")
            except Exception as e:
                print(f"Error processing message: {e}")
                
        # Process any remaining text when Deepgram connection closes
        final_sentence = transcript_buffer.get_final_buffer()
        if final_sentence and client_ws.client_state.name == 'CONNECTED':
            print(f"📚 Processing final buffer: {final_sentence}")
            await process_complete_sentence(client_ws, final_sentence)
            
    except Exception as e:
        print(f"Error in send_transcripts: {e}")