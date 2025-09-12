# test_conversation.py
import asyncio
import sys
import os

# Add the app directory to the Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.conversation_service import conversation_service
from app.models.intent_model import IntentResponse, IntentType

async def test_conversation_flow():
    """Test the multi-turn conversation logic"""
    print("🧪 Testing Conversation Service...\n")
    
    # Simulate a unique session (like a WebSocket connection ID)
    test_session_id = "test_session_123"
    
    # TEST 1: User starts a booking but only provides their name
    print("1. User says: 'Hi, my name is Tausha and I want to book an appointment.'")
    intent_response_1 = IntentResponse(
        intent=IntentType.BOOK_APPOINTMENT,
        entities={"patient_name": "Tausha"},  # Only name provided
        confidence=0.95,
        raw_transcript="Hi my name is Tausha and I want to book an appointment",
        processed_response=""
    )
    
    result_1, should_speak_1 = await conversation_service.process_intent(intent_response_1, test_session_id)
    print(f"   AI should ask for: '{result_1}'")
    print(f"   Should speak: {should_speak_1}\n")
    
    # TEST 2: User responds with the doctor's name
    print("2. User says: 'Dr. Kavin'")
    intent_response_2 = IntentResponse(
        intent=IntentType.BOOK_APPOINTMENT,  # Same intent!
        entities={},  # No entities extracted from just "Dr. Kavin"
        confidence=0.3,  # Low confidence because it's not a full sentence
        raw_transcript="Dr. Kavin",  # This is the key - the raw answer
        processed_response=""
    )
    
    result_2, should_speak_2 = await conversation_service.process_intent(intent_response_2, test_session_id)
    print(f"   AI should ask for: '{result_2}'")
    print(f"   Should speak: {should_speak_2}\n")
    
    # TEST 3: User provides the date
    print("3. User says: 'Tomorrow at 4 PM'")
    intent_response_3 = IntentResponse(
        intent=IntentType.BOOK_APPOINTMENT,
        entities={"date": "2024-01-15", "time": "16:00"},  # OpenAI extracts this
        confidence=0.95,
        raw_transcript="Tomorrow at 4 PM",
        processed_response=""
    )
    
    result_3, should_speak_3 = await conversation_service.process_intent(intent_response_3, test_session_id)
    print(f"   AI should confirm: '{result_3}'")
    print(f"   Should speak: {should_speak_3}\n")

if __name__ == "__main__":
    asyncio.run(test_conversation_flow())