# test_full_pipeline.py
import asyncio
import json
from pathlib import Path
from app.services.openai_service import openai_service
from app.services.elevenlabs_service import elevenlabs_service

async def test_complete_ai_pipeline():
    """Test the complete AI pipeline: Input text → OpenAI → ElevenLabs → Audio"""
    print("🧪 Testing Complete AI Pipeline")
    print("=" * 50)
    
    # Test inputs - try different types of queries
    test_queries = [
        "Hello, how are you today?",
        "What's the weather like?",
        "Can you tell me a joke?",
        "What time is it?",
        "How does this voice sound?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔹 Test {i}: '{query}'")
        print("-" * 30)
        
        try:
            # Step 1: Process with OpenAI
            print("1. 🤖 Processing with OpenAI...")
            intent_response = await openai_service.analyze_intent(query)
            
            if not hasattr(intent_response, 'processed_response') or not intent_response.processed_response:
                print("❌ No response from OpenAI")
                continue
                
            print(f"✅ OpenAI Response: {intent_response.processed_response}")
            print(f"   Intent: {getattr(intent_response, 'intent', 'N/A')}")
            print(f"   Confidence: {getattr(intent_response, 'confidence', 'N/A')}")
            
            # Step 2: Convert to speech with ElevenLabs
            print("2. 🎵 Converting to speech with ElevenLabs...")
            audio = await elevenlabs_service.generate_speech(intent_response.processed_response)
            
            if audio:
                # Convert generator to bytes
                audio_bytes = b''.join([chunk for chunk in audio])
                
                # Save to file
                filename = f"pipeline_test_{i}.mp3"
                with open(filename, "wb") as f:
                    f.write(audio_bytes)
                
                print(f"✅ Generated: {len(audio_bytes)} bytes")
                print(f"💾 Saved: {filename}")
                print("🔊 Play this file to hear the AI's response!")
                
            else:
                print("❌ Failed to generate audio")
                
        except Exception as e:
            print(f"❌ Error in pipeline: {e}")
            import traceback
            traceback.print_exc()
        
        print("=" * 50)
        await asyncio.sleep(1)  # Brief pause between tests

    print("\n🎉 Pipeline test completed! Check the generated MP3 files.")

if __name__ == "__main__":
    asyncio.run(test_complete_ai_pipeline())