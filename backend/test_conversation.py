# test_conversation.py
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.conversation_service import conversation_service
from app.models.conversation import ConversationState
from app.models.intent_model import IntentResponse, IntentType

async def test_conversation_flow():
    print("🧪 Testing Conversation Logic...\n")
    
    # Initialize a fresh conversation state
    current_state = ConversationState()
    
    # Test Scenario 1: User wants to cancel but doesn't provide enough info
    print("1. User says: 'I want to cancel my appointment'")
    intent_response_1 = IntentResponse(
        intent=IntentType.CANCEL_APPOINTMENT,
        entities={},  # Empty - no details provided
        confidence=0.95,
        raw_transcript="I want to cancel my appointment",
        processed_response=""
    )
    
    response_1, new_state_1 = await conversation_service.process_intent(intent_response_1, current_state)
    print(f"   AI should ask for missing info: {response_1}")
    print(f"   Conversation state updated: {new_state_1.dict()}\n")
    
    # Test Scenario 2: User provides their name
    print("2. User says: 'My name is John Doe'")
    intent_response_2 = IntentResponse(
        intent=IntentType.CANCEL_APPOINTMENT,  # Same intent!
        entities={"patient_name": "John Doe"}, # GPT might extract this
        confidence=0.95,
        raw_transcript="My name is John Doe",
        processed_response=""
    )
    
    response_2, new_state_2 = await conversation_service.process_intent(intent_response_2, new_state_1)
    print(f"   AI should ask for next missing info: {response_2}")
    print(f"   Conversation state updated: {new_state_2.dict()}\n")
    
    # Test Scenario 3: User provides the date
    print("3. User says: 'It's for this Friday'")
    intent_response_3 = IntentResponse(
        intent=IntentType.CANCEL_APPOINTMENT,
        entities={"date": "2024-01-26"}, # Assuming GPT extracts the date
        confidence=0.95,
        raw_transcript="It's for this Friday",
        processed_response=""
    )
    
    response_3, new_state_3 = await conversation_service.process_intent(intent_response_3, new_state_2)
    print(f"   AI should confirm action: {response_3}")
    print(f"   Conversation state should be reset: {new_state_3.dict()}\n")
    
    print("✅ Conversation flow test completed!")

if __name__ == "__main__":
    asyncio.run(test_conversation_flow())